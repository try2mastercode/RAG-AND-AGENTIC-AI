import threading

from groq import Groq

import config

_client: Groq | None = None
_client_lock = threading.Lock()

# gpt-oss-120b is a reasoning model: it can spend its entire max_tokens budget on
# hidden chain-of-thought and return an empty string with a normal 200 response
# (no exception to catch). Capping concurrent in-flight calls avoids Groq 429
# storms when LangGraph fans out several agent calls in parallel, and retrying
# once with a larger budget recovers from the empty-completion case.
_concurrency_limit = threading.Semaphore(2)


def get_client() -> Groq:
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                _client = Groq(api_key=config.require_groq_key())
    return _client


def _create(messages: list[dict], model: str | None, temperature: float, max_tokens: int) -> str:
    client = get_client()
    with _concurrency_limit:
        response = client.chat.completions.create(
            model=model or config.GROQ_TEXT_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    return response.choices[0].message.content or ""


def complete(prompt: str, model: str | None = None, temperature: float = 0.2, max_tokens: int = 800) -> str:
    messages = [{"role": "user", "content": prompt}]
    result = _create(messages, model, temperature, max_tokens)
    if not result.strip():
        result = _create(messages, model, temperature, max_tokens * 2)
    return result


def complete_chat(
    system: str, user: str, model: str | None = None, temperature: float = 0.3, max_tokens: int = 1200
) -> str:
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    result = _create(messages, model, temperature, max_tokens)
    if not result.strip():
        result = _create(messages, model, temperature, max_tokens * 2)
    return result
