"""
CHROMADB PRACTICE - Vector Indexing, HNSW Tuning, and Search Filters
======================================================================
Chroma version installed: 1.5.9

This script walks through the core "vector DB engineering" concepts you
need for a RAG exam:
  1. Persistent client + collection creation
  2. HNSW index configuration (space, ef_construction, max_neighbors, ef_search)
  3. Adding documents (text gets auto-embedded by the default embedding fn)
  4. Similarity search (pure vector search)
  5. Metadata filtering (structured filters -> `where`)
  6. Full-text filtering (substring/regex on the raw text -> `where_document`)
  7. Combining metadata + full-text filters
  8. $in / $nin list-based metadata filtering
  9. where_document case sensitivity, $not_contains, $or
  10. Explicit embedding function (SentenceTransformerEmbeddingFunction)
  11. Updating ef_search at query time (no rebuild needed)
  12. Other important ops: get-by-id, upsert, delete, count, peek

Run it with:
    python "chroma_hnsw_practice.py"

Key tips:
  - where_document ($contains) is CASE-SENSITIVE — "Pandas" != "pandas".
  - Combine `where` + `where_document` for precise, narrowed results.
  - `where_document` is Chroma's full-text search / SQL LIKE equivalent.
  - `where` is Chroma's SQL WHERE equivalent, but composable with vector search.
"""

import chromadb
from chromadb.api.collection_configuration import (
    CreateCollectionConfiguration,
    CreateHNSWConfiguration,
    UpdateCollectionConfiguration,
    UpdateHNSWConfiguration,
)


# ======================================================================
# SECTION 1: PERSISTENT CLIENT
# ======================================================================
client = chromadb.PersistentClient(path="./chroma_store")


# ======================================================================
# SECTION 2: HNSW INDEX CONFIGURATION
# ======================================================================
collection_config = CreateCollectionConfiguration(
    hnsw=CreateHNSWConfiguration(
        space="cosine",
        ef_construction=100,
        max_neighbors=16,
        ef_search=10,
    )
)

collection = client.get_or_create_collection(
    name="practice_docs",
    configuration=collection_config,
)


# ======================================================================
# SECTION 3: ADD DOCUMENTS (with metadata)
# ======================================================================
documents = [
    "The cat sat quietly on the warm windowsill.",
    "Dogs are loyal animals that need daily walks.",
    "Python is a popular programming language for AI.",
    "Vector databases store embeddings for fast similarity search.",
    "The stock market fell sharply after the interest rate announcement.",
    "Golden retrievers are known for their friendly temperament.",
    "HNSW graphs allow approximate nearest neighbor search at scale.",
    "Central banks raise interest rates to control inflation.",
]

metadatas = [
    {"topic": "animals", "source": "blog", "year": 2021},
    {"topic": "animals", "source": "blog", "year": 2022},
    {"topic": "tech", "source": "docs", "year": 2023},
    {"topic": "tech", "source": "docs", "year": 2024},
    {"topic": "finance", "source": "news", "year": 2023},
    {"topic": "animals", "source": "news", "year": 2020},
    {"topic": "tech", "source": "docs", "year": 2024},
    {"topic": "finance", "source": "news", "year": 2024},
]

ids = [f"doc_{i}" for i in range(len(documents))]

collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

print(f"Collection now has {collection.count()} documents.\n")


# ======================================================================
# SECTION 4: SIMILARITY SEARCH (pure vector search)
# ======================================================================
print("=== SECTION 4: Similarity search ===")
results = collection.query(
    query_texts=["a furry pet that barks"],
    n_results=3,
    include=["documents", "distances", "metadatas"],
)
for doc, dist, meta in zip(
    results["documents"][0], results["distances"][0], results["metadatas"][0]
):
    print(f"  dist={dist:.4f}  meta={meta}  doc={doc}")
print()


# ======================================================================
# SECTION 5: METADATA FILTERING (`where`)
# ======================================================================
print("=== SECTION 5: Metadata filtering ===")
results = collection.query(
    query_texts=["something about computers"],
    n_results=3,
    where={"topic": "tech"},
    include=["documents", "distances", "metadatas"],
)
for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
    print(f"  meta={meta}  doc={doc}")
print()

results = collection.query(
    query_texts=["something recent about computers"],
    n_results=3,
    where={"$and": [{"topic": "tech"}, {"year": {"$gte": 2024}}]},
    include=["documents", "metadatas"],
)
print("  Compound filter (tech AND year>=2024):")
for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
    print(f"    meta={meta}  doc={doc}")
print()


# ======================================================================
# SECTION 6: FULL-TEXT FILTERING (`where_document`)
# ======================================================================
print("=== SECTION 6: Full-text filtering ===")
results = collection.get(
    where_document={"$contains": "interest rate"},
    include=["documents", "metadatas"],
)
for doc, meta in zip(results["documents"], results["metadatas"]):
    print(f"  meta={meta}  doc={doc}")
print()


# ======================================================================
# SECTION 7: COMBINING METADATA + FULL-TEXT FILTERS
# ======================================================================
print("=== SECTION 7: Combined metadata + full-text filter ===")
results = collection.query(
    query_texts=["economic news"],
    n_results=3,
    where={"topic": "finance"},
    where_document={"$contains": "rate"},
    include=["documents", "metadatas", "distances"],
)
for doc, dist, meta in zip(
    results["documents"][0], results["distances"][0], results["metadatas"][0]
):
    print(f"  dist={dist:.4f}  meta={meta}  doc={doc}")
print()


# ======================================================================
# SECTION 8: $in / $nin — LIST-BASED METADATA FILTERING
# ======================================================================
print("=== SECTION 8: $in / $nin ===")
results = collection.get(
    where={"source": {"$in": ["news", "docs"]}},
    include=["documents", "metadatas"],
)
print(f"  source in [news, docs]: {len(results['ids'])} matches")

results = collection.get(
    where={"topic": {"$nin": ["animals"]}},
    include=["metadatas"],
)
print(f"  topic not in [animals]: {len(results['ids'])} matches\n")


# ======================================================================
# SECTION 9: CASE SENSITIVITY + $not_contains + $or ON where_document
# ======================================================================
print("=== SECTION 9: where_document details ===")

r_lower = collection.get(where_document={"$contains": "interest"})
r_upper = collection.get(where_document={"$contains": "Interest"})
print(f"  contains 'interest' (lower): {len(r_lower['ids'])} matches")
print(f"  contains 'Interest' (upper): {len(r_upper['ids'])} matches  <- case-sensitive")

r_not = collection.get(where_document={"$not_contains": "rate"})
print(f"  not_contains 'rate': {len(r_not['ids'])} matches")

r_or = collection.get(
    where_document={"$or": [{"$contains": "cat"}, {"$contains": "dog"}]}
)
print(f"  contains 'cat' OR 'dog': {len(r_or['ids'])} matches\n")


# ======================================================================
# SECTION 10: EXPLICIT EMBEDDING FUNCTION
# ======================================================================
from chromadb.utils import embedding_functions

ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
explicit_collection = client.get_or_create_collection(
    name="explicit_ef_demo",
    embedding_function=ef,
)
print("=== SECTION 10: Explicit embedding function ===")
print(f"  collection created with explicit ef: {explicit_collection.name}\n")


# ======================================================================
# SECTION 11: TUNING ef_search AT QUERY TIME
# ======================================================================
print("=== SECTION 11: Updating ef_search live ===")
collection.modify(
    configuration=UpdateCollectionConfiguration(
        hnsw=UpdateHNSWConfiguration(ef_search=50)
    )
)
print("  ef_search raised to 50 (higher recall, slightly slower queries)\n")


# ======================================================================
# SECTION 12: OTHER IMPORTANT OPS
# ======================================================================
print("=== SECTION 12: Other important ops ===")

one = collection.get(ids=["doc_2"], include=["documents", "metadatas"])
print(f"  get by id: {one['documents']}")

peek = collection.peek(limit=2)
print(f"  peek ids: {peek['ids']}")

print(f"  count: {collection.count()}")

# collection.delete(where={"source": "blog"})

print("\nDone. Data persisted under ./chroma_store — re-run any time.")
