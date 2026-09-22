from pathlib import Path

from dotenv import load_dotenv
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Verified against the live Groq model list at the start of Phase 1, not guessed from training data.
GROQ_TEXT_MODEL = os.getenv("GROQ_TEXT_MODEL", "")
GROQ_VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "")

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
STRUCTURED_DIR = DATA_DIR / "structured"
RECIPES_DIR = DATA_DIR / "recipes"
IMAGES_DIR = DATA_DIR / "images"
REVIEWS_DIR = DATA_DIR / "reviews"

CHROMA_DIR = PROJECT_ROOT / "chroma_data"
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"

TEXT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TEXT_EMBEDDING_DIM = 384
IMAGE_EMBEDDING_MODEL = "ViT-B/32"
IMAGE_EMBEDDING_DIM = 512

RESTAURANT_ARTICLES_COLLECTION = "restaurant_articles"
FOOD_IMAGES_COLLECTION = "food_images"


def require_groq_key() -> str:
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and fill it in."
        )
    return GROQ_API_KEY
