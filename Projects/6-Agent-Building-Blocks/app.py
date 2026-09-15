import uuid
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import lcel_lab
import manual_calling
import sql_agent_lab
import support_agent
import tools_lab
import viz_agent_lab

app = FastAPI(
    title="Agent Building Blocks",
    description="Tool creation, manual tool calling, LCEL runnables, an "
    "orchestrating agent with memory, a SQL agent, and a data-visualization "
    "agent - the fundamentals folder's concepts, backed by Groq.",
)


# ---------- SECTION 1: REQUEST MODELS ----------
class ToolInvokeRequest(BaseModel):
    name: str
    input: dict


class QuestionRequest(BaseModel):
    question: str


class TextRequest(BaseModel):
    text: str


class ChatRequest(BaseModel):
    session_id: str
    message: str


# ---------- SECTION 2: TOOL CREATION & INSPECTION ----------
@app.get("/api/tools")
def api_list_tools():
    return {"tools": tools_lab.list_tool_schemas()}


@app.post("/api/tools/invoke")
def api_invoke_tool(req: ToolInvokeRequest):
    return tools_lab.invoke_tool(req.name, req.input)


# ---------- SECTION 3: MANUAL TOOL CALLING (bind_tools loop) ----------
@app.post("/api/manual-calling")
def api_manual_calling(req: QuestionRequest):
    return manual_calling.run_tool_calling(req.question)


# ---------- SECTION 4: LCEL RUNNABLES ----------
@app.post("/api/lcel/parallel")
def api_lcel_parallel(req: TextRequest):
    return lcel_lab.run_parallel(req.text)


@app.post("/api/lcel/passthrough")
def api_lcel_passthrough(req: QuestionRequest):
    return lcel_lab.run_passthrough(req.question)


@app.post("/api/lcel/lambda")
def api_lcel_lambda(req: TextRequest):
    return lcel_lab.run_lambda(req.text)


@app.post("/api/lcel/branch")
def api_lcel_branch(req: TextRequest):
    return lcel_lab.run_branch(req.text)


# ---------- SECTION 5: ORCHESTRATING AGENT + MEMORY ----------
@app.get("/api/new-session")
def new_session():
    return {"session_id": str(uuid.uuid4())}


@app.post("/api/support/traced")
def api_support_traced(req: QuestionRequest):
    return support_agent.run_traced(req.question)


@app.post("/api/support/chat")
def api_support_chat(req: ChatRequest):
    return {"reply": support_agent.chat(req.session_id, req.message)}


# ---------- SECTION 6: SQL AGENT ----------
@app.post("/api/sql-agent")
def api_sql_agent(req: QuestionRequest):
    return sql_agent_lab.ask(req.question)


# ---------- SECTION 7: DATA-VISUALIZATION AGENT ----------
@app.post("/api/viz-agent")
def api_viz_agent(req: TextRequest):
    return viz_agent_lab.ask(req.text)


# ---------- SECTION 8: FRONTEND (served at "/") ----------
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
