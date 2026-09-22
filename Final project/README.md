# Restaurant Recommendation Capstone

End-to-end multimodal AI restaurant recommendation system — the IBM AI Engineering capstone. Unstructured restaurant text and food images are turned into a structured, retrievable knowledge base, served by a multi-agent recommendation workflow, exposed through a Gradio chatbot, and wired to the outside world through an MCP server/client/host stack.

See [`PROJECT_SPEC.md`](PROJECT_SPEC.md) for the phase tracker and build decisions, and [`NOTE/`](NOTE/) for the full course/lab source material.

## Setup

```bash
py -3.11 -m venv .venv
.venv/Scripts/pip install -e .
.venv/Scripts/pip install -r requirements.txt
cp .env.example .env   # then fill in GROQ_API_KEY
```

## Verify the environment

```bash
.venv/Scripts/pytest tests/unit/test_environment.py -v
```

## Layout

```text
data/          raw + generated datasets, per pipeline stage
src/           application code (data, schemas, llm, retrieval, agents, chatbot, mcp)
tests/         unit + integration tests
chroma_data/   persistent vector store (generated, gitignored)
screenshots/   the 12 required final-submission screenshots
NOTE/          original IBM lab material + execution spec (source of truth)
```

## Status

Phase 0 (scaffolding) — see [`PROJECT_SPEC.md`](PROJECT_SPEC.md) for the full phase tracker.
