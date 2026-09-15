"""End-to-end test with a scripted fake LLM: no API key or network needed.

Run from this project folder:  pytest -q
"""
import os
import tempfile
from pathlib import Path

from langchain_core.messages import AIMessage

TMP = tempfile.mkdtemp()
os.environ["TASKS_DB"] = str(Path(TMP) / "tasks.db")
os.environ["CHECKPOINT_DB"] = str(Path(TMP) / "checkpoints.db")


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
    AIMessage(content="Added “Buy milk” for tomorrow."),
    call("delete_task", {"task_id": 1}, "c2"),
    AIMessage(content="Okay, I kept it."),
    call("delete_task", {"task_id": 1}, "c3"),
    AIMessage(content="Deleted."),
]

import agent  # noqa: E402

_real_build = agent.build_graph
agent.build_graph = lambda checkpointer=None: _real_build(model=FakeModel(SCRIPT), checkpointer=checkpointer)

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
