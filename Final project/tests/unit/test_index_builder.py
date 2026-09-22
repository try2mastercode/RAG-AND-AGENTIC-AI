import json

import numpy as np

import config
from retrieval import index_builder


class FakeCollection:
    def __init__(self):
        self.upsert_calls = []

    def upsert(self, **kwargs):
        self.upsert_calls.append(kwargs)


RESTAURANTS = [
    {
        "id": "r001",
        "name": "Test Diner",
        "cuisine": "American",
        "location": "Testville",
        "price_range": "$$",
        "rating": 4.2,
        "signature_dishes": ["burger", "fries"],
        "vibe": ["casual", "lively"],
        "summary": "A reliable diner.",
    },
    {
        "id": "r002",
        "name": "Mock Sushi",
        "cuisine": "Japanese",
        "location": "Testville",
        "price_range": "$$$",
        "rating": 4.6,
        "signature_dishes": ["nigiri"],
        "vibe": ["quiet"],
        "summary": "Quiet omakase counter.",
    },
]

RECIPES = [
    {"id": "rc001", "name": "Test Dish", "cuisine": "American", "image_path": "a.png", "source": "Test Diner", "caption": "a plate"},
]


def test_restaurant_page_content_includes_name_cuisine_location():
    content = index_builder._restaurant_page_content(RESTAURANTS[0])
    assert "Test Diner" in content
    assert "American" in content
    assert "Testville" in content


def test_build_restaurant_articles_collection_upserts_all(tmp_path, monkeypatch):
    restaurants_path = tmp_path / "restaurants.json"
    restaurants_path.write_text(json.dumps(RESTAURANTS), encoding="utf-8")
    monkeypatch.setattr(config, "STRUCTURED_RESTAURANTS_FILE", restaurants_path)

    fake_collection = FakeCollection()
    monkeypatch.setattr(index_builder, "reset_collection", lambda name: fake_collection)
    monkeypatch.setattr(
        index_builder, "embed_text", lambda docs: np.zeros((len(docs), config.TEXT_EMBEDDING_DIM), dtype=np.float32)
    )

    count = index_builder.build_restaurant_articles_collection()

    assert count == 2
    assert len(fake_collection.upsert_calls) == 1
    call = fake_collection.upsert_calls[0]
    assert call["ids"] == ["r001", "r002"]
    assert len(call["embeddings"]) == 2
    assert len(call["embeddings"][0]) == config.TEXT_EMBEDDING_DIM
    assert call["metadatas"][0]["vibe"] == "casual, lively"


def test_build_food_images_collection_upserts_all(tmp_path, monkeypatch):
    recipes_path = tmp_path / "recipes.json"
    recipes_path.write_text(json.dumps(RECIPES), encoding="utf-8")
    monkeypatch.setattr(config, "RECIPES_FILE", recipes_path)

    fake_collection = FakeCollection()
    monkeypatch.setattr(index_builder, "reset_collection", lambda name: fake_collection)
    monkeypatch.setattr(
        index_builder, "embed_image", lambda path: np.zeros(config.IMAGE_EMBEDDING_DIM, dtype=np.float32)
    )

    count = index_builder.build_food_images_collection()

    assert count == 1
    call = fake_collection.upsert_calls[0]
    assert call["documents"] == ["Test Dish"]
    assert len(call["embeddings"][0]) == config.IMAGE_EMBEDDING_DIM
    assert call["metadatas"][0]["source"] == "Test Diner"
