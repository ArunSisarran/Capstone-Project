import json
import urllib.error
import urllib.request
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.models import Ingredient
from app.schemas.schemas import ScanOut
from app.services.vocabulary import resolve

router = APIRouter(prefix="/scan", tags=["scan"])

MAX_IMAGE_BYTES = 20_000_000  # same limit as serve.py -Arun


def call_vision(image: bytes) -> dict:
    """Sends the photo to serve.py /detect and returns its JSON. -Arun"""
    request = urllib.request.Request(f"{settings.vision_url.rstrip('/')}/detect", data=image, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:  # longer than serve.py's 15 s Gemini wait -Arun
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code in (400, 413):
            raise HTTPException(status_code=error.code, detail="Send one JPEG or PNG photo, at most 20 MB.")
        raise HTTPException(status_code=502, detail="The ingredient detector failed.")
    except (urllib.error.URLError, TimeoutError):
        raise HTTPException(status_code=503, detail="The ingredient detector is not running.")


def canonical_name(detected: str) -> Optional[str]:
    """Maps a detected name to its Ingredient table name, or None. -Arun"""
    record = resolve(detected)
    if record is None or record.is_staple or record.ignore_for_matching:
        return None
    return record.canonical.lower()


@router.post("", response_model=ScanOut)
async def scan(request: Request, db: Session = Depends(get_db)):
    """Takes raw photo bytes and returns the detected ingredients with their ids. -Arun"""
    image = b""
    async for chunk in request.stream():
        image += chunk
        if len(image) > MAX_IMAGE_BYTES:
            raise HTTPException(status_code=413, detail="The photo is over 20 MB.")
    if not image:
        raise HTTPException(status_code=400, detail="Send a photo as the request body.")

    result = await run_in_threadpool(call_vision, image)

    canonical = {item["name"]: canonical_name(item["name"]) for item in result["items"]}
    wanted = [name for name in canonical.values() if name]
    rows = db.query(Ingredient).filter(func.lower(Ingredient.name).in_(wanted)).all()
    ids = {row.name.lower(): row.id for row in rows}

    return ScanOut(
        vlm=result.get("vlm"),
        items=[
            {"name": item["name"], "count": item["count"], "ingredient_id": ids.get(canonical[item["name"]])}
            for item in result["items"]
        ],
    )
