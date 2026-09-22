import pytest
from pydantic import ValidationError

from schemas.recipe import Recipe
from schemas.restaurant import Restaurant
from schemas.user import User, VisitRecord

VALID_RESTAURANT = {
    "id": "r001",
    "name": "Test Place",
    "cuisine": "Fusion",
    "location": "Testville",
    "price_range": "$$",
    "rating": 4.2,
    "signature_dishes": ["dish a", "dish b"],
    "vibe": ["casual"],
    "summary": "A place for testing.",
}


def test_valid_restaurant_passes():
    r = Restaurant.model_validate(VALID_RESTAURANT)
    assert r.name == "Test Place"


def test_invalid_price_range_rejected():
    bad = {**VALID_RESTAURANT, "price_range": "cheap"}
    with pytest.raises(ValidationError):
        Restaurant.model_validate(bad)


def test_rating_out_of_range_rejected():
    bad = {**VALID_RESTAURANT, "rating": 7.0}
    with pytest.raises(ValidationError):
        Restaurant.model_validate(bad)


def test_empty_signature_dishes_rejected():
    bad = {**VALID_RESTAURANT, "signature_dishes": []}
    with pytest.raises(ValidationError):
        Restaurant.model_validate(bad)


def test_blank_only_signature_dishes_rejected():
    bad = {**VALID_RESTAURANT, "signature_dishes": ["   ", ""]}
    with pytest.raises(ValidationError):
        Restaurant.model_validate(bad)


def test_valid_recipe_passes():
    r = Recipe.model_validate(
        {
            "id": "rc001",
            "name": "Test Dish",
            "cuisine": "Test",
            "ingredients": ["a", "b"],
            "instructions": "Cook it.",
            "image_path": "data/images/rc001.png",
        }
    )
    assert r.caption is None


def test_valid_user_passes():
    u = User.model_validate(
        {
            "id": "user_001",
            "name": "Test User",
            "visit_history": [
                {"restaurant_name": "Test Place", "date": "2026-01-01", "rating": 4.5, "comment": "good"}
            ],
            "social_posts": ["loves spicy food"],
        }
    )
    assert isinstance(u.visit_history[0], VisitRecord)
