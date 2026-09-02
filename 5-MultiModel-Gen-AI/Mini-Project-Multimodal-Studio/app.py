import base64
import os

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from groq import APIError
from pydantic import BaseModel

from multimodal import caption_image, synthesize_speech, transcribe_audio

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

app = FastAPI(
    title="Multimodal Studio",
    description="Mini project: image captioning/VQA, speech-to-text, text-to-speech, "
    "and image-to-speech fusion, all backed by Groq.",
)


# ---------- SECTION 0: SURFACE GROQ API ERRORS AS READABLE JSON ----------
@app.exception_handler(APIError)
async def groq_error_handler(request: Request, exc: APIError):
    return JSONResponse(status_code=502, content={"detail": str(exc)})


# ---------- SECTION 1: REQUEST MODELS ----------
class SpeakRequest(BaseModel):
    text: str


# ---------- SECTION 2: API ROUTES ----------
@app.post("/api/caption")
async def caption(image: UploadFile = File(...), question: str = Form("")):
    image_bytes = await image.read()
    result = caption_image(image_bytes, question or None)
    return {"result": result}


@app.post("/api/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    audio_bytes = await audio.read()
    transcript = transcribe_audio(audio_bytes, audio.filename or "audio.webm")
    return {"transcript": transcript}


@app.post("/api/speak")
def speak(req: SpeakRequest):
    audio_bytes = synthesize_speech(req.text)
    return Response(content=audio_bytes, media_type="audio/wav")


@app.post("/api/narrate")
async def narrate(image: UploadFile = File(...)):
    image_bytes = await image.read()
    caption_text = caption_image(image_bytes)
    audio_bytes = synthesize_speech(caption_text)
    return {"caption": caption_text, "audio_base64": base64.b64encode(audio_bytes).decode("utf-8")}


# ---------- SECTION 3: FRONTEND (served at "/") ----------
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
