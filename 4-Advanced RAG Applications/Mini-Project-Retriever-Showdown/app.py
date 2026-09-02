from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from retrievers import CORPUS, run_baseline, run_bm25, run_mmr, run_multiquery, run_rrf

app = FastAPI(
    title="Retriever Showdown",
    description="Mini project: run one question through five advanced retrieval "
    "strategies (baseline, MMR, multi-query, BM25, reciprocal rank fusion) and "
    "compare the results side by side.",
)


class QuestionRequest(BaseModel):
    question: str


# ---------- SECTION 1: CORPUS ----------
@app.get("/api/corpus")
def get_corpus():
    return {"documents": CORPUS}


# ---------- SECTION 2: ONE ROUTE PER RETRIEVAL STRATEGY ----------
@app.post("/api/baseline")
def baseline(req: QuestionRequest):
    return {"results": run_baseline(req.question)}


@app.post("/api/mmr")
def mmr(req: QuestionRequest):
    return {"results": run_mmr(req.question)}


@app.post("/api/multiquery")
def multiquery(req: QuestionRequest):
    return run_multiquery(req.question)


@app.post("/api/bm25")
def bm25(req: QuestionRequest):
    return {"results": run_bm25(req.question)}


@app.post("/api/rrf")
def rrf(req: QuestionRequest):
    return {"results": run_rrf(req.question)}


# ---------- SECTION 3: FRONTEND (served at "/") ----------
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
