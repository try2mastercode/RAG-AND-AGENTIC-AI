# Multimodal Studio

A small full-stack app proving out multimodal model calls
(`multimodal.py`) — image captioning/VQA, speech-to-text, text-to-speech, and
an image-to-speech fusion pipeline, running live against Groq behind a plain
HTML/CSS/JS frontend.

| Panel | Concept | Source pattern |
|---|---|---|
| Caption / VQA | image → text, optional question | `multimodal.py` (`caption_image`) |
| Transcribe | audio → text | `multimodal.py` (`transcribe_audio`) |
| Speak | text → audio | `multimodal.py` (`synthesize_speech`) |
| Narrate | image → caption → audio, chained | `app.py` (`narrate`) |

The "Narrate" panel is the fusion case — it chains the vision call and the
TTS call so an uploaded image comes back as spoken narration in one request.

**Stack:** FastAPI + Groq (vision-capable chat model for captioning/VQA,
`whisper-large-v3` for transcription, `canopylabs/orpheus-v1-english` for
speech synthesis).

## Run it

Needs a `.env` file in this folder with `GROQ_API_KEY` set (copy `.env.example` and fill it in).

```bash
pip install -r requirements.txt
python -m uvicorn app:app --reload
```

Then open http://localhost:8000 (or whichever port you pass with `--port`).
Interactive API docs (Swagger UI) are at `/docs`.
