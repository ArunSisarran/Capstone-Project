"""
model.py - yolo11s as a plain nn.Module: inspect it, do surgery on it, train it
with your own loop.

Ultralytics' YOLO(...).train() is a wrapper. Underneath, `yolo11s.pt` is a
pickled `DetectionModel` - an `nn.Sequential` of 24 blocks. Everything below
touches that directly, so every knob is visible instead of hidden in a config.

    python model.py inspect      # module tree, params, head shape
    python model.py selfcheck    # asserts the head surgery is correct
    python model.py surgery      # write a re-headed checkpoint, no training
    python model.py train --freeze 10 --epochs 30
"""

import argparse
import csv
import json
import math
import re
import time
from copy import deepcopy
from pathlib import Path

import torch
import torch.nn as nn
from ultralytics.cfg import get_cfg
from ultralytics.data.build import build_dataloader, build_yolo_dataset
from ultralytics.data.utils import check_det_dataset
from ultralytics.utils.loss import v8DetectionLoss
from ultralytics.utils.torch_utils import ModelEMA

HERE = Path(__file__).parent
BACKBONE_END = 10  # yolo11 yaml: layers 0-10 are backbone, 11-23 are head/neck


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------
def load(path="yolo11s.pt"):
    """The checkpoint is a dict; ckpt['model'] is a live nn.Module, not a state_dict."""
    ckpt = torch.load(HERE / path, map_location="cpu", weights_only=False)
    model = ckpt["model"].float()  # ships as fp16
    for p in model.parameters():
        p.requires_grad_(True)  # ships frozen
    return model


# --------------------------------------------------------------------------
# inspect
# --------------------------------------------------------------------------
def cmd_inspect(args):
    model = load(args.weights)
    print(f"{type(model).__name__}: {len(model.model)} blocks, "
          f"{sum(p.numel() for p in model.parameters()):,} params\n")
    print(f"{'i':>3} {'from':>12} {'params':>10}  module")
    for i, m in enumerate(model.model):
        n = sum(p.numel() for p in m.parameters())
        tag = "backbone" if i <= BACKBONE_END else "neck/head"
        print(f"{i:>3} {str(m.f):>12} {n:>10,}  {type(m).__name__:<16} [{tag}]")

    h = model.model[-1]
    print(f"\nDetect head: nc={h.nc} reg_max={h.reg_max} nl={h.nl} "
          f"stride={h.stride.tolist()}")
    print("  cv2[i] -> box branch, outputs 4*reg_max=%d channels (DFL bins)" % (4 * h.reg_max))
    print("  cv3[i] -> cls branch, outputs nc=%d channels (raw logits)" % h.nc)
    for i in range(h.nl):
        print(f"  P{i + 3}: cls conv = {h.cv3[i][2]}  bias[:3] = "
              f"{h.cv3[i][2].bias.data[:3].tolist()}")
    print("\nThose final 1x1 convs are the only class-dependent weights in the net.")
    print("Everything else is class-agnostic feature extraction -> reusable.")


# --------------------------------------------------------------------------
# surgery: replace the 80-class head, warm-starting the classes COCO already knows
# --------------------------------------------------------------------------
def normalize(name):
    """Matching key for class names: 'Hot-Dog!' -> 'hot dog'."""
    s = name.strip().lower()
    s = re.sub(r"[_\-]+", " ", s)
    s = re.sub(r"[^\w\s&]", "", s)
    return re.sub(r"\s+", " ", s).strip()


COCO_ALIASES = {  # coco name -> your canonical name, where normalize() won't match
    "hot dog": "Sausage/Hot Dog Link",
    "broccoli": "Broccoli (head)",
}


def reshape_head(model, names, warm_start=True, verbose=True):
    """Swap Detect's per-scale class convs from 80 -> len(names) outputs.

    The box branch (cv2) is untouched: box regression doesn't know about classes,
    so it transfers for free. Only cv3's last 1x1 conv is class-shaped.
    """
    h = model.model[-1]
    old_names = model.names if isinstance(model.names, dict) else dict(enumerate(model.names))
    nc = len(names)

    # which new class index inherits which old COCO row
    transfer = {}
    if warm_start:
        old_by_norm = {normalize(v): k for k, v in old_names.items()}
        for j, new in enumerate(names):
            for cand in (normalize(new), normalize(COCO_ALIASES.get(normalize(new), ""))):
                if cand and cand in old_by_norm:
                    transfer[j] = old_by_norm[cand]
                    break
        for coco, mine in COCO_ALIASES.items():
            if mine in names and normalize(coco) in old_by_norm:
                transfer.setdefault(names.index(mine), old_by_norm[normalize(coco)])

    for i in range(h.nl):
        old = h.cv3[i][2]
        new = nn.Conv2d(old.in_channels, nc, 1).to(old.weight.device)

        # focal-style prior: start every class predicting ~few objects per image,
        # so the first steps aren't dominated by the background BCE term.
        nn.init.normal_(new.weight, std=0.01)
        new.bias.data.fill_(math.log(5 / nc / (640 / h.stride[i].item()) ** 2))

        for j, k in transfer.items():  # copy the COCO rows we can keep
            new.weight.data[j] = old.weight.data[k]
            new.bias.data[j] = old.bias.data[k]

        h.cv3[i][2] = new

    h.nc = nc
    h.no = nc + h.reg_max * 4
    model.nc = nc
    model.names = dict(enumerate(names))
    model.yaml["nc"] = nc

    if verbose:
        kept = ", ".join(sorted(names[j] for j in transfer)) or "none"
        print(f"head: 80 -> {nc} classes; warm-started {len(transfer)}: {kept}")
    return transfer


def cmd_surgery(args):
    data = check_det_dataset(args.data)
    names = [data["names"][i] for i in sorted(data["names"])]
    model = load(args.weights)
    reshape_head(model, names, warm_start=not args.cold)
    torch.save({"model": model.half(), "names": model.names}, args.out)
    print(f"saved {args.out}")


# --------------------------------------------------------------------------
# training loop
# --------------------------------------------------------------------------
def param_groups(model, decay):
    """YOLO's split: weight decay on conv/linear weights only, never on BN or bias.

    Decaying a BatchNorm scale pulls it toward 0 and quietly kills the channel.
    """
    g_decay, g_nodecay = [], []
    for m in model.modules():
        if isinstance(m, nn.modules.batchnorm._BatchNorm):
            g_nodecay += [p for p in (m.weight, m.bias) if p is not None]
        else:
            if getattr(m, "bias", None) is not None and isinstance(m.bias, nn.Parameter):
                g_nodecay.append(m.bias)
            if getattr(m, "weight", None) is not None and isinstance(m.weight, nn.Parameter):
                g_decay.append(m.weight)
    return [{"params": g_decay, "weight_decay": decay},
            {"params": g_nodecay, "weight_decay": 0.0}]


def freeze_backbone(model, freeze):
    """Layers 0..freeze stop receiving gradients. BN running stats still update
    unless you also .eval() them - that's the classic transfer-learning gotcha."""
    n = 0
    for name, p in model.named_parameters():
        idx = name.split(".")[1]
        if idx.isdigit() and int(idx) <= freeze:
            p.requires_grad_(False)
            n += p.numel()
    return n


def to_device(batch, device):
    batch["img"] = batch["img"].to(device, non_blocking=True).float() / 255
    for k in ("cls", "bboxes", "batch_idx"):
        batch[k] = batch[k].to(device)
    return batch


def cmd_train(args):
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "args.json").write_text(json.dumps(vars(args), indent=2))
    device = torch.device(args.device)
    data = check_det_dataset(args.data)
    names = [data["names"][i] for i in sorted(data["names"])]

    cfg = get_cfg(overrides={"data": args.data, "imgsz": args.imgsz, "batch": args.batch,
                             "mosaic": args.mosaic, "mode": "train", "task": "detect"})

    model = load(args.weights)
    reshape_head(model, names, warm_start=not args.cold)
    model.args = cfg  # v8DetectionLoss reads model.args.box / .cls / .dfl
    model.to(device)

    frozen = freeze_backbone(model, args.freeze) if args.freeze >= 0 else 0
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"frozen {frozen:,} params, training {trainable:,}")

    train_ds = build_yolo_dataset(cfg, data["train"], args.batch, data, mode="train", stride=32)
    val_ds = build_yolo_dataset(cfg, data["val"], args.batch, data, mode="val", stride=32, rect=True)
    train_dl = build_dataloader(train_ds, args.batch, args.workers, shuffle=True)
    val_dl = build_dataloader(val_ds, args.batch, args.workers, shuffle=False)

    crit = v8DetectionLoss(model)
    groups = param_groups(model, args.weight_decay)
    if args.optimizer == "sgd":
        opt = torch.optim.SGD(groups, lr=args.lr0, momentum=0.937, nesterov=True)
    else:
        opt = torch.optim.AdamW(groups, lr=args.lr0, betas=(0.937, 0.999))
    # 0.1 is an SGD number. On AdamW a hot bias lr diverges within ~40 steps
    # (val loss 8 -> 283 here), because Adam already normalizes by grad scale.
    warmup_bias_lr = args.warmup_bias_lr if args.warmup_bias_lr is not None else (
        0.1 if args.optimizer == "sgd" else args.lr0)
    # linear decay lr0 -> lr0*lrf, same shape ultralytics uses by default
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda e: (1 - e / args.epochs) * (1 - args.lrf) + args.lrf)
    scaler = torch.amp.GradScaler("cuda", enabled=device.type == "cuda")
    ema = ModelEMA(model)

    nb = len(train_dl)
    accumulate = max(1, round(args.nbs / args.batch))  # simulate batch=64
    nw = max(3 * nb, 100)  # warmup iterations
    best = float("inf")
    last_opt = -1
    log = out / "results.csv"  # one row per epoch, restarted each run (like last.pt/best.pt)
    with open(log, "w", newline="") as f:
        csv.writer(f).writerow(["epoch", "train_box", "train_cls", "train_dfl", "val_loss", "lr", "elapsed_s"])
    t0 = time.time()

    for epoch in range(args.epochs):
        model.train()
        running = torch.zeros(3, device=device)
        for i, batch in enumerate(train_dl):
            ni = i + nb * epoch
            if ni <= nw:
                # Warmup: biases/BN start hot (0.1) and cool down, weights start at 0
                # and ramp up. Skipping this on a fresh head blows up in ~20 steps.
                a = min(1.0, ni / nw)
                target = sched.get_last_lr()[0]
                for j, g in enumerate(opt.param_groups):
                    start = warmup_bias_lr if j else 0.0
                    g["lr"] = start + a * (target - start)
                accumulate = max(1, round(args.nbs / args.batch * a))

            batch = to_device(batch, device)
            with torch.amp.autocast("cuda", enabled=device.type == "cuda"):
                preds = model(batch["img"])       # dict: boxes, scores, feats (raw, no DFL)
                loss, items = crit(preds, batch)  # 3-vector (box, cls, dfl), already * batch
            scaler.scale(loss.sum()).backward()   # .sum() -> the scalar autograd needs

            if ni - last_opt >= accumulate:
                scaler.unscale_(opt)
                nn.utils.clip_grad_norm_(model.parameters(), 10.0)
                scaler.step(opt)
                scaler.update()
                opt.zero_grad(set_to_none=True)
                ema.update(model)
                last_opt = ni

            running += torch.stack(list(items.values()))
            if i % 50 == 0:
                b, c, d = (running / (i + 1)).tolist()
                print(f"e{epoch} {i}/{nb}  box {b:.3f}  cls {c:.3f}  dfl {d:.3f}  "
                      f"lr {opt.param_groups[0]['lr']:.2e}", flush=True)
            steps = i + 1
            if args.max_steps and steps >= args.max_steps:
                break
        lr = opt.param_groups[0]["lr"]  # the lr this epoch ended on, before the scheduler moves it
        sched.step()

        vl = validate(ema.ema, crit, val_dl, device, args.max_steps)
        print(f"epoch {epoch}: train {(running / steps).sum():.3f}  val {vl:.4f}")
        b, c, d = (running / steps).tolist()
        with open(log, "a", newline="") as f:
            csv.writer(f).writerow([epoch, round(b, 4), round(c, 4), round(d, 4), round(vl, 4),
                                    f"{lr:.3e}", round(time.time() - t0)])
        save(ema.ema, cfg, out / "last.pt")
        if vl < best:
            best = vl
            save(ema.ema, cfg, out / "best.pt")
            print(f"  new best {best:.4f}")

    print(f"\ndone. mAP:  yolo val model={args.out}/best.pt data={args.data}")


@torch.no_grad()
def validate(model, crit, dl, device, max_steps=0):
    model.eval()
    # eval() makes Detect decode boxes; we want the raw maps the loss expects
    total, n = torch.zeros(3, device=device), 0
    for i, batch in enumerate(dl):
        batch = to_device(batch, device)
        with torch.amp.autocast("cuda", enabled=device.type == "cuda"):
            _, items = crit(model(batch["img"]), batch)  # crit unwraps the eval tuple
        total += torch.stack(list(items.values()))
        n += 1
        if max_steps and n >= max_steps:
            break
    return (total / max(n, 1)).sum().item()


def save(model, cfg, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    m = deepcopy(model).half()
    m.args = {k: v for k, v in vars(cfg).items()}
    torch.save({"model": m, "train_args": vars(cfg), "epoch": -1}, path)


# --------------------------------------------------------------------------
# selfcheck
# --------------------------------------------------------------------------
def cmd_selfcheck(args):
    model = load(args.weights)
    old = model.model[-1]
    old_w = deepcopy(old.cv3[0][2].weight.data)
    old_cv2 = deepcopy(old.cv2[0][2].weight.data)
    coco = {v: k for k, v in model.names.items()}

    names = ["Apple", "Banana", "Broccoli (head)", "Sausage/Hot Dog Link", "Tofu Block"]
    transfer = reshape_head(model, names, verbose=False)
    h = model.model[-1]

    assert h.nc == 5 and h.no == 5 + 4 * h.reg_max, "nc/no not updated"
    assert h.cv3[0][2].out_channels == 5, "cls conv not reshaped"
    assert torch.equal(h.cv2[0][2].weight.data, old_cv2), "box branch must be untouched"
    assert set(transfer) == {0, 1, 2, 3}, f"expected 4 warm starts, got {transfer}"
    assert not torch.equal(h.cv3[0][2].weight.data[4], old_w[coco["apple"]]), "Tofu warm-started?"
    for j, coco_name in [(0, "apple"), (1, "banana"), (2, "broccoli"), (3, "hot dog")]:
        assert torch.equal(h.cv3[0][2].weight.data[j], old_w[coco[coco_name]]), coco_name

    x = torch.rand(1, 3, 320, 320)
    model.eval()
    y, raw = model(x)
    # eval mode already applied DFL: 4 xywh + nc, not 4*reg_max + nc
    assert y.shape[1] == 4 + 5, f"decoded forward gives {y.shape}"
    assert raw["scores"].shape[1] == 5, f"raw scores {raw['scores'].shape}"
    assert raw["boxes"].shape[1] == 4 * h.reg_max, f"raw boxes {raw['boxes'].shape}"

    model.train()
    out = model(x)  # train mode returns only the raw dict
    assert out["scores"].shape[1] == 5 and len(out["feats"]) == 3, "train-mode shape"

    n = freeze_backbone(model, BACKBONE_END)
    assert n > 0 and not model.model[0].conv.weight.requires_grad
    assert model.model[-1].cv3[0][2].weight.requires_grad, "head must stay trainable"

    print("selfcheck ok")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--weights", default="yolo11s.pt")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("inspect")
    sub.add_parser("selfcheck")

    s = sub.add_parser("surgery")
    s.add_argument("--data", default="ingredients-top/data.yaml")
    s.add_argument("--out", default="yolo11s-ingredients.pt")
    s.add_argument("--cold", action="store_true", help="skip COCO warm start")

    t = sub.add_parser("train")
    t.add_argument("--data", default="ingredients-top/data.yaml")
    t.add_argument("--out", default="runs/train")
    t.add_argument("--epochs", type=int, default=50)
    t.add_argument("--batch", type=int, default=16)
    t.add_argument("--nbs", type=int, default=64, help="nominal batch to accumulate to")
    t.add_argument("--imgsz", type=int, default=640)
    t.add_argument("--workers", type=int, default=8)
    t.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    t.add_argument("--optimizer", choices=("adamw", "sgd"), default="adamw")
    t.add_argument("--lr0", type=float, default=1e-3, help="use ~0.01 for sgd")
    t.add_argument("--lrf", type=float, default=0.01)
    t.add_argument("--weight-decay", type=float, default=5e-4)
    t.add_argument("--warmup-bias-lr", type=float, default=None)
    t.add_argument("--mosaic", type=float, default=1.0)
    t.add_argument("--freeze", type=int, default=-1, help="freeze layers 0..N (10 = backbone)")
    t.add_argument("--cold", action="store_true")
    t.add_argument("--max-steps", type=int, default=0, help="cut epochs short (smoke test)")

    args = p.parse_args()
    {"inspect": cmd_inspect, "surgery": cmd_surgery,
     "train": cmd_train, "selfcheck": cmd_selfcheck}[args.cmd](args)


if __name__ == "__main__":
    main()
