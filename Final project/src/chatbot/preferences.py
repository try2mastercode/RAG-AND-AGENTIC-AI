import json
import logging

from data.json_utils import extract_json
from llm.groq_client import complete

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

INTENT_CATEGORIES = ["restaurant_request", "recipe_request", "both", "clarification"]


def classify_intent(message: str) -> str:
    prompt = f"""Classify this user message into exactly one of: {', '.join(INTENT_CATEGORIES)}.

Examples:
"Suggest some Italian restaurants" -> restaurant_request
"How do I make pad thai?" -> recipe_request
"I'm vegetarian and love spicy food, what should I eat?" -> both
"I'm looking for dinner ideas" -> clarification

User message: "{message}"

Respond with only the category name, nothing else."""

    # max_tokens must stay generous: gpt-oss-120b is a reasoning model that spends
    # tokens on hidden chain-of-thought before emitting the visible answer - a tight
    # budget here silently truncates to an empty string before the category ever
    # appears (confirmed: max_tokens=10 returned '', max_tokens=200 correctly returned
    # the category).
    response = complete(prompt, max_tokens=200, temperature=0.0).strip().lower()
    for category in INTENT_CATEGORIES:
        if category in response:
            return category
    return "clarification"


def extract_preferences(message: str) -> dict:
    """Converts a free-form user message into structured dining preferences."""
    prompt = f"""Extract user preferences from this message. Return JSON with keys:
dietary_restrictions, flavor_preferences, dining_occasion, price_range, favorite_cuisines.

dietary_restrictions: list of strings
flavor_preferences: list of strings
dining_occasion: string or null
price_range: one of "$", "$$", "$$$", "$$$$", or null
favorite_cuisines: list of strings

Use an empty list or null when a field isn't mentioned. Return ONLY the JSON object.

User message: "{message}"

JSON:"""

    raw = complete(prompt, temperature=0.1)
    try:
        data = json.loads(extract_json(raw))
    except json.JSONDecodeError:
        logger.warning("extract_preferences: could not parse JSON from LLM output: %s", raw)
        data = {}

    return {
        "dietary_restrictions": data.get("dietary_restrictions") or [],
        "flavor_preferences": data.get("flavor_preferences") or [],
        "dining_occasion": data.get("dining_occasion"),
        "price_range": data.get("price_range"),
        "favorite_cuisines": data.get("favorite_cuisines") or [],
    }


if __name__ == "__main__":
    test_message = "I'm vegetarian, love spicy food, and want something casual and affordable."
    print(f"Testing extract_preferences with: {test_message!r}")
    result = extract_preferences(test_message)
    print(json.dumps(result, indent=2))
