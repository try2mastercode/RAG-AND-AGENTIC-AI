import json
import logging

from agents.graph import build_graph
from chatbot.preferences import classify_intent, extract_preferences

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_compiled_graph = None

CLARIFICATION_REPLY = (
    "I'd be happy to help! Are you looking for restaurant recommendations, recipe "
    "ideas, or both? Tell me a bit about your preferences (cuisines, dietary "
    "restrictions, budget) and I'll take it from there."
)

SAMPLE_PROMPTS = [
    "I'm vegetarian and love spicy Thai food, any restaurant ideas?",
    "I want to try cooking Vietnamese food at home, got a recipe?",
    "Budget-friendly comfort food for a casual weeknight dinner",
]


def _get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


def respond(message: str) -> str:
    intent = classify_intent(message)
    logger.info("intent=%s message=%r", intent, message)

    if intent == "clarification":
        return CLARIFICATION_REPLY

    preferences = extract_preferences(message)
    logger.info("preferences=%s", preferences)

    initial_state = {
        "user_id": "chat_session",
        "visit_history": [],
        "social_posts": [message, json.dumps(preferences)],
        "errors": [],
    }

    try:
        result = _get_graph().invoke(initial_state)
    except Exception as e:
        logger.error("workflow failed: %s", e)
        return f"Sorry, something went wrong while putting together recommendations: {e}"

    if result.get("errors"):
        logger.warning("workflow completed with errors: %s", result["errors"])

    return result.get("final_recommendations") or "Sorry, I couldn't come up with a recommendation this time."
