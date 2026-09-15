import uuid
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from chains import run_branch, run_chat, run_parallel, run_sequential

app = FastAPI(
    title="Cuisine Chain Explorer",
    description="LangChain sequential chains, parallel runnables, branching, "
    "and conversational memory, backed by Groq.",
)


# ---------- SECTION 1: REQUEST MODELS ----------
class LocationRequest(BaseModel):
    location: str


class DishRequest(BaseModel):
    dish: str


class BranchRequest(BaseModel):
    topic: str
    detailed: bool = False


class ChatRequest(BaseModel):
    session_id: str
    message: str


# ---------- SECTION 2: API ROUTES ----------
@app.get("/api/new-session")
def new_session():
    return {"session_id": str(uuid.uuid4())}


@app.post("/api/sequential")
def sequential(req: LocationRequest):
    return run_sequential(req.location)


@app.post("/api/parallel")
def parallel(req: DishRequest):
    return run_parallel(req.dish)


@app.post("/api/branch")
def branch(req: BranchRequest):
    return {"explanation": run_branch(req.topic, req.detailed)}


@app.post("/api/chat")
def chat(req: ChatRequest):
    return {"reply": run_chat(req.session_id, req.message)}


# ---------- SECTION 3: FRONTEND (served at "/") ----------
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
