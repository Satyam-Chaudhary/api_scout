import asyncio

from models.extraction import ExtractionResult
from tools.llm import generate_structured


async def main():
    prompt = """
You are a strict SaaS API research data extractor.

Extract facts ONLY from the evidence provided.

Rules:
1. Never infer facts that are not explicitly supported.
2. If API types are mentioned, public_api should be YES.
3. Authentication methods must include explicitly mentioned methods.
4. official_mcp must be UNKNOWN unless MCP is explicitly mentioned.
5. api_breadth must be UNKNOWN unless breadth is explicitly established.
6. primary_blocker must be empty if no blocker is mentioned.
7. Do not interpret missing information as NO.
8. Do not use external knowledge.

Evidence:

Salesforce provides REST, SOAP, Bulk and Metadata APIs.
OAuth 2.0 is used for authentication.

Extract the following:
- Description
- Public API availability
- Authentication methods
- Developer access requirements
- API types
- API breadth
- Official MCP availability
- MCP URL
- Primary blocker
"""

    result = await generate_structured(
        prompt,
        ExtractionResult,
    )

    print("\nStructured result:")
    print(result)

    print("\nJSON:")
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())