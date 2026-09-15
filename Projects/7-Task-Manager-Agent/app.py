"""FastAPI server: chat endpoints for the agent + a plain tasks API + the static frontend."""
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # must run before build_graph() so GROQ_API_KEY is in the environment

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command
from pydantic import BaseModel, Field

import db
from agent import build_graph

BASE_DIR = Path(__file__).parent

db.init_db()

# Conversation memory survives server restarts because it lives in SQLite.
# check_same_thread=False: FastAPI runs sync endpoints in a thread pool.
CHECKPOINT_DB = os.getenv("CHECKPOINT_DB", str(BASE_DIR / "checkpoints.db"))
checkpoint_conn = sqlite3.connect(CHECKPOINT_DB, check_same_thread=False)
graph = build_graph(checkpointer=SqliteSaver(checkpoint_conn))

app = FastAPI(
    title="Task Manager Agent",
    description="A LangGraph tool-calling agent with a checkpointed "
    "memory and a human-in-the-loop delete confirmation, backed by Groq.",
)


# ---------- SECTION 1: REQUEST MODELS ----------
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


# ---------- SECTION 2: CHAT ROUTES (agent-driven) ----------
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


# ---------- SECTION 3: PLAIN TASK ROUTES (no LLM call) ----------
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


# ---------- SECTION 4: FRONTEND (served at "/") ----------
STATIC_DIR = BASE_DIR / "static"
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
