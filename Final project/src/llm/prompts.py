RESTAURANT_SCHEMA_DESCRIPTION = """{
  "name": string,
  "cuisine": string,
  "location": string (city),
  "price_range": one of "$", "$$", "$$$", "$$$$",
  "rating": float between 0 and 5 (estimate one if the text does not state it explicitly),
  "signature_dishes": list of 2-5 short strings,
  "vibe": list of 1-4 short descriptive tags (e.g. "romantic", "casual", "lively", "quiet", "family-friendly", "trendy"),
  "summary": one sentence summarizing the restaurant
}"""

ONE_SHOT_EXAMPLE_INPUT = (
    "Tucked into a quiet corner of North Beach, Nonna Lucia's has been serving "
    "handmade pasta since 1987. Expect a wait on weekends for the truffle "
    "tagliatelle and the osso buco. Candlelit tables and a small wine list make "
    "it a favorite for anniversaries. Plan to spend around $60 a head."
)

ONE_SHOT_EXAMPLE_OUTPUT = """{
  "name": "Nonna Lucia's",
  "cuisine": "Italian",
  "location": "San Francisco",
  "price_range": "$$$",
  "rating": 4.6,
  "signature_dishes": ["truffle tagliatelle", "osso buco"],
  "vibe": ["romantic", "quiet"],
  "summary": "A candlelit North Beach institution known for handmade pasta and osso buco, ideal for a special night out."
}"""


def build_extraction_prompt(raw_text: str) -> str:
    return f"""You extract structured restaurant data from unstructured descriptions.

Return ONLY a single valid JSON object matching exactly this shape (no markdown fences, no commentary):
{RESTAURANT_SCHEMA_DESCRIPTION}

Example input:
{ONE_SHOT_EXAMPLE_INPUT}

Example output:
{ONE_SHOT_EXAMPLE_OUTPUT}

Now extract from this description:
{raw_text}

JSON:"""


def build_repair_prompt(bad_json: str, error_message: str) -> str:
    return f"""The following JSON was supposed to match this schema:
{RESTAURANT_SCHEMA_DESCRIPTION}

It failed validation with this error:
{error_message}

Broken JSON:
{bad_json}

Return ONLY a corrected, valid JSON object matching the schema exactly (no markdown fences, no commentary). Fix every issue named in the error message."""
