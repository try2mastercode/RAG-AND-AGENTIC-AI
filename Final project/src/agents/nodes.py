import logging

from agents.personas import (
    FOOD_STYLE_EXPERT,
    FOOD_TREND_ANALYST,
    NUTRITION_EXPERT,
    RECOMMENDATION_EXPERT,
    USER_PROFILE_GENERATOR,
    AgentPersona,
)
from agents.state import RecommendationState
from llm.groq_client import complete_chat
from retrieval.similarity import retrieve_recipes, retrieve_restaurants

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Few-shot examples for the User Profile Generator, per the M3L1 prompting pattern.
FEW_SHOT_PROFILE_EXAMPLES = """Example 1:
User preference: "I love spicy food"
Extracted profile: Cuisine preferences: Sichuan, Thai, Mexican; Spice tolerance: High

Example 2:
User preference: "I'm trying to eat more plant-based meals"
Extracted profile: Dietary restriction: Vegetarian/Vegan preferred; Health focus: Plant-based nutrition"""


def _system_prompt(persona: AgentPersona) -> str:
    return f"You are the {persona.role}.\n\nGoal: {persona.goal}\n\nBackstory: {persona.backstory}"


def _call_agent(persona: AgentPersona, user_message: str, max_tokens: int = 1200) -> tuple[str, str | None]:
    try:
        return complete_chat(_system_prompt(persona), user_message, max_tokens=max_tokens), None
    except Exception as e:
        logger.error("%s failed: %s", persona.role, e)
        return f"[{persona.role} analysis unavailable: {e}]", f"{persona.role}: {e}"


def _error_delta(error: str | None) -> list[str]:
    """Returns only the new error to add this step, never the accumulated list -
    the `errors` state key has an Annotated reducer that concatenates deltas, so
    returning the full list here would double-count on every subsequent node."""
    return [error] if error else []


def _format_candidates(candidates: dict) -> str:
    lines = []
    for r in candidates.get("restaurants", []):
        meta = r["metadata"]
        lines.append(f"- Restaurant: {meta['name']} ({meta['cuisine']}, {meta['location']}, {meta['price_range']})")
    for r in candidates.get("recipes", []):
        meta = r["metadata"]
        lines.append(f"- Recipe: {r['document']} ({meta['cuisine']}) - {meta.get('caption', '')}")
    return "\n".join(lines) if lines else "(no candidates retrieved)"


def node_generate_user_profile(state: RecommendationState) -> RecommendationState:
    user_message = (
        f"{FEW_SHOT_PROFILE_EXAMPLES}\n\n"
        f"Visit history: {state.get('visit_history', [])}\n"
        f"Social posts: {state.get('social_posts', [])}\n\n"
        "Extract a comprehensive profile covering favorite cuisines, dietary "
        "restrictions, price sensitivity, and dining patterns."
    )
    profile, error = _call_agent(USER_PROFILE_GENERATOR, user_message)
    logger.info("user profile generated (%d chars)", len(profile))
    return {"user_profile": profile, "errors": _error_delta(error)}


def node_retrieve_candidates(state: RecommendationState) -> RecommendationState:
    profile = state.get("user_profile", "")
    restaurants = retrieve_restaurants(profile, k=10)
    recipes = retrieve_recipes(profile, k=10)
    candidates = {"restaurants": restaurants, "recipes": recipes}
    logger.info("retrieved %d restaurants + %d recipes", len(restaurants), len(recipes))
    return {"retrieved_candidates": candidates}


def node_analyze_trends(state: RecommendationState) -> RecommendationState:
    user_message = (
        f"User profile: {state['user_profile']}\n\n"
        f"Candidate restaurants and recipes:\n{_format_candidates(state['retrieved_candidates'])}\n\n"
        "Identify current food trends and emerging patterns reflected in these "
        "candidates, and note which ones feel most timely for this user."
    )
    analysis, error = _call_agent(FOOD_TREND_ANALYST, user_message)
    return {"trend_analysis": analysis, "errors": _error_delta(error)}


def node_analyze_styles(state: RecommendationState) -> RecommendationState:
    user_message = (
        f"User profile: {state['user_profile']}\n\n"
        f"Candidate restaurants and recipes:\n{_format_candidates(state['retrieved_candidates'])}\n\n"
        "Analyze the cuisine types, cooking methods, and flavor profiles of these "
        "candidates relative to the user's preferences."
    )
    analysis, error = _call_agent(FOOD_STYLE_EXPERT, user_message)
    return {"style_analysis": analysis, "errors": _error_delta(error)}


def node_analyze_nutrition(state: RecommendationState) -> RecommendationState:
    user_message = (
        f"User profile: {state['user_profile']}\n\n"
        f"Candidate restaurants and recipes:\n{_format_candidates(state['retrieved_candidates'])}\n\n"
        "Evaluate nutritional fit, allergens, and dietary compliance for these "
        "candidates given the user's dietary restrictions."
    )
    analysis, error = _call_agent(NUTRITION_EXPERT, user_message)
    return {"nutrition_analysis": analysis, "errors": _error_delta(error)}


def node_synthesize_recommendations(state: RecommendationState) -> RecommendationState:
    user_message = (
        f"User profile: {state['user_profile']}\n\n"
        f"Candidates:\n{_format_candidates(state['retrieved_candidates'])}\n\n"
        f"Trend analysis: {state.get('trend_analysis', '')}\n\n"
        f"Style analysis: {state.get('style_analysis', '')}\n\n"
        f"Nutrition analysis: {state.get('nutrition_analysis', '')}\n\n"
        "Synthesize the above into a final list of up to 3 restaurant and 3 recipe "
        "recommendations, each with a one-sentence explanation. Keep the whole answer "
        "under 300 words total so it fits in one response - be concise, not exhaustive."
    )
    # Larger budget than the other agent calls: this response is markdown (headings +
    # tables) which is token-heavy, and a truncated mid-table response reads as broken
    # output to the user rather than just a shorter answer.
    recommendations, error = _call_agent(RECOMMENDATION_EXPERT, user_message, max_tokens=2000)
    return {"final_recommendations": recommendations, "errors": _error_delta(error)}
