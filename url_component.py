import asyncio
from datetime import timedelta

from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

from pydantic import BaseModel, Field

from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.field_typing import Tool
from langflow.schema import Data
from langflow.schema.message import Message


class URLComponent(Component):
    display_name = "MCP URL Client Component"
    description = "Connect to an MCP Server and fetch a URL"
    documentation: str = "http://docs.langflow.org/components/custom"
    icon = "custom_components"
    name = "URLComponent"

    inputs = [
        MessageTextInput(
            name="url",
            display_name="URL",
            info="URL to fetch",
            value="https://example.com",
        ),
    ]

    outputs = [
        Output(display_name="URL Content", name="url_content", method="build_output"),
        Output(display_name="URL Content", name="url_content", method="build_tool"),
    ]

    async def _fetch_url(self, url: str) -> str:
        """Fetch the content of a URL with a rate limit of 150,000 characters"""
        async with sse_client("http://localhost:3000/sse") as streams:
            async with ClientSession(
                streams[0], streams[1], timedelta(seconds=10)
            ) as session:
                try:
                    await session.initialize()
                    result = await session.call_tool("fetch", {"url": url})
                    return result.content[0].text[:150_000]  # rate limit
                except Exception as e:
                    return f"Error: {e}"

    def build_output(self, url: str) -> Message:
        """Build the output of the URL component"""
        return Message(text=asyncio.run(self._fetch_url(url)))

    class FetchURLTool(BaseModel):
        """Input schema for the fetch_url tool"""

        url: str = Field(..., description="The URL to fetch")

    def build_tool(self) -> Tool:
        """Build the tool of the URL component"""
        tool = Tool.from_function(
            name="fetch_url",
            description="Fetch the content of a URL",
            func=self.build_output,
            args_schema=self.FetchURLTool,
        )
        return tool
