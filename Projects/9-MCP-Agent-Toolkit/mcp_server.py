"""The MCP server: exposes notes/tasks as Tools, Resources and a Prompt over stdio.

Run standalone for debugging: `python mcp_server.py`
Run wired into the agent: spawned as a subprocess by mcp_client.py via stdio_client.
"""
import ast
import operator

from mcp.server.fastmcp import FastMCP

import db

db.init_db()

mcp = FastMCP("toolkit")


# ---------- SECTION 1: TOOLS (actions the model can invoke, with side effects) ----------
@mcp.tool()
def add_note(title: str, content: str, tags: str = "") -> dict:
    """Save a note. tags is a comma-separated string, e.g. "exam,rag"."""
    return db.add_note(title, content, tags)


@mcp.tool()
def search_notes(query: str) -> list[dict]:
    """Search notes by title, content or tags (substring match)."""
    return db.search_notes(query)


@mcp.tool()
def add_task(title: str, due_date: str | None = None, priority: str = "normal") -> dict:
    """Add a task. due_date is YYYY-MM-DD. priority is low, normal or high."""
    return db.add_task(title, due_date, priority)


@mcp.tool()
def list_tasks(include_done: bool = True) -> list[dict]:
    """List tasks, optionally excluding ones already marked done."""
    return db.list_tasks(include_done)


@mcp.tool()
def complete_task(task_id: int) -> dict | None:
    """Mark a task done by its id."""
    return db.complete_task(task_id)


@mcp.tool()
def delete_task(task_id: int) -> bool:
    """Delete a task by its id. Returns whether a row was actually removed."""
    return db.delete_task(task_id)


_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg,
}


def _safe_eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("unsupported expression")


@mcp.tool()
def calculate(expression: str) -> float:
    """Evaluate a plain arithmetic expression, e.g. "12 * (3 + 4)". No variables or functions."""
    return _safe_eval(ast.parse(expression, mode="eval").body)


# ---------- SECTION 2: RESOURCES (read-only data, addressed by URI, no side effects) ----------
@mcp.resource("notes://all")
def all_notes() -> list[dict]:
    """Every saved note."""
    return db.list_notes()


@mcp.resource("tasks://all")
def all_tasks() -> list[dict]:
    """Every task, done or not."""
    return db.list_tasks()


# ---------- SECTION 3: PROMPTS (reusable, parameterised prompt templates) ----------
@mcp.prompt()
def daily_planner() -> str:
    """Build a 'plan my day' prompt seeded with the current open tasks."""
    open_tasks = db.list_tasks(include_done=False)
    if not open_tasks:
        return "I have no open tasks right now. Suggest how I should plan my day anyway."
    lines = "\n".join(f"- [{t['priority']}] {t['title']} (due {t['due_date'] or 'no date'})" for t in open_tasks)
    return f"Here are my open tasks:\n{lines}\n\nHelp me plan today: what order should I do these in, and why?"


if __name__ == "__main__":
    mcp.run(transport="stdio")
