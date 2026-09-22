from pydantic import BaseModel, Field


class Recipe(BaseModel):
    id: str
    name: str = Field(min_length=1)
    cuisine: str = Field(min_length=1)
    ingredients: list[str] = Field(min_length=1)
    instructions: str = Field(min_length=1)
    image_path: str
    source: str | None = None
    caption: str | None = None
