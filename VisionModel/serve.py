"""Ingredient-detection HTTP service: YOLO + Gemini on every photo, merged.

    python serve.py [--weights runs/merged-v2/best.pt] [--port 8000] [--vlm gemini-3.6-flash|off] [--vlm-rpm 5]
    curl --data-binary @fridge.jpg http://localhost:8000/detect
    python serve.py check
    python serve.py prelabel PHOTOS OUT

GEMINI_API_KEY comes from the environment, else from .env next to this file.

POST /detect returns:
    {"model_version", "vlm": <model id> | "unavailable" | "off", "image": {"width", "height"},
     "items": [{"name", "count", "max_confidence", "source": "both" | "model" | "vlm"}],
     "suggestions": [name],
     "detections": [{"name", "class_id", "confidence", "box": [x1, y1, x2, y2]}]}
"""
import argparse, base64, csv, glob, io, json, os, threading, time, urllib.error, urllib.request
from collections import Counter, defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image, ImageOps
from ultralytics import YOLO

DET_CONF = 0.25
ITEM_CONF = 0.4
PRELABEL_CONF = 0.3

INGREDIENTS = Path(__file__).with_name("ingredients.csv")
VLM_MODEL = "gemini-3.6-flash"
VLM_URL = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent"
VLM_TIMEOUT = 15
VLM_MAX_SIDE = 1536
VLM_PROMPT = ("This is a photo of a fridge, freezer or pantry. List every food item visible, including items that are "
              "partly hidden, small, in see-through containers or packaging, or identifiable from their label or packaging. "
              "Use only names from the allowed list, choosing the closest match. "
              "count = how many separate units of it are visible. "
              "Return an empty list only if there is no food in the photo.")
VLM_THINKING = "low"
VLM_RPM = 5
VLM_PAUSE = 60

_yolo_lock = threading.Lock()  # ultralytics predict isn't thread-safe
_vlm_pool = ThreadPoolExecutor(8)
_vlm_lock, _vlm_calls, _vlm_paused_until = threading.Lock(), deque(), 0.0


def load_env(path=Path(__file__).with_name(".env")):
    if path.exists():
        for line in path.read_text().splitlines():
            k, sep, v = line.strip().removeprefix("export ").partition("=")
            if sep and not k.startswith("#"):
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))


def vlm_allowed(rpm=None, now=None):
    rpm, now = rpm or VLM_RPM, time.monotonic() if now is None else now
    with _vlm_lock:
        while _vlm_calls and _vlm_calls[0] <= now - 60:
            _vlm_calls.popleft()
        if now < _vlm_paused_until or len(_vlm_calls) >= rpm:
            return False
        _vlm_calls.append(now)
        return True


def load_ingredients(path=INGREDIENTS):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    names = [r["name"] for r in rows]
    assert len(names) == len(set(names)), f"duplicate names in {path}"
    assert all(r["type"] in ("Discrete", "Bulk") for r in rows), f"type must be Discrete or Bulk in {path}"
    return {r["name"]: r for r in rows}


def predict(model, img, conf):
    img = ImageOps.exif_transpose(img).convert("RGB")
    with _yolo_lock:
        return img, model.predict(img, conf=conf, iou=0.5, agnostic_nms=True, verbose=False)[0]


def ask_vlm(img, names, model, key):
    img = img.copy()
    img.thumbnail((VLM_MAX_SIDE, VLM_MAX_SIDE))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=90)
    schema = {"type": "object", "required": ["items"], "properties": {"items": {"type": "array", "items": {
        "type": "object", "required": ["name", "count"],
        "properties": {"name": {"type": "string", "enum": names}, "count": {"type": "integer", "minimum": 1}}}}}}
    body = {"contents": [{"parts": [
                {"inlineData": {"mimeType": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}},
                {"text": VLM_PROMPT}]}],
            "generationConfig": {"responseMimeType": "application/json", "responseJsonSchema": schema,
                                 "thinkingConfig": {"thinkingLevel": VLM_THINKING}}}
    req = urllib.request.Request(VLM_URL.format(model), json.dumps(body).encode(),
                                 {"Content-Type": "application/json", "x-goog-api-key": key})
    with urllib.request.urlopen(req, timeout=VLM_TIMEOUT) as r:
        parts = json.load(r)["candidates"][0]["content"]["parts"]
    return json.loads("".join(p.get("text", "") for p in parts if not p.get("thought")))["items"]


def merge(dets, vlm, ing):
    sure, seen = defaultdict(lambda: {"count": 0, "max_confidence": 0.0}), defaultdict(float)
    for d in dets:
        seen[d["name"]] = max(seen[d["name"]], d["confidence"])
        if d["confidence"] >= ITEM_CONF:
            sure[d["name"]]["count"] += 1
            sure[d["name"]]["max_confidence"] = max(sure[d["name"]]["max_confidence"], d["confidence"])

    asked = defaultdict(int)
    for v in vlm or []:
        if isinstance(v, dict) and v.get("name") in ing:
            c = v.get("count")
            asked[v["name"]] += c if isinstance(c, int) and c > 0 else 1

    def sheet_name(cls):
        rows = [n for n, r in ing.items() if r["yolo_class"] == cls]
        return rows[0] if len(rows) == 1 else cls

    shared = Counter(ing[n]["yolo_class"] for n in asked)
    items, used = {}, set()
    for n, c in asked.items():
        cls = ing[n]["yolo_class"]
        if cls in sure:  # YOLO's count covers every sheet item sharing its class, so only use it for a lone one
            items[n] = {"count": sure[cls]["count"] if shared[cls] == 1 else c,
                        "max_confidence": sure[cls]["max_confidence"], "source": "both"}
        elif cls in seen:
            items[n] = {"count": c, "max_confidence": seen[cls], "source": "both"}
        else:
            items[n] = {"count": c, "max_confidence": None, "source": "vlm"}
        used.add(cls)
    for cls, it in sure.items():
        if cls not in used:
            items.setdefault(sheet_name(cls), {**it, "source": "model"})
    for n, it in items.items():
        if n in ing and ing[n]["type"] == "Bulk":
            it["count"] = 1
    suggestions = sorted({sheet_name(c) for c in seen if c not in sure and c not in used} - items.keys())
    return [{"name": n, **v} for n, v in sorted(items.items())], suggestions


def detect(model, version, img, ing, ask=None, vlm_name="off"):
    img = ImageOps.exif_transpose(img).convert("RGB")
    global _vlm_paused_until
    future = _vlm_pool.submit(ask, img) if ask and vlm_allowed() else None
    if ask and not future:
        print("vlm skipped: over the rate limit, replying YOLO-only")
    img, r = predict(model, img, DET_CONF)
    dets = [{"name": r.names[int(c)], "class_id": int(c), "confidence": round(float(s), 2),
             "box": [round(v) for v in b.tolist()]}
            for c, s, b in zip(r.boxes.cls, r.boxes.conf, r.boxes.xyxy)]
    vlm = None
    if future:
        try:
            reply = future.result(timeout=VLM_TIMEOUT)
            if not isinstance(reply, list):
                raise ValueError(f"expected a list, got {reply!r:.100}")
            vlm = reply
        except Exception as e:
            detail = e.read()[:300].decode(errors="replace") if isinstance(e, urllib.error.HTTPError) else ""
            if getattr(e, "code", None) == 429:
                _vlm_paused_until = time.monotonic() + VLM_PAUSE
            print(f"vlm failed, replying YOLO-only: {e!r} {detail}")
    items, suggestions = merge(dets, vlm, ing)
    return {"model_version": version, "vlm": vlm_name if vlm is not None else "unavailable" if ask else "off",
            "image": {"width": img.width, "height": img.height},
            "items": items, "suggestions": suggestions, "detections": dets}


def serve(model, version, ing, ask, vlm_name, port):
    class Handler(BaseHTTPRequestHandler):
        def reply(self, code, obj):
            body = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/health":
                self.reply(200, {"ok": True, "model_version": version, "vlm": vlm_name})
            else:
                self.reply(404, {"error": "not found"})

        def do_POST(self):
            if self.path != "/detect":
                return self.reply(404, {"error": "not found"})
            n = int(self.headers.get("Content-Length", 0))
            if not 0 < n <= 20_000_000:
                return self.reply(413 if n else 400, {"error": "send 1 image, at most 20 MB, as the request body"})
            try:
                img = Image.open(io.BytesIO(self.rfile.read(n)))
            except Exception:
                return self.reply(400, {"error": "body is not an image"})
            self.reply(200, detect(model, version, img, ing, ask, vlm_name))

    print(f"serving {version} + vlm {vlm_name} on :{port}")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


def prelabel(model, src, dst):
    dst = Path(dst)
    (dst / "images").mkdir(parents=True, exist_ok=True)
    (dst / "labels").mkdir(exist_ok=True)
    done, skipped, boxes = 0, [], 0
    for f in sorted(Path(src).iterdir()):
        if not f.is_file():
            continue
        try:
            img, r = predict(model, Image.open(f), PRELABEL_CONF)
        except Exception:
            skipped.append(f.name)
            continue
        img.save(dst / "images" / f"{f.stem}.jpg", quality=95)  # saved upright so the boxes match in any importer
        rows = [f"{int(c)} {x:.6f} {y:.6f} {w:.6f} {h:.6f}" for c, (x, y, w, h) in zip(r.boxes.cls, r.boxes.xywhn.tolist())]
        (dst / "labels" / f"{f.stem}.txt").write_text("".join(row + "\n" for row in rows))
        done, boxes = done + 1, boxes + len(rows)
    names = [model.names[i] for i in range(len(model.names))]
    (dst / "data.yaml").write_text(f"nc: {len(names)}\nnames: {json.dumps(names)}\n")  # a JSON list is valid YAML
    print(f"{done} images, {boxes} boxes -> {dst}" + (f"; skipped (not readable): {skipped}" if skipped else ""))
    return done


def check(model, version, ing):
    bad = {r["yolo_class"] for r in ing.values()} - set(model.names.values()) - {""}
    assert not bad, f"ingredients.csv yolo_class not in the model: {bad}"

    d = lambda n, c: {"name": n, "class_id": 0, "confidence": c, "box": [0, 0, 1, 1]}
    dets = [d("Apple", .9), d("Apple", .8), d("Sauce", .7), d("Sauce", .5), d("Tomato", .9),
            d("Egg", .3), d("Garlic", .3), d("Pineapple", .6)]
    vlm = [{"name": "Apple", "count": 3}, {"name": "Ketchup Bottle", "count": 1}, {"name": "Mustard Bottle", "count": 1},
           {"name": "Egg", "count": 6}, {"name": "Canned Soup", "count": 2}, {"name": "Rice", "count": 4},
           {"name": "Cherry Tomatoes", "count": 10}, {"name": "Unicorn", "count": 1}, {"name": "Canned Soup", "count": 1}]
    items, sugg = merge(dets, vlm, ing)
    got = {i["name"]: (i["count"], i["source"]) for i in items}
    assert got == {"Apple": (2, "both"),
                   "Ketchup Bottle": (1, "both"), "Mustard Bottle": (1, "both"),
                   "Egg": (6, "both"),
                   "Canned Soup": (3, "vlm"),
                   "Rice": (1, "vlm"), "Cherry Tomatoes": (1, "both"),
                   "Pineapple": (1, "model")}, got
    assert sugg == ["Garlic (bulb)"], sugg
    assert next(i for i in items if i["name"] == "Canned Soup")["max_confidence"] is None
    items, sugg = merge(dets, None, ing)
    assert {i["name"]: i["source"] for i in items} == {"Apple": "model", "Sauce": "model", "Tomato": "model",
                                                       "Pineapple": "model"}, items
    assert sugg == ["Egg", "Garlic (bulb)"], sugg
    print("merge ok")

    _vlm_calls.clear()
    assert [vlm_allowed(2, now=t) for t in (0, 1, 2, 59, 60.5, 61, 61.5)] == [True, True, False, False, True, True, False]
    _vlm_calls.clear()
    print("rate limit ok")

    path = sorted(glob.glob("datasets/merged-v3/test/images/fridge-object-v3__*"))[0]
    for ask, want in ((None, "off"), (lambda im: [{"name": "Ketchup Bottle", "count": 2}], "fake"),
                      (lambda im: 1 / 0, "unavailable")):
        out = detect(model, version, Image.open(path), ing, ask, "fake")
        json.dumps(out)
        assert set(out) == {"model_version", "vlm", "image", "items", "suggestions", "detections"} and out["vlm"] == want
        assert all(d["confidence"] >= DET_CONF and len(d["box"]) == 4 and d["name"] == model.names[d["class_id"]]
                   for d in out["detections"])
        assert all(i["count"] >= 1 and i["source"] in ("both", "model", "vlm") for i in out["items"])
        assert not set(out["suggestions"]) & {i["name"] for i in out["items"]}
        print(want, json.dumps(out["items"]), out["suggestions"], f"{len(out['detections'])} detections, ok")

    import tempfile
    with tempfile.TemporaryDirectory() as t:
        up = Image.open(path).convert("RGB")
        (Path(t) / "src").mkdir()
        up.save(Path(t) / "src/upright.jpg", quality=95)
        exif = Image.Exif(); exif[0x0112] = 6  # EXIF orientation 6: rotate 90 degrees clockwise to display
        up.rotate(90, expand=True).save(Path(t) / "src/sideways.jpg", quality=95, exif=exif)
        (Path(t) / "src/notes.txt").write_text("not an image")
        assert prelabel(model, Path(t) / "src", Path(t) / "out") == 2
        a, b = ([[float(v) for v in row.split()] for row in (Path(t) / f"out/labels/{n}.txt").read_text().splitlines()]
                for n in ("upright", "sideways"))
        assert a and len(a) == len(b) and all(x[0] == y[0] and max(abs(p - q) for p, q in zip(x[1:], y[1:])) < 0.01
                                              for x, y in zip(sorted(a), sorted(b))), (a, b)
        assert Image.open(Path(t) / "out/images/sideways.jpg").size == up.size
    print("prelabel ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="serve", choices=["serve", "check", "prelabel"])
    ap.add_argument("paths", nargs="*", help="prelabel: PHOTOS_DIR OUT_DIR")
    ap.add_argument("--weights", default="runs/merged-v2/best.pt")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--vlm", default=VLM_MODEL, help="Gemini model id, or 'off' for YOLO only")
    ap.add_argument("--vlm-rpm", type=int, default=VLM_RPM, help="max Gemini calls per minute")
    a = ap.parse_args()
    VLM_RPM = a.vlm_rpm
    load_env()
    model, version, ing = YOLO(a.weights), Path(a.weights).parent.name, load_ingredients()
    if a.cmd == "check":
        check(model, version, ing)
    elif a.cmd == "prelabel":
        prelabel(model, *a.paths)
    else:
        key = os.environ.get("GEMINI_API_KEY")
        if a.vlm != "off" and not key:
            print("WARNING: GEMINI_API_KEY is not set, running YOLO only (pass --vlm off to silence this)")
            a.vlm = "off"
        names = list(ing)
        ask = None if a.vlm == "off" else lambda img: ask_vlm(img, names, a.vlm, key)
        serve(model, version, ing, ask, a.vlm, a.port)
