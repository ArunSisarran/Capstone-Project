"""Tests for POST /scan. -Arun"""
from app.core.config import settings
from app.models.models import Ingredient
from app.routers import scan


def test_scan_maps_detected_names_to_ingredient_ids(client, db, monkeypatch):
    db.add(Ingredient(name="apple"))
    db.commit()
    apple_id = db.query(Ingredient).one().id

    # Apple matches, Kale is unknown, Salt is ignored for matching -Arun
    monkeypatch.setattr(scan, "call_vision", lambda image: {"vlm": "gemini", "items": [
        {"name": "Apple", "count": 3},
        {"name": "Kale", "count": 1},
        {"name": "Salt", "count": 1},
    ]})
    response = client.post("/scan", content=b"fake image bytes")

    assert response.status_code == 200
    assert response.json() == {"vlm": "gemini", "items": [
        {"name": "Apple", "count": 3, "ingredient_id": apple_id},
        {"name": "Kale", "count": 1, "ingredient_id": None},
        {"name": "Salt", "count": 1, "ingredient_id": None},
    ]}


def test_scan_rejects_an_empty_body(client):
    assert client.post("/scan", content=b"").status_code == 400


def test_scan_reports_when_the_vision_service_is_down(client, monkeypatch):
    monkeypatch.setattr(settings, "vision_url", "http://127.0.0.1:9")  # nothing listens on port 9 -Arun
    assert client.post("/scan", content=b"fake image bytes").status_code == 503
