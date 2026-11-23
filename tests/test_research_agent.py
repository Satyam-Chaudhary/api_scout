import asyncio
import json

from agents.research_agent import analyze_app


async def main():
    app_name = "Supabase"

    # print(f"\nResearching {app_name}...")
    # print("This may take a while.\n")

    # result = await analyze_app(app_name)

    # print("\n" + "=" * 60)
    # print("API SCOUT RESEARCH RESULT")
    # print("=" * 60)

    # print(result)

    # print("\n" + "=" * 60)
    # print("JSON OUTPUT")
    # print("=" * 60)

    # print(result.model_dump_json(indent=2))
    # print("\nRETRIEVED SOURCES")
    # for source in result.sources:
    #     print(f"\nTitle: {source.title}")
    #     print(f"URL: {source.url}")
    #     print(f"Source type: {source.source_type}")
    #     print(f"Score: {source.source_score}")
    
    print(f"\nResearching {app_name}...\n")

    result = await analyze_app(app_name)

    # Convert Pydantic models, enums, URLs and timestamps to JSON-compatible data.
    output = result.model_dump(mode="json")

    # Keep source provenance, but shorten excerpts to make terminal output manageable.
    for source in output.get("sources", []):
        source["excerpt"] = source.get("excerpt", "")[:300]

    print("\n" + "=" * 40)
    print("API SCOUT JSON RESULT")
    print("=" * 40)

    print(json.dumps(output, indent=2, ensure_ascii=False))

    print("\n" + "=" * 40)


if __name__ == "__main__":
    asyncio.run(main())