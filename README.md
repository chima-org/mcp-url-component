# MCP Client Integration with Langflow

This repository provides integration between MCP (Model Context Protocol) servers and Langflow.

## Features

### MCP Client
- Asynchronous client for connecting to MCP servers
- Support for Server-Sent Events (SSE) transport
- Tool discovery and invocation capabilities
- Error handling and connection management
- Clean async context manager implementation

### URLComponent for Langflow
- Custom Langflow component for URL content fetching
- Rate-limited URL content retrieval (150,000 characters per request)
- Integration with MCP's fetch tool
- Pydantic schema validation
- Both direct output and tool-based interfaces
