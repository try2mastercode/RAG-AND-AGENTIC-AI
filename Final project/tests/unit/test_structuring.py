import json

import pytest

from data import structuring

VALID_JSON = json.dumps(
    {
        "name": "Mock Diner",
        "cuisine": "American",
        "location": "Testville",
        "price_range": "$$",
        "rating": 4.1,
        "signature_dishes": ["burger", "fries"],
        "vibe": ["casual"],
        "summary": "A reliable mock diner.",
    }
)

INVALID_JSON = json.dumps({"name": "Broken", "price_range": "cheap"})


def test_new_data_entry_process_succeeds_on_first_try(monkeypatch):
    monkeypatch.setattr(structuring, "complete", lambda prompt, **kw: VALID_JSON)
    restaurant = structuring.new_data_entry_process("some raw text", "r001")
    assert restaurant.id == "r001"
    assert restaurant.name == "Mock Diner"


def test_new_data_entry_process_repairs_after_one_bad_attempt(monkeypatch):
    responses = iter([INVALID_JSON, VALID_JSON])
    monkeypatch.setattr(structuring, "complete", lambda prompt, **kw: next(responses))
    restaurant = structuring.new_data_entry_process("some raw text", "r002")
    assert restaurant.id == "r002"
    assert restaurant.name == "Mock Diner"


def test_new_data_entry_process_gives_up_after_max_repairs(monkeypatch):
    monkeypatch.setattr(structuring, "complete", lambda prompt, **kw: INVALID_JSON)
    with pytest.raises(ValueError):
        structuring.new_data_entry_process("some raw text", "r003")


def test_structure_all_restaurants_writes_only_validated_records(tmp_path, monkeypatch):
    raw_file = tmp_path / "raw.txt"
    raw_file.write_text("Good place one.\n===\nGood place two.", encoding="utf-8")
    monkeypatch.setattr(structuring.config, "CALIFORNIA_CULINARY_MAP_FILE", raw_file)
    monkeypatch.setattr(structuring, "complete", lambda prompt, **kw: VALID_JSON)

    out_path = tmp_path / "restaurants.json"
    results = structuring.structure_all_restaurants(save_path=out_path)

    assert len(results) == 2
    saved = json.loads(out_path.read_text(encoding="utf-8"))
    assert len(saved) == 2
    assert saved[0]["id"] == "r001"
    assert saved[1]["id"] == "r002"


def test_structure_all_restaurants_skips_unrepairable_entries(tmp_path, monkeypatch):
    raw_file = tmp_path / "raw.txt"
    raw_file.write_text("Good place.\n===\nBad place.", encoding="utf-8")
    monkeypatch.setattr(structuring.config, "CALIFORNIA_CULINARY_MAP_FILE", raw_file)

    responses = iter([VALID_JSON] + [INVALID_JSON] * 10)
    monkeypatch.setattr(structuring, "complete", lambda prompt, **kw: next(responses))

    out_path = tmp_path / "restaurants.json"
    results = structuring.structure_all_restaurants(save_path=out_path)

    assert len(results) == 1
    saved = json.loads(out_path.read_text(encoding="utf-8"))
    assert len(saved) == 1
