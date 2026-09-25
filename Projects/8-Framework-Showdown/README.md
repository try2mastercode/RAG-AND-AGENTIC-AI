# Framework Showdown

The same two-agent idea — a **researcher** finds facts, a **writer** turns them into a pitch —
built three different ways, plus a fourth agent style that doesn't fit that mold at all:

| File | Framework | Orchestration style |
|---|---|---|
| `crewai_runner.py` | CrewAI | `Process.sequential` crew: two `Task`s, the second declares `context=[research_task]` |
| `autogen_lab.py` | AutoGen | `RoundRobinGroupChat`: two agents take turns seeing the full conversation, until `TERMINATE` |
| `beeai_runner.py` | BeeAI | `ReActAgent`: one agent, one tool, decides for itself whether the question needs it |

(LangGraph, the fourth framework in this course folder, already has its own project —
see `Projects/7-Task-Manager-Agent`.)

## Why three Python interpreters

CrewAI pins `pydantic<2.13`; BeeAI needs `pydantic-core>=2.46.5` (which pulls in
`pydantic>=2.13`) — they can't share a venv. Neither installs cleanly on this machine's
default/global Python 3.14 either (CrewAI's `tiktoken`/`regex` chain wants a Rust compiler
to build from source there; BeeAI *imports* fine on 3.14 but hits a
`TypeAdapter ... is not fully defined` pydantic error the moment it actually builds a
`ChatModel`). AutoGen has none of these issues and runs fine on 3.14.

So `app.py` (FastAPI, on the default interpreter) calls AutoGen directly in-process, and
shells out to two separate Python 3.11 venvs as subprocesses for CrewAI and BeeAI:

```
app.py (Python 3.14, FastAPI)
 ├─ autogen_lab.py        -> in-process, same interpreter
 ├─ subprocess: C:\v8\crewai\Scripts\python.exe crewai_runner.py '{"topic": "..."}'
 └─ subprocess: C:\v8\beeai\Scripts\python.exe  beeai_runner.py  '{"question": "..."}'
```

Each runner script prints exactly one line of JSON to stdout and nothing else (both are
called with `verbose=False`); `app.py` parses that line as the response. If your venvs live
somewhere else, point `CREWAI_VENV_PYTHON` / `BEEAI_VENV_PYTHON` env vars at their
`python.exe` instead of editing the code.

## Setting up the two venvs

```bash
py -3.11 -m venv C:\v8\crewai
C:\v8\crewai\Scripts\pip install crewai litellm python-dotenv

py -3.11 -m venv C:\v8\beeai
C:\v8\beeai\Scripts\pip install beeai-framework python-dotenv
```

Use a short venv path (not a deeply nested temp directory) — `pip install crewai[litellm]`
hits a Windows `OSError` on very long asset paths inside litellm's guardrails folder unless
long-path support is enabled.

## Run it

Needs the two venvs above, plus a `.env` file in this folder with `GROQ_API_KEY`
set (copy `.env.example` and fill it in — both subprocesses inherit it from
`app.py`'s environment):

```bash
pip install -r requirements.txt
python -m uvicorn app:app --reload --port 8008
```

Then open http://localhost:8008. Interactive API docs (Swagger UI) are at `/docs`.

## Test it

```bash
pip install -r requirements.txt
python -m pytest test_showdown.py -v
```

The tests check request validation and that the venv wiring is in place — they don't call
Groq, so they need no API key. Trying the three agents live in the browser is the only way
to see the actual model output.
