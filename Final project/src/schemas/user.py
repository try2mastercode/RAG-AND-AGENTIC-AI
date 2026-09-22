from pydantic import BaseModel, Field


class VisitRecord(BaseModel):
    restaurant_name: str = Field(min_length=1)
    date: str
    rating: float = Field(ge=0, le=5)
    comment: str


class User(BaseModel):
    id: str
    name: str = Field(min_length=1)
    visit_history: list[VisitRecord] = Field(default_factory=list)
    social_posts: list[str] = Field(default_factory=list)
