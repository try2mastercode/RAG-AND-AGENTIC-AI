from retrieval import fusion


def test_normalize_scores_min_max():
    scores = {"a": 0.0, "b": 5.0, "c": 10.0}
    normalized = fusion.normalize_scores(scores)
    assert normalized == {"a": 0.0, "b": 0.5, "c": 1.0}


def test_normalize_scores_empty_returns_empty():
    assert fusion.normalize_scores({}) == {}


def test_normalize_scores_all_equal_returns_ones():
    assert fusion.normalize_scores({"a": 3.0, "b": 3.0}) == {"a": 1.0, "b": 1.0}


def test_fused_ranking_text_only_weight_matches_text_ranking(monkeypatch):
    monkeypatch.setattr(fusion, "text_scores_by_restaurant", lambda q: {"A": 0.2, "B": 0.9})
    monkeypatch.setattr(fusion, "image_scores_by_restaurant", lambda q: {"A": 0.9, "B": 0.1})

    ranking = fusion.fused_restaurant_ranking("query", weights={"text": 1.0, "image": 0.0}, k=2)

    assert [r["restaurant"] for r in ranking] == ["B", "A"]


def test_fused_ranking_image_only_weight_matches_image_ranking(monkeypatch):
    monkeypatch.setattr(fusion, "text_scores_by_restaurant", lambda q: {"A": 0.2, "B": 0.9})
    monkeypatch.setattr(fusion, "image_scores_by_restaurant", lambda q: {"A": 0.9, "B": 0.1})

    ranking = fusion.fused_restaurant_ranking("query", weights={"text": 0.0, "image": 1.0}, k=2)

    assert [r["restaurant"] for r in ranking] == ["A", "B"]


def test_fused_ranking_changes_with_different_weights(monkeypatch):
    monkeypatch.setattr(fusion, "text_scores_by_restaurant", lambda q: {"A": 0.1, "B": 1.0})
    monkeypatch.setattr(fusion, "image_scores_by_restaurant", lambda q: {"A": 1.0, "B": 0.1})

    text_heavy = fusion.fused_restaurant_ranking("query", {"text": 1.0, "image": 0.0}, k=1)
    image_heavy = fusion.fused_restaurant_ranking("query", {"text": 0.0, "image": 1.0}, k=1)

    assert text_heavy[0]["restaurant"] != image_heavy[0]["restaurant"]


def test_fused_ranking_missing_modality_defaults_to_zero(monkeypatch):
    monkeypatch.setattr(fusion, "text_scores_by_restaurant", lambda q: {"A": 0.5})
    monkeypatch.setattr(fusion, "image_scores_by_restaurant", lambda q: {})

    ranking = fusion.fused_restaurant_ranking("query", weights={"text": 0.5, "image": 0.5}, k=1)

    assert ranking[0]["restaurant"] == "A"
    assert ranking[0]["image_score"] == 0.0
