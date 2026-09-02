import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from rag import answer
from vector_store import collection_info, search, set_ef_search

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

app = FastAPI(
    title="Vector Retrieval Lab",
    description="Mini project: ChromaDB collections, HNSW tuning, metadata/full-text "
    "filters, and RAG retrieval, backed by Groq.",
)


# ---------- SECTION 1: REQUEST MODELS ----------
class SearchRequest(BaseModel):
    query: str
    top_k: int = 3
    topic: str | None = None
    source: str | None = None
    contains: str | None = None


class EfRequest(BaseModel):
    ef_search: int


class AskRequest(BaseModel):
    question: str
    top_k: int = 3
    topic: str | None = None
    source: str | None = None
    contains: str | None = None


# ---------- SECTION 2: API ROUTES ----------
@app.get("/api/collection-info")
def info():
    return collection_info()


@app.post("/api/search")
def do_search(req: SearchRequest):
    return {"matches": search(req.query, req.top_k, req.topic, req.source, req.contains)}


@app.post("/api/tune-ef")
def tune_ef(req: EfRequest):
    set_ef_search(req.ef_search)
    return {"ef_search": req.ef_search}


@app.post("/api/ask")
def ask(req: AskRequest):
    return answer(req.question, req.top_k, req.topic, req.source, req.contains)


# ---------- SECTION 3: FRONTEND (served at "/") ----------
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
