import clip
import numpy as np
import torch
from PIL import Image
from sentence_transformers import SentenceTransformer

import config

_text_model = None
_clip_model = None
_clip_preprocess = None
_device = "cpu"


def get_text_model() -> SentenceTransformer:
    global _text_model
    if _text_model is None:
        _text_model = SentenceTransformer(config.TEXT_EMBEDDING_MODEL)
    return _text_model


def embed_text(texts: list[str]) -> np.ndarray:
    model = get_text_model()
    embeddings = model.encode(texts, normalize_embeddings=True)
    return np.asarray(embeddings, dtype=np.float32)


def get_clip_model():
    global _clip_model, _clip_preprocess
    if _clip_model is None:
        _clip_model, _clip_preprocess = clip.load(config.IMAGE_EMBEDDING_MODEL, device=_device)
        _clip_model.eval()
    return _clip_model, _clip_preprocess


def _l2_normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=-1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)
    return vectors / norms


def embed_image(image_path: str) -> np.ndarray:
    model, preprocess = get_clip_model()
    image = Image.open(image_path).convert("RGB")
    tensor = preprocess(image).unsqueeze(0).to(_device)
    with torch.no_grad():
        features = model.encode_image(tensor)
    vector = features.cpu().numpy().astype(np.float32)
    return _l2_normalize(vector)[0]


def embed_text_for_image_query(texts: list[str]) -> np.ndarray:
    """Embeds text into CLIP's joint text-image space, so it can query the food_images
    collection (built from CLIP image embeddings) directly - this is what makes the
    text-vs-image fusion in M2L3 possible."""
    model, _ = get_clip_model()
    tokens = clip.tokenize(texts).to(_device)
    with torch.no_grad():
        features = model.encode_text(tokens)
    vectors = features.cpu().numpy().astype(np.float32)
    return _l2_normalize(vectors)
