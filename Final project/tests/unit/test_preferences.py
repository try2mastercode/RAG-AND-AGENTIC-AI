import json

from chatbot import preferences


def test_classify_intent_restaurant_request(monkeypatch):
    monkeypatch.setattr(preferences, "complete", lambda prompt, **kw: "restaurant_request")
    assert preferences.classify_intent("Suggest some Italian restaurants") == "restaurant_request"


def test_classify_intent_recipe_request(monkeypatch):
    monkeypatch.setattr(preferences, "complete", lambda prompt, **kw: "recipe_request")
    assert preferences.classify_intent("How do I make pad thai?") == "recipe_request"


def test_classify_intent_falls_back_to_clarification_on_unexpected_output(monkeypatch):
    monkeypatch.setattr(preferences, "complete", lambda prompt, **kw: "something unrelated")
    assert preferences.classify_intent("hi") == "clarification"


def test_classify_intent_uses_generous_max_tokens(monkeypatch):
    # Regression test: gpt-oss-120b is a reasoning model that spends tokens on hidden
    # chain-of-thought before the visible answer - max_tokens=10 was confirmed to
    # truncate to an empty string every time. Guard against reintroducing a tiny budget.
    captured = {}

    def fake_complete(prompt, **kw):
        captured.update(kw)
        return "restaurant_request"

    monkeypatch.setattr(preferences, "complete", fake_complete)
    preferences.classify_intent("Suggest some Italian restaurants")

    assert captured["max_tokens"] >= 100


def test_extract_preferences_parses_valid_json(monkeypatch):
    payload = {
        "dietary_restrictions": ["vegetarian"],
        "flavor_preferences": ["spicy"],
        "dining_occasion": "casual",
        "price_range": "$",
        "favorite_cuisines": ["Thai"],
    }
    monkeypatch.setattr(preferences, "complete", lambda prompt, **kw: json.dumps(payload))

    result = preferences.extract_preferences("I'm vegetarian, love spicy food, casual and cheap, Thai food")

    assert result == payload


def test_extract_preferences_handles_markdown_fenced_json(monkeypatch):
    payload = {"dietary_restrictions": [], "flavor_preferences": [], "dining_occasion": None, "price_range": None, "favorite_cuisines": []}
    monkeypatch.setattr(preferences, "complete", lambda prompt, **kw: f"```json\n{json.dumps(payload)}\n```")

    result = preferences.extract_preferences("something vague")

    assert result["dietary_restrictions"] == []
    assert result["price_range"] is None


def test_extract_preferences_handles_malformed_json_gracefully(monkeypatch):
    monkeypatch.setattr(preferences, "complete", lambda prompt, **kw: "not json at all")

    result = preferences.extract_preferences("whatever")

    assert result == {
        "dietary_restrictions": [],
        "flavor_preferences": [],
        "dining_occasion": None,
        "price_range": None,
        "favorite_cuisines": [],
    }


def test_extract_preferences_missing_fields_default_to_empty(monkeypatch):
    monkeypatch.setattr(preferences, "complete", lambda prompt, **kw: json.dumps({"dietary_restrictions": ["vegan"]}))

    result = preferences.extract_preferences("I'm vegan")

    assert result["dietary_restrictions"] == ["vegan"]
    assert result["favorite_cuisines"] == []
