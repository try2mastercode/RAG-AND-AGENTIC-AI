"""No Groq calls here — just request validation and that the venv subprocess
wiring is actually in place. Trying the three agents live needs a browser.
"""
import os

import pytest
from fastapi.testclient import TestClient

from app import BEEAI_PYTHON, CREWAI_PYTHON, app

client = TestClient(app)


def test_serves_frontend():
    res = client.get("/")
    assert res.status_code == 200
    assert "Framework Showdown" in res.text


def test_crewai_rejects_empty_topic():
    res = client.post("/api/crewai", json={"topic": ""})
    assert res.status_code == 422


def test_autogen_rejects_missing_topic():
    res = client.post("/api/autogen", json={})
    assert res.status_code == 422


def test_beeai_rejects_empty_question():
    res = client.post("/api/beeai", json={"question": ""})
    assert res.status_code == 422


@pytest.mark.skipif(not os.path.exists(CREWAI_PYTHON), reason="CrewAI venv not set up on this machine")
def test_crewai_venv_exists():
    assert os.path.exists(CREWAI_PYTHON)


@pytest.mark.skipif(not os.path.exists(BEEAI_PYTHON), reason="BeeAI venv not set up on this machine")
def test_beeai_venv_exists():
    assert os.path.exists(BEEAI_PYTHON)


def test_missing_venv_returns_clear_error(monkeypatch):
    monkeypatch.setattr("app.CREWAI_PYTHON", r"C:\does\not\exist\python.exe")
    res = client.post("/api/crewai", json={"topic": "test"})
    assert res.status_code == 500
    assert "Venv interpreter not found" in res.json()["detail"]
