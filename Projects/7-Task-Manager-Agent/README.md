# Task Manager Agent — Mini Project

A small full-stack app proving out the agent patterns from this folder's
`how-to-do.md` guide: a LangGraph tool-calling agent that adds, lists, updates,
completes and deletes tasks, remembers the conversation across requests via a
SQLite checkpointer, and pauses mid-run for a human-in-the-loop confirmation
before it deletes anything — running live behind a plain HTML/CSS/JS frontend.

| File | What it teaches |
|---|---|
| `db.py` | Plain `sqlite3` storage layer, no ORM |
| `tools.py` | `@tool`-decorated functions + `interrupt()` for human-in-the-loop |
| `agent.py` | The graph itself: `agent` node ⇄ `tools` node, `tools_condition` routing |
| `app.py` | FastAPI wiring: `SqliteSaver` checkpointer, `Command(resume=...)` |
| `static/` | Chat + task list UI, with a "How it works" panel and a raw request/response inspector |
| `test_agent.py` | Scripted `FakeModel` end-to-end test — no API key or network needed |

**Stack:** FastAPI + LangGraph (`MessagesState`, `ToolNode`, `tools_condition`,
`interrupt`/`Command`) + `SqliteSaver` for conversation memory + Groq for
generation (`qwen/qwen3.8-27b`, which supports tool calling on this account).

## Run it

From the repo root (needs the repo's `.env` with `GROQ_API_KEY` set):

```bash
pip install -r "7-Agentic AI with LangChain and LangGraph/Mini-Project-Task-Manager-Agent/requirements.txt"
python -m uvicorn app:app --reload --app-dir "7-Agentic AI with LangChain and LangGraph/Mini-Project-Task-Manager-Agent"
```

Then open http://localhost:8000 (or whichever port you pass with `--port`).
Interactive API docs (Swagger UI) are at `/docs`.

Try: *"add submit DBMS assignment due Friday, high priority"*, *"what's still
pending?"*, then *"delete the gym task"* to see the confirmation card. Refresh
the page — the conversation is still there, because it lives in
`checkpoints.db`.

## Test it without an API key

```bash
cd "7-Agentic AI with LangChain and LangGraph/Mini-Project-Task-Manager-Agent"
pytest -q
```

This swaps in a scripted `FakeModel` but still exercises the real graph, real
tools, real interrupt/resume and real SQLite storage — a pattern worth reusing
whenever you add features to an agent.
