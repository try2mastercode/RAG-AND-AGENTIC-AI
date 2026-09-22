import logging

import config
from retrieval.chroma_client import get_client
from retrieval.embeddings import embed_text

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def retrieve_restaurants(query: str, k: int = 5, filters: dict | None = None) -> list[dict]:
    client = get_client()
    collection = client.get_collection(config.RESTAURANT_ARTICLES_COLLECTION)
    query_embedding = embed_text([query])[0].tolist()

    results = collection.query(query_embeddings=[query_embedding], n_results=k, where=filters)

    hits = []
    for idx in range(len(results["ids"][0])):
        distance = results["distances"][0][idx]
        hits.append(
            {
                "id": results["ids"][0][idx],
                "document": results["documents"][0][idx],
                "metadata": results["metadatas"][0][idx],
                "distance": distance,
                "similarity": 1 - distance,
            }
        )
    return hits


def demo() -> list[dict]:
    query = "cozy romantic dinner spot with a great wine list"
    filters = {"price_range": {"$in": ["$$$", "$$$$"]}}

    logger.info("stage started: similarity retrieval with metadata filtering")
    logger.info("query=%r filters=%r", query, filters)

    results = retrieve_restaurants(query, k=5, filters=filters)
    for rank, hit in enumerate(results, start=1):
        meta = hit["metadata"]
        logger.info(
            "#%d %s (similarity=%.3f) - %s, %s, %s",
            rank, meta["name"], hit["similarity"], meta["cuisine"], meta["location"], meta["price_range"],
        )

    logger.info("stage completed: %d results", len(results))
    print("Similarity Retrieval with Metadata Filtering COMPLETE")
    return results


if __name__ == "__main__":
    demo()
