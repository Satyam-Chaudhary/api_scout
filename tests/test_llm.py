import asyncio

from models.extraction import ExtractionResult
from tools.llm import generate_structured


async def main():
    prompt = """
    Research the fictional application TestApp.

    TestApp has a public REST API.
    It uses OAuth 2.0 authentication.
    Developers can access its API through self-service registration.

    Extract these facts into the provided schema.
    """

    result = await generate_structured(
        prompt,
        ExtractionResult,
    )

    print("\nLLM TEST RESULT")
    print("=" * 50)
    print(result)
    print("\nJSON:")
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())