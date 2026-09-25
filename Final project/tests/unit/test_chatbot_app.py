import json

import config
from chatbot import app

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


def test_add_restaurant_ui_saves_and_reports(tmp_path, monkeypatch):
    path = tmp_path / "restaurants.json"
    path.write_text(json.dumps(SAMPLE_RECORDS), encoding="utf-8")
    monkeypatch.setattr(config, "STRUCTURED_RESTAURANTS_FILE", path)
    monkeypatch.setattr(
        app,
        "add_restaurant",
        lambda records, raw_text: records + [{**SAMPLE_RECORDS[0], "id": "r002", "name": "New Spot"}],
    )

    result = app._add_restaurant_ui("some raw description")

    assert "New Spot" in result
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert len(saved) == 2


def test_add_restaurant_ui_rejects_empty_input():
    assert "paste a restaurant description" in app._add_restaurant_ui("   ")


def test_delete_restaurant_ui_removes_record(tmp_path, monkeypatch):
    path = tmp_path / "restaurants.json"
    path.write_text(json.dumps(SAMPLE_RECORDS), encoding="utf-8")
    monkeypatch.setattr(config, "STRUCTURED_RESTAURANTS_FILE", path)

    result = app._delete_restaurant_ui("r001")

    assert "Deleted r001" in result
    assert json.loads(path.read_text(encoding="utf-8")) == []


def test_delete_restaurant_ui_unknown_id_reports_error(tmp_path, monkeypatch):
    path = tmp_path / "restaurants.json"
    path.write_text(json.dumps(SAMPLE_RECORDS), encoding="utf-8")
    monkeypatch.setattr(config, "STRUCTURED_RESTAURANTS_FILE", path)

    result = app._delete_restaurant_ui("does-not-exist")

    assert "Could not delete" in result


def test_update_rating_ui_updates_and_saves(tmp_path, monkeypatch):
    path = tmp_path / "restaurants.json"
    path.write_text(json.dumps(SAMPLE_RECORDS), encoding="utf-8")
    monkeypatch.setattr(config, "STRUCTURED_RESTAURANTS_FILE", path)

    result = app._update_rating_ui("r001", 4.9)

    assert "Updated r001" in result
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved[0]["rating"] == 4.9
