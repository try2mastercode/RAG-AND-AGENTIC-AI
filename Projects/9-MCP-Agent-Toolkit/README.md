# MCP Agent Toolkit

A small full-stack app proving out the **Model Context Protocol** end to end: a real MCP
server (its own process) exposing notes/tasks as Tools, Resources and a Prompt, and a Groq
agent that reaches every one of them only through an MCP `ClientSession` over stdio — never
by calling a local Python function directly.

| File | What it teaches |
|---|---|
| `mcp_server.py` | A `FastMCP` server: `@mcp.tool()`, `@mcp.resource()`, `@mcp.prompt()` |
| `db.py` | Plain `sqlite3` storage layer, no ORM |
| `agent.py` | `MCPSession` (spawns the server, speaks MCP over stdio) + the Groq tool-calling loop |
| `app.py` | FastAPI wiring: one shared `MCPSession` for the app's lifetime, `/protocol` introspection |
| `static/` | Chat UI, a live "what the client discovered" panel, and a per-turn MCP call trace |
| `test_mcp.py` | Spins up the real server and drives it through `MCPSession` — no API key needed |

## The three MCP primitives, concretely

- **Tools** (`add_note`, `search_notes`, `add_task`, `list_tasks`, `complete_task`,
  `delete_task`, `calculate`) — actions with side effects, called by the model.
- **Resources** (`notes://all`, `tasks://all`) — read-only data, addressed by URI, fetched
  by the client directly (the sidebar reads these, not the chat tools).
- **Prompts** (`daily_planner`) — a template the server builds server-side from the current
  task list; "Plan my day" fetches it and feeds it to the agent as the next user turn.

## Why a separate process matters here

`mcp_server.py` never imports `agent.py`, and `agent.py` never imports the tool functions
from `mcp_server.py`. The only thing connecting them is `StdioServerParameters` +
`stdio_client` + `ClientSession` — the same mechanism you'd use to talk to *any* MCP server,
including ones written in a different language or running on a different machine. Swapping
in a real third-party MCP server (filesystem, GitHub, Slack, ...) only means changing the
`StdioServerParameters` in `agent.py`; nothing about the agent loop or the Groq tool-calling
code changes.

## Stack

FastAPI + the official `mcp` Python SDK (`FastMCP` server, `ClientSession` client) + the raw
`groq` SDK for OpenAI-style tool calling (`qwen/qwen3.8-27b`, which supports tool calling on
this account) + `sqlite3` for storage.

## Run it

Needs a `.env` file in this folder with `GROQ_API_KEY` set (copy `.env.example` and fill it in).

```bash
pip install -r requirements.txt
python -m uvicorn app:app --reload --port 8007
```

Then open http://localhost:8007. Interactive API docs (Swagger UI) are at `/docs`.

The "What the client discovered from the server" panel and the per-turn "Under the hood"
trace are real: they're the actual `list_tools`/`list_resources`/`list_prompts` results and
the actual `call_tool` arguments/results from that request, not simulated for the UI.

## Test it without an API key

```bash
pip install -r requirements.txt
python -m pytest test_mcp.py -v
```

This spawns the real `mcp_server.py` subprocess and drives it through `MCPSession` -
discovery, tool calls, resource reads, and the prompt template - with no Groq call at all,
so it needs no API key and no network.
