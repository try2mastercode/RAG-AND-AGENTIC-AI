import logging

import config
from retrieval.chroma_client import get_client
from retrieval.embeddings import embed_text, embed_text_for_image_query

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

TOP_N_PER_MODALITY = 8


def normalize_scores(scores: dict[str, float]) -> dict[str, float]:
    if not scores:
        return {}
    values = list(scores.values())
    lo, hi = min(values), max(values)
    if hi == lo:
        return dict.fromkeys(scores, 1.0)
    return {k: (v - lo) / (hi - lo) for k, v in scores.items()}


def text_scores_by_restaurant(query: str) -> dict[str, float]:
    client = get_client()
    collection = client.get_collection(config.RESTAURANT_ARTICLES_COLLECTION)
    query_embedding = embed_text([query])[0].tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=TOP_N_PER_MODALITY)

    scores: dict[str, float] = {}
    for idx, meta in enumerate(results["metadatas"][0]):
        scores[meta["name"]] = 1 - results["distances"][0][idx]
    return scores


def image_scores_by_restaurant(query: str) -> dict[str, float]:
    """Embeds the query into CLIP's text space and queries food_images directly, then
    aggregates per source restaurant (best-matching dish wins) via the recipe->restaurant
    link established in M1/M2L1."""
    client = get_client()
    collection = client.get_collection(config.FOOD_IMAGES_COLLECTION)
    query_embedding = embed_text_for_image_query([query])[0].tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=TOP_N_PER_MODALITY)

    scores: dict[str, float] = {}
    for idx, meta in enumerate(results["metadatas"][0]):
        source = meta.get("source")
        if not source:
            continue
        similarity = 1 - results["distances"][0][idx]
        scores[source] = max(scores.get(source, 0.0), similarity)
    return scores


def fused_restaurant_ranking(query: str, weights: dict[str, float], k: int = 5) -> list[dict]:
    text_scores = normalize_scores(text_scores_by_restaurant(query))
    image_scores = normalize_scores(image_scores_by_restaurant(query))

    fused = []
    for name in set(text_scores) | set(image_scores):
        t = text_scores.get(name, 0.0)
        i = image_scores.get(name, 0.0)
        fused_score = weights.get("text", 0.0) * t + weights.get("image", 0.0) * i
        fused.append({"restaurant": name, "text_score": t, "image_score": i, "fused_score": fused_score})

    fused.sort(key=lambda r: r["fused_score"], reverse=True)
    return fused[:k]


def demo() -> None:
    query = "spicy comforting noodle soup"
    weight_configs = [
        {"text": 1.0, "image": 0.0},
        {"text": 0.5, "image": 0.5},
        {"text": 0.0, "image": 1.0},
    ]

    logger.info("stage started: multimodal similarity fusion and retrieval ranking")
    logger.info("query=%r", query)

    for weights in weight_configs:
        ranking = fused_restaurant_ranking(query, weights, k=5)
        logger.info("weights=%s", weights)
        for rank, r in enumerate(ranking, start=1):
            logger.info(
                "  #%d %s - fused=%.3f (text=%.3f, image=%.3f)",
                rank, r["restaurant"], r["fused_score"], r["text_score"], r["image_score"],
            )

    logger.info("stage completed")
    print("Multimodal Similarity Fusion and Retrieval Ranking COMPLETE")


if __name__ == "__main__":
    demo()
