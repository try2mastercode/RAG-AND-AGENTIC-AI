# Retriever Showdown

A small full-stack app proving out the advanced retrieval strategies from this
folder (`Max-Marginal-Releveance.py`, `LangChain-Adv-Retriever/Multi-Query-Retriever.py`,
`Llamaindex-Adv-Retriever/Vector-Index-Retriever/BM25-retriever.py`,
`Llamaindex-Adv-Retriever/Fusion-Stratergies/Reciprocal-rank-fusion.py`) by running
the *same* question through five of them at once and showing how the results differ.

| Strategy | What it does | Source pattern |
|---|---|---|
| Baseline | Plain dense vector similarity search | any `vectorstore.similarity_search` |
| MMR | Diversity-aware dense search | `Max-Marginal-Releveance.py` |
| Multi-query | LLM rewords the question 3 ways, results merged | `LangChain-Adv-Retriever/Multi-Query-Retriever.py` |
| BM25 | Sparse/keyword ranking, no embeddings | `Llamaindex-Adv-Retriever/.../BM25-retriever.py` |
| Reciprocal Rank Fusion | Fuses the baseline + BM25 rankings into one score | `Llamaindex-Adv-Retriever/Fusion-Stratergies/Reciprocal-rank-fusion.py` |

BM25 and RRF are reimplemented on the LangChain side (`langchain_community.retrievers.BM25Retriever`
+ a manual reciprocal-rank-fusion formula) rather than pulling in LlamaIndex too, so the whole
project runs on one stack. All five strategies search the exact same fixed six-sentence corpus, which
is what makes the side-by-side comparison meaningful — same documents, same question, different math.

The frontend isn't just a results viewer — each strategy has a one-line explanation of what makes it
different, and every panel has an "Under the hood" box showing the raw request/response JSON.

## Run it

Needs a `.env` file in this folder with `GROQ_API_KEY` set (copy `.env.example` and fill it in).

```bash
pip install -r requirements.txt
python -m uvicorn app:app --reload
```

Then open http://localhost:8000 (or whichever port you pass with `--port`).
Interactive API docs (Swagger UI) are at `/docs`.
