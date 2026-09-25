from agents import graph as graph_module
from agents import nodes
from agents.user_data import load_all_users


def _patch_llm_and_retrieval(monkeypatch):
    monkeypatch.setattr(nodes, "complete_chat", lambda system, user, **kwargs: f"response to: {user[:30]}")
    monkeypatch.setattr(nodes, "retrieve_restaurants", lambda query, k: [])
    monkeypatch.setattr(nodes, "retrieve_recipes", lambda query, k: [])


def test_build_graph_compiles():
    app = graph_module.build_graph()
    assert app is not None


def test_run_recommendation_workflow_produces_all_expected_state_keys(monkeypatch):
    _patch_llm_and_retrieval(monkeypatch)

    result = graph_module.run_recommendation_workflow("user_001")

    for key in ["user_profile", "retrieved_candidates", "trend_analysis", "style_analysis", "nutrition_analysis", "final_recommendations"]:
        assert key in result
    assert result["errors"] == []


def test_run_recommendation_workflow_unknown_user_raises(monkeypatch):
    _patch_llm_and_retrieval(monkeypatch)
    import pytest

    with pytest.raises(ValueError):
        graph_module.run_recommendation_workflow("does-not-exist")


def test_all_four_real_test_personas_run_end_to_end(monkeypatch):
    """Exercises the four required test personas (health-conscious, adventurous foodie,
    budget-conscious student, family with dietary restrictions) through the compiled
    graph, with the LLM/retrieval calls mocked for speed."""
    _patch_llm_and_retrieval(monkeypatch)

    users = load_all_users()
    assert len(users) == 4

    for user in users:
        result = graph_module.run_recommendation_workflow(user["id"])
        assert result["final_recommendations"]
        assert result["errors"] == []
