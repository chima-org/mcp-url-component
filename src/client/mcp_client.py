import asyncio
import logging
from datetime import timedelta

from mcp import ClientSession
from mcp.client.sse import sse_client
from typing import Any, List


class MCPClient:
    def __init__(self, server_params: str):
        self.server_params = server_params
        self.session = None
        self._client = None

        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("mcp-client")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        try:
            if self.session:
                await self.session.__aexit__(exc_type, exc_val, exc_tb)
                self.session = None
            if self._client:
                await self._client.__aexit__(exc_type, exc_val, exc_tb)
                self._client = None
        except Exception as e:
            self.logger.error(f"Error exiting context manager: {e}")

    async def connect(self):
        """Establishes connection to MCP server"""
        self._client = sse_client(self.server_params)
        self.read, self.write = await self._client.__aenter__()
        session = ClientSession(self.read, self.write, timedelta(seconds=5))
        self.session = await session.__aenter__()
        await self.session.initialize()
        self.logger.info("Connected to MCP server")

    async def get_available_tools(self) -> List[Any]:
        """List available tools"""
        if not self.session:
            self.logger.error("Not connected to MCP server")
            raise RuntimeError("Not connected to MCP server")

        tools = await self.session.list_tools()
        _, tools_list = tools
        _, tools_list = tools_list
        return tools_list

    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """Call a tool with given arguments"""
        if not self.session:
            self.logger.error("Not connected to MCP server")
            raise RuntimeError("Not connected to MCP server")

        result = await self.session.call_tool(tool_name, arguments=arguments)
        return result


if __name__ == "__main__":

    async def test_mcp_client():
        client = MCPClient("http://localhost:3000/sse")
        await client.connect()

        tools = await client.get_available_tools()
        print(tools)

    def main():
        try:
            asyncio.run(test_mcp_client())
        except Exception as e:
            print(e)

    main()
