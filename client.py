import asyncio

from fastmcp import Client


async def main():
    async with Client("http://localhost:8080/mcp") as client:
        result = await client.get_prompt(
            name="aon_prompt"
        )
        print(result)
        config = await client.read_resource("config://version")
        print(config)


if __name__ == '__main__':
    asyncio.run(main())
