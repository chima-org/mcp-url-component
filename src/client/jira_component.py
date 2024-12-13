import asyncio
from datetime import timedelta

from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

from pydantic import BaseModel, Field

from langchain_core.tools import StructuredTool
from langflow.custom import Component
from langflow.io import MessageTextInput, Output, SecretStrInput
from langflow.field_typing import Tool
from langflow.schema.message import Message


class JiraComponent(Component):
    display_name = "Jira Component"
    description = "Connect to Jira and fetch data"
    documentation: str = "http://docs.langflow.org/components/custom"
    icon = "custom_components"
    name = "JiraComponent"

    inputs = [
        SecretStrInput(
            name="jira_api_token",
            display_name="Jira API Token",
            info="The API token to use for Jira",
            required=True,
            show=False,
        ),
        MessageTextInput(
            name="project_id",
            display_name="Jira Project ID",
            info="The ID of the Jira project to fetch project details from",
        ),
        MessageTextInput(
            name="issue_ids",
            display_name="Jira Issue IDs",
            info="The IDs of the Jira issues to fetch issue details from",
        ),
        MessageTextInput(
            name="project_ids",
            display_name="Jira Project IDs",
            info="The IDs of the Jira projects to fetch project details from",
        ),
    ]

    outputs = [
        Output(
            type="tool",
            required_inputs=["project_id"],
            display_name="Jira Project Details",
            name="jira_project_details",
            method="build_get_project_details_tool",
        ),
        Output(
            type="tool",
            required_inputs=[],
            display_name="Jira List Projects",
            name="jira_list_projects",
            method="build_list_projects_tool",
        ),
        Output(
            type="tool",
            required_inputs=["issue_ids", "project_ids"],
            display_name="Jira Search Issues",
            name="jira_search_issues",
            method="build_search_issues_tool",
        ),
    ]

    def fetch_project_details(self, project_id: str) -> Message:
        async def _fetch_project_details(project_id: str) -> str:
            """Fetch the project details from Jira"""
            async with sse_client("http://localhost:3001/sse") as streams:
                async with ClientSession(
                    streams[0], streams[1], timedelta(seconds=3)
                ) as session:
                    await session.initialize()
                    result = await session.call_tool(
                        "jira_get_project_details", {"project_id": project_id}
                    )
                    return result.content[0].text

        return Message(text=asyncio.run(_fetch_project_details(project_id)))

    def list_projects(self, project_id: str) -> Message:
        async def _list_projects() -> str:
            """List all Jira projects"""
            async with sse_client(
                "http://localhost:3001/sse",
                headers={
                    "Authorization": f"Bearer {self.inputs['jira_api_token'].get_secret_value()}"
                },
            ) as streams:
                async with ClientSession(
                    streams[0], streams[1], timedelta(seconds=3)
                ) as session:
                    # TODO: Add API token to the session
                    await session.initialize()
                    result = await session.call_tool("jira_list_projects")
                    return result.content[0].text

        return Message(text=asyncio.run(_list_projects()))

    def search_issues(self, issue_ids: list[str], project_ids: list[str]) -> Message:
        async def _search_issues() -> str:
            """Search for issues in a Jira project"""
            async with sse_client("http://localhost:3001/sse") as streams:
                async with ClientSession(
                    streams[0], streams[1], timedelta(seconds=3)
                ) as session:
                    await session.initialize()
                    result = await session.call_tool(
                        "jira_search_issues",
                        {
                            "issue_ids": issue_ids,
                            "project_ids": project_ids,
                        },
                    )
                    return result.content[0].text

        return Message(text=asyncio.run(_search_issues()))

    def add_issue_comment(self, issue_id: str, comment: str) -> Message:
        async def _add_issue_comment() -> str:
            """Create an issue in a Jira project"""
            async with sse_client("http://localhost:3001/sse") as streams:
                async with ClientSession(
                    streams[0], streams[1], timedelta(seconds=3)
                ) as session:
                    await session.initialize()
                    result = await session.call_tool(
                        "jira_add_issue_comment",
                        {
                            "issue_id": issue_id,
                            "comment": comment,
                        },
                    )
                    return result.content[0].text

        return Message(text=asyncio.run(_add_issue_comment()))

    class FetchProjectDetailsTool(BaseModel):
        """Input schema for the fetch_project_details tool"""

        project_id: str = Field(
            ..., description="The ID of the Jira project to fetch details from"
        )

    class SearchIssuesTool(BaseModel):
        """Input schema for the search_issues tool"""

        issue_ids: list[str] = Field(
            ..., description="The IDs of the Jira issues to search"
        )
        project_ids: list[str] = Field(
            ..., description="The IDs of the Jira projects to search issues in"
        )

    def build_get_project_details_tool(self) -> Tool:
        """Build the output of the Jira component"""
        return Tool(
            name="jira_get_project_details",
            description="Fetch the details of a Jira project",
            func=self.fetch_project_details,
            args_schema=self.FetchProjectDetailsTool,
        )

    def build_list_projects_tool(self) -> Tool:
        """Build the output of the Jira component"""
        return Tool(
            name="jira_list_projects",
            description="List all Jira projects",
            func=self.list_projects,
        )

    def build_search_issues_tool(self) -> StructuredTool:
        """Build the output of the Jira component"""
        return StructuredTool(
            name="jira_search_issues",
            description="Search for issues in a Jira project",
            func=self.search_issues,
            args_schema=self.SearchIssuesTool,
        )
