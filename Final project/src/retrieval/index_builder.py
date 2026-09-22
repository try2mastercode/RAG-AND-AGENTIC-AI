import json
import logging

import numpy as np

import config
from retrieval.chroma_client import reset_collection
from retrieval.embeddings import embed_image, embed_text

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _restaurant_page_content(r: dict) -> str:
    """Built from restaurant name, cuisine, and location per the M2L1 spec, plus the
    summary for richer semantic content."""
    return f"{r['name']} is a {r['cuisine']} restaurant in {r['location']}. {r['summary']}"


def build_restaurant_articles_collection() -> int:
    restaurants = json.loads(config.STRUCTURED_RESTAURANTS_FILE.read_text(encoding="utf-8"))
    collection = reset_collection(config.RESTAURANT_ARTICLES_COLLECTION)

    documents = [_restaurant_page_content(r) for r in restaurants]
    embeddings = embed_text(documents)
    assert embeddings.shape[1] == config.TEXT_EMBEDDING_DIM, "text embedding dimension mismatch"

    collection.upsert(
        ids=[r["id"] for r in restaurants],
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=[
            {
                "name": r["name"],
                "cuisine": r["cuisine"],
                "location": r["location"],
                "price_range": r["price_range"],
                "rating": r["rating"],
                "vibe": ", ".join(r["vibe"]),
                "signature_dishes": ", ".join(r["signature_dishes"]),
            }
            for r in restaurants
        ],
    )
    logger.info("restaurant_articles: upserted %d restaurants (dim=%d)", len(restaurants), embeddings.shape[1])
    return len(restaurants)


def build_food_images_collection() -> int:
    recipes = json.loads(config.RECIPES_FILE.read_text(encoding="utf-8"))
    collection = reset_collection(config.FOOD_IMAGES_COLLECTION)

    documents = [r["name"] for r in recipes]  # page_content = recipe name, per the M2L1 spec
    embeddings = np.stack([embed_image(r["image_path"]) for r in recipes])
    assert embeddings.shape[1] == config.IMAGE_EMBEDDING_DIM, "image embedding dimension mismatch"

    collection.upsert(
        ids=[r["id"] for r in recipes],
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=[
            {
                "image_path": r["image_path"],
                "cuisine": r["cuisine"],
                "source": r.get("source") or "",
                "caption": r.get("caption") or "",
            }
            for r in recipes
        ],
    )
    logger.info("food_images: upserted %d recipes (dim=%d)", len(recipes), embeddings.shape[1])
    return len(recipes)


def build_all() -> None:
    logger.info("stage started: multimodal vector index construction")
    n_restaurants = build_restaurant_articles_collection()
    n_images = build_food_images_collection()
    logger.info("stage completed: %d restaurant_articles, %d food_images", n_restaurants, n_images)
    print("Multimodal Vector Index Construction COMPLETE")


if __name__ == "__main__":
    build_all()
