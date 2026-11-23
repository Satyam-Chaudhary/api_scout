import asyncio

from tools.fetcher import fetch_page
from tools.parser import extract_text
from tools.research import search_web


async def research_app(app_name: str) -> list[dict]:

    queries = [
        f"{app_name} official API documentation",
        f"{app_name} API authentication developer access",
        f"{app_name} official MCP Model Context Protocol",
    ]

    search_results = await asyncio.gather(
        *[search_web(query, max_results=5) for query in queries]
    )

    # Flatten the nested lists
    results = [
        result
        for group in search_results
        for result in group
    ]

    # Deduplicate by URL
    unique_results = {}

    for result in results:
        url = result.get("url")

        if url:
            unique_results[url] = result

    results = list(unique_results.values())

    # Prioritize results with higher search relevance scores
    results.sort(
        key=lambda result: result.get("score", 0),
        reverse=True,
    )

    # Limit the number of pages fetched per app
    results = results[:8]

    # Fetch pages concurrently
    async def fetch_result(result):
        try:
            page = await fetch_page(result["url"])

            if "html" not in page:
                return None

            text = extract_text(page["html"])

            return {
                "title": result.get("title", ""),
                "url": page["url"],
                "search_score": result.get("score", 0),
                "content": text[:12000],
            }

        except Exception as e:  # noqa: BLE001
            print(f"Failed to fetch {result.get('url')}: {e}")
            return None

    fetched = await asyncio.gather(
        *[fetch_result(result) for result in results]
    )

    # Remove failed fetches
    return [
        result
        for result in fetched
        if result is not None
    ]