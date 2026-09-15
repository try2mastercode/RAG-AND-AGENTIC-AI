# How to build a Task Manager Assistant Agent with LangGraph

This guide walks you through building a chat assistant that manages your to-do list. You type things like "add submit DBMS assignment due Friday, high priority" or "what's still pending?", and the agent decides which database action to take, runs it, and replies. Before it deletes anything, it pauses and asks you to confirm.

The backend is Python (LangGraph + FastAPI + SQLite). The frontend is plain HTML, CSS and JavaScript with no build step. Every file is included in full below, and the code has been run and tested end to end.

## Contents

1. What you're building
2. Prerequisites
3. Project structure
4. Set up the project
5. The database layer (`db.py`)
6. The agent's tools (`tools.py`)
7. The LangGraph agent (`agent.py`)
8. The API server (`app.py`)
9. The frontend (`index.html`, `style.css`, `app.js`)
10. Run it
11. Test it without an API key
12. How a request flows through the system
13. API reference
14. Troubleshooting
15. Where to take it next

---

## 1. What you're building

```
┌──────────────────────────┐        HTTP (JSON)       ┌────────────────────────────────────┐
│  Browser                 │ ───────────────────────► │  FastAPI  (app.py)                 │
│  index.html / app.js     │ ◄─────────────────────── │                                    │
│  chat panel + task list  │                          │   ┌──────────── LangGraph ───────┐ │
└──────────────────────────┘                          │   │                              │ │
                                                      │   │  START → agent ⇄ tools → END │ │
                                                      │   │           │        │         │ │
                                                      │   └───────────┼────────┼─────────┘ │
                                                      │               │        │           │
                                                      │            LLM API   SQLite        │
                                                      │         (Gemini etc.) tasks.db     │
                                                      │                                    │
                                                      │   checkpoints.db ← conversation    │
                                                      │                    memory          │
                                                      └────────────────────────────────────┘
```

The agent is a small graph with two nodes. The **agent** node sends the conversation to the LLM, which either answers directly or asks to call one or more tools. If it asks for tools, the **tools** node runs them and hands the results back to the agent node. That loop repeats until the LLM gives a plain answer.

Three LangGraph features do the heavy lifting here. `MessagesState` holds the conversation. A **checkpointer** saves that state to SQLite after every step, keyed by a `thread_id`, which is how the agent remembers the conversation between requests and even after a server restart. And `interrupt()` lets the `delete_task` tool pause the whole graph mid-run, wait for the user to click a button, and continue from exactly where it stopped.

## 2. Prerequisites

You need Python 3.10 or newer, a modern browser, and an API key for one LLM provider that supports tool calling. The guide defaults to Google Gemini because it has a free tier, but Groq, OpenAI and Anthropic work by changing two lines in `.env`.

The code was tested with `langgraph` 1.2 and `langchain` 1.4. LangGraph moves quickly, so the requirements file pins the major version (`<2`) to keep the APIs used here stable.

## 3. Project structure

```
task-agent/
├── backend/
│   ├── app.py              # FastAPI server, serves API + frontend
│   ├── agent.py            # LangGraph graph definition
│   ├── tools.py            # tools the LLM can call
│   ├── db.py               # SQLite helpers for tasks
│   ├── requirements.txt
│   └── .env.example        # copy to .env and add your key
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── tests/
│   └── test_agent.py       # end-to-end test with a fake LLM
└── .gitignore
```

FastAPI serves the `frontend/` folder itself, so the browser and the API share one origin and you don't need any CORS setup.

## 4. Set up the project

Create the folders and a virtual environment:

```bash
mkdir -p task-agent/backend task-agent/frontend task-agent/tests
cd task-agent
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

Create `backend/requirements.txt`:

```text
langgraph>=1.1,<2
langgraph-checkpoint-sqlite>=3.0
langchain>=1.0,<2
langchain-google-genai
fastapi
uvicorn[standard]
python-dotenv

# for running the tests
pytest
httpx
```

Install everything:

```bash
pip install -r backend/requirements.txt
```

Create `backend/.env.example`, then copy it to `backend/.env` and paste in your real key. Only the uncommented `MODEL` and key lines are used. If you switch providers, also `pip install` that provider's package, as noted beside each option.

```ini
# Pick ONE provider. Format for MODEL is "provider:model-name".

# Google Gemini (has a free tier) -> pip install langchain-google-genai
MODEL=google_genai:gemini-2.5-flash
GOOGLE_API_KEY=your-key-here

# Groq -> pip install langchain-groq
# MODEL=groq:llama-3.3-70b-versatile
# GROQ_API_KEY=your-key-here

# OpenAI -> pip install langchain-openai
# MODEL=openai:gpt-4o-mini
# OPENAI_API_KEY=your-key-here

# Anthropic -> pip install langchain-anthropic
# MODEL=anthropic:claude-sonnet-4-5
# ANTHROPIC_API_KEY=your-key-here
```

Model names change over time, so check your provider's docs for the current name if one of these is rejected. The format is always `provider:model-name`, which LangChain's `init_chat_model` understands.

Create `.gitignore` in the project root so your key and local databases never get committed:

```text
.venv/
__pycache__/
.env
*.db
.pytest_cache/
```

## 5. The database layer (`backend/db.py`)

This file knows nothing about AI. It's a thin set of functions over one SQLite table, which keeps the agent code focused and makes the storage easy to swap for Postgres later. The `CHECK` constraints mean bad values from the LLM get rejected by the database rather than silently stored. `list_tasks` sorts pending tasks first, then by priority, then by due date.

```python
"""SQLite storage for tasks. Plain sqlite3, no ORM, so the focus stays on the agent."""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = os.getenv("TASKS_DB", str(Path(__file__).parent / "tasks.db"))

PRIORITIES = ("low", "medium", "high")


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT NOT NULL,
                priority   TEXT NOT NULL DEFAULT 'medium'
                           CHECK (priority IN ('low', 'medium', 'high')),
                due_date   TEXT,
                status     TEXT NOT NULL DEFAULT 'pending'
                           CHECK (status IN ('pending', 'done')),
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )


def create_task(title: str, priority: str = "medium", due_date: str | None = None) -> dict:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (title, priority, due_date) VALUES (?, ?, ?)",
            (title, priority, due_date),
        )
        task_id = cur.lastrowid
    return get_task(task_id)


def get_task(task_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return dict(row) if row else None


def list_tasks(status: str | None = None) -> list[dict]:
    query = "SELECT * FROM tasks"
    params: tuple = ()
    if status:
        query += " WHERE status = ?"
        params = (status,)
    # pending first, then high > medium > low, then earliest due date
    query += """
        ORDER BY status = 'done',
                 CASE priority WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END,
                 due_date IS NULL, due_date, id
    """
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def update_task(task_id: int, **fields) -> dict | None:
    allowed = {"title", "priority", "due_date", "status"}
    fields = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not fields:
        return get_task(task_id)
    sets = ", ".join(f"{k} = ?" for k in fields)
    with get_conn() as conn:
        conn.execute(f"UPDATE tasks SET {sets} WHERE id = ?", (*fields.values(), task_id))
    return get_task(task_id)


def delete_task(task_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return cur.rowcount > 0
```

## 6. The agent's tools (`backend/tools.py`)

Tools are ordinary Python functions wrapped with `@tool`. LangChain turns each function's name, type hints and docstring into a schema the LLM reads when deciding what to call, so those docstrings matter more than usual. Using `Literal["low", "medium", "high"]` means the model is told the only allowed values up front.

`delete_task` is where human-in-the-loop happens. Calling `interrupt(payload)` stops the graph, saves its state through the checkpointer, and returns `payload` to whoever invoked the graph. Later, invoking the graph with `Command(resume="approve")` restarts this tool from the top, and this time `interrupt()` returns `"approve"` instead of pausing. Because the tool re-runs from the beginning on resume, any code before `interrupt()` should be safe to run twice (a read, like here, is fine).

```python
"""Tools the agent can call. The docstrings are what the LLM reads, so keep them clear."""
from typing import Literal

from langchain_core.tools import tool
from langgraph.types import interrupt

import db

Priority = Literal["low", "medium", "high"]


@tool
def add_task(title: str, priority: Priority = "medium", due_date: str | None = None) -> dict:
    """Create a new task.

    Args:
        title: Short description of the task.
        priority: low, medium or high.
        due_date: Due date as YYYY-MM-DD, or null if the user gave none.
    """
    return db.create_task(title, priority, due_date)


@tool
def list_tasks(status: Literal["pending", "done", "all"] = "all") -> list[dict]:
    """List tasks. Use this before updating or deleting so you know the task ids."""
    return db.list_tasks(None if status == "all" else status)


@tool
def update_task(
    task_id: int,
    title: str | None = None,
    priority: Priority | None = None,
    due_date: str | None = None,
) -> dict | str:
    """Change the title, priority or due date (YYYY-MM-DD) of an existing task."""
    task = db.update_task(task_id, title=title, priority=priority, due_date=due_date)
    return task or f"No task with id {task_id}."


@tool
def complete_task(task_id: int) -> dict | str:
    """Mark a task as done."""
    task = db.update_task(task_id, status="done")
    return task or f"No task with id {task_id}."


@tool
def delete_task(task_id: int) -> str:
    """Permanently delete a task. The app asks the user to confirm first."""
    task = db.get_task(task_id)
    if task is None:
        return f"No task with id {task_id}."

    # Human-in-the-loop: the graph pauses here and the API returns this payload
    # to the frontend. When the user answers, the graph resumes and `decision`
    # holds the value sent with Command(resume=...).
    decision = interrupt(
        {
            "action": "delete_task",
            "task_id": task_id,
            "question": f"Delete task #{task_id} \u201c{task['title']}\u201d?",
        }
    )
    if decision != "approve":
        return "The user cancelled the deletion. The task was kept."

    db.delete_task(task_id)
    return f"Deleted task #{task_id}."


TOOLS = [add_task, list_tasks, update_task, complete_task, delete_task]
```

## 7. The LangGraph agent (`backend/agent.py`)

This is the core of the project, and it's short.

`MessagesState` is a built-in state schema with a single `messages` list. Its reducer appends new messages rather than replacing the list, so each node only returns what it adds.

The `agent` node prepends a system prompt (with today's date, so "tomorrow" can be turned into a real date) and calls the model. `bind_tools` attaches the tool schemas to each call.

`ToolNode` is a prebuilt node that reads the tool calls from the last AI message, runs the matching functions, and appends a `ToolMessage` for each result.

`tools_condition` is a prebuilt router: if the last message contains tool calls it returns `"tools"`, otherwise it returns `END`.

`build_graph` accepts an optional `model` so the tests can pass in a fake one.

```python
"""The LangGraph agent: an LLM node and a tool node in a loop.

    START -> agent --(tool calls?)--> tools -> agent -> ... -> END
"""
import os
from datetime import date

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from tools import TOOLS

SYSTEM_PROMPT = """You are a task manager assistant. Today is {today}.

You help the user add, view, update, complete and delete tasks using your tools.
Rules:
- Convert relative dates ("tomorrow", "next Friday") to YYYY-MM-DD.
- If the user refers to a task by name, call list_tasks first to find its id.
- Never invent task ids.
- After a tool call, confirm what changed in one or two short sentences.
- If a request is not about tasks, answer briefly and steer back to tasks.
"""


def build_graph(model=None, checkpointer=None):
    if model is None:
        model = init_chat_model(os.getenv("MODEL", "google_genai:gemini-2.5-flash"), temperature=0)
    llm = model.bind_tools(TOOLS)

    def agent(state: MessagesState):
        system = SystemMessage(SYSTEM_PROMPT.format(today=date.today().isoformat()))
        response = llm.invoke([system, *state["messages"]])
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent)
    graph.add_node("tools", ToolNode(TOOLS))

    graph.add_edge(START, "agent")
    # tools_condition sends us to "tools" if the last message has tool calls, else END
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    return graph.compile(checkpointer=checkpointer)
```

The resulting graph looks like this:

```
        ┌─────────┐
        │  START  │
        └────┬────┘
             ▼
        ┌─────────┐   no tool calls   ┌───────┐
   ┌──► │  agent  │ ────────────────► │  END  │
   │    └────┬────┘                   └───────┘
   │         │ has tool calls
   │         ▼
   │    ┌─────────┐
   └─── │  tools  │  (delete_task may pause here with interrupt)
        └─────────┘
```

If you want to see it rendered, you can run `print(build_graph().get_graph().draw_mermaid())` and paste the output into mermaid.live.

## 8. The API server (`backend/app.py`)

The server compiles the graph once at startup with a `SqliteSaver` checkpointer. Every request passes a `thread_id` in the config, and LangGraph loads that thread's saved messages before running, so the frontend only ever sends the new message.

`run_graph` handles both outcomes of a run. When the graph pauses, `invoke()` returns a result containing an `__interrupt__` key, and the API sends its payload to the frontend as `confirm`. Otherwise it sends the last AI message as `reply`. The response always includes the current task list so the sidebar stays in sync.

Two details prevent subtle bugs. First, `/api/chat` refuses new messages while a thread is waiting on a confirmation, because most LLM providers return an error if a tool call is left without a result. Second, `message_text` handles providers that return content as a list of blocks instead of a plain string.

`/api/history/{thread_id}` lets the page redraw the conversation after a refresh, and `/api/tasks/{id}/toggle` lets the checkboxes work directly without going through the LLM, which is faster and costs nothing.

```python
"""FastAPI server: chat endpoints for the agent + a plain tasks API + the static frontend."""
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # must run before build_graph() so API keys are in the environment

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command
from pydantic import BaseModel, Field

import db
from agent import build_graph

BASE_DIR = Path(__file__).parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

db.init_db()

# Conversation memory survives server restarts because it lives in SQLite.
# check_same_thread=False: FastAPI runs sync endpoints in a thread pool.
CHECKPOINT_DB = os.getenv("CHECKPOINT_DB", str(BASE_DIR / "checkpoints.db"))
checkpoint_conn = sqlite3.connect(CHECKPOINT_DB, check_same_thread=False)
graph = build_graph(checkpointer=SqliteSaver(checkpoint_conn))

app = FastAPI(title="Task Manager Agent")


class ChatIn(BaseModel):
    thread_id: str = Field(min_length=1)
    message: str = Field(min_length=1, max_length=2000)


class ResumeIn(BaseModel):
    thread_id: str = Field(min_length=1)
    approved: bool


def message_text(message) -> str:
    """Providers return content as a string or as a list of content blocks."""
    content = message.content
    if isinstance(content, str):
        return content
    return "".join(
        block.get("text", "") if isinstance(block, dict) else str(block) for block in content
    )


def config_for(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def pending_confirm(thread_id: str):
    """If this thread is paused on a confirmation, return its payload."""
    state = graph.get_state(config_for(thread_id))
    return state.interrupts[0].value if state.interrupts else None


def run_graph(graph_input, thread_id: str) -> dict:
    config = config_for(thread_id)
    try:
        result = graph.invoke(graph_input, config)
    except Exception as exc:  # model/API errors should reach the UI, not crash it
        raise HTTPException(status_code=502, detail=f"Agent error: {exc}") from exc

    interrupts = result.get("__interrupt__")
    if interrupts:
        return {"reply": None, "confirm": interrupts[0].value, "tasks": db.list_tasks()}

    return {
        "reply": message_text(result["messages"][-1]),
        "confirm": None,
        "tasks": db.list_tasks(),
    }


@app.post("/api/chat")
def chat(body: ChatIn):
    # A thread paused on "delete?" must be answered before it can take new input,
    # otherwise the model sees a tool call with no result and most providers error.
    confirm = pending_confirm(body.thread_id)
    if confirm:
        return {"reply": "Please answer the confirmation above first.", "confirm": confirm,
                "tasks": db.list_tasks()}
    return run_graph({"messages": [{"role": "user", "content": body.message}]}, body.thread_id)


@app.post("/api/chat/resume")
def resume(body: ResumeIn):
    decision = "approve" if body.approved else "reject"
    return run_graph(Command(resume=decision), body.thread_id)


@app.get("/api/history/{thread_id}")
def history(thread_id: str):
    """Visible chat history, so a page refresh can redraw the conversation."""
    state = graph.get_state(config_for(thread_id))
    messages = []
    for m in state.values.get("messages", []):
        if m.type not in ("human", "ai"):
            continue  # skip tool results
        text = message_text(m)
        if text:  # skip AI messages that only contain tool calls
            messages.append({"role": "user" if m.type == "human" else "bot", "text": text})
    return {"messages": messages, "confirm": pending_confirm(thread_id)}


@app.get("/api/tasks")
def get_tasks():
    return db.list_tasks()


@app.post("/api/tasks/{task_id}/toggle")
def toggle_task(task_id: int):
    task = db.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    new_status = "pending" if task["status"] == "done" else "done"
    return db.update_task(task_id, status=new_status)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Mounted last so /api/* routes win. html=True serves index.html at "/".
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
```

## 9. The frontend

### `frontend/index.html`

Two panels: the chat on the left and your task list on the right (stacked on phones). The suggestion buttons show new users what they can ask.

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Taskmate</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <header class="topbar">
    <div class="topbar-inner">
      <h1>Taskmate</h1>
      <button id="new-chat" class="ghost" type="button">New conversation</button>
    </div>
  </header>

  <main class="layout">
    <section class="chat" aria-label="Chat with the assistant">
      <ol id="messages" class="messages" aria-live="polite">
        <li class="empty" id="empty-state">
          <p>Tell me what you need to get done. For example:</p>
          <div class="suggestions">
            <button type="button" class="chip">Add “submit assignment” due Friday, high priority</button>
            <button type="button" class="chip">What’s still pending?</button>
            <button type="button" class="chip">Move the gym task to next Monday</button>
          </div>
        </li>
      </ol>

      <form id="composer" class="composer">
        <label for="input" class="sr-only">Message</label>
        <textarea id="input" rows="1" placeholder="Add or update a task…" autocomplete="off"></textarea>
        <button id="send" type="submit">Send</button>
      </form>
    </section>

    <aside class="tasks" aria-label="Your tasks">
      <div class="tasks-head">
        <h2>Your tasks</h2>
        <span id="task-count" class="count"></span>
      </div>
      <ul id="task-list" class="task-list"></ul>
      <p id="tasks-empty" class="tasks-empty" hidden>No tasks yet. Ask the assistant to add one.</p>
    </aside>
  </main>

  <script src="app.js"></script>
</body>
</html>
```

### `frontend/style.css`

A calm sage-and-pine palette, with a coloured stripe on each task showing its priority (red for high, amber for medium, green for low). It includes visible keyboard focus and a single-column layout for small screens.

```css
:root {
  --bg: #eef2f0;
  --surface: #ffffff;
  --ink: #1d2b28;
  --muted: #5e6e6a;
  --line: #d5ddda;
  --accent: #2e6b5e;
  --accent-ink: #ffffff;
  --high: #b42318;
  --medium: #b7791f;
  --low: #4a7c59;
  --radius: 10px;
  font-family: "Atkinson Hyperlegible", system-ui, sans-serif;
  color: var(--ink);
  background: var(--bg);
}

* { box-sizing: border-box; }
body { margin: 0; min-height: 100vh; display: flex; flex-direction: column; }
button, textarea { font: inherit; color: inherit; }
button { cursor: pointer; }
:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }

.sr-only {
  position: absolute; width: 1px; height: 1px; overflow: hidden;
  clip: rect(0 0 0 0); white-space: nowrap;
}

/* ---------- top bar ---------- */
.topbar { border-bottom: 1px solid var(--line); }
.topbar-inner {
  display: flex; align-items: center; justify-content: space-between;
  max-width: 1200px; margin: 0 auto; padding: 0.9rem 1.5rem;
}
.topbar h1 { margin: 0; font-size: 1.35rem; letter-spacing: -0.01em; }

.ghost {
  background: none; border: 1px solid var(--line); border-radius: 999px;
  padding: 0.4rem 0.9rem; font-size: 0.9rem;
}
.ghost:hover { border-color: var(--accent); color: var(--accent); }

/* ---------- layout ---------- */
.layout {
  flex: 1;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 1.5rem;
  padding: 1.5rem;
  max-width: 1200px; width: 100%; margin: 0 auto;
  min-height: 0;
}

/* ---------- chat ---------- */
.chat {
  display: flex; flex-direction: column;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  height: calc(100vh - 7rem);
}
.messages {
  list-style: none; margin: 0; padding: 1.25rem;
  flex: 1; overflow-y: auto;
  display: flex; flex-direction: column; gap: 0.75rem;
}
.msg {
  max-width: 75ch; padding: 0.65rem 0.9rem;
  border-radius: 14px; line-height: 1.5; white-space: pre-wrap;
}
.msg.user { align-self: flex-end; background: var(--accent); color: var(--accent-ink); border-bottom-right-radius: 4px; }
.msg.bot  { align-self: flex-start; background: var(--bg); border-bottom-left-radius: 4px; }
.msg.error { align-self: flex-start; background: #fdecea; color: var(--high); }
.msg.thinking { color: var(--muted); font-style: italic; }

.empty { color: var(--muted); margin: auto 0; }
.empty p { margin: 0 0 0.75rem; }
.suggestions { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.chip {
  background: var(--surface); border: 1px solid var(--line);
  border-radius: 999px; padding: 0.45rem 0.9rem; text-align: left;
}
.chip:hover { border-color: var(--accent); }

/* confirmation card for deletes */
.confirm {
  align-self: flex-start; max-width: 75ch;
  border: 2px solid var(--high); border-radius: var(--radius);
  padding: 0.8rem 1rem; background: var(--surface);
}
.confirm p { margin: 0 0 0.7rem; font-weight: 700; }
.confirm .actions { display: flex; gap: 0.5rem; }
.danger { background: var(--high); color: #fff; border: 0; border-radius: 8px; padding: 0.45rem 0.9rem; }
.plain  { background: none; border: 1px solid var(--line); border-radius: 8px; padding: 0.45rem 0.9rem; }
.confirm.answered { border-color: var(--line); opacity: 0.7; }

.composer {
  display: flex; gap: 0.6rem; padding: 0.9rem;
  border-top: 1px solid var(--line);
}
.composer textarea {
  flex: 1; resize: none; max-height: 8rem;
  border: 1px solid var(--line); border-radius: 8px;
  padding: 0.6rem 0.75rem; background: var(--surface);
}
#send {
  background: var(--accent); color: var(--accent-ink);
  border: 0; border-radius: 8px; padding: 0 1.2rem; font-weight: 700;
}
#send:disabled { opacity: 0.5; cursor: not-allowed; }

/* ---------- task list ---------- */
.tasks { align-self: start; }
.tasks-head { display: flex; align-items: baseline; justify-content: space-between; }
.tasks-head h2 { margin: 0 0 0.8rem; font-size: 1.1rem; }
.count { color: var(--muted); font-size: 0.9rem; }

.task-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.5rem; }
.task {
  display: grid; grid-template-columns: auto 1fr; gap: 0.2rem 0.7rem;
  align-items: start;
  background: var(--surface);
  border: 1px solid var(--line);
  border-left: 5px solid var(--prio, var(--line));
  border-radius: 6px;
  padding: 0.65rem 0.8rem;
}
.task.high   { --prio: var(--high); }
.task.medium { --prio: var(--medium); }
.task.low    { --prio: var(--low); }
.task input { width: 1.15rem; height: 1.15rem; margin-top: 0.15rem; accent-color: var(--accent); }
.task .title { font-weight: 700; overflow-wrap: anywhere; }
.task .meta { grid-column: 2; color: var(--muted); font-size: 0.85rem; }
.task .meta .overdue { color: var(--high); font-weight: 700; }
.task.done .title { text-decoration: line-through; color: var(--muted); font-weight: 400; }
.task.done { border-left-color: var(--line); }

.tasks-empty { color: var(--muted); }

/* ---------- small screens ---------- */
@media (max-width: 800px) {
  .layout { grid-template-columns: 1fr; padding: 1rem; }
  .topbar-inner { padding: 0.9rem 1rem; }
  .chat { height: 70vh; }
}

@media (prefers-reduced-motion: no-preference) {
  .task { transition: opacity 0.2s; }
}
```

### `frontend/app.js`

The script keeps a `thread_id` in `localStorage`, so refreshing the page continues the same conversation, and "New conversation" simply generates a fresh one. All model output is inserted with `textContent`, never `innerHTML`, because text coming from an LLM should be treated as untrusted. When a response contains `confirm`, the script draws a card with "Delete task" and "Keep task" buttons that call `/api/chat/resume`.

```javascript
// Plain JS, no build step. Talks to the FastAPI backend on the same origin.

const API = "/api";

const els = {
  messages: document.getElementById("messages"),
  empty: document.getElementById("empty-state"),
  form: document.getElementById("composer"),
  input: document.getElementById("input"),
  send: document.getElementById("send"),
  taskList: document.getElementById("task-list"),
  tasksEmpty: document.getElementById("tasks-empty"),
  taskCount: document.getElementById("task-count"),
  newChat: document.getElementById("new-chat"),
};

// One thread_id = one conversation in the LangGraph checkpointer.
// Kept in localStorage so a page refresh continues the same conversation.
function getThreadId() {
  let id = localStorage.getItem("thread_id");
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem("thread_id", id);
  }
  return id;
}
let threadId = getThreadId();

// ---------- rendering ----------

function addMessage(text, kind) {
  els.empty.hidden = true;
  const li = document.createElement("li");
  li.className = `msg ${kind}`;
  li.textContent = text; // textContent, never innerHTML: model output is untrusted
  els.messages.appendChild(li);
  li.scrollIntoView({ block: "end" });
  return li;
}

function addConfirm(payload) {
  const li = document.createElement("li");
  li.className = "confirm";

  const question = document.createElement("p");
  question.textContent = payload.question;

  const actions = document.createElement("div");
  actions.className = "actions";

  const yes = document.createElement("button");
  yes.className = "danger";
  yes.type = "button";
  yes.textContent = "Delete task";

  const no = document.createElement("button");
  no.className = "plain";
  no.type = "button";
  no.textContent = "Keep task";

  const answer = async (approved) => {
    if (li.classList.contains("answered")) return;
    li.classList.add("answered");
    yes.disabled = no.disabled = true;
    question.textContent += approved ? " — you chose delete." : " — you chose keep.";
    await send(`${API}/chat/resume`, { thread_id: threadId, approved });
  };
  yes.addEventListener("click", () => answer(true));
  no.addEventListener("click", () => answer(false));

  actions.append(yes, no);
  li.append(question, actions);
  els.messages.appendChild(li);
  li.scrollIntoView({ block: "end" });
  no.focus();
}

function formatDue(due) {
  if (!due) return null;
  const today = new Date().toISOString().slice(0, 10);
  const date = new Date(`${due}T00:00:00`);
  const label = date.toLocaleDateString(undefined, { day: "numeric", month: "short" });
  return { label, overdue: due < today };
}

function renderTasks(tasks) {
  els.taskList.replaceChildren();
  els.tasksEmpty.hidden = tasks.length > 0;
  const pending = tasks.filter((t) => t.status === "pending").length;
  els.taskCount.textContent = tasks.length ? `${pending} pending` : "";

  for (const task of tasks) {
    const li = document.createElement("li");
    li.className = `task ${task.priority} ${task.status}`;

    const box = document.createElement("input");
    box.type = "checkbox";
    box.checked = task.status === "done";
    box.id = `task-${task.id}`;
    box.addEventListener("change", () => toggleTask(task.id));

    const title = document.createElement("label");
    title.className = "title";
    title.htmlFor = box.id;
    title.textContent = task.title;

    const meta = document.createElement("div");
    meta.className = "meta";
    const parts = [`#${task.id}`, `${task.priority} priority`];
    meta.textContent = parts.join(", ");
    const due = formatDue(task.due_date);
    if (due) {
      meta.append(", ");
      const span = document.createElement("span");
      if (due.overdue && task.status !== "done") {
        span.className = "overdue";
        span.textContent = `overdue since ${due.label}`;
      } else {
        span.textContent = `due ${due.label}`;
      }
      meta.appendChild(span);
    }

    li.append(box, title, meta);
    els.taskList.appendChild(li);
  }
}

// ---------- network ----------

async function send(url, body) {
  setBusy(true);
  const thinking = addMessage("Thinking…", "bot thinking");
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    thinking.remove();

    if (!res.ok) {
      addMessage(data.detail || `Request failed (${res.status}).`, "error");
      return;
    }
    if (data.reply) addMessage(data.reply, "bot");
    if (data.confirm) addConfirm(data.confirm);
    renderTasks(data.tasks);
  } catch (err) {
    thinking.remove();
    addMessage("Can't reach the server. Check that uvicorn is running.", "error");
  } finally {
    setBusy(false);
  }
}

async function loadTasks() {
  try {
    const res = await fetch(`${API}/tasks`);
    renderTasks(await res.json());
  } catch {
    els.tasksEmpty.hidden = false;
    els.tasksEmpty.textContent = "Can't load tasks. Check that the server is running.";
  }
}

async function toggleTask(id) {
  await fetch(`${API}/tasks/${id}/toggle`, { method: "POST" });
  // Redraw the conversation after a page refresh
async function loadHistory() {
  try {
    const res = await fetch(`${API}/history/${threadId}`);
    const data = await res.json();
    for (const m of data.messages) addMessage(m.text, m.role);
    if (data.confirm) addConfirm(data.confirm);
  } catch {
    /* no history yet, nothing to show */
  }
}

loadHistory();
loadTasks();
}

function setBusy(busy) {
  els.send.disabled = busy;
  els.input.disabled = busy;
  // leave focus on the confirm buttons if a question is waiting
  const waiting = els.messages.querySelector(".confirm:not(.answered)");
  if (!busy && !waiting) els.input.focus();
}

// ---------- events ----------

els.form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = els.input.value.trim();
  if (!text) return;
  addMessage(text, "user");
  els.input.value = "";
  autoGrow();
  send(`${API}/chat`, { thread_id: threadId, message: text });
});

// Enter sends, Shift+Enter makes a new line
els.input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    els.form.requestSubmit();
  }
});

function autoGrow() {
  els.input.style.height = "auto";
  els.input.style.height = `${els.input.scrollHeight}px`;
}
els.input.addEventListener("input", autoGrow);

document.querySelectorAll(".chip").forEach((chip) =>
  chip.addEventListener("click", () => {
    els.input.value = chip.textContent.replace(/[“”]/g, '"');
    els.form.requestSubmit();
  })
);

els.newChat.addEventListener("click", () => {
  localStorage.removeItem("thread_id");
  threadId = getThreadId();
  els.messages.replaceChildren(els.empty);
  els.empty.hidden = false;
  els.input.focus();
});

// Redraw the conversation after a page refresh
async function loadHistory() {
  try {
    const res = await fetch(`${API}/history/${threadId}`);
    const data = await res.json();
    for (const m of data.messages) addMessage(m.text, m.role);
    if (data.confirm) addConfirm(data.confirm);
  } catch {
    /* no history yet, nothing to show */
  }
}

loadHistory();
loadTasks();
```

## 10. Run it

From the `backend/` folder, with your virtual environment active and `.env` filled in:

```bash
cd backend
uvicorn app:app --reload
```

Open http://127.0.0.1:8000 in your browser. A good first session to try:

```
add submit DBMS assignment due Friday, high priority
also add gym on Monday, low priority
what's pending?
move the gym one to Tuesday
delete the gym task          ← a confirmation card appears
```

Click "Keep task" once to confirm nothing changes, then ask again and click "Delete task". Refresh the page and the conversation is still there. Stop and restart uvicorn and it's still there, because it lives in `checkpoints.db`.

FastAPI also generates interactive API docs at http://127.0.0.1:8000/docs, which is handy for calling the endpoints directly.

## 11. Test it without an API key

The test replaces the real LLM with a `FakeModel` that returns pre-written messages in order, including tool calls. That means it exercises the real graph, the real tools, the real interrupt and resume, the real SQLite storage and the real HTTP endpoints, without any network access. It uses temporary databases so your real data is untouched.

Create `tests/test_agent.py`:

```python
"""End-to-end test with a scripted fake LLM: no API key or network needed.

Run from the project root:  pytest -q
"""
import os
import sys
import tempfile
from pathlib import Path

from langchain_core.messages import AIMessage

# Use throwaway databases and make backend/ importable
TMP = tempfile.mkdtemp()
os.environ["TASKS_DB"] = str(Path(TMP) / "tasks.db")
os.environ["CHECKPOINT_DB"] = str(Path(TMP) / "checkpoints.db")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))


class FakeModel:
    """Returns pre-written AI messages in order, standing in for a real LLM."""

    def __init__(self, script):
        self.script = list(script)

    def bind_tools(self, tools):
        return self

    def invoke(self, messages):
        return self.script.pop(0)


def call(name, args, call_id):
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": call_id}])


SCRIPT = [
    call("add_task", {"title": "Buy milk", "priority": "high", "due_date": "2026-09-16"}, "c1"),
    AIMessage(content="Added \u201cBuy milk\u201d for tomorrow."),
    call("delete_task", {"task_id": 1}, "c2"),
    AIMessage(content="Okay, I kept it."),
    call("delete_task", {"task_id": 1}, "c3"),
    AIMessage(content="Deleted."),
]

import agent  # noqa: E402

_real_build = agent.build_graph
agent.build_graph = lambda checkpointer=None: _real_build(
    model=FakeModel(SCRIPT), checkpointer=checkpointer
)

import app as app_module  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

client = TestClient(app_module.app)
THREAD = "test-thread"


def test_full_flow():
    # 1. add a task through the agent
    r = client.post("/api/chat", json={"thread_id": THREAD, "message": "add buy milk tomorrow, high"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["reply"].startswith("Added")
    assert data["tasks"][0]["title"] == "Buy milk"

    # 2. ask to delete -> graph pauses for confirmation
    r = client.post("/api/chat", json={"thread_id": THREAD, "message": "delete it"})
    data = r.json()
    assert data["reply"] is None
    assert data["confirm"]["action"] == "delete_task"

    # while paused, a new message is refused and the question is repeated
    r = client.post("/api/chat", json={"thread_id": THREAD, "message": "hello?"})
    assert r.json()["confirm"]["action"] == "delete_task"
    h = client.get(f"/api/history/{THREAD}").json()
    assert h["confirm"] is not None
    assert h["messages"][0] == {"role": "user", "text": "add buy milk tomorrow, high"}

    # 3. user says no -> task survives
    r = client.post("/api/chat/resume", json={"thread_id": THREAD, "approved": False})
    data = r.json()
    assert data["reply"] == "Okay, I kept it."
    assert len(data["tasks"]) == 1

    # 4. ask again, user says yes -> task gone
    client.post("/api/chat", json={"thread_id": THREAD, "message": "delete it"})
    r = client.post("/api/chat/resume", json={"thread_id": THREAD, "approved": True})
    data = r.json()
    assert data["reply"] == "Deleted."
    assert data["tasks"] == []


def test_toggle_and_frontend():
    task = app_module.db.create_task("Write report")
    r = client.post(f"/api/tasks/{task['id']}/toggle")
    assert r.json()["status"] == "done"
    assert client.post("/api/tasks/9999/toggle").status_code == 404
    assert client.get("/").status_code == 200  # index.html is served
```

Run it from the project root:

```bash
pytest -q
```

You should see `2 passed`. This pattern of scripting the model's outputs is worth keeping as you add features, since it makes agent tests fast and deterministic.

## 12. How a request flows through the system

Here's what happens when you type "delete the gym task" and then click "Delete task".

```
Browser                    FastAPI                   LangGraph                     SQLite
   │ POST /api/chat           │                          │                            │
   │ {thread_id, message} ──► │ pending_confirm? no      │                            │
   │                          │ invoke(messages) ──────► │ load thread from           │
   │                          │                          │ checkpoints.db             │
   │                          │                          │ agent: LLM → list_tasks    │
   │                          │                          │ tools: list_tasks ───────► │ SELECT
   │                          │                          │ agent: LLM → delete_task(2)│
   │                          │                          │ tools: delete_task         │
   │                          │                          │   interrupt(...)  ⏸ saved  │
   │ ◄── {confirm: {...}} ─── │ ◄── __interrupt__ ────── │                            │
   │                          │                          │                            │
   │ user clicks Delete       │                          │                            │
   │ POST /api/chat/resume ─► │ invoke(Command(resume=   │                            │
   │ {thread_id, approved}    │        "approve")) ────► │ re-run delete_task,        │
   │                          │                          │ interrupt → "approve"      │
   │                          │                          │ db.delete_task ──────────► │ DELETE
   │                          │                          │ agent: LLM → "Deleted."    │
   │ ◄── {reply, tasks} ───── │ ◄── final state ──────── │                            │
```

## 13. API reference

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/api/chat` | `{ "thread_id": str, "message": str }` | `{ reply, confirm, tasks }` |
| POST | `/api/chat/resume` | `{ "thread_id": str, "approved": bool }` | `{ reply, confirm, tasks }` |
| GET | `/api/history/{thread_id}` | none | `{ messages: [{role, text}], confirm }` |
| GET | `/api/tasks` | none | list of tasks |
| POST | `/api/tasks/{id}/toggle` | none | the updated task, or 404 |
| GET | `/api/health` | none | `{ "status": "ok" }` |

In chat responses, exactly one of `reply` and `confirm` is set (except when a new message arrives while a confirmation is still waiting, where both are set so the UI can remind you). A task looks like this:

```json
{
  "id": 1,
  "title": "Submit DBMS assignment",
  "priority": "high",
  "due_date": "2026-09-18",
  "status": "pending",
  "created_at": "2026-09-15 07:11:02"
}
```

## 14. Troubleshooting

**"Unable to import langchain_google_genai" (or groq/openai/anthropic).** The provider package isn't installed. Run `pip install langchain-google-genai` (or the package named next to your chosen provider in `.env.example`).

**The server starts, but chat returns "Agent error: … API key …".** Check that `backend/.env` exists (not just `.env.example`), that you started uvicorn from inside `backend/`, and that the key variable name matches your provider.

**"Agent error: … model not found".** The model name has changed or isn't available on your account. Look up the current name in your provider's docs and update `MODEL`.

**The agent replies but never changes any tasks.** Some smaller models are weak at tool calling. Try a stronger model, and keep `temperature=0`.

**Dates are wrong.** The system prompt uses the server's clock via `date.today()`. If your server runs in a different time zone from you, pass the user's local date from the frontend and put that in the prompt instead.

**The page loads but says it can't reach the server.** Open the page through uvicorn (http://127.0.0.1:8000), not by double-clicking `index.html`, because the script calls `/api/...` on the same origin.

**A conversation seems stuck.** It's probably waiting on a confirmation. Answer the card, or click "New conversation" to start a fresh thread. Deleting `checkpoints.db` wipes all conversation memory.

**"database is locked".** SQLite allows one writer at a time. That's fine for a personal project; for many users, move to Postgres (see below).

## 15. Where to take it next

These extensions each teach a useful LangGraph or backend concept, roughly in order of effort.

**Stream the reply.** Use `graph.stream(..., stream_mode="messages")` and return a `StreamingResponse` (server-sent events), then read it in `app.js` with `fetch` and a `ReadableStream` so text appears as it's generated.

**Show tool activity.** Stream with `stream_mode="updates"` and display small notes like "Looking up your tasks…" while tools run.

**Add users.** Add JWT auth, a `user_id` column on `tasks`, and pass the user id into the tools through the graph config (`config["configurable"]["user_id"]`) rather than letting the LLM supply it, so one user can never touch another's tasks.

**Move to Postgres.** Swap `db.py` for SQLAlchemy or psycopg and `SqliteSaver` for `PostgresSaver` from `langgraph-checkpoint-postgres`. The graph code doesn't change.

**Richer tasks.** Add tags, notes, recurring tasks or subtasks. Each is a new column plus a tool parameter, and the LLM picks them up from the updated docstrings.

**A planning node.** Add a node that, when you ask "plan my week", reads all pending tasks and proposes a schedule. This is a good first step toward multi-node graphs beyond the basic tool loop.

**Deploy it.** Add a `Dockerfile` that runs `uvicorn app:app --host 0.0.0.0 --port $PORT` from `backend/`, set your API key as an environment variable on the host (Railway, Render, Fly.io), and use a mounted volume or Postgres so the databases survive redeploys.

**Trace it.** Set `LANGSMITH_TRACING=true` and `LANGSMITH_API_KEY` to see each graph step, prompt and tool call in LangSmith, which makes debugging agent behaviour much easier.
