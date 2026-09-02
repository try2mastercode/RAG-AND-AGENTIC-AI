import os

import chromadb
from chromadb.api.collection_configuration import (
    CreateCollectionConfiguration,
    CreateHNSWConfiguration,
    UpdateCollectionConfiguration,
    UpdateHNSWConfiguration,
)
from chromadb.utils import embedding_functions

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_store")

ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path=CHROMA_PATH)


# ---------- SECTION 1: KNOWLEDGE BASE ----------
DOCUMENTS = [
    "The James Webb Space Telescope observes the universe primarily in infrared light.",
    "Saturn's rings are made mostly of ice particles with a smaller amount of rocky debris.",
    "A neural network's weights are adjusted during training using backpropagation.",
    "Vector databases index embeddings so semantically similar text can be found quickly.",
    "HNSW builds a multi-layer graph to approximate nearest-neighbor search at scale.",
    "Sourdough bread rises because wild yeast and bacteria ferment sugars in the dough.",
    "Braising combines searing meat first, then slow-cooking it in liquid.",
    "The Roman Empire split into Western and Eastern halves in 285 CE.",
    "The printing press, invented by Gutenberg, sped up the spread of written knowledge.",
    "Retrieval-augmented generation grounds an LLM's answer in retrieved documents instead of memory alone.",
    "Cosine similarity measures the angle between two vectors, ignoring their magnitude.",
    "Interest rate hikes by central banks are meant to slow inflation by cooling demand.",
]

METADATAS = [
    {"topic": "space", "source": "science", "year": 2022},
    {"topic": "space", "source": "science", "year": 2020},
    {"topic": "ai", "source": "docs", "year": 2023},
    {"topic": "ai", "source": "docs", "year": 2024},
    {"topic": "ai", "source": "docs", "year": 2024},
    {"topic": "cooking", "source": "blog", "year": 2021},
    {"topic": "cooking", "source": "blog", "year": 2022},
    {"topic": "history", "source": "encyclopedia", "year": 2019},
    {"topic": "history", "source": "encyclopedia", "year": 2019},
    {"topic": "ai", "source": "docs", "year": 2024},
    {"topic": "ai", "source": "docs", "year": 2023},
    {"topic": "finance", "source": "news", "year": 2024},
]

IDS = [f"doc_{i}" for i in range(len(DOCUMENTS))]


# ---------- SECTION 2: COLLECTION (HNSW-configured) ----------
collection = client.get_or_create_collection(
    name="knowledge_base",
    embedding_function=ef,
    configuration=CreateCollectionConfiguration(
        hnsw=CreateHNSWConfiguration(space="cosine", ef_construction=100, max_neighbors=16, ef_search=10)
    ),
)

if collection.count() == 0:
    collection.upsert(ids=IDS, documents=DOCUMENTS, metadatas=METADATAS)


# ---------- SECTION 3: INTROSPECTION ----------
def collection_info():
    topics = sorted({m["topic"] for m in METADATAS})
    sources = sorted({m["source"] for m in METADATAS})
    return {
        "count": collection.count(),
        "topics": topics,
        "sources": sources,
        "hnsw": {"space": "cosine", "ef_construction": 100, "max_neighbors": 16},
    }


# ---------- SECTION 4: FILTERED VECTOR SEARCH ----------
def _build_where(topic, source):
    clauses = []
    if topic:
        clauses.append({"topic": topic})
    if source:
        clauses.append({"source": source})
    if not clauses:
        return None
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}


def search(query: str, top_k: int = 3, topic: str | None = None, source: str | None = None, contains: str | None = None):
    where = _build_where(topic, source)
    where_document = {"$contains": contains} if contains else None
    top_k = max(1, min(top_k, collection.count()))

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where=where,
        where_document=where_document,
        include=["documents", "metadatas", "distances"],
    )

    docs, metas, dists = results["documents"][0], results["metadatas"][0], results["distances"][0]
    return [{"document": d, "metadata": m, "distance": dist} for d, m, dist in zip(docs, metas, dists)]


# ---------- SECTION 5: LIVE HNSW TUNING ----------
def set_ef_search(ef_search: int):
    collection.modify(configuration=UpdateCollectionConfiguration(hnsw=UpdateHNSWConfiguration(ef_search=ef_search)))
