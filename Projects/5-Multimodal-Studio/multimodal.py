import base64
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

VISION_MODEL = "qwen/qwen3.8-27b"
STT_MODEL = "whisper-large-v3"
TTS_MODEL = "canopylabs/orpheus-v1-english"
TTS_VOICE = "troy"


# ---------- SECTION 1: IMAGE -> TEXT (captioning / VQA) ----------
def caption_image(image_bytes: bytes, question: str | None = None) -> str:
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    prompt = question or "Describe this image in one or two sentences."
    response = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                ],
            }
        ],
        temperature=0.3,
        max_tokens=300,
    )
    return response.choices[0].message.content


# ---------- SECTION 2: AUDIO -> TEXT (speech-to-text) ----------
def transcribe_audio(audio_bytes: bytes, filename: str) -> str:
    response = client.audio.transcriptions.create(
        model=STT_MODEL,
        file=(filename, audio_bytes),
    )
    return response.text


# ---------- SECTION 3: TEXT -> AUDIO (text-to-speech) ----------
def synthesize_speech(text: str) -> bytes:
    response = client.audio.speech.create(
        model=TTS_MODEL,
        voice=TTS_VOICE,
        input=text,
        response_format="wav",
    )
    return response.read()
