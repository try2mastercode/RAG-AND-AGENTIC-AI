"""Plain sqlite3 storage for notes and tasks, no ORM."""
import os
import sqlite3
from pathlib import Path

DB_PATH = os.getenv("MCP_DB_PATH", str(Path(__file__).parent / "toolkit.db"))


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT NOT NULL DEFAULT ''
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                due_date TEXT,
                priority TEXT NOT NULL DEFAULT 'normal',
                done INTEGER NOT NULL DEFAULT 0
            )
        """)


# ---------- notes ----------
def add_note(title: str, content: str, tags: str = "") -> dict:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO notes (title, content, tags) VALUES (?, ?, ?)",
            (title, content, tags),
        )
        # same connection, before commit - a fresh get_conn() here wouldn't see the insert yet
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (cur.lastrowid,)).fetchone()
        return dict(row)


def get_note(note_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        return dict(row) if row else None


def search_notes(query: str) -> list[dict]:
    like = f"%{query}%"
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? OR tags LIKE ? ORDER BY id DESC",
            (like, like, like),
        ).fetchall()
        return [dict(r) for r in rows]


def list_notes() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM notes ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]


# ---------- tasks ----------
def add_task(title: str, due_date: str | None = None, priority: str = "normal") -> dict:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (title, due_date, priority) VALUES (?, ?, ?)",
            (title, due_date, priority),
        )
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (cur.lastrowid,)).fetchone()
        return dict(row)


def get_task(task_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return dict(row) if row else None


def list_tasks(include_done: bool = True) -> list[dict]:
    with get_conn() as conn:
        query = "SELECT * FROM tasks" if include_done else "SELECT * FROM tasks WHERE done = 0"
        rows = conn.execute(query + " ORDER BY id DESC").fetchall()
        return [dict(r) for r in rows]


def complete_task(task_id: int) -> dict | None:
    with get_conn() as conn:
        conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return dict(row) if row else None


def delete_task(task_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return cur.rowcount > 0
