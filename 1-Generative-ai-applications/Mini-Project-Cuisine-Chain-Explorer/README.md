# Cuisine Chain Explorer — Mini Project

A small full-stack app proving out the LangChain concepts from this folder
(`LangChain.py`, `memory.py`, `runnable parallel and sequence.py`), running live
against Groq behind a plain HTML/CSS/JS frontend.

| Panel | Concept | Source pattern |
|---|---|---|
| Sequential chain | `prompt \| llm \| parser`, staged | `LangChain.py` (`SequentialChain`) |
| Parallel chain | `RunnableParallel` | `runnable parallel and sequence.py` |
| Branch chain | `RunnableBranch` | `runnable parallel and sequence.py` |
| Conversational memory | `InMemoryChatMessageHistory` | `memory.py` |

The frontend isn't just a results viewer — each panel explains the concept it's
demonstrating, and has a collapsible "Under the hood" box showing the raw
request/response JSON for that call, so it doubles as a walkthrough of how a
generative-AI API round trip actually works.

## Run it

From the repo root (needs the repo's `.env` with `GROQ_API_KEY` set):

```bash
pip install -r "1-Generative-ai-applications/Mini-Project-Cuisine-Chain-Explorer/requirements.txt"
python -m uvicorn app:app --reload --app-dir "1-Generative-ai-applications/Mini-Project-Cuisine-Chain-Explorer"
```

Then open http://localhost:8000. Interactive API docs (Swagger UI) are at
http://localhost:8000/docs.
