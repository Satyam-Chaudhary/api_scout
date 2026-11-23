import asyncio

from pipeline.researcher import research_app


async def main():
    app_name = "Salesforce"

    results = await research_app(app_name)

    print(f"\nResearch results for {app_name}")
    print(f"Pages fetched successfully: {len(results)}")

    for i, result in enumerate(results, start=1):
        print(f"\n{'=' * 60}")
        print(f"PAGE {i}")
        print(f"{'=' * 60}")

        print("Title:", result["title"])
        print("URL:", result["url"])
        print("Search score:", result["search_score"])
        print("Content preview:")
        print(result["content"][:1000])


if __name__ == "__main__":
    asyncio.run(main())