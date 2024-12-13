import asyncio
from datetime import timedelta
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession


async def test_mcp_url_connection():
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


async def test_mcp_jira_connection():
    async with sse_client("http://localhost:3001/sse") as streams:
        async with ClientSession(
            streams[0], streams[1], timedelta(seconds=3)
        ) as session:
            await session.initialize()

            # List available tools
            # tools = await session.list_tools()
            # print(tools)

            # Call the jira_list_projects tool
            # result = await session.call_tool("jira_list_projects", {})
            # print(result.content[0].text)

            # Call the jira_get_project_details tool
            # result = await session.call_tool(
            #     "jira_get_project_details", {"project_id": "AE"}
            # )
            # print(result.content[0].text)

            # Call the jira_search_issues tool
            result = await session.call_tool(
                "jira_search_issues",
                {
                    "issue_ids": ["AE-1008", "AE-990"],
                    "number": 10,
                },
            )
            print(result.content[0].text)


if __name__ == "__main__":
    asyncio.run(test_mcp_jira_connection())
