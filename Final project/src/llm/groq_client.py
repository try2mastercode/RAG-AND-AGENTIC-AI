from groq import Groq

import config

_client: Groq | None = None


def get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=config.require_groq_key())
    return _client


def complete(prompt: str, model: str | None = None, temperature: float = 0.2, max_tokens: int = 800) -> str:
    client = get_client()
    response = client.chat.completions.create(
        model=model or config.GROQ_TEXT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def complete_chat(
    system: str, user: str, model: str | None = None, temperature: float = 0.3, max_tokens: int = 700
) -> str:
    client = get_client()
    response = client.chat.completions.create(
        model=model or config.GROQ_TEXT_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content
