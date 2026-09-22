import json
import logging

from pydantic import ValidationError

import config
from data.json_utils import extract_json
from llm.groq_client import complete
from llm.prompts import build_extraction_prompt, build_repair_prompt
from schemas.restaurant import Restaurant

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MAX_REPAIR_ATTEMPTS = 3


def load_raw_restaurant_blocks(path=None) -> list[str]:
    path = path or config.CALIFORNIA_CULINARY_MAP_FILE
    text = path.read_text(encoding="utf-8")
    return [block.strip() for block in text.split("\n===\n") if block.strip()]


def new_data_entry_process(raw_text: str, restaurant_id: str) -> Restaurant:
    """LLM response -> parse -> validate -> if invalid: repair -> validate again.

    Shared by the M1L1 batch loop below and the M1L3 CLI's "add restaurant" flow,
    so both reuse this one structured-extraction pipeline rather than duplicating it.
    """
    prompt = build_extraction_prompt(raw_text)
    candidate = extract_json(complete(prompt))

    last_error: Exception | None = None
    for attempt in range(MAX_REPAIR_ATTEMPTS + 1):
        try:
            data = json.loads(candidate)
            data["id"] = restaurant_id
            return Restaurant.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = e
            if attempt == MAX_REPAIR_ATTEMPTS:
                break
            logger.warning("repair attempt %d/%d for %s: %s", attempt + 1, MAX_REPAIR_ATTEMPTS, restaurant_id, e)
            candidate = extract_json(complete(build_repair_prompt(candidate, str(e))))

    raise ValueError(f"could not produce valid JSON for {restaurant_id} after {MAX_REPAIR_ATTEMPTS} repairs: {last_error}")


def structure_all_restaurants(save_path=None) -> list[Restaurant]:
    save_path = save_path or config.STRUCTURED_RESTAURANTS_FILE
    raw_blocks = load_raw_restaurant_blocks()
    logger.info("stage started: structuring %d raw restaurant descriptions", len(raw_blocks))

    results: list[Restaurant] = []
    failures: list[dict] = []

    # ---- required loop: generate + validate (+ repair) structured JSON for each restaurant ----
    for idx, raw_text in enumerate(raw_blocks, start=1):
        restaurant_id = f"r{idx:03d}"
        try:
            restaurant = new_data_entry_process(raw_text, restaurant_id)
            results.append(restaurant)
            logger.info("validated %d/%d: %s (%s)", idx, len(raw_blocks), restaurant.name, restaurant.location)
        except ValueError as e:
            failures.append({"index": idx, "id": restaurant_id, "error": str(e)})
            logger.error("skipped %s after repair failures: %s", restaurant_id, e)

    save_path.parent.mkdir(parents=True, exist_ok=True)
    save_path.write_text(json.dumps([r.model_dump() for r in results], indent=2), encoding="utf-8")

    logger.info(
        "stage completed: %d structured, %d failed, saved to %s",
        len(results), len(failures), save_path,
    )
    if failures:
        logger.warning("failures: %s", failures)
    return results


if __name__ == "__main__":
    structure_all_restaurants()
