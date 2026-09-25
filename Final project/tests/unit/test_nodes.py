from agents import nodes

CANDIDATES = {
    "restaurants": [
        {
            "id": "r001",
            "document": "doc",
            "metadata": {"name": "Green Papaya", "cuisine": "Vietnamese", "location": "San Jose", "price_range": "$$"},
        }
    ],
    "recipes": [
        {
            "id": "rc001",
            "document": "Vietnamese Beef Pho",
            "metadata": {"cuisine": "Vietnamese", "caption": "a bowl of noodles"},
        }
    ],
}


def test_node_generate_user_profile_calls_agent_and_updates_state(monkeypatch):
    monkeypatch.setattr(nodes, "complete_chat", lambda system, user, **kwargs: "profile text")
    state = {"visit_history": [{"restaurant_name": "Green Papaya"}], "social_posts": ["loves spicy food"]}

    result = nodes.node_generate_user_profile(state)

    assert result["user_profile"] == "profile text"
    assert result["errors"] == []


def test_node_generate_user_profile_records_error_on_failure(monkeypatch):
    def boom(system, user, **kwargs):
        raise RuntimeError("rate limited")

    monkeypatch.setattr(nodes, "complete_chat", boom)
    result = nodes.node_generate_user_profile({"visit_history": [], "social_posts": []})

    assert "unavailable" in result["user_profile"]
    assert len(result["errors"]) == 1
    assert "rate limited" in result["errors"][0]


def test_node_retrieve_candidates_calls_both_collections(monkeypatch):
    monkeypatch.setattr(nodes, "retrieve_restaurants", lambda query, k: CANDIDATES["restaurants"])
    monkeypatch.setattr(nodes, "retrieve_recipes", lambda query, k: CANDIDATES["recipes"])

    result = nodes.node_retrieve_candidates({"user_profile": "likes noodles"})

    assert result["retrieved_candidates"]["restaurants"] == CANDIDATES["restaurants"]
    assert result["retrieved_candidates"]["recipes"] == CANDIDATES["recipes"]


def test_node_analyze_styles_builds_user_message_with_profile_and_candidates(monkeypatch):
    captured = {}

    def fake_complete_chat(system, user, **kwargs):
        captured["system"] = system
        captured["user"] = user
        return "style analysis"

    monkeypatch.setattr(nodes, "complete_chat", fake_complete_chat)

    state = {
        "user_profile": "Loves spicy Vietnamese food",
        "retrieved_candidates": CANDIDATES,
        "errors": [],
    }
    result = nodes.node_analyze_styles(state)

    assert result["style_analysis"] == "style analysis"
    assert "Loves spicy Vietnamese food" in captured["user"]
    assert "Green Papaya" in captured["user"]
    assert "Vietnamese Beef Pho" in captured["user"]
    assert "Food Style Expert" in captured["system"]


def test_node_analyze_trends_and_nutrition_also_use_profile_and_candidates(monkeypatch):
    monkeypatch.setattr(nodes, "complete_chat", lambda system, user, **kwargs: user)

    state = {"user_profile": "profile X", "retrieved_candidates": CANDIDATES, "errors": []}

    trends = nodes.node_analyze_trends(state)
    nutrition = nodes.node_analyze_nutrition(state)

    assert "profile X" in trends["trend_analysis"]
    assert "profile X" in nutrition["nutrition_analysis"]


def test_node_synthesize_recommendations_includes_all_prior_analyses(monkeypatch):
    captured = {}

    def fake_complete_chat(system, user, **kwargs):
        captured["user"] = user
        return "final list"

    monkeypatch.setattr(nodes, "complete_chat", fake_complete_chat)

    state = {
        "user_profile": "profile X",
        "retrieved_candidates": CANDIDATES,
        "trend_analysis": "trend text",
        "style_analysis": "style text",
        "nutrition_analysis": "nutrition text",
        "errors": [],
    }
    result = nodes.node_synthesize_recommendations(state)

    assert result["final_recommendations"] == "final list"
    for expected in ("trend text", "style text", "nutrition text"):
        assert expected in captured["user"]
