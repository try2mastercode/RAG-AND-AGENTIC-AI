# Project Spec — Pointer + Phase Tracker

The canonical, detailed specification lives in [`NOTE/IBM_AI_Engineering_Project_Execution_Spec_v2.md`](NOTE/IBM_AI_Engineering_Project_Execution_Spec_v2.md). This file is a short index kept at the project root so an assistant or reviewer can orient quickly without opening the full 2500-line document, plus a running tracker of build progress.

## Source-of-truth order (unchanged from the spec)

1. `NOTE/Submission instruction.txt` — exact Q1-Q12 screenshot requirements
2. `NOTE/M1L1.txt` … `NOTE/M4L3.txt` — individual lab scope
3. `NOTE/info.md`, `NOTE/Transcript.txt` — framing/narrative
4. `NOTE/IBM_AI_Engineering_Project_Execution_Spec_v2.md` — consolidated execution view
5. `NOTE/Generative_AI_Course_AI_Knowledge_Base.md` — course-structure reference + labeled "AI-enriched" filler for the two labs (M2L2, M2L3) whose original text was never supplied

## Names that must never be casually renamed

`restaurant_articles`, `food_images` (Chroma collections) · `new_data_entry_process`, `node_analyze_styles`, `extract_preferences` (functions) · `get_restaurant_info`, `recommend_by_vibe`, `get_review` (MCP tools) · the 12 screenshot filenames in `screenshots/`.

## Build decisions locked in for this implementation

- LLM provider: **Groq only**, everywhere — including M4L2's sampling callback (lab text says "Anthropic API"; user chose to stay on one provider since it's not screenshot-visible). **Exception: M1L2 image captioning runs on a local BLIP model** (`transformers`, already installed) — Groq has no vision-capable model on this account (confirmed: `llama-3.2-*-vision-preview` decommissioned, `llama-4-scout`/`llama-4-maverick` inaccessible/404), so this is a forced exception, not a provider-consistency choice.
- Python: 3.11 venv (`.venv/`), not the machine's global 3.14 — the ML stack here (torch/sentence-transformers/CLIP/chromadb) is heavier than other folders in this repo that hit 3.14 build issues.
- M1L3 CLI backs up the JSON file before any destructive/modifying write (list → backup → apply → save) — a `Generative_AI_Course_AI_Knowledge_Base.md` suggestion, not an IBM requirement, but cheap and safe to include.
- M2L2/M2L3 (original lab text missing): implemented against the *stated final requirements* (similarity + metadata filtering + top-K; weighted late fusion across configs + rerank), using reasonable default metadata fields and a standard fusion sequence — not fabricated as if they were literal IBM-specified names.
- Dataset: the actual IBM lab notebook's source dataset (raw restaurant descriptions, food images, user visit history, social posts, California Culinary Map text) was not supplied to this repo. It will be authored as a coherent synthetic dataset in Phase 1, sized and shaped to match what each lab describes.

## Phase tracker

| Phase | Scope | Status |
|---|---|---|
| 0 | Scaffolding: repo layout, venv, deps, config, base tests | done |
| 1 | Data layer — M1L1, M1L2, M1L3 | done |
| 2 | Retrieval layer — M2L1, M2L2, M2L3 | done |
| 3 | Agent layer — M3L1, M3L2, M3L3 | done |
| 4 | MCP layer — M4L1, M4L2, M4L3 | not started |
| 5 | Screenshot capture + submission audit | not started |

Each phase gets a self-review pass (acceptance checklist from the spec, plus tests) before moving to the next, and is only marked complete after that review. See [`WHATTODO.md`](WHATTODO.md) for the detailed, per-phase running status.
