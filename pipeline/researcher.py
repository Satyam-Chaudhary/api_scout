import asyncio

from tools.fetcher import fetch_page
from tools.parser import extract_text
from tools.research import search_web
from tools.source_ranker import classify_source

from models.source import SourceRecord


async def research_app(app_name: str) -> list[SourceRecord]:

    queries = [
        f"{app_name} official API documentation",
        f"{app_name} API authentication developer access",
        f"{app_name} official MCP Model Context Protocol",
    ]

    search_results = await asyncio.gather(
        *[search_web(query, max_results=5) for query in queries]
    )

    # Flatten the nested lists
    results = [result for group in search_results for result in group]

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

            source_info = classify_source(
                page["url"],
                app_name,
            )

            return {
                "title": result.get("title", ""),
                "url": page["url"],
                "search_score": result.get("score", 0),
                "content": text[:12000],
                **source_info,
            }

        except Exception as e:  # noqa: BLE001
            print(f"Failed to fetch {result.get('url')}: {e}")
            return None

    fetched = await asyncio.gather(
        *[fetch_result(result) for result in results]
    )

    # Remove failed fetches
    fetched = [
        result for result in fetched
        if result is not None
    ]

    # Convert fetched pages into validated SourceRecord objects
    source_records = []

    for page in fetched:
        source_records.append(
            SourceRecord(
                title=page.get("title", ""),
                url=page["url"],
                source_type=page.get("source_type", "unknown"),
                excerpt=page.get("content", ""),
                search_score=page.get("search_score", 0.0),
                source_score=page.get("source_score", 0.0),
            )
        )

    return source_records