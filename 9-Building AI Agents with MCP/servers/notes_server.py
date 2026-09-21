# ---------- SECTION 1: IMPORTS ----------
from mcp.server.fastmcp import FastMCP


# ---------- SECTION 2: SERVER + IN-MEMORY STATE ----------
# Real MCP servers are usually stateful processes (a DB, a filesystem, an API
# session) - this one keeps its notes in a plain list for the same reason: the
# state lives in the SERVER, and every client call is a real round trip to it.
mcp = FastMCP("notes-server")
_notes: list[dict] = []
_next_id = 1


# ---------- SECTION 3: CRUD TOOLS ----------
@mcp.tool()
def add_note(title: str, content: str) -> dict:
    """Create a note and return it, including its new id."""
    global _next_id
    note = {"id": _next_id, "title": title, "content": content}
    _notes.append(note)
    _next_id += 1
    return note


@mcp.tool()
def list_notes() -> list[dict]:
    """List every saved note."""
    return _notes


@mcp.tool()
def delete_note(note_id: int) -> bool:
    """Delete a note by id. Returns whether a note was actually removed."""
    before = len(_notes)
    _notes[:] = [n for n in _notes if n["id"] != note_id]
    return len(_notes) < before


# ---------- SECTION 4: A RESOURCE MIRRORING THE SAME STATE ----------
# Tools and resources can read the same underlying state; the difference is
# intent - a resource is meant to be fetched for context, not "invoked".
@mcp.resource("notes://all")
def all_notes() -> list[dict]:
    """Every saved note, as a resource instead of a tool call."""
    return _notes


if __name__ == "__main__":
    mcp.run(transport="stdio")
