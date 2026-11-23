import os

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()

# =========================
# OLLAMA
# =========================

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434",
).rstrip("/")

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5:7b",
)

# =========================
# OPENROUTER
# =========================

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "google/gemma-3-4b-it:free",
)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# =========================
# REQUESTY
# =========================

REQUESTY_API_KEY = os.getenv("REQUESTY_API_KEY")

REQUESTY_MODEL = os.getenv(
    "REQUESTY_MODEL",
    "",
)

REQUESTY_URL = os.getenv(
    "REQUESTY_BASE_URL",
    "https://router.requesty.ai/v1",
).rstrip("/") + "/chat/completions"


# =========================
# OLLAMA CHAT
# =========================

async def _ollama_chat(
    prompt: str,
    schema: type[BaseModel] | None = None,
) -> str:

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "stream": False,
    }

    if schema:
        payload["format"] = schema.model_json_schema()

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{OLLAMA_URL}/api/chat",
            json=payload,
        )

        response.raise_for_status()

        data = response.json()

    return data["message"]["content"]


# =========================
# OPENROUTER CHAT
# =========================

async def _openrouter_chat(
    prompt: str,
    schema: type[BaseModel] | None = None,
) -> str:

    if not OPENROUTER_API_KEY:
        raise ValueError(
            "OPENROUTER_API_KEY is missing from .env"
        )

    if schema:
        prompt += (
            "\n\nReturn valid JSON matching this schema:\n"
            f"{schema.model_json_schema()}"
        )

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }

    if schema:
        payload["response_format"] = {
            "type": "json_object",
        }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            OPENROUTER_URL,
            json=payload,
            headers=headers,
        )

        response.raise_for_status()

        data = response.json()

    return data["choices"][0]["message"]["content"]


# =========================
# REQUESTY CHAT
# =========================

async def _requesty_chat(
    prompt: str,
    schema: type[BaseModel] | None = None,
) -> str:

    if not REQUESTY_API_KEY:
        raise ValueError(
            "REQUESTY_API_KEY is missing from .env"
        )

    if not REQUESTY_MODEL:
        raise ValueError(
            "REQUESTY_MODEL is missing from .env"
        )

    if schema:
        prompt += (
            "\n\nReturn valid JSON matching this schema:\n"
            f"{schema.model_json_schema()}"
        )

    payload = {
        "model": REQUESTY_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }

    if schema:
        payload["response_format"] = {
            "type": "json_object",
        }

    headers = {
        "Authorization": f"Bearer {REQUESTY_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com",
        "X-Title": "API Scout",
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            REQUESTY_URL,
            json=payload,
            headers=headers,
        )

        response.raise_for_status()

        data = response.json()

    return data["choices"][0]["message"]["content"]


# =========================
# NORMAL RESPONSE ROUTER
# =========================

async def generate_response(prompt: str) -> str:

    if LLM_PROVIDER == "openrouter":
        return await _openrouter_chat(prompt)

    if LLM_PROVIDER == "ollama":
        return await _ollama_chat(prompt)

    if LLM_PROVIDER == "requesty":
        return await _requesty_chat(prompt)

    raise ValueError(
        f"Unsupported LLM provider: {LLM_PROVIDER}"
    )


# =========================
# STRUCTURED RESPONSE ROUTER
# =========================

async def generate_structured(
    prompt: str,
    schema: type[BaseModel],
) -> BaseModel:

    if LLM_PROVIDER == "openrouter":
        content = await _openrouter_chat(
            prompt,
            schema,
        )

    elif LLM_PROVIDER == "ollama":
        content = await _ollama_chat(
            prompt,
            schema,
        )

    elif LLM_PROVIDER == "requesty":
        content = await _requesty_chat(
            prompt,
            schema,
        )

    else:
        raise ValueError(
            f"Unsupported LLM provider: {LLM_PROVIDER}"
        )

    return schema.model_validate_json(content)