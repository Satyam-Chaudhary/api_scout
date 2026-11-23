import asyncio

from tools.research import search_web


async def main():
    query = "Salesforce official API documentation authentication"

    results = await search_web(query, max_results=5)

    print(f"\nQuery: {query}")
    print(f"Results found: {len(results)}")

    for i, result in enumerate(results, start=1):
        print(f"\n--- Result {i} ---")
        print("Title:", result.get("title"))
        print("URL:", result.get("url"))
        print("Score:", result.get("score"))
        print("Content:", result.get("content", "")[:500])


if __name__ == "__main__":
    asyncio.run(main())