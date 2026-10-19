# VisionModel

Ingredient detection (YOLO11s) for pantry/fridge photos.

```
model.py           inspect / selfcheck / surgery / train
serve.py           HTTP service: POST /detect (raw image bytes) -> JSON ingredients
remap_dataset.py   remap a Roboflow dataset onto the canonical ingredient list (local only)
weights/           pretrained starting weights (yolo11s.pt, COCO)
datasets/          training datasets, one folder each with data.yaml
runs/<name>/       one folder per training run: args.json, results.csv, best.pt, last.pt
```

    python model.py selfcheck
    python model.py train --data datasets/X/data.yaml --out runs/X
    python serve.py            # :8000, curl --data-binary @photo.jpg localhost:8000/detect
