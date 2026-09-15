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
            "question": f"Delete task #{task_id} “{task['title']}”?",
        }
    )
    if decision != "approve":
        return "The user cancelled the deletion. The task was kept."

    db.delete_task(task_id)
    return f"Deleted task #{task_id}."


TOOLS = [add_task, list_tasks, update_task, complete_task, delete_task]
