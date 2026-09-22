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

## Phase 1 — Data layer (M1L1, M1L2, M1L3) — ✅ DONE (2026-09-22)

**What was built:**

- `src/data/dataset_gen.py` — synthetic dataset generator: 12 raw restaurant paragraphs (`data/raw/california_culinary_map.txt`), 10 recipes with programmatically-generated plate images (`data/recipes/recipes.json`, `data/images/*.png`), 4 synthetic users with visit history + social posts (`data/reviews/users.json`) whose personas already match M3L2's 4 test personas for later reuse.
- `src/schemas/{restaurant,recipe,user}.py` — pydantic schemas with real validators (price_range enum, rating 0-5, non-empty lists).
- `src/llm/groq_client.py` + `src/llm/prompts.py` — Groq wrapper (`openai/gpt-oss-120b`) and one-shot extraction + repair prompt templates.
- `src/data/json_utils.py` — strips markdown fences / prose around LLM JSON output.
- `src/data/structuring.py` (**M1L1**) — `new_data_entry_process(raw_text, id)`: LLM call -> parse -> validate -> repair loop (up to 3 attempts) -> validate again. `structure_all_restaurants()` loops over all raw blocks calling it, saves only validated records. **Ran for real: 12/12 restaurants structured, 0 failures** (Groq hit 429 twice, SDK auto-retried).
- `src/data/captioning.py` (**M1L2**) — local BLIP (`Salesforce/blip-image-captioning-base`) captioning. `caption_sample()` tests a few images first, `caption_all_recipes()` loops over all recipes. Review context from `users.json` is appended as a separate sentence after the visual caption, never fed into the model as a generation prefix (see bug fix below). **Ran for real: 10/10 recipes captioned.**
- `src/data/cli.py` (**M1L3**) — menu-driven CLI (list/view/add/edit/delete). "Add" calls the *same* `new_data_entry_process` from `structuring.py` (no duplicated extraction logic, per spec 9.3). Edit/delete require `y/N` confirmation; every write backs up the previous file to `data/structured/backups/` first.
- Tests: `test_json_utils`, `test_schemas`, `test_structuring`, `test_captioning`, `test_cli` — 35 new tests (40 total in the repo), all mocking the LLM/vision calls for speed/determinism, plus real end-to-end runs of all three labs against live Groq/BLIP.

**Bug caught and fixed during build:** first captioning pass fed the review-comment text into BLIP as a conditional-generation prefix, and the model just echoed it back verbatim instead of describing the image (e.g. captioned a plate as "a dish at green papaya, reviewed as: huge bowl of pho..."). Fixed by always captioning unconditionally first, then appending context as a separate sentence (`build_caption()`) - re-ran the full batch afterward with correct, visually-grounded captions.

**Verified:** `pytest tests/` -> 40/40 passed. CLI smoke-tested against real data (list/view). Screenshots (Q1-Q3) are your manual step from here - the loops/functions all run and print the required content.

---

## Phase 2 — Retrieval layer (M2L1, M2L2, M2L3) — DONE (2026-09-22)

**What was built:**

- `src/retrieval/chroma_client.py` - `PersistentClient` at `chroma_data/`, `reset_collection()` deletes+recreates by name before rebuild (no duplicate vectors on re-run), collections created with `hnsw:space: cosine` so distances are directly interpretable as `1 - cosine_similarity`.
- `src/retrieval/embeddings.py` - `embed_text()` (MiniLM, `normalize_embeddings=True`), `embed_image()` (CLIP ViT-B/32, manual L2 normalize), `embed_text_for_image_query()` (CLIP text encoder, same joint space as the image embeddings - this is what makes M2L3's cross-modal fusion possible).
- `src/retrieval/index_builder.py` (**M2L1**) - builds `restaurant_articles` (page_content = name+cuisine+location+summary, metadata = cuisine/location/price_range/rating/vibe/signature_dishes) and `food_images` (page_content = recipe name per spec, metadata = image_path/cuisine/source/caption). **Ran for real: 12 restaurants (384d), 10 images (512d), exact completion message `Multimodal Vector Index Construction COMPLETE` printed.**
- `src/retrieval/similarity.py` (**M2L2**) - `retrieve_restaurants(query, k, filters)` using Chroma's `where` clause. Demo query filtered to `price_range in [$$$, $$$$]`, correctly returned only the 4 matching restaurants ranked by similarity. **Ran for real, exact completion message `Similarity Retrieval with Metadata Filtering COMPLETE` printed.**
- `src/retrieval/fusion.py` (**M2L3**) - since restaurants and recipes are different entity types, fusion links them via the recipe's `source` field (restaurant name): text score from `restaurant_articles`, image score from `food_images` aggregated per source restaurant (best matching dish wins), both min-max normalized then weighted-summed. Tested 3 weight configs (text-only / 50-50 / image-only) - **ranking genuinely shifted (#1 moved from Spice Route to Olive & Thyme as image weight increased), proving the fusion isn't a no-op.** Completion message `Multimodal Similarity Fusion and Retrieval Ranking COMPLETE` (Q6 doesn't mandate exact wording, chosen for consistency with M2L1/M2L2).
- Tests: `test_embeddings`, `test_index_builder`, `test_similarity`, `test_fusion` - 13 new tests (53 total in the repo), all mocking Chroma/embedding calls, plus real end-to-end runs of all three labs against the live index.

**Bug caught and fixed during build (repo-wide, not just Phase 2):** root `.gitignore`'s `chroma_data/*` pattern was silently root-anchored (git treats any pattern containing a mid-string slash as relative to the `.gitignore`'s own directory, not matched at any depth), so it never actually matched `Final project/chroma_data/*` - only the unrelated `*.sqlite3` rule happened to catch the database file, leaving the vector-store's binary UUID subdirectories untracked. Fixed to `**/chroma_data/*` + `!**/chroma_data/.gitkeep`.

**Verified:** `pytest tests/` -> 53/53 passed. All three labs run for real against the live persisted Chroma index. Screenshots (Q4-Q6) are your manual step from here.

---

## Phase 3 — Agent layer (M3L1, M3L2, M3L3) — DONE (2026-09-22)

**What was built:**

- `src/agents/personas.py` (**M3L1**) - 6 `AgentPersona`s (role/goal/backstory) + `AgentTask`s (description/expected_output/context/dependencies) for User Profile Generator, RAG Retriever, Food Trend Analyst, Food Style Expert, Nutrition Expert, Recommendation Expert. `__main__` prints all 6 - Food Style Expert's block is what Q7 screenshots.
- `src/agents/state.py` - `RecommendationState` TypedDict; `errors` uses `Annotated[list[str], operator.add]` (see bug below).
- `src/agents/nodes.py` (**M3L2**) - one node per agent, each building its own `user_message` from `state` and calling `complete_chat()`. `node_analyze_styles` is the Q8 screenshot target. Every LLM call is wrapped in try/except - failures degrade to a placeholder string + an error record rather than crashing the graph (spec 8.3/8.5).
- `src/agents/graph.py` (**M3L2**) - LangGraph hybrid workflow: `generate_profile` -> `retrieve_candidates` -> `[analyze_trends, analyze_styles, analyze_nutrition]` (parallel fan-out/fan-in) -> `synthesize`. `run_for_all_test_personas()` runs all 4 personas from `data/reviews/users.json` (already shaped to match M3L2's 4 required personas back in Phase 1).
- `src/retrieval/similarity.py` extended with `retrieve_recipes()` (CLIP text-encoder query against `food_images`) so the RAG Retriever agent can pull both restaurants and recipes - ~20 candidates total per M3L2's "top 20" spec.
- `src/chatbot/preferences.py` (**M3L3**) - `classify_intent()` (4 categories) and `extract_preferences()` (dietary_restrictions/flavor_preferences/dining_occasion/price_range/favorite_cuisines). `__main__` is the Q9 screenshot target.
- `src/chatbot/app.py` (**M3L3**) - Gradio Blocks app: Chat tab (chatbot, textbox, 3 sample-prompt buttons, Send/Clear) wired to intent-classify -> extract-preferences -> LangGraph workflow -> reply; Manage Restaurants tab (add/update-rating/delete, reusing M1L3's `data.cli` pure functions). Verified live in the browser end-to-end, both tabs.
- Tests: `test_personas`, `test_nodes`, `test_graph`, `test_preferences`, `test_chatbot_app`, plus additions to `test_similarity`/`test_embeddings` - 33 new tests (86 total in the repo).

**Known limitation, not a bug:** follow-up messages don't carry prior-turn context into the workflow yet - each `respond()` call starts a fresh state with only the latest message. The spec lists multi-turn refinement as a nice-to-have ("Handle follow-ups"), not a core M3L3 requirement, so this is flagged rather than fixed now.

**Four real bugs caught and fixed while testing live (not just in unit tests):**

1. **LangGraph parallel fan-out conflict.** The three parallel analysis nodes were each returning `{**state, ...}` (the full state), so when they ran concurrently every shared key got written more than once in the same step -> `InvalidUpdateError`. Fixed: nodes now return only the keys they change, and `errors` got an `operator.add` reducer since multiple parallel branches can each append to it in the same step.
2. **CLIP's 77-token hard limit.** The RAG Retriever passed a full LLM-generated user profile (1000+ chars) straight into `embed_text_for_image_query()`, which crashed with `RuntimeError: Input ... is too long for context length 77`. Fixed with `clip.tokenize(texts, truncate=True)`.
3. **Reasoning-model token starvation.** `classify_intent` used `max_tokens=10`; `gpt-oss-120b` spends tokens on hidden chain-of-thought before the visible answer, so the 10-token budget was consumed entirely by reasoning and returned `''` every time, silently defaulting every message to "clarification." Confirmed by direct test (`max_tokens=10` -> `''`, `max_tokens=200` -> `'restaurant_request'`). Fixed by raising to 200.
4. **Gradio LaTeX rendering ate price symbols.** Recommendations naturally contain `$`/`$$`/`$$$` price notation, and `gr.Chatbot`'s default LaTeX delimiters treat `$...$` as math mode - live-tested output showed a whole table cell mangled into spaceless math-italic Unicode after a stray `$`. Fixed with `gr.Chatbot(latex_delimiters=[])`.

**Verified:** `pytest tests/` -> 86/86 passed. All three labs run for real against live Groq (M3L1 print, M3L2 all 4 personas including graceful degradation under real 429s, M3L3 `extract_preferences`). Chatbot UI verified live in the browser: sample prompts, Send, both restaurant and recipe requests produced real personalized cross-referenced recommendations, Manage Restaurants tab's update-rating tested live (then reverted, since it touched the real dataset).

---

## Phase 4 — MCP layer (M4L1, M4L2, M4L3) — DONE (2026-09-22)

**What was built:**

- `src/mcp_app/server.py` (**M4L1**) - FastMCP server named "California Restaurant Server": 1 resource (`resource://california-culinary-map`, the raw Phase 1 text) + 3 tools - `get_restaurant_info` (partial-name search), `recommend_by_vibe` (two-pass: structured `vibe` tags first, then a raw-text fallback scan), `get_review` (pulls matching visits out of `users.json`). All return JSON strings.
- `src/mcp_app/client.py` (**M4L2**) - stdio client (`StdioServerParameters` + `ClientSession`), `list_roots_callback` (scoped to `config.PROJECT_ROOT`, not the whole filesystem), `handle_sampling` (forwards server-delegated prompts to Groq via `AsyncGroq` - reused the exact proven pattern from `9-Building AI Agents with MCP/11_sampling_client_with_groq_handler.py`), `verify_server_capabilities()` + shared `call_tool()` helper, demo calls to all 3 tools.
- `src/mcp_app/host_app.py` (**M4L3**) - full ReAct-loop Gradio host: discovers tools at runtime via `list_tools()`, converts MCP's `.inputSchema` straight into Groq's function-calling format (direct pass-through, no bridging needed), loops LLM -> tool-call? -> `call_tool()` -> feed result back -> repeat (capped at 5 iterations) until a plain-text answer. Gradio Blocks UI: chat window, text input, 3 quick-start buttons, Send/Clear, async-generator `respond()` that yields a `Thinking...` placeholder immediately then replaces it with the real answer.
- Tests: `test_mcp_server.py` (8, mocked data files), `test_host_app.py` (4, mocked session/Groq - covers no-tool-call / one-tool-call / max-iterations-exhausted paths), `tests/integration/test_mcp_server_client.py` (3, spawns the **real** server subprocess and drives it through the real client - no mocks) - 15 new tests (101 total in the repo).

**Real bug found and fixed - a genuine environment/versioning trap:** `src/mcp/` (the natural directory name) **shadowed the real `mcp` SDK** we needed to import from, since the editable install puts `src/` directly on `sys.path` and Python resolved our own empty local package before/instead of site-packages in this import chain - `from mcp.server import server` (our own file) actually tried to resolve against the *real* SDK's `mcp.server` subpackage and failed. Renamed the local package to `src/mcp_app/` to remove the ambiguity entirely, and updated `pyproject.toml`'s auto-discovery accordingly (no separate change needed, it re-discovers by directory name).

**Second real bug, more serious - a package version trap:** the unpinned `mcp` install from Phase 0's `requirements.txt` grabbed the newest release, **`mcp==2.2.0`, which renamed `FastMCP` to `MCPServer` and changed other APIs** - `from mcp.server.fastmcp import FastMCP` raised `ModuleNotFoundError` with a migration-guide pointer. Checked this repo's other MCP code (`9-Building AI Agents with MCP/`, proven working) and found it targets `mcp==1.30.0`. Since the IBM lab text explicitly says "FastMCP" by name, pinned `mcp<2` in `requirements.txt` rather than adapt to the differently-named v2 surface - matches spec section 15.3 ("never modernize away a required assignment feature") and reuses already-proven patterns instead of guessing at a new API.

**Also confirmed empirically before building M4L3:** `openai/gpt-oss-120b` (this project's Groq text model) *does* support Groq tool-calling correctly (folder 9 found `allam-2-7b` does **not** - worth checking per-model, not assuming).

**Verified:** `pytest tests/` -> 101/101 passed. All three labs run for real: M4L1+M4L2's real client run printed genuine tool discovery, resource discovery, configured roots (`file:///D:/CODE/RAG%20and%20Agentic%20AI/Final%20project`), and valid JSON from all 3 tools. M4L3 verified live in the browser end-to-end for two different quick-start prompts - server logs confirmed exactly one real `CallToolRequest` per turn (not the LLM hallucinating), `Thinking...` placeholder captured, both responses correctly grounded in real tool data matching the M4L2 client's direct output.

---

## Final pre-submission audit (2026-09-22) — PASSED, ready for screenshots

Followed spec section 24's procedure: fresh full test suite, then re-ran all 12 labs for real, in dependency order, from the actual committed state (not just trusting earlier phase runs).

- **Environment:** Python 3.11.9, all deps import clean, `mcp==1.30.0` (still pinned correctly), `GROQ_API_KEY` set.
- **Tests:** `pytest tests/` -> **101/101 passed**, twice (before and after the re-runs).
- **M1L1-M1L3:** re-ran for real - 12/12 restaurants structured (0 failures), 10/10 recipes captioned, CLI list confirmed against the fresh data.
- **M2L1-M2L3:** vector index rebuilt from the fresh M1 output (12 restaurants/384d, 10 images/512d), similarity+filter demo and fusion demo both re-ran with correct exact completion messages and genuinely shifting rankings.
- **M3L1-M3L3:** personas re-printed, full LangGraph workflow re-ran for all 4 personas against live Groq (graceful degradation under real rate limits confirmed again, same as Phase 3 - not a regression), `extract_preferences` re-tested live.
- **M4L1-M4L3:** MCP client re-run against the real server (tool/resource discovery, configured roots, all 3 tools), and the M4L3 ReAct loop re-checked directly (real tool call, correctly grounded answer).
- **Data refresh:** `data/structured/restaurants.json` changed slightly (ordinary LLM non-determinism - reordered lists, reworded summaries - not a functional change) and was committed as the current audit-verified snapshot. `recipes.json` was unchanged (BLIP captioning is deterministic).

**No regressions found.** Nothing needed fixing this pass - the build is stable and ready for you to run each script/app yourself and capture the 12 required screenshots per `NOTE/Submission instruction.txt`.

---

## Phase 5 — Screenshot capture + submission audit — ⬜ NOT STARTED

- Run every phase end-to-end, capture all 12 exact-named screenshots into `screenshots/`, cross-check each against `NOTE/Submission instruction.txt`.

---

## Standing rules (apply to every phase)

- Groq only, everywhere, including MCP sampling.
- Never rename IBM-mandated names/collections/functions/tools/screenshot filenames.
- Self-review + tests after each phase, reported back before moving on.
- Don't fabricate missing M2L2/M2L3 implementation detail as if it were literal IBM wording — implement the stated end requirements with reasonable defaults instead.
