import json

from mcp.server.fastmcp import FastMCP

import config

mcp = FastMCP("California Restaurant Server")


def _load_restaurants() -> list[dict]:
    return json.loads(config.STRUCTURED_RESTAURANTS_FILE.read_text(encoding="utf-8"))


def _load_users() -> list[dict]:
    return json.loads(config.USERS_FILE.read_text(encoding="utf-8"))


@mcp.resource("resource://california-culinary-map")
def california_culinary_map() -> str:
    """Raw California Culinary Map restaurant descriptions (unstructured source text)."""
    return config.CALIFORNIA_CULINARY_MAP_FILE.read_text(encoding="utf-8")


@mcp.tool()
def get_restaurant_info(name: str) -> str:
    """Look up restaurant details by partial name match. Returns a JSON list."""
    restaurants = _load_restaurants()
    matches = [r for r in restaurants if name.lower() in r["name"].lower()]
    return json.dumps(matches, indent=2)


@mcp.tool()
def recommend_by_vibe(vibe: str, limit: int = 5) -> str:
    """Recommend restaurants matching a vibe/mood. Two-pass search: structured vibe
    tags first, then a fallback scan of the raw California Culinary Map text for
    restaurants whose description mentions the vibe. Returns a JSON list."""
    restaurants = _load_restaurants()
    vibe_lower = vibe.lower()

    matches = [r for r in restaurants if any(vibe_lower in tag.lower() for tag in r["vibe"])]

    if len(matches) < limit:
        raw_blocks = config.CALIFORNIA_CULINARY_MAP_FILE.read_text(encoding="utf-8").split("\n===\n")
        matched_names = {r["name"] for r in matches}
        for r in restaurants:
            if r["name"] in matched_names:
                continue
            for block in raw_blocks:
                if r["name"] in block and vibe_lower in block.lower():
                    matches.append(r)
                    break

    return json.dumps(matches[:limit], indent=2)


@mcp.tool()
def get_review(restaurant_name: str) -> str:
    """Retrieve augmented user reviews for a restaurant by (partial) name. Returns a JSON list."""
    users = _load_users()
    reviews = []
    for user in users:
        for visit in user.get("visit_history", []):
            if restaurant_name.lower() in visit["restaurant_name"].lower():
                reviews.append(
                    {
                        "user": user["name"],
                        "restaurant": visit["restaurant_name"],
                        "rating": visit["rating"],
                        "comment": visit["comment"],
                        "date": visit.get("date"),
                    }
                )
    return json.dumps(reviews, indent=2)


if __name__ == "__main__":
    mcp.run(transport="stdio")
