import os

import httpx
from dotenv import load_dotenv

load_dotenv()

TAVILY_URL = "https://api.tavily.com/search"


async def search_web(query: str, max_results: int = 5) -> list[dict]:
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise ValueError("TAVILY_API_KEY is missing from .env")

    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": max_results,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            TAVILY_URL,
            json=payload,
        )

        response.raise_for_status()

        data = response.json()

    return data.get("results", [])