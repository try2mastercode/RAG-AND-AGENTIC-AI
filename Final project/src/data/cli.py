import json
import shutil
import time
from pathlib import Path

import config
from data.structuring import new_data_entry_process
from schemas.restaurant import Restaurant


def load_restaurants(path=None) -> list[dict]:
    path = path or config.STRUCTURED_RESTAURANTS_FILE
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def backup_restaurants(path=None) -> Path | None:
    """Current data -> backup -> (caller applies modification) -> save updated data."""
    path = path or config.STRUCTURED_RESTAURANTS_FILE
    if not path.exists():
        return None
    backup_dir = path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{path.stem}.{int(time.time() * 1000)}.json"
    shutil.copy2(path, backup_path)
    return backup_path


def save_restaurants(records: list[dict], path=None) -> None:
    path = path or config.STRUCTURED_RESTAURANTS_FILE
    backup_restaurants(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2), encoding="utf-8")


def next_restaurant_id(records: list[dict]) -> str:
    existing = {r["id"] for r in records}
    idx = len(records) + 1
    candidate = f"r{idx:03d}"
    while candidate in existing:
        idx += 1
        candidate = f"r{idx:03d}"
    return candidate


def find_restaurant(records: list[dict], restaurant_id: str) -> dict | None:
    return next((r for r in records if r["id"] == restaurant_id), None)


def add_restaurant(records: list[dict], raw_text: str) -> list[dict]:
    restaurant_id = next_restaurant_id(records)
    restaurant = new_data_entry_process(raw_text, restaurant_id)
    return records + [restaurant.model_dump()]


def edit_restaurant(records: list[dict], restaurant_id: str, updates: dict) -> list[dict]:
    found = False
    updated = []
    for r in records:
        if r["id"] == restaurant_id:
            found = True
            merged = Restaurant.model_validate({**r, **updates}).model_dump()
            updated.append(merged)
        else:
            updated.append(r)
    if not found:
        raise ValueError(f"no restaurant with id {restaurant_id}")
    return updated


def delete_restaurant(records: list[dict], restaurant_id: str) -> list[dict]:
    updated = [r for r in records if r["id"] != restaurant_id]
    if len(updated) == len(records):
        raise ValueError(f"no restaurant with id {restaurant_id}")
    return updated


def _print_summary(records: list[dict]) -> None:
    if not records:
        print("(no restaurants yet)")
    for r in records:
        print(f"{r['id']}: {r['name']} ({r['cuisine']}, {r['location']}) - {r['price_range']} - {r['rating']}")


def _confirm(prompt: str) -> bool:
    return input(f"{prompt} [y/N]: ").strip().lower() == "y"


def run_cli() -> None:
    records = load_restaurants()
    menu = "\n1. List restaurants\n2. View restaurant\n3. Add restaurant\n4. Edit restaurant\n5. Delete restaurant\n6. Exit\n"

    while True:
        print(menu)
        choice = input("Choose an option: ").strip()

        if choice == "1":
            _print_summary(records)

        elif choice == "2":
            rid = input("Restaurant id: ").strip()
            record = find_restaurant(records, rid)
            print(json.dumps(record, indent=2) if record else f"no restaurant with id {rid}")

        elif choice == "3":
            raw_text = input("Paste the raw restaurant description: ").strip()
            if not raw_text:
                print("empty description, cancelled.")
                continue
            try:
                candidate_records = add_restaurant(records, raw_text)
            except ValueError as e:
                print(f"could not structure that description: {e}")
                continue
            new_entry = candidate_records[-1]
            print(json.dumps(new_entry, indent=2))
            if _confirm(f"Save new restaurant '{new_entry['name']}'?"):
                save_restaurants(candidate_records)
                records = candidate_records
                print("saved.")
            else:
                print("cancelled, nothing was saved.")

        elif choice == "4":
            rid = input("Restaurant id to edit: ").strip()
            record = find_restaurant(records, rid)
            if not record:
                print(f"no restaurant with id {rid}")
                continue
            field = input(f"Field to edit {list(record.keys())}: ").strip()
            if field not in record:
                print("unknown field.")
                continue
            raw_value = input(f"New value for {field}: ").strip()
            if field in {"signature_dishes", "vibe"}:
                new_value = [v.strip() for v in raw_value.split(",") if v.strip()]
            elif field == "rating":
                new_value = float(raw_value)
            else:
                new_value = raw_value
            try:
                candidate_records = edit_restaurant(records, rid, {field: new_value})
            except Exception as e:
                print(f"edit failed validation: {e}")
                continue
            if _confirm(f"Save changes to '{rid}'?"):
                save_restaurants(candidate_records)
                records = candidate_records
                print("saved.")
            else:
                print("cancelled, nothing was saved.")

        elif choice == "5":
            rid = input("Restaurant id to delete: ").strip()
            record = find_restaurant(records, rid)
            if not record:
                print(f"no restaurant with id {rid}")
                continue
            print(f"About to delete: {record['name']}")
            if _confirm("This cannot be undone. Delete?"):
                records = delete_restaurant(records, rid)
                save_restaurants(records)
                print("deleted.")
            else:
                print("cancelled, nothing was deleted.")

        elif choice == "6":
            print("goodbye.")
            break

        else:
            print("unknown option.")


if __name__ == "__main__":
    run_cli()
