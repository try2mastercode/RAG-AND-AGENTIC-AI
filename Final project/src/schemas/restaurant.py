from pydantic import BaseModel, Field, field_validator

ALLOWED_PRICE_RANGES = {"$", "$$", "$$$", "$$$$"}


class Restaurant(BaseModel):
    id: str
    name: str = Field(min_length=1)
    cuisine: str = Field(min_length=1)
    location: str = Field(min_length=1)
    price_range: str
    rating: float = Field(ge=0, le=5)
    signature_dishes: list[str] = Field(min_length=1)
    vibe: list[str] = Field(min_length=1)
    summary: str = Field(min_length=1)

    @field_validator("price_range")
    @classmethod
    def price_range_must_be_valid(cls, v: str) -> str:
        if v not in ALLOWED_PRICE_RANGES:
            raise ValueError(f"price_range must be one of {sorted(ALLOWED_PRICE_RANGES)}, got {v!r}")
        return v

    @field_validator("signature_dishes", "vibe")
    @classmethod
    def no_blank_entries(cls, v: list[str]) -> list[str]:
        cleaned = [item.strip() for item in v if item and item.strip()]
        if not cleaned:
            raise ValueError("list must contain at least one non-empty entry")
        return cleaned
