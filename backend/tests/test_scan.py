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
    assert response.json() == {"vlm": "gemini", "suggestions": [], "items": [
        {"name": "Apple", "count": 3, "ingredient_id": apple_id},
        {"name": "Kale", "count": 1, "ingredient_id": None},
        {"name": "Salt", "count": 1, "ingredient_id": None},
    ]}


def test_scan_returns_only_usable_suggestions_once_each(client, db, monkeypatch):
    db.add_all([Ingredient(name="apple"), Ingredient(name="milk")])
    db.commit()
    ids = {row.name: row.id for row in db.query(Ingredient).all()}

    # Milk maps to a row; Kale has none and Salt is ignored; Apple is already detected; the second Milk is a repeat
    monkeypatch.setattr(scan, "call_vision", lambda image: {"vlm": "gemini", "items": [
        {"name": "Apple", "count": 1},
    ], "suggestions": ["Milk", "Kale", "Salt", "Apple", "Milk"]})
    response = client.post("/scan", content=b"fake image bytes")

    assert response.status_code == 200
    assert response.json()["suggestions"] == [{"name": "Milk", "ingredient_id": ids["milk"]}]


def test_scan_is_rate_limited_per_client(client, monkeypatch):
    monkeypatch.setattr(scan, "call_vision", lambda image: {"vlm": "off", "items": []})

    # the limit is 5 per minute: the first five get through, the sixth is blocked
    for _ in range(5):
        assert client.post("/scan", content=b"fake image bytes").status_code == 200
    blocked = client.post("/scan", content=b"fake image bytes")

    assert blocked.status_code == 429
    assert "detail" in blocked.json()


def test_scan_rejects_an_empty_body(client):
    assert client.post("/scan", content=b"").status_code == 400


def test_scan_reports_when_the_vision_service_is_down(client, monkeypatch):
    monkeypatch.setattr(settings, "vision_url", "http://127.0.0.1:9")  # nothing listens on port 9 -Arun
    assert client.post("/scan", content=b"fake image bytes").status_code == 503