from chatbot import service


def test_respond_returns_clarification_message_for_ambiguous_input(monkeypatch):
    monkeypatch.setattr(service, "classify_intent", lambda message: "clarification")
    assert service.respond("I'm looking for dinner ideas") == service.CLARIFICATION_REPLY


def test_respond_runs_workflow_for_restaurant_request(monkeypatch):
    monkeypatch.setattr(service, "classify_intent", lambda message: "restaurant_request")
    monkeypatch.setattr(service, "extract_preferences", lambda message: {"favorite_cuisines": ["Thai"]})

    class FakeGraph:
        def invoke(self, state):
            assert state["social_posts"][0] == "Thai food please"
            return {"final_recommendations": "Try Spice Route!"}

    monkeypatch.setattr(service, "_get_graph", lambda: FakeGraph())

    result = service.respond("Thai food please")
    assert result == "Try Spice Route!"


def test_respond_handles_workflow_failure_gracefully(monkeypatch):
    monkeypatch.setattr(service, "classify_intent", lambda message: "recipe_request")
    monkeypatch.setattr(service, "extract_preferences", lambda message: {})

    class FailingGraph:
        def invoke(self, state):
            raise RuntimeError("groq is down")

    monkeypatch.setattr(service, "_get_graph", lambda: FailingGraph())

    result = service.respond("give me a recipe")
    assert "groq is down" in result


def test_respond_falls_back_when_workflow_produces_no_recommendations(monkeypatch):
    monkeypatch.setattr(service, "classify_intent", lambda message: "restaurant_request")
    monkeypatch.setattr(service, "extract_preferences", lambda message: {})

    class EmptyGraph:
        def invoke(self, state):
            return {"final_recommendations": "", "errors": ["Recommendation Expert: empty completion"]}

    monkeypatch.setattr(service, "_get_graph", lambda: EmptyGraph())

    result = service.respond("Thai food please")
    assert "couldn't come up with a recommendation" in result
