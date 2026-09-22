import json

import pytest

import config
from data import cli
from schemas.restaurant import Restaurant

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

NEW_RESTAURANT = Restaurant.model_validate(
    {
        "id": "r002",
        "name": "New Spot",
        "cuisine": "Fusion",
        "location": "Testville",
        "price_range": "$",
        "rating": 4.0,
        "signature_dishes": ["special roll"],
        "vibe": ["trendy"],
        "summary": "A new spot.",
    }
)


def test_next_restaurant_id_increments():
    assert cli.next_restaurant_id([]) == "r001"
    assert cli.next_restaurant_id(SAMPLE_RECORDS) == "r002"


def test_add_restaurant_appends(monkeypatch):
    monkeypatch.setattr(cli, "new_data_entry_process", lambda raw_text, rid: NEW_RESTAURANT)
    result = cli.add_restaurant(SAMPLE_RECORDS, "some raw description")
    assert len(result) == 2
    assert result[-1]["name"] == "New Spot"


def test_edit_restaurant_updates_and_revalidates():
    updated = cli.edit_restaurant(SAMPLE_RECORDS, "r001", {"rating": 4.8})
    assert updated[0]["rating"] == 4.8


def test_edit_restaurant_invalid_update_raises():
    with pytest.raises(Exception):
        cli.edit_restaurant(SAMPLE_RECORDS, "r001", {"price_range": "cheap"})


def test_edit_restaurant_unknown_id_raises():
    with pytest.raises(ValueError):
        cli.edit_restaurant(SAMPLE_RECORDS, "does-not-exist", {"rating": 4.0})


def test_delete_restaurant_removes_entry():
    updated = cli.delete_restaurant(SAMPLE_RECORDS, "r001")
    assert updated == []


def test_delete_restaurant_unknown_id_raises():
    with pytest.raises(ValueError):
        cli.delete_restaurant(SAMPLE_RECORDS, "does-not-exist")


def test_backup_restaurants_creates_backup(tmp_path):
    path = tmp_path / "restaurants.json"
    path.write_text(json.dumps(SAMPLE_RECORDS), encoding="utf-8")
    backup_path = cli.backup_restaurants(path)
    assert backup_path is not None
    assert backup_path.exists()
    assert json.loads(backup_path.read_text(encoding="utf-8")) == SAMPLE_RECORDS


def test_backup_restaurants_no_file_returns_none(tmp_path):
    path = tmp_path / "does_not_exist.json"
    assert cli.backup_restaurants(path) is None


def test_save_restaurants_backs_up_before_overwrite(tmp_path):
    path = tmp_path / "restaurants.json"
    path.write_text(json.dumps(SAMPLE_RECORDS), encoding="utf-8")
    new_records = SAMPLE_RECORDS + [NEW_RESTAURANT.model_dump()]

    cli.save_restaurants(new_records, path)

    assert json.loads(path.read_text(encoding="utf-8")) == new_records
    backups = list((tmp_path / "backups").glob("*.json"))
    assert len(backups) == 1
    assert json.loads(backups[0].read_text(encoding="utf-8")) == SAMPLE_RECORDS


def _run_cli_with_inputs(monkeypatch, restaurants_path, inputs):
    monkeypatch.setattr(config, "STRUCTURED_RESTAURANTS_FILE", restaurants_path)
    responses = iter(inputs)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
    cli.run_cli()


def test_cli_add_then_cancel_does_not_save(tmp_path, monkeypatch):
    import config

    path = tmp_path / "restaurants.json"
    path.write_text(json.dumps(SAMPLE_RECORDS), encoding="utf-8")
    monkeypatch.setattr(cli, "new_data_entry_process", lambda raw_text, rid: NEW_RESTAURANT)

    _run_cli_with_inputs(
        monkeypatch,
        path,
        inputs=["3", "a raw description of a new place", "n", "6"],
    )

    assert json.loads(path.read_text(encoding="utf-8")) == SAMPLE_RECORDS
    assert not (tmp_path / "backups").exists()


def test_cli_add_then_confirm_saves(tmp_path, monkeypatch):
    import config

    path = tmp_path / "restaurants.json"
    path.write_text(json.dumps(SAMPLE_RECORDS), encoding="utf-8")
    monkeypatch.setattr(cli, "new_data_entry_process", lambda raw_text, rid: NEW_RESTAURANT)

    _run_cli_with_inputs(
        monkeypatch,
        path,
        inputs=["3", "a raw description of a new place", "y", "6"],
    )

    saved = json.loads(path.read_text(encoding="utf-8"))
    assert len(saved) == 2
    assert saved[-1]["name"] == "New Spot"


def test_cli_delete_then_cancel_keeps_record(tmp_path, monkeypatch):
    import config

    path = tmp_path / "restaurants.json"
    path.write_text(json.dumps(SAMPLE_RECORDS), encoding="utf-8")

    _run_cli_with_inputs(
        monkeypatch,
        path,
        inputs=["5", "r001", "n", "6"],
    )

    assert json.loads(path.read_text(encoding="utf-8")) == SAMPLE_RECORDS


def test_cli_delete_then_confirm_removes_record(tmp_path, monkeypatch):
    import config

    path = tmp_path / "restaurants.json"
    path.write_text(json.dumps(SAMPLE_RECORDS), encoding="utf-8")

    _run_cli_with_inputs(
        monkeypatch,
        path,
        inputs=["5", "r001", "y", "6"],
    )

    assert json.loads(path.read_text(encoding="utf-8")) == []
