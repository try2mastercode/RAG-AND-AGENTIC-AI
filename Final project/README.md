# Restaurant Recommendation Capstone

End-to-end multimodal AI restaurant recommendation system. Unstructured restaurant text and food images are turned into a structured, retrievable knowledge base, served by a multi-agent recommendation workflow (LangGraph + Groq), and exposed through a FastAPI backend + a plain HTML/CSS/JS frontend. A Gradio prototype and an MCP server/client/host stack are also included.

## Setup

```bash
py -3.11 -m venv .venv
.venv/Scripts/pip install -e .
.venv/Scripts/pip install -r requirements.txt
cp .env.example .env   # then fill in GROQ_API_KEY
```

## Verify the environment

```bash
.venv/Scripts/pytest tests/unit/test_environment.py -v
```

## Layout

```text
data/          raw + generated datasets, per pipeline stage
src/           application code (data, schemas, llm, retrieval, agents, chatbot, api, mcp_app)
frontend/      plain HTML/CSS/JS client for the FastAPI backend
tests/         unit + integration tests
chroma_data/   persistent vector store (generated, gitignored — built by a setup step, see below)
Procfile       process type for platforms that read one (Render/Railway/Heroku-style)
runtime.txt    pins the Python version for platforms that read one
```

## Running the deployable app (backend + frontend)

The FastAPI backend serves both the REST API and the static frontend from one process — no Docker,
just plain Python. On Windows, `run.bat` does all of this for you.

```bash
.venv/Scripts/pip install -e .
.venv/Scripts/pip install -r requirements.txt
.venv/Scripts/python -m retrieval.index_builder   # builds chroma_data/ from data/ (one-time, or after editing data/)
.venv/Scripts/uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 — the Chat tab talks to `/api/chat`, and Manage Restaurants talks to
`/api/restaurants`. See `src/api/main.py` for the full route list (`/api/health`,
`/api/sample-prompts`, `/api/chat`, `/api/restaurants` CRUD, `/api/recipes`).

### Deploying (no Docker)

This is a plain Python web service — any host that runs a Python app from a git repo works
(Render's native Python runtime, Railway, PythonAnywhere, a bare VM, etc.). `chroma_data/` is
gitignored (regenerable binary store), so it needs to be built once as part of your deploy's build
step, not assumed to already be on disk:

- **Build command:** `pip install -e . && pip install -r requirements.txt && python -m retrieval.index_builder`
- **Start command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT` (also in [`Procfile`](Procfile)
  for platforms that read one)
- **Environment variable:** `GROQ_API_KEY` (copy from your `.env`)
- **Python version:** 3.11 (pinned in [`runtime.txt`](runtime.txt) for platforms that read one — the
  ML stack here, torch/sentence-transformers/CLIP/chromadb, is not yet reliable on 3.14)

Re-run the `index_builder` step (or trigger a redeploy) any time `data/structured/restaurants.json`
or `data/recipes/recipes.json` change, since the vector index isn't rebuilt automatically from
API-driven CRUD edits.

### Notes on reliability

The recommendation workflow makes several Groq calls per chat message (intent classification,
preference extraction, profile generation, then 3 parallel agent analyses + synthesis). On a
free-tier Groq account this can hit per-minute rate limits under heavy use — `src/llm/groq_client.py`
caps concurrent in-flight calls and retries once on an empty completion (a known behavior of
reasoning models under a tight token budget) to keep this from surfacing as a silent failure, but a
paid/higher-limit Groq tier will make chat responses noticeably faster and more consistent.

## Other entry points

- `.venv/Scripts/python -m src.chatbot.app` — the original Gradio prototype (same `chatbot.service`
  logic as the API, different UI).
- `.venv/Scripts/python -m src.mcp_app.server` / `.mcp_app.client` / `.mcp_app.host_app` — an
  MCP server/client/host stack.
- `.venv/Scripts/python -m src.data.cli` — terminal CRUD for the restaurant dataset.
