import json
import logging

from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor

import config

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_processor = None
_model = None


def _get_model():
    global _processor, _model
    if _model is None:
        logger.info("loading BLIP model %s (first run downloads weights)", config.BLIP_MODEL_NAME)
        _processor = BlipProcessor.from_pretrained(config.BLIP_MODEL_NAME)
        _model = BlipForConditionalGeneration.from_pretrained(config.BLIP_MODEL_NAME)
    return _processor, _model


def caption_image(image_path: str) -> str:
    """Unconditional captioning, grounded purely in the image - never fed a text prefix,
    since conditioning BLIP on a full sentence makes it parrot the prefix back instead of
    describing the picture."""
    processor, model = _get_model()
    image = Image.open(image_path).convert("RGB")
    inputs = processor(image, return_tensors="pt")
    output_ids = model.generate(**inputs, max_new_tokens=40)
    return processor.decode(output_ids[0], skip_special_tokens=True).strip()


def build_caption(image_path: str, context: str | None = None) -> str:
    """Visual caption first, contextual review info appended afterward - never blended
    into the model's generation input."""
    visual_caption = caption_image(image_path)
    return f"{visual_caption}. {context}." if context else visual_caption


def _find_review_context(restaurant_name: str, users: list[dict]) -> str | None:
    if not restaurant_name:
        return None
    for user in users:
        for visit in user.get("visit_history", []):
            if visit.get("restaurant_name") == restaurant_name and visit.get("comment"):
                return f'Reviewed at {restaurant_name}: "{visit["comment"]}"'
    return None


def caption_sample(n: int = 2, recipes_path=None) -> list[dict]:
    """Small-scale test on a few images before running the full batch (per lab requirement)."""
    recipes_path = recipes_path or config.RECIPES_FILE
    recipes = json.loads(recipes_path.read_text(encoding="utf-8"))
    sample = []
    for recipe in recipes[:n]:
        caption = caption_image(recipe["image_path"])
        logger.info("sample caption: %s -> %s", recipe["name"], caption)
        sample.append({"name": recipe["name"], "caption": caption})
    return sample


def caption_all_recipes(recipes_path=None, users_path=None) -> list[dict]:
    recipes_path = recipes_path or config.RECIPES_FILE
    users_path = users_path or config.USERS_FILE

    recipes = json.loads(recipes_path.read_text(encoding="utf-8"))
    users = json.loads(users_path.read_text(encoding="utf-8")) if users_path.exists() else []

    logger.info("stage started: captioning %d recipe images", len(recipes))

    # ---- required loop: call the vision model and assign a caption to each recipe entry ----
    for idx, recipe in enumerate(recipes, start=1):
        context = _find_review_context(recipe.get("source", ""), users)
        caption = build_caption(recipe["image_path"], context=context)
        recipe["caption"] = caption
        logger.info("captioned %d/%d: %s -> %s", idx, len(recipes), recipe["name"], caption)

    recipes_path.write_text(json.dumps(recipes, indent=2), encoding="utf-8")
    logger.info("stage completed: %d recipes captioned, saved to %s", len(recipes), recipes_path)
    return recipes


if __name__ == "__main__":
    caption_sample()
    caption_all_recipes()
