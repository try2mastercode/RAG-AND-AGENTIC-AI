import json

from fastapi.testclient import TestClient

import config
from api.main import app
from chatbot import service

SAMPLE_RECORDS = [
    {
        "id": "r001",
        "name": "Mock Diner",
        "cuisine": "American",
        "location": "Testville",
        "price_range": "$$",
        "rating": 4.1,
        "signature_dishes": ["burger"],
        "vibe": ["casual"],
        "summary": "A mock diner.",
    }
]

client = TestClient(app)


def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_sample_prompts():
    res = client.get("/api/sample-prompts")
    assert res.status_code == 200
    assert res.json()["prompts"] == service.SAMPLE_PROMPTS


def test_chat_returns_reply(monkeypatch):
    monkeypatch.setattr("api.main.respond", lambda message: f"echo: {message}")
    res = client.post("/api/chat", json={"message": "hi"})
    assert res.status_code == 200
    assert res.json() == {"reply": "echo: hi"}


def test_chat_rejects_empty_message():
    res = client.post("/api/chat", json={"message": ""})
    assert res.status_code == 422


def test_list_restaurants(tmp_path, monkeypatch):
    path = tmp_path / "restaurants.json"
    path.write_text(json.dumps(SAMPLE_RECORDS), encoding="utf-8")
    monkeypatch.setattr(config, "STRUCTURED_RESTAURANTS_FILE", path)

    res = client.get("/api/restaurants")
    assert res.status_code == 200
    assert res.json() == SAMPLE_RECORDS


def test_get_restaurant_not_found(tmp_path, monkeypatch):
    path = tmp_path / "restaurants.json"
    path.write_text(json.dumps(SAMPLE_RECORDS), encoding="utf-8")
    monkeypatch.setattr(config, "STRUCTURED_RESTAURANTS_FILE", path)

    res = client.get("/api/restaurants/does-not-exist")
    assert res.status_code == 404


def test_create_restaurant(tmp_path, monkeypatch):
    path = tmp_path / "restaurants.json"
    path.write_text(json.dumps(SAMPLE_RECORDS), encoding="utf-8")
    monkeypatch.setattr(config, "STRUCTURED_RESTAURANTS_FILE", path)
    monkeypatch.setattr(
        "api.main.add_restaurant",
        lambda records, raw_text: records + [{**SAMPLE_RECORDS[0], "id": "r002", "name": "New Spot"}],
    )

    res = client.post("/api/restaurants", json={"raw_text": "a new place"})
    assert res.status_code == 201
    assert res.json()["name"] == "New Spot"
    assert len(json.loads(path.read_text(encoding="utf-8"))) == 2


def test_update_restaurant(tmp_path, monkeypatch):
    path = tmp_path / "restaurants.json"
    path.write_text(json.dumps(SAMPLE_RECORDS), encoding="utf-8")
    monkeypatch.setattr(config, "STRUCTURED_RESTAURANTS_FILE", path)

    res = client.put("/api/restaurants/r001", json={"updates": {"rating": 4.9}})
    assert res.status_code == 200
    assert res.json()["rating"] == 4.9


def test_delete_restaurant(tmp_path, monkeypatch):
    path = tmp_path / "restaurants.json"
    path.write_text(json.dumps(SAMPLE_RECORDS), encoding="utf-8")
    monkeypatch.setattr(config, "STRUCTURED_RESTAURANTS_FILE", path)

    res = client.delete("/api/restaurants/r001")
    assert res.status_code == 204
    assert json.loads(path.read_text(encoding="utf-8")) == []


def test_delete_restaurant_not_found(tmp_path, monkeypatch):
    path = tmp_path / "restaurants.json"
    path.write_text(json.dumps(SAMPLE_RECORDS), encoding="utf-8")
    monkeypatch.setattr(config, "STRUCTURED_RESTAURANTS_FILE", path)

    res = client.delete("/api/restaurants/does-not-exist")
    assert res.status_code == 404
