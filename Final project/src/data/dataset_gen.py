import json
import random

from PIL import Image, ImageDraw, ImageFont

import config

# The original IBM lab notebook's source dataset (raw restaurant text, food images,
# user history) was never supplied to this repo - this module authors a coherent
# synthetic stand-in, deliberately varied in style/completeness like real-world text.
RAW_RESTAURANT_TEXT = """Green Papaya has been dishing out steaming bowls of pho and fresh summer rolls in San Jose's Little Saigon since 2005. The broth simmers for eighteen hours and regulars swear by the shaking beef. Lunch combos run about $14, dinner closer to $20 a plate. Fluorescent lights and formica tables keep it firmly in casual territory, but the line out the door on Sunday mornings says everything about the food.
===
El Mercado Cantina brings Mexico City street food to a strip mall in East LA, and somehow it works. The al pastor is carved off a spit by the register, the birria tacos come with a cup of consomme for dipping, and a michelada costs less than a coffee downtown. Loud, bright, plastic patio furniture, mariachi on the speakers most nights - locals rate it 4.7 stars and mean it.
===
Bluefin & Co. sits on a quiet San Diego side street and does omakase the old-fashioned way: no menu, no substitutions, just whatever chef Aki sourced that morning. Expect uni, fatty tuna, and a tamago that somehow tastes like dessert. It is not cheap - closer to $150 a head - but the eight-seat bar books out weeks in advance for a reason. Hushed, minimalist, very much a special-occasion spot.
===
Smoke & Char in Oakland smells like post oak from half a block away. The brisket gets a twelve-hour cook and the mac and cheese is smoked right alongside it. Picnic tables, paper plates, a self-serve sauce bar with three heat levels. Plates run $16-24 depending on the meat. It's loud, it's messy, and on a Friday night the whole parking lot smells incredible.
===
Spice Route in Berkeley has quietly become the neighborhood's go-to for Indian food that doesn't dumb down the heat. The chicken tikka masala is solid but the lamb vindaloo and the garlic naan are what people actually talk about. Warm lighting, sitar music low in the background, prices hover around $$ for a full dinner. Reliable four-star favorite for a Tuesday night dinner that doesn't feel like a compromise.
===
Olive & Thyme overlooks the water in Santa Barbara and leans hard into Mediterranean comfort - whole grilled branzino, lamb kofta, a mezze spread big enough for four. White tablecloths, an extensive rose list, and a sunset view that justifies the $$$$ price tag. Reservations recommended for the patio. Romantic, polished, the kind of place you save for anniversaries.
===
Kimchi Garden is a Koreatown LA staple where you cook your own bulgogi and short rib tableside over charcoal. Banchan keeps arriving whether you ask for it or not, and the soju flows freely on weekends. Expect a wait after 7pm and expect to leave smelling like smoke in the best way. Lively, a little chaotic, roughly $$ per person - it's a group dinner kind of restaurant.
===
Harvest Table sources almost everything from within thirty miles of its Napa dining room, and the menu changes with whatever the farm delivered that week. Think roasted beets with goat cheese one month, heirloom tomato salad the next. Wine pairings from the valley next door, a tasting menu around $95, and a dining room built almost entirely of reclaimed wood. Quiet, earthy, unmistakably farm-to-table.
===
Tagine House brings Ethiopian and Moroccan cooking together under one roof in Sacramento, which sounds odd until you taste the misir wot served alongside a proper lamb tagine, both scooped up with injera instead of silverware. Communal low tables, woven baskets on the walls, and a price point friendly enough for a weeknight - most dinners land under $20. Warm, communal, built for sharing plates with a group.
===
The Vegan Anchor in San Francisco proves plant-based seafood can actually be craveable - the "crab" cakes are made from hearts of palm and nobody at the table notices the difference. Chef's tasting menu leans playful, cocktail list is inventive, and the whole thing sits at a $$$ price point that matches the ambition. Sleek, modern, a magnet for the city's vegetarian and vegan crowd.
===
Pacific Catch Shack is about as close to the water as a restaurant can get in Monterey - the daily catch comes off boats you can see from the patio. Cioppino is the thing to order, though the fish tacos have their own cult following among locals. Picnic benches, paper menus, cash preferred, $$ a plate. Casual, salty-air, the kind of spot tourists stumble into and locals never leave.
===
Desert Bloom Cafe in Palm Springs does breakfast and lunch only, and does it extremely well - shakshuka, a citrus salad with dates and pistachios, cold-brew that actually holds up in the heat. Patio seating under string lights, bright Mediterranean-Californian menu, $$ average check. Bright, airy, a brunch spot that easily earns its 4.5-star reputation among the regulars who show up every weekend."""

RECIPES = [
    {
        "id": "rc001",
        "name": "Vietnamese Beef Pho",
        "cuisine": "Vietnamese",
        "ingredients": ["beef bones", "rice noodles", "star anise", "charred onion", "thai basil", "bean sprouts"],
        "instructions": "Simmer bones with charred aromatics for at least 6 hours, strain, then ladle over rice noodles and thinly sliced beef. Serve with basil, sprouts, and lime.",
        "source": "Green Papaya",
        "palette": "green",
    },
    {
        "id": "rc002",
        "name": "Birria Tacos",
        "cuisine": "Mexican",
        "ingredients": ["chuck roast", "dried guajillo chiles", "corn tortillas", "onion", "cilantro", "queso oaxaca"],
        "instructions": "Braise beef with toasted chiles until falling apart, shred, and pan-fry tortillas dipped in the braising fat. Serve with a cup of consomme for dipping.",
        "source": "El Mercado Cantina",
        "palette": "red",
    },
    {
        "id": "rc003",
        "name": "Spicy Tuna Roll",
        "cuisine": "Japanese",
        "ingredients": ["sushi rice", "ahi tuna", "sriracha mayo", "nori", "cucumber", "scallion"],
        "instructions": "Dice tuna and mix with sriracha mayo, roll tightly with rice and cucumber in nori, slice and top with scallion.",
        "source": "Bluefin & Co.",
        "palette": "pink",
    },
    {
        "id": "rc004",
        "name": "Smoked Brisket Plate",
        "cuisine": "American BBQ",
        "ingredients": ["beef brisket", "black pepper", "kosher salt", "smoked mac and cheese", "pickles"],
        "instructions": "Rub brisket with salt and pepper, smoke low and slow over post oak for around 12 hours, rest, then slice against the grain.",
        "source": "Smoke & Char",
        "palette": "brown",
    },
    {
        "id": "rc005",
        "name": "Chicken Tikka Masala",
        "cuisine": "Indian",
        "ingredients": ["chicken thigh", "yogurt", "garam masala", "tomato puree", "cream", "garlic naan"],
        "instructions": "Marinate chicken in yogurt and spices, char under high heat, then simmer in a tomato-cream sauce until thick. Serve with naan.",
        "source": "Spice Route",
        "palette": "orange",
    },
    {
        "id": "rc006",
        "name": "Greek Lemon Chicken with Orzo",
        "cuisine": "Mediterranean",
        "ingredients": ["chicken thigh", "orzo", "lemon", "oregano", "feta", "kalamata olives"],
        "instructions": "Roast chicken with lemon and oregano, cook orzo in the pan drippings, and finish with crumbled feta and olives.",
        "source": "Olive & Thyme",
        "palette": "yellow",
    },
    {
        "id": "rc007",
        "name": "Korean Bulgogi Bowl",
        "cuisine": "Korean",
        "ingredients": ["ribeye", "soy sauce", "pear puree", "sesame oil", "steamed rice", "kimchi"],
        "instructions": "Marinate thin-sliced ribeye in soy, pear, and sesame oil, sear quickly over high heat, and serve over rice with kimchi.",
        "source": "Kimchi Garden",
        "palette": "red",
    },
    {
        "id": "rc008",
        "name": "Roasted Root Vegetable Harvest Bowl",
        "cuisine": "American Farm-to-Table",
        "ingredients": ["beets", "carrots", "goat cheese", "arugula", "walnuts", "sherry vinaigrette"],
        "instructions": "Roast beets and carrots until caramelized, toss with arugula and a sherry vinaigrette, and finish with goat cheese and walnuts.",
        "source": "Harvest Table",
        "palette": "purple",
    },
    {
        "id": "rc009",
        "name": "Ethiopian Misir Wot with Injera",
        "cuisine": "Ethiopian",
        "ingredients": ["red lentils", "berbere spice", "onion", "garlic", "injera flatbread"],
        "instructions": "Slow-cook lentils with berbere, onion, and garlic until thick and deeply spiced. Serve scooped up with torn injera.",
        "source": "Tagine House",
        "palette": "orange",
    },
    {
        "id": "rc010",
        "name": "Grilled Peach and Burrata Salad",
        "cuisine": "Californian",
        "ingredients": ["peaches", "burrata", "arugula", "basil", "balsamic glaze", "toasted almonds"],
        "instructions": "Grill peach halves until charred, arrange over arugula with torn burrata, and finish with basil, almonds, and balsamic glaze.",
        "source": "Desert Bloom Cafe",
        "palette": "yellow",
    },
]

USERS = [
    {
        "id": "user_001",
        "name": "Maya Chen",
        "persona": "health-conscious",
        "visit_history": [
            {"restaurant_name": "Olive & Thyme", "date": "2026-06-02", "rating": 4.5, "comment": "Loved the mezze spread, easy to keep it plant-heavy here."},
            {"restaurant_name": "The Vegan Anchor", "date": "2026-07-14", "rating": 5.0, "comment": "The heart-of-palm crab cakes actually fooled me."},
        ],
        "social_posts": [
            "trying to eat more plant-based this year, always hunting for good vegetarian spots",
            "gluten-free and loving it - Mediterranean food makes this so easy",
        ],
    },
    {
        "id": "user_002",
        "name": "Jordan Alvarez",
        "persona": "adventurous foodie",
        "visit_history": [
            {"restaurant_name": "Bluefin & Co.", "date": "2026-05-20", "rating": 5.0, "comment": "Best omakase I've had outside Tokyo, no notes."},
            {"restaurant_name": "Tagine House", "date": "2026-08-01", "rating": 4.5, "comment": "Never had Ethiopian and Moroccan on one table, incredible combo."},
        ],
        "social_posts": [
            "always down to try a cuisine I've never had before",
            "fine dining tasting menus are basically my hobby at this point",
        ],
    },
    {
        "id": "user_003",
        "name": "Sam Okafor",
        "persona": "budget-conscious student",
        "visit_history": [
            {"restaurant_name": "El Mercado Cantina", "date": "2026-06-10", "rating": 4.7, "comment": "Best tacos for the price, full period."},
            {"restaurant_name": "Green Papaya", "date": "2026-07-02", "rating": 4.3, "comment": "Huge bowl of pho for under $15, perfect after class."},
        ],
        "social_posts": [
            "grad student budget so anything under $15 a plate is a win",
            "comfort food > fancy food, fight me",
        ],
    },
    {
        "id": "user_004",
        "name": "The Kim Family",
        "persona": "family with dietary restrictions",
        "visit_history": [
            {"restaurant_name": "Kimchi Garden", "date": "2026-06-25", "rating": 4.2, "comment": "Kids loved cooking at the table, staff was careful about the nut allergy."},
            {"restaurant_name": "Spice Route", "date": "2026-07-20", "rating": 4.0, "comment": "They remade a dish without cashews without any hassle."},
        ],
        "social_posts": [
            "one of us has a severe nut allergy so we always call ahead",
            "looking for casual, kid-friendly spots that take allergies seriously",
        ],
    },
]

PALETTES = {
    "green": ["#2f5233", "#6b8e23", "#a8c66c", "#f2f0e6"],
    "red": ["#7a1f1f", "#b3402a", "#e0754a", "#f4e3c1"],
    "pink": ["#7a1f3d", "#c94277", "#f2a6c1", "#fdf0f5"],
    "brown": ["#3b2412", "#6f4518", "#a9713b", "#f0dcb8"],
    "orange": ["#7a3b12", "#c9701f", "#f2a541", "#fdeccb"],
    "yellow": ["#7a6a12", "#c9b022", "#f2dc5c", "#fdf6d8"],
    "purple": ["#3b1f4d", "#6b3d8e", "#a879c4", "#efe3f5"],
}


def generate_food_image(name: str, palette_key: str, seed: int, size: int = 384) -> Image.Image:
    """Draws a deterministic, cuisine-toned synthetic plate image (no external image dataset available)."""
    rng = random.Random(seed)
    colors = PALETTES.get(palette_key, PALETTES["orange"])
    img = Image.new("RGB", (size, size), colors[3])
    draw = ImageDraw.Draw(img)

    plate_margin = size // 10
    draw.ellipse(
        [plate_margin, plate_margin, size - plate_margin, size - plate_margin],
        fill="#fdfdfb",
        outline="#d8d8d0",
        width=4,
    )

    center = size // 2
    for _ in range(rng.randint(6, 10)):
        color = rng.choice(colors[:3])
        cx = center + rng.randint(-size // 4, size // 4)
        cy = center + rng.randint(-size // 4, size // 4)
        r = rng.randint(size // 16, size // 8)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    for _ in range(rng.randint(8, 14)):
        color = rng.choice(colors[:3])
        cx = center + rng.randint(-size // 3, size // 3)
        cy = center + rng.randint(-size // 3, size // 3)
        r = rng.randint(3, 7)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    try:
        font = ImageFont.load_default()
        draw.text((10, size - 20), name[:28], fill="#333333", font=font)
    except Exception:
        pass

    return img


def generate_all() -> None:
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    config.CALIFORNIA_CULINARY_MAP_FILE.write_text(RAW_RESTAURANT_TEXT, encoding="utf-8")

    config.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    config.RECIPES_DIR.mkdir(parents=True, exist_ok=True)
    recipes_out = []
    for idx, recipe in enumerate(RECIPES, start=1):
        image_name = f"{recipe['id']}.png"
        image_path = config.IMAGES_DIR / image_name
        img = generate_food_image(recipe["name"], recipe["palette"], seed=idx)
        img.save(image_path)

        record = {k: v for k, v in recipe.items() if k != "palette"}
        record["image_path"] = str(image_path)
        record["caption"] = None
        recipes_out.append(record)

    config.RECIPES_FILE.write_text(json.dumps(recipes_out, indent=2), encoding="utf-8")

    config.REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    config.USERS_FILE.write_text(json.dumps(USERS, indent=2), encoding="utf-8")

    print(f"wrote {config.CALIFORNIA_CULINARY_MAP_FILE}")
    print(f"wrote {len(recipes_out)} recipes + images to {config.RECIPES_FILE} / {config.IMAGES_DIR}")
    print(f"wrote {len(USERS)} users to {config.USERS_FILE}")


if __name__ == "__main__":
    generate_all()
