import json

from data import captioning


def test_find_review_context_matches_restaurant():
    users = [
        {
            "visit_history": [
                {"restaurant_name": "Green Papaya", "comment": "amazing pho"},
            ]
        }
    ]
    context = captioning._find_review_context("Green Papaya", users)
    assert context is not None
    assert "amazing pho" in context


def test_find_review_context_no_match_returns_none():
    users = [{"visit_history": [{"restaurant_name": "Other Place", "comment": "fine"}]}]
    assert captioning._find_review_context("Green Papaya", users) is None


def test_find_review_context_blank_restaurant_returns_none():
    assert captioning._find_review_context("", []) is None


def test_build_caption_appends_context_without_feeding_it_to_the_model(monkeypatch):
    monkeypatch.setattr(captioning, "caption_image", lambda image_path: "a plate of noodles")
    result = captioning.build_caption("some/path.png", context='Reviewed at X: "great broth"')
    assert result == 'a plate of noodles. Reviewed at X: "great broth".'


def test_build_caption_without_context_returns_visual_caption_only(monkeypatch):
    monkeypatch.setattr(captioning, "caption_image", lambda image_path: "a plate of noodles")
    assert captioning.build_caption("some/path.png", context=None) == "a plate of noodles"


def test_caption_all_recipes_writes_captions(tmp_path, monkeypatch):
    recipes_path = tmp_path / "recipes.json"
    users_path = tmp_path / "users.json"

    recipes_path.write_text(
        json.dumps(
            [
                {"id": "rc001", "name": "Dish A", "image_path": "a.png", "source": "Green Papaya", "caption": None},
                {"id": "rc002", "name": "Dish B", "image_path": "b.png", "source": "Unknown Place", "caption": None},
            ]
        ),
        encoding="utf-8",
    )
    users_path.write_text(
        json.dumps([{"visit_history": [{"restaurant_name": "Green Papaya", "comment": "great broth"}]}]),
        encoding="utf-8",
    )

    calls = []

    def fake_build_caption(image_path, context=None):
        calls.append((image_path, context))
        return "a mock caption"

    monkeypatch.setattr(captioning, "build_caption", fake_build_caption)

    result = captioning.caption_all_recipes(recipes_path=recipes_path, users_path=users_path)

    assert all(r["caption"] == "a mock caption" for r in result)
    assert calls[0][1] is not None and "great broth" in calls[0][1]
    assert calls[1][1] is None

    saved = json.loads(recipes_path.read_text(encoding="utf-8"))
    assert saved[0]["caption"] == "a mock caption"
