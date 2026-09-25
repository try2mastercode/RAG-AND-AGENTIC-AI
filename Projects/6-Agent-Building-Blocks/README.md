# Agent Building Blocks

A small full-stack app proving out the agent fundamentals from this folder
(`tool-fundamentals-and-agents.py`, `tool-creation-methods-and-lcel.py`,
`tool-calling-and-chaining.py`, `lcel-and-manual-tool-calling.py`,
`step-by-step-building-an-agent.py`, `sql-agent.py`,
`natural-language-data-visualization-agent.py`), running live behind a plain
HTML/CSS/JS frontend.

| Panel | Concept | Source pattern |
|---|---|---|
| 1. Tool creation | `@tool`, `@tool` + `args_schema`, `StructuredTool.from_function`, subclassing `BaseTool`, legacy `Tool` | `tools_lab.py` |
| 2. Manual tool calling | `bind_tools()` + a hand-written loop (single / parallel / chained calls) | `manual_calling.py` |
| 3. LCEL runnables | `RunnableParallel`, `RunnablePassthrough`, `RunnableLambda`, `RunnableBranch` | `lcel_lab.py` |
| 4. Orchestrating agent | `create_agent`, streamed step-by-step | `support_agent.py` (`run_traced`) |
| 5. Agent memory | `create_agent` + `InMemorySaver` checkpointer, keyed by `thread_id` | `support_agent.py` (`chat`) |
| 6. SQL agent | `create_sql_agent` + `SQLDatabaseToolkit` over a SQLite DB | `sql_agent_lab.py` |
| 7. Data-visualization agent | Custom agent with `describe_dataset` / `create_chart` tools | `viz_agent_lab.py` |

Panels 2, 4 and 7 show the full step-by-step trace (each tool call and its result), not just the
final answer — the point being that an "agent" is just a loop around tool calls, visible end to
end here instead of hidden behind one black-box response.

**Stack:** FastAPI + LangChain (`create_agent`, `bind_tools`, LCEL runnables) + LangGraph
(`InMemorySaver`) + `langchain-community` (`SQLDatabaseToolkit`, `create_sql_agent`) + pandas/
matplotlib for the chart agent + Groq for generation (`qwen/qwen3.8-27b`, tool-calling-capable).

## Run it

Needs a `.env` file in this folder with `GROQ_API_KEY` set (copy `.env.example` and fill it in).

```bash
pip install -r requirements.txt
python -m uvicorn app:app --reload
```

Then open http://localhost:8000 (or whichever port you pass with `--port`).
Interactive API docs (Swagger UI) are at `/docs`.

The SQL agent's `company.db` and the chart agent's `output_chart.png` are created on first run
inside this folder and are gitignored (regenerable, not checked in).
