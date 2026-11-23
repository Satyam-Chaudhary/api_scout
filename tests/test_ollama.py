import asyncio

from tools.llm import generate_response



async def main():
    prompt = """
    You are a SaaS API research analyst.

    
    """

    result = await generate_response(prompt)

    print("\nModel response:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())