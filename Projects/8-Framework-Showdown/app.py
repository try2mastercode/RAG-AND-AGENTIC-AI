"""FastAPI server exposing all three folder-8 frameworks behind one frontend.

AutoGen runs in-process. CrewAI and BeeAI each run in their own Python 3.11
venv subprocess, because their dependency chains conflict with each other
(and BeeAI's `pydantic-core` conflicts with the pydantic version the global
Python 3.14 interpreter would otherwise pick up) — see README.md.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from autogen_lab import run_autogen_chat

BASE_DIR = Path(__file__).parent

# Overridable via env var in case these venvs live elsewhere on another machine.
CREWAI_PYTHON = os.getenv("CREWAI_VENV_PYTHON", r"C:\v8\crewai\Scripts\python.exe")
BEEAI_PYTHON = os.getenv("BEEAI_VENV_PYTHON", r"C:\v8\beeai\Scripts\python.exe")

app = FastAPI(
    title="Multi-Agent Framework Showdown",
    description="The same 'researcher + writer' idea run through CrewAI and AutoGen, "
    "plus a BeeAI ReAct tool-calling agent — three different multi-agent orchestration styles.",
)


# ---------- SECTION 1: REQUEST MODELS ----------
class TopicIn(BaseModel):
    topic: str = Field(min_length=1, max_length=200)


class QuestionIn(BaseModel):
    question: str = Field(min_length=1, max_length=400)


# ---------- SECTION 2: VENV SUBPROCESS HELPER (CrewAI, BeeAI) ----------
def _run_in_venv(python_exe: str, script: str, payload: dict) -> dict:
    if not os.path.exists(python_exe):
        raise HTTPException(
            status_code=500,
            detail=f"Venv interpreter not found at {python_exe}. See README.md to set it up, "
            f"or point CREWAI_VENV_PYTHON/BEEAI_VENV_PYTHON at your own venv.",
        )

    result = subprocess.run(
        [python_exe, str(BASE_DIR / script), json.dumps(payload)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=BASE_DIR,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    if result.returncode != 0:
        raise HTTPException(status_code=502, detail=f"{script} failed:\n{result.stderr[-2000:]}")

    try:
        return json.loads(result.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError) as exc:
        raise HTTPException(status_code=502, detail=f"{script} produced no JSON:\n{result.stdout[-2000:]}") from exc


# ---------- SECTION 3: CREWAI (sequential crew, subprocess-isolated) ----------
@app.post("/api/crewai")
async def crewai_endpoint(body: TopicIn):
    return _run_in_venv(CREWAI_PYTHON, "crewai_runner.py", {"topic": body.topic})


# ---------- SECTION 4: AUTOGEN (round-robin team, in-process) ----------
@app.post("/api/autogen")
async def autogen_endpoint(body: TopicIn):
    try:
        return await run_autogen_chat(body.topic)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AutoGen run failed: {exc}") from exc


# ---------- SECTION 5: BEEAI (ReAct tool-calling agent, subprocess-isolated) ----------
@app.post("/api/beeai")
async def beeai_endpoint(body: QuestionIn):
    return _run_in_venv(BEEAI_PYTHON, "beeai_runner.py", {"question": body.question})


app.mount("/", StaticFiles(directory=str(BASE_DIR / "static"), html=True), name="static")
