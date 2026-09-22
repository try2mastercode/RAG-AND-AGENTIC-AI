# What To Do — Live Status Tracker

Running record of what's done and what's next, organized by the 6 build phases. Updated after every phase review. See [`PROJECT_SPEC.md`](PROJECT_SPEC.md) for the full spec pointer and locked-in build decisions.

---

## Phase 0 — Scaffolding — ✅ DONE (2026-09-22)

**What was built:**

- Directory layout: `data/{raw,structured,recipes,images,reviews}`, `src/{data,schemas,llm,retrieval,agents,chatbot,mcp}`, `tests/{unit,integration,fixtures}`, `chroma_data/`, `screenshots/`.
- `pyproject.toml` — src-layout package config + pytest config (`pythonpath = ["src"]`).
- `requirements.txt` — full dependency list by phase; `requirements.lock.txt` — exact frozen versions actually installed (149 packages).
- `.env.example`, `src/config.py` — central config (paths, collection names, embedding dims/models, Groq key loader).
- `.venv/` — **Python 3.11** virtual environment (not the machine's default 3.14).
- `tests/unit/test_environment.py` — 5 tests, all passing.
- Root `.gitignore` updated to also ignore `chroma_data/*` (keeping `.gitkeep`).
- `README.md`, `PROJECT_SPEC.md` written.

**Verified:**

- [x] All core + heavy deps installed and import cleanly: `torch 2.14.0+cpu`, `chromadb 1.5.9`, `sentence-transformers 6.1.0`, `clip` (confirms `ViT-B/32` available), `langchain 1.4.2`, `langgraph`, `langchain-groq`, `gradio 6.28.0`, `mcp`.
- [x] `GROQ_API_KEY` loads from `.env` and authenticates against the live Groq API.
- [x] Collection names (`restaurant_articles`, `food_images`) and embedding dims (384/512) match the IBM spec exactly.
- [x] `pytest tests/` → 5/5 passed.

**Resolved (2026-09-22):** Groq has no vision model on this account — confirmed twice: `models.list()` shows 11 models, none vision-capable, and direct calls to `llama-3.2-11b/90b-vision-preview` return "decommissioned," while `llama-4-scout`/`llama-4-maverick` 404 as inaccessible. **Decision:** M1L2 image captioning runs on a **local open-source BLIP model** (`transformers`, already installed as a `sentence-transformers` dependency — no new package, no new API key). Every other lab stays on Groq per the standing rule.

---

## Phase 1 — Data layer (M1L1, M1L2, M1L3) — ⬜ NOT STARTED

**Will build:**

- Self-authored synthetic raw dataset: restaurant descriptions, recipe/food images + metadata, user visit history, social posts, California Culinary Map text (the original IBM lab's dataset files weren't supplied to this repo — see [`PROJECT_SPEC.md`](PROJECT_SPEC.md)).
- M1L1: LLM structured-extraction pipeline (prompt → JSON → schema validate → repair loop → persist), processed in a loop over all restaurants.
- M1L2: vision-LLM captioning pipeline for food images, merged back into recipe JSON (blocked on the vision-model decision above).
- M1L3: command-line CRUD tool with `new_data_entry_process` (reuses the M1L1 pipeline), edit/delete with confirmation, JSON backup before writes, unit tests.

**Needed before starting:** resolve the vision-model provider question.

---

## Phase 2 — Retrieval layer (M2L1, M2L2, M2L3) — ⬜ NOT STARTED

- M2L1: Chroma collections `restaurant_articles` (MiniLM/384d) + `food_images` (CLIP ViT-B/32/512d), L2-normalized, persisted.
- M2L2: similarity retrieval + metadata filtering, top-K, completion message.
- M2L3: weighted late fusion across text/image scores, multiple weight configs, reranking, completion message.

---

## Phase 3 — Agent layer (M3L1, M3L2, M3L3) — ⬜ NOT STARTED

- M3L1: 6 agents (User Profile Generator, RAG Retriever, Food Trend Analyst, Food Style Expert, Nutrition Expert, Recommendation Expert) with role/goal/backstory.
- M3L2: LangGraph hybrid workflow (sequential → sequential → parallel → sequential), `node_analyze_styles`, 4 test personas.
- M3L3: Gradio chatbot, intent classification, `extract_preferences`, DB add/update/delete features.

---

## Phase 4 — MCP layer (M4L1, M4L2, M4L3) — ⬜ NOT STARTED

- M4L1: FastMCP server — 1 resource (California Culinary Map text) + 3 tools (`get_restaurant_info`, `recommend_by_vibe`, `get_review`).
- M4L2: MCP client over stdio — `list_tools()`/`list_resources()`, `list_roots` + `handle_sampling` callbacks (Groq-backed per the locked-in decision), calls all 3 tools.
- M4L3: full ReAct-loop host app in Gradio Blocks — runtime tool discovery, quick-start buttons, `Thinking...` placeholder, `Built with Gradio` footer.

---

## Phase 5 — Screenshot capture + submission audit — ⬜ NOT STARTED

- Run every phase end-to-end, capture all 12 exact-named screenshots into `screenshots/`, cross-check each against `NOTE/Submission instruction.txt`.

---

## Standing rules (apply to every phase)

- Groq only, everywhere, including MCP sampling.
- Never rename IBM-mandated names/collections/functions/tools/screenshot filenames.
- Self-review + tests after each phase, reported back before moving on.
- Don't fabricate missing M2L2/M2L3 implementation detail as if it were literal IBM wording — implement the stated end requirements with reasonable defaults instead.
