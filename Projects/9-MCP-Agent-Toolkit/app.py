"""FastAPI server: chat endpoint backed by the MCP agent, plain resource/prompt
endpoints for the sidebar, and the static frontend."""
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from groq import AsyncGroq
from pydantic import BaseModel, Field

from agent import MCPSession, run_turn

BASE_DIR = Path(__file__).parent

conversations: dict[str, list[dict]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.mcp = await MCPSession().start()
    app.state.groq = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    yield
    await app.state.mcp.close()


app = FastAPI(
    title="MCP Agent Toolkit",
    description="A Groq agent that talks to its notes/tasks tools over the real "
    "Model Context Protocol, not local function calls.",
    lifespan=lifespan,
)


# ---------- SECTION 1: REQUEST MODELS ----------
class ChatIn(BaseModel):
    thread_id: str = Field(min_length=1)
    message: str = Field(min_length=1, max_length=2000)


# ---------- SECTION 2: PROTOCOL INTROSPECTION (what the client discovered from the server) ----------
@app.get("/protocol")
async def protocol():
    mcp = app.state.mcp
    return {
        "tools": [
            {"name": t.name, "description": t.description, "schema": t.inputSchema}
            for t in mcp.mcp_tools
        ],
        "resources": [{"uri": str(r.uri), "name": r.name, "description": r.description} for r in mcp.resources],
        "prompts": [{"name": p.name, "description": p.description} for p in mcp.prompts],
    }


# ---------- SECTION 3: CHAT (each turn is a real MCP round trip per tool call) ----------
@app.post("/chat")
async def chat(body: ChatIn):
    history = conversations.setdefault(body.thread_id, [])
    history.append({"role": "user", "content": body.message})
    try:
        result = await run_turn(app.state.mcp, app.state.groq, history)
    except Exception as exc:  # model/API errors should reach the UI, not crash it
        history.pop()
        raise HTTPException(status_code=502, detail=f"Agent error: {exc}") from exc

    history.append({"role": "assistant", "content": result["reply"]})
    return result


@app.post("/chat/{thread_id}/reset")
async def reset(thread_id: str):
    conversations.pop(thread_id, None)
    return {"ok": True}


# ---------- SECTION 4: RESOURCES + PROMPT (read straight from the MCP server, for the sidebar) ----------
@app.get("/notes")
async def notes():
    return await app.state.mcp.read_resource("notes://all")


@app.get("/tasks")
async def tasks():
    return await app.state.mcp.read_resource("tasks://all")


@app.post("/plan")
async def plan(body: ChatIn):
    """Run the server's daily_planner MCP prompt as the next user turn."""
    prompt_text = await app.state.mcp.get_prompt("daily_planner")
    history = conversations.setdefault(body.thread_id, [])
    history.append({"role": "user", "content": prompt_text})
    result = await run_turn(app.state.mcp, app.state.groq, history)
    history.append({"role": "assistant", "content": result["reply"]})
    return result


app.mount("/", StaticFiles(directory=str(BASE_DIR / "static"), html=True), name="static")
