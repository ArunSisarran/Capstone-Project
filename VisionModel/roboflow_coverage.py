"""
roboflow_coverage.py  --  vet Roboflow datasets against the ingredient class list.

Step 1  (download)  Pull the candidate datasets from Roboflow in YOLO format.
Step 2  (map)       Read each dataset's data.yaml (+ label files), match class names
                    to the ingredient sheet, and write:
                      - <out>/ingredient_list_filled.csv   sheet with 'In Roboflow Dataset?' filled
                      - <out>/coverage_report.md           gaps, review items, low-data classes
                      - <out>/class_map.json               source class -> ingredient (for the merge step)

Setup:
    pip install pyyaml roboflow          # roboflow only needed for `download`

    Create a .env file next to this script (needs a free Roboflow API key:
    app.roboflow.com -> Settings -> API Keys):
        ROBOFLOW_API_KEY=xxxx
    Don't commit .env -- add it to .gitignore.

Usage:
    # 1. download (reads the key from .env automatically)
    python roboflow_coverage.py download --out datasets/

    # 2. map  (export the 'Ingredient List' tab of the Google Sheet as CSV first)
    python roboflow_coverage.py map --ingredients "Ingredient List.csv" \
        --datasets datasets/ --out results/

You can also skip `download` and drop any YOLO-format export folders (each containing
data.yaml) under datasets/ yourself -- `map` picks up every <datasets>/*/data.yaml.
"""

import argparse
import csv
import difflib
import json
import os
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

# --------------------------------------------------------------------------- config

# (workspace, project, version, local folder name)
# Check the version numbers on each project's page (use the latest one).
# grocery-ipcry shows 0 versions: open it in Roboflow, fork it, and generate a
# version first, then point this entry at your fork.
DATASETS = [
    ("wonkeun-jung-vfcwn", "ingredients-agbcq", 1, "ingredients"),
    ("food-recipe-ingredient-images-0gnku", "food-ingredients-dataset", 4, "food-ingredients"),
    ("theplacetoputprojects", "grocery-ipcry", 1, "grocery-ipcry"),
    ("fvd-v4-with-split", "fruits-and-vegetables-pufaj", 3, "fvd"),
]

# source-class name -> sheet ingredient name. Keys/values go through the same
# normalization as everything else (case, plurals, punctuation ignored).
SYNONYMS = {
    "capsicum": "bell pepper",
    "brinjal": "eggplant",
    "aubergine": "eggplant",
    "beetroot": "beet",
    "minced meat": "ground beef",
    "ground meat": "ground beef",
    "mayonnaise": "mayo",
    "mayonaise": "mayo",
    "coriander": "cilantro",
    "cornflakes": "cereal",
    "corn flakes": "cereal",
    "yoghurt": "yogurt",
    "grated cheese": "shredded cheese",
    "baby tomato": "cherry tomatoes",
    "green peas": "peas",
    "garden peas": "peas",
    "butternut squash": "squash",
    "acorn squash": "squash",
    "spring onion": "onion",
    "hot dog": "sausage",
    "strawberry": "berries",
    "blueberry": "berries",
}

# words dropped when trying a "modifier-stripped" match ("whole-onions" -> "onion")
MODIFIERS = {"fresh", "whole", "raw", "organic"}
STOP = {"of", "and", "the"}
FUZZY_THRESHOLD = 0.90
LABEL_SPLITS = ("train", "valid", "val", "test")

# --------------------------------------------------------------------------- normalization


def singular(t):
    if len(t) <= 3:
        return t
    if t.endswith("ies"):
        return t[:-3] + "y"
    if t.endswith("oes"):
        return t[:-2]
    if t.endswith("s") and not t.endswith(("ss", "us", "is")):
        return t[:-1]
    return t


def tokens(s):
    s = re.sub(r"\([^)]*\)", " ", s)  # drop parentheticals: "Lemon (Nimbu)" -> "Lemon"
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("&", " and ")
    return [singular(t) for t in re.findall(r"[a-z0-9]+", s) if t not in STOP]


def norm(s):
    return " ".join(tokens(s))


def strip_mod(n):
    return " ".join(t for t in n.split() if t not in MODIFIERS)


SYN = {norm(k): norm(v) for k, v in SYNONYMS.items()}

# --------------------------------------------------------------------------- .env


def load_dotenv(path=".env"):
    """Minimal .env reader: KEY=VALUE per line, '#' comments, no external dependency.
    Only sets variables not already present in the real environment, so an
    `export ROBOFLOW_API_KEY=...` still wins if both exist.
    """
    p = Path(path)
    if not p.is_file():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        os.environ.setdefault(key, val)


# --------------------------------------------------------------------------- step 1


def cmd_download(args):
    try:
        from roboflow import Roboflow
    except ImportError:
        sys.exit("pip install roboflow  (needed for the download step)")
    load_dotenv(args.env_file)
    key = args.api_key or os.environ.get("ROBOFLOW_API_KEY")
    if not key:
        sys.exit(f"No API key found. Add ROBOFLOW_API_KEY=xxxx to {args.env_file}, "
                  f"or pass --api-key, or export ROBOFLOW_API_KEY.")
    rf = Roboflow(api_key=key)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for ws, proj, ver, name in DATASETS:
        dest = out / name
        if (dest / "data.yaml").exists():
            print(f"[skip] {name}: already downloaded")
            continue
        print(f"[download] {ws}/{proj} v{ver} -> {dest}")
        try:
            rf.workspace(ws).project(proj).version(ver).download("yolov8", location=str(dest))
        except Exception as e:  # keep going so one bad dataset doesn't block the rest
            print(f"  FAILED: {e}\n  (check the version number in DATASETS, or fork the "
                  f"project into your own workspace first)")
    print("done. next: python roboflow_coverage.py map ...")


# --------------------------------------------------------------------------- step 2


def load_dataset(ddir):
    """Return list of (class_id, name, instances, images) for one YOLO export."""
    import yaml

    cfg = yaml.safe_load((ddir / "data.yaml").read_text(encoding="utf-8"))
    names = cfg.get("names", [])
    if isinstance(names, dict):
        names = [names[k] for k in sorted(names, key=int)]
    inst = defaultdict(int)
    imgs = defaultdict(int)
    have_labels = False
    for split in LABEL_SPLITS:
        ldir = ddir / split / "labels"
        if not ldir.is_dir():
            continue
        have_labels = True
        for f in ldir.glob("*.txt"):
            seen = set()
            for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
                parts = line.split()
                if not parts:
                    continue
                try:
                    cid = int(float(parts[0]))
                except ValueError:
                    continue
                inst[cid] += 1
                seen.add(cid)
            for cid in seen:
                imgs[cid] += 1
    return [
        (i, str(n), inst[i] if have_labels else None, imgs[i] if have_labels else None)
        for i, n in enumerate(names)
    ]


def read_sheet(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = list(reader.fieldnames)
        rows = list(reader)

    def col(label):
        for c in fields:
            if c.strip().lower() == label:
                return c
        return None

    ing_col = col("ingredient")
    if not ing_col:
        sys.exit(f"No 'Ingredient' column found. Columns: {fields}")
    return fields, rows, {
        "ingredient": ing_col,
        "category": col("category"),
        "type": col("type (discrete/bulk)"),
        "flag": col("in roboflow dataset?"),
    }


def build_index(rows, ing_col):
    """normalized variant -> set(row index). Splits 'A/B' names, adds modifier-stripped forms."""
    index = defaultdict(set)
    ing_tokens = {}
    for i, r in enumerate(rows):
        name = (r.get(ing_col) or "").strip()
        if not name:
            continue
        base = re.sub(r"\([^)]*\)", " ", name)
        ing_tokens[i] = set(tokens(name))
        for part in base.split("/"):
            n = norm(part)
            if not n:
                continue
            index[n].add(i)
            st = strip_mod(n)
            if st:
                index[st].add(i)
    return index, ing_tokens


def match_source(name, index, ing_tokens, rows, ing_col):
    """Return (kind, [row indices]) with kind in confident|review|none."""
    s = norm(name)
    if not s:
        return "none", []
    hits = {}

    def add(key, kind):
        for i in index.get(key, ()):
            hits.setdefault(i, kind)

    add(s, "exact")
    if s in SYN:
        add(SYN[s], "synonym")
    st = strip_mod(s)
    if st and st != s:
        add(st, "modifier")
        if st in SYN:
            add(SYN[st], "synonym")
    if hits:
        return "confident", sorted(hits)

    # fuzzy (typos like "brocoli") -> always flagged for review
    keys = [k for k in index if len(k) >= 5 and len(s) >= 5]
    best, best_r = [], 0.0
    for k in keys:
        r = difflib.SequenceMatcher(None, s, k).ratio()
        if r > best_r + 1e-9:
            best, best_r = [k], r
        elif abs(r - best_r) <= 1e-9:
            best.append(k)
    if best_r >= FUZZY_THRESHOLD:
        return "review", sorted({i for k in best for i in index[k]})

    # token containment -> review
    S = set(s.split())
    cands = []
    for i, I in ing_tokens.items():
        if not I:
            continue
        fwd = len(I) >= 2 and I <= S           # "chicken breast diced" contains "chicken breast"
        rev = S <= I and len(I) >= 2           # "pasta sauce" is inside "jar pasta sauce"
        if fwd or rev:
            iname = norm(rows[i][ing_col])
            cands.append((difflib.SequenceMatcher(None, s, iname).ratio(), i))
    cands.sort(reverse=True)
    if cands:
        return "review", [i for _, i in cands[:4]]
    return "none", []


def cmd_map(args):
    fields, rows, cols = read_sheet(args.ingredients)
    ing_col = cols["ingredient"]
    index, ing_tokens = build_index(rows, ing_col)

    root = Path(args.datasets)
    dirs = sorted(p.parent for p in root.glob("*/data.yaml"))
    if not dirs:
        sys.exit(f"No <dataset>/data.yaml found under {root}. Run `download` first.")

    confirmed = defaultdict(list)   # row idx -> [(dataset, source, instances, images)]
    review = defaultdict(list)
    class_map = {}
    unmapped = []                   # (dataset, name, instances)
    dupes = []

    for d in dirs:
        ds = d.name
        classes = load_dataset(d)
        cm = {"confirmed": {}, "review": {}, "unmapped": []}
        per_ing = defaultdict(list)
        for cid, name, inst, imgs in classes:
            kind, idxs = match_source(name, index, ing_tokens, rows, ing_col)
            if kind == "confident":
                cm["confirmed"][name] = [rows[i][ing_col].strip() for i in idxs]
                for i in idxs:
                    confirmed[i].append((ds, name, inst, imgs))
                    per_ing[i].append(name)
            elif kind == "review":
                cm["review"][name] = [rows[i][ing_col].strip() for i in idxs]
                for i in idxs:
                    review[i].append((ds, name, inst, imgs))
            else:
                cm["unmapped"].append(name)
                unmapped.append((ds, name, inst or 0))
        for i, names in per_ing.items():
            if len(names) > 1:
                dupes.append((ds, rows[i][ing_col].strip(), names))
        class_map[ds] = cm
        print(f"[{ds}] {len(classes)} classes: {len(cm['confirmed'])} matched, "
              f"{len(cm['review'])} to review, {len(cm['unmapped'])} unmapped")

    # ---- fill sheet
    flag_col = cols["flag"] or "In Roboflow Dataset?"
    out_fields = list(fields)
    for extra in (flag_col, "Roboflow Sources", "Instances"):
        if extra not in out_fields:
            out_fields.append(extra)

    status = {}
    for i, r in enumerate(rows):
        if not (r.get(ing_col) or "").strip():
            continue
        if i in confirmed:
            st = "Yes"
            src = confirmed[i]
        elif i in review:
            st = "Review"
            src = review[i]
        else:
            st = "No"
            src = []
        status[i] = st
        r[flag_col] = st
        r["Roboflow Sources"] = "; ".join(
            f"{ds}:{n}" + (f"({inst})" if inst is not None else "") for ds, n, inst, _ in src
        )
        known = [inst for _, _, inst, _ in confirmed.get(i, []) if inst is not None]
        r["Instances"] = sum(known) if (st == "Yes" and known) else ""

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "ingredient_list_filled.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=out_fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    (out / "class_map.json").write_text(json.dumps(class_map, indent=2, ensure_ascii=False))

    # ---- report
    write_report(out / "coverage_report.md", rows, cols, status, confirmed, review,
                 unmapped, dupes, args.min_instances)
    print(f"\nWrote {out}/ingredient_list_filled.csv, coverage_report.md, class_map.json")
    tally = defaultdict(int)
    for st in status.values():
        tally[st] += 1
    print(f"Coverage: {tally['Yes']} Yes / {tally['Review']} Review / {tally['No']} No "
          f"of {len(status)} ingredients")


def write_report(path, rows, cols, status, confirmed, review, unmapped, dupes, min_inst):
    ing, cat, typ = cols["ingredient"], cols["category"], cols["type"]
    tally = defaultdict(int)
    for st in status.values():
        tally[st] += 1
    L = ["# Roboflow coverage report", ""]
    L.append(f"**{len(status)} ingredients**: {tally['Yes']} covered, {tally['Review']} need review, "
             f"{tally['No']} not covered.")
    L.append("")

    # by category
    bycat = defaultdict(lambda: defaultdict(int))
    for i, st in status.items():
        bycat[(rows[i].get(cat) or "?") if cat else "all"][st] += 1
    L += ["## By category", "", "| Category | Yes | Review | No |", "|---|---|---|---|"]
    for c, t in bycat.items():
        L.append(f"| {c} | {t['Yes']} | {t['Review']} | {t['No']} |")
    L.append("")

    def label(i):
        r = rows[i]
        t = f" [{r.get(typ)}]" if typ and r.get(typ) else ""
        return f"{r[ing].strip()}{t}"

    L += ["## Not covered (hand-label or find another dataset)", ""]
    for c in bycat:
        miss = [i for i, st in status.items()
                if st == "No" and ((rows[i].get(cat) or "?") if cat else "all") == c]
        if miss:
            L.append(f"- **{c}**: " + ", ".join(label(i) for i in miss))
    L.append("")

    L += ["## Needs review (decide the mapping by hand)", ""]
    for i, st in status.items():
        if st == "Review":
            cands = ", ".join(f"{ds}:{n}" for ds, n, _, _ in review[i])
            L.append(f"- {label(i)}  <-  {cands}")
    L.append("")

    L += [f"## Covered but thin (< {min_inst} instances)", ""]
    thin = []
    for i in confirmed:
        known = [inst for _, _, inst, _ in confirmed[i] if inst is not None]
        if known and sum(known) < min_inst:
            thin.append((sum(known), i))
    for n, i in sorted(thin):
        L.append(f"- {label(i)}: {n} instances")
    if not thin:
        L.append("- none")
    L.append("")

    L += ["## Duplicate source classes that map to one ingredient (merge them)", ""]
    for ds, ing_name, names in dupes:
        L.append(f"- {ds}: {', '.join(names)}  ->  {ing_name}")
    if not dupes:
        L.append("- none")
    L.append("")

    L += ["## Largest source classes not on your list (candidates to add)", ""]
    for ds, n, inst in sorted(unmapped, key=lambda x: -x[2])[:40]:
        L.append(f"- {ds}: {n} ({inst})")
    L.append("")
    path.write_text("\n".join(L), encoding="utf-8")


# --------------------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("download", help="download datasets from Roboflow (YOLO format)")
    d.add_argument("--out", default="datasets")
    d.add_argument("--api-key", help="overrides .env / ROBOFLOW_API_KEY if given")
    d.add_argument("--env-file", default=".env", help="path to .env (default: ./.env)")
    d.set_defaults(fn=cmd_download)

    m = sub.add_parser("map", help="match dataset classes to the ingredient sheet")
    m.add_argument("--ingredients", required=True, help="CSV export of the 'Ingredient List' tab")
    m.add_argument("--datasets", default="datasets", help="folder containing <name>/data.yaml")
    m.add_argument("--out", default="results")
    m.add_argument("--min-instances", type=int, default=100)
    m.set_defaults(fn=cmd_map)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
