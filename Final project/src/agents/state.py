import operator
from typing import Annotated, TypedDict


class RecommendationState(TypedDict, total=False):
    user_id: str
    visit_history: list[dict]
    social_posts: list[str]
    user_profile: str
    retrieved_candidates: dict
    trend_analysis: str
    style_analysis: str
    nutrition_analysis: str
    final_recommendations: str
    # Annotated with a reducer because the three parallel analysis nodes can each
    # append an error in the same graph step - without this, LangGraph rejects
    # concurrent writes to the same key ("InvalidUpdateError: Can receive only one
    # value per step"). Each node returns only its own delta (e.g. [] or [error]),
    # never the accumulated list, and the reducer concatenates them.
    errors: Annotated[list[str], operator.add]
