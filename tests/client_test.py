import asyncio
from datetime import timedelta
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession


async def test_mcp_connection():
    async with sse_client("http://localhost:3000/sse") as streams:
        async with ClientSession(
            streams[0], streams[1], timedelta(seconds=3)
        ) as session:
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print(tools)

            # Call the fetch tool
            result = await session.call_tool("fetch", {"url": "https://example.com"})
            print(result.content[0].text)


if __name__ == "__main__":
    asyncio.run(test_mcp_connection())
