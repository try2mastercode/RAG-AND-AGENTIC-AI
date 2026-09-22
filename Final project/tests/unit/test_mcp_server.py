import json

import config
from mcp_app import server

RESTAURANTS = [
    {
        "id": "r001",
        "name": "Green Papaya",
        "cuisine": "Vietnamese",
        "location": "San Jose",
        "price_range": "$$",
        "rating": 4.3,
        "signature_dishes": ["pho"],
        "vibe": ["casual", "lively"],
        "summary": "A pho spot.",
    },
    {
        "id": "r006",
        "name": "Olive & Thyme",
        "cuisine": "Mediterranean",
        "location": "Santa Barbara",
        "price_range": "$$$$",
        "rating": 4.7,
        "signature_dishes": ["branzino"],
        "vibe": ["romantic", "quiet"],
        "summary": "A romantic Mediterranean spot.",
    },
]

USERS = [
    {
        "id": "user_001",
        "name": "Sam Okafor",
        "visit_history": [
            {"restaurant_name": "Green Papaya", "date": "2026-07-02", "rating": 4.3, "comment": "great pho"}
        ],
    }
]

RAW_TEXT = "Green Papaya is a great spot.\n===\nOlive & Thyme is a candlelit, intimate hideaway."


def _setup(tmp_path, monkeypatch):
    restaurants_path = tmp_path / "restaurants.json"
    restaurants_path.write_text(json.dumps(RESTAURANTS), encoding="utf-8")
    users_path = tmp_path / "users.json"
    users_path.write_text(json.dumps(USERS), encoding="utf-8")
    raw_path = tmp_path / "raw.txt"
    raw_path.write_text(RAW_TEXT, encoding="utf-8")

    monkeypatch.setattr(config, "STRUCTURED_RESTAURANTS_FILE", restaurants_path)
    monkeypatch.setattr(config, "USERS_FILE", users_path)
    monkeypatch.setattr(config, "CALIFORNIA_CULINARY_MAP_FILE", raw_path)


def test_california_culinary_map_resource_returns_raw_text(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    assert server.california_culinary_map() == RAW_TEXT


def test_get_restaurant_info_partial_match_returns_json(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    result = json.loads(server.get_restaurant_info("papaya"))
    assert len(result) == 1
    assert result[0]["name"] == "Green Papaya"


def test_get_restaurant_info_no_match_returns_empty_list(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    assert json.loads(server.get_restaurant_info("nonexistent")) == []


def test_recommend_by_vibe_structured_tag_match(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    result = json.loads(server.recommend_by_vibe("romantic"))
    assert len(result) == 1
    assert result[0]["name"] == "Olive & Thyme"


def test_recommend_by_vibe_falls_back_to_raw_text_scan(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    # "intimate" isn't a structured vibe tag on any restaurant, only in the raw text
    result = json.loads(server.recommend_by_vibe("intimate"))
    assert any(r["name"] == "Olive & Thyme" for r in result)


def test_recommend_by_vibe_respects_limit(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    result = json.loads(server.recommend_by_vibe("a", limit=1))  # "a" matches both loosely
    assert len(result) <= 1


def test_get_review_returns_matching_visits(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    result = json.loads(server.get_review("Green Papaya"))
    assert len(result) == 1
    assert result[0]["user"] == "Sam Okafor"
    assert result[0]["comment"] == "great pho"


def test_get_review_no_match_returns_empty_list(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    assert json.loads(server.get_review("Nonexistent Place")) == []
