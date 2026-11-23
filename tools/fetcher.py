import httpx


async def fetch_page(url: str) -> dict:
    headers = {
        "User-Agent": (
            "APIScout/1.0 "
            "(research agent; public developer documentation research)"
        )
    }

    async with httpx.AsyncClient(
        timeout=30.0,
        follow_redirects=True,
        headers=headers,
    ) as client:
        response = await client.get(url)
        response.raise_for_status()

    return {
        "url": str(response.url),
        "status_code": response.status_code,
        "content_type": response.headers.get("content-type", ""),
        "html": response.text,
    }