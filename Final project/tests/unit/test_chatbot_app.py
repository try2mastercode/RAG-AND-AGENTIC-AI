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


def test_respond_returns_clarification_message_for_ambiguous_input(monkeypatch):
    monkeypatch.setattr(app, "classify_intent", lambda message: "clarification")
    assert app.respond("I'm looking for dinner ideas") == app.CLARIFICATION_REPLY


def test_respond_runs_workflow_for_restaurant_request(monkeypatch):
    monkeypatch.setattr(app, "classify_intent", lambda message: "restaurant_request")
    monkeypatch.setattr(app, "extract_preferences", lambda message: {"favorite_cuisines": ["Thai"]})

    class FakeGraph:
        def invoke(self, state):
            assert state["social_posts"][0] == "Thai food please"
            return {"final_recommendations": "Try Spice Route!"}

    monkeypatch.setattr(app, "_get_graph", lambda: FakeGraph())

    result = app.respond("Thai food please")
    assert result == "Try Spice Route!"


def test_respond_handles_workflow_failure_gracefully(monkeypatch):
    monkeypatch.setattr(app, "classify_intent", lambda message: "recipe_request")
    monkeypatch.setattr(app, "extract_preferences", lambda message: {})

    class FailingGraph:
        def invoke(self, state):
            raise RuntimeError("groq is down")

    monkeypatch.setattr(app, "_get_graph", lambda: FailingGraph())

    result = app.respond("give me a recipe")
    assert "groq is down" in result


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
