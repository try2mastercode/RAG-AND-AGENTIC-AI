# Vector Retrieval Lab

A small full-stack app proving out ChromaDB retrieval fundamentals
(`vector_store.py`, `rag.py`) — collection setup, HNSW index tuning, metadata/
full-text filtered search, and RAG retrieval, running live behind a plain
HTML/CSS/JS frontend.

| Panel | Concept | Source pattern |
|---|---|---|
| Collection info | HNSW config (`space`, `ef_construction`, `max_neighbors`) | `vector_store.py` (`collection_info`) |
| Filtered search | metadata (`topic`/`source`) + full-text (`$contains`) filters, no LLM | `vector_store.py` (`search`, `_build_where`) |
| Live HNSW tuning | adjusting `ef_search` at query time and seeing recall/speed trade off | `vector_store.py` (`set_ef_search`) |
| Ask | retrieve + augment + generate | `rag.py` (`answer`) |

The knowledge base is a small fixed set of documents spanning five topics
(space, AI, cooking, history, finance), so filter combinations are easy to
reason about while testing.

**Stack:** FastAPI + ChromaDB (`PersistentClient`, on-disk at `chroma_store/`)
+ local `sentence-transformers/all-MiniLM-L6-v2` embeddings (no API cost) +
LangChain + Groq for generation.

## Run it

Needs a `.env` file in this folder with `GROQ_API_KEY` set (copy `.env.example` and fill it in).

```bash
pip install -r requirements.txt
python -m uvicorn app:app --reload
```

Then open http://localhost:8000 (or whichever port you pass with `--port`).
Interactive API docs (Swagger UI) are at `/docs`.

The `chroma_store/` folder is created on first run and is gitignored
(regenerable, not checked in).
