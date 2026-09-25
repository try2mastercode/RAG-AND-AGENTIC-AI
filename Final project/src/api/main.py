import json
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import config
from chatbot.service import SAMPLE_PROMPTS, respond
from data.cli import add_restaurant, delete_restaurant, edit_restaurant, find_restaurant, load_restaurants, save_restaurants

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="California Restaurant & Recipe Recommender API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    reply: str


class AddRestaurantRequest(BaseModel):
    raw_text: str = Field(min_length=1)


class EditRestaurantRequest(BaseModel):
    updates: dict


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/sample-prompts")
def sample_prompts():
    return {"prompts": SAMPLE_PROMPTS}


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    reply = respond(payload.message)
    return ChatResponse(reply=reply)


@app.get("/api/restaurants")
def list_restaurants():
    return load_restaurants()


@app.get("/api/restaurants/{restaurant_id}")
def get_restaurant(restaurant_id: str):
    record = find_restaurant(load_restaurants(), restaurant_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"no restaurant with id {restaurant_id}")
    return record


@app.post("/api/restaurants", status_code=201)
def create_restaurant(payload: AddRestaurantRequest):
    records = load_restaurants()
    try:
        updated = add_restaurant(records, payload.raw_text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"could not structure that description: {e}")
    save_restaurants(updated)
    return updated[-1]


@app.put("/api/restaurants/{restaurant_id}")
def update_restaurant(restaurant_id: str, payload: EditRestaurantRequest):
    records = load_restaurants()
    try:
        updated = edit_restaurant(records, restaurant_id, payload.updates)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    save_restaurants(updated)
    return find_restaurant(updated, restaurant_id)


@app.delete("/api/restaurants/{restaurant_id}", status_code=204)
def remove_restaurant(restaurant_id: str):
    records = load_restaurants()
    try:
        updated = delete_restaurant(records, restaurant_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    save_restaurants(updated)


@app.get("/api/recipes")
def list_recipes():
    if not config.RECIPES_FILE.exists():
        return []
    return json.loads(config.RECIPES_FILE.read_text(encoding="utf-8"))


_frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if _frontend_dir.exists():
    app.mount("/", StaticFiles(directory=_frontend_dir, html=True), name="frontend")
