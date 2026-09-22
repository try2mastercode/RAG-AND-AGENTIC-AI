import logging

from langgraph.graph import END, StateGraph

from agents.nodes import (
    node_analyze_nutrition,
    node_analyze_styles,
    node_analyze_trends,
    node_generate_user_profile,
    node_retrieve_candidates,
    node_synthesize_recommendations,
)
from agents.state import RecommendationState
from agents.user_data import load_all_users, load_user

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def build_graph():
    """Hybrid workflow: sequential -> sequential -> parallel (fan-out/fan-in) -> sequential."""
    graph = StateGraph(RecommendationState)
    graph.add_node("generate_profile", node_generate_user_profile)
    graph.add_node("retrieve_candidates", node_retrieve_candidates)
    graph.add_node("analyze_trends", node_analyze_trends)
    graph.add_node("analyze_styles", node_analyze_styles)
    graph.add_node("analyze_nutrition", node_analyze_nutrition)
    graph.add_node("synthesize", node_synthesize_recommendations)

    graph.set_entry_point("generate_profile")
    graph.add_edge("generate_profile", "retrieve_candidates")
    graph.add_edge("retrieve_candidates", "analyze_trends")
    graph.add_edge("retrieve_candidates", "analyze_styles")
    graph.add_edge("retrieve_candidates", "analyze_nutrition")
    graph.add_edge("analyze_trends", "synthesize")
    graph.add_edge("analyze_styles", "synthesize")
    graph.add_edge("analyze_nutrition", "synthesize")
    graph.add_edge("synthesize", END)

    return graph.compile()


def run_recommendation_workflow(user_id: str) -> RecommendationState:
    user = load_user(user_id)
    initial_state: RecommendationState = {
        "user_id": user_id,
        "visit_history": user.get("visit_history", []),
        "social_posts": user.get("social_posts", []),
        "errors": [],
    }
    app = build_graph()
    return app.invoke(initial_state)


def run_for_all_test_personas() -> None:
    for user in load_all_users():
        logger.info("=== %s (%s) ===", user["name"], user.get("persona", "unknown persona"))
        result = run_recommendation_workflow(user["id"])
        logger.info(result.get("final_recommendations", "(no recommendations produced)"))
        if result.get("errors"):
            logger.warning("errors: %s", result["errors"])


if __name__ == "__main__":
    run_for_all_test_personas()
