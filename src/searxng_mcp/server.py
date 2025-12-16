"""MCP server implementation for SearXNG web search."""

import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .config import Config
from .searxng_client import (
    SearXNGClient,
    SearXNGClientError,
    SearXNGConnectionError,
    SearXNGTimeoutError,
    SearXNGResponseError,
)

logger = logging.getLogger(__name__)


class SearXNGMCPServer:
    """MCP server for SearXNG web search.

    Provides web_search tool that interfaces with a local SearXNG instance
    for privacy-focused web search capabilities.
    """

    def __init__(self, config: Config):
        """Initialize the MCP server.

        Args:
            config: Configuration object with SearXNG settings
        """
        self.config = config
        self.server = Server("searxng-mcp")
        self.client: SearXNGClient | None = None

        # Register tool handlers
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register MCP tool handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="web_search",
                    description=(
                        "Search the web using SearXNG, a privacy-focused metasearch engine. "
                        "Returns relevant search results including titles, URLs, and content snippets. "
                        "Supports filtering by language, categories, and time range."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to execute",
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results to return (default: 10)",
                                "default": 10,
                                "minimum": 1,
                                "maximum": self.config.max_results_limit,
                            },
                            "categories": {
                                "type": "array",
                                "description": "SearXNG categories to search (e.g., general, news, images, videos, files, science)",
                                "items": {"type": "string"},
                            },
                            "language": {
                                "type": "string",
                                "description": "ISO 639-1 language code (e.g., 'en', 'de', 'fr')",
                            },
                            "time_range": {
                                "type": "string",
                                "description": "Filter results by time range",
                                "enum": ["day", "week", "month", "year"],
                            },
                        },
                        "required": ["query"],
                    },
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Handle tool calls."""
            if name != "web_search":
                raise ValueError(f"Unknown tool: {name}")

            return await self._handle_web_search(arguments)

    async def _handle_web_search(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle web_search tool calls.

        Args:
            arguments: Tool arguments including query, max_results, etc.

        Returns:
            List of TextContent with search results

        Raises:
            ValueError: If arguments are invalid
        """
        # Extract and validate arguments
        query = arguments.get("query")
        if not query:
            raise ValueError("'query' parameter is required")

        max_results = arguments.get("max_results", 10)
        categories = arguments.get("categories")
        language = arguments.get("language")
        time_range = arguments.get("time_range")

        # Validate max_results
        if not isinstance(max_results, int) or max_results < 1:
            raise ValueError("'max_results' must be a positive integer")

        if max_results > self.config.max_results_limit:
            raise ValueError(
                f"'max_results' exceeds limit of {self.config.max_results_limit}"
            )

        logger.info(f"Processing web search: query='{query}', max_results={max_results}")

        # Initialize client if needed
        if self.client is None:
            self.client = SearXNGClient(self.config)

        try:
            # Perform search
            results = await self.client.search(
                query=query,
                max_results=max_results,
                categories=categories,
                language=language,
                time_range=time_range,
            )

            # Format results
            formatted_results = self._format_search_results(results)

            return [
                TextContent(
                    type="text",
                    text=formatted_results,
                )
            ]

        except SearXNGConnectionError as e:
            error_msg = (
                f"Failed to connect to SearXNG: {e}\n\n"
                f"Please ensure SearXNG is running at {self.config.searxng_base_url}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg) from e

        except SearXNGTimeoutError as e:
            error_msg = f"Search request timed out: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e

        except SearXNGResponseError as e:
            error_msg = f"Invalid response from SearXNG: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e

        except SearXNGClientError as e:
            error_msg = f"SearXNG client error: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error during search: {e}"
            logger.exception(error_msg)
            raise ValueError(error_msg) from e

    def _format_search_results(self, results: Any) -> str:
        """Format search results as readable text.

        Args:
            results: SearchResults object from SearXNGClient

        Returns:
            Formatted string with search results
        """
        if not results.results:
            return f"No results found for query: {results.query}"

        lines = [
            f"Search results for: {results.query}",
            f"Found {results.number_of_results} results\n",
        ]

        for i, result in enumerate(results.results, 1):
            lines.append(f"{i}. {result.title}")
            lines.append(f"   URL: {result.url}")

            if result.content:
                # Truncate very long content
                content = result.content[:300]
                if len(result.content) > 300:
                    content += "..."
                lines.append(f"   {content}")

            if result.publishedDate:
                lines.append(f"   Published: {result.publishedDate}")

            if result.engines:
                lines.append(f"   Sources: {', '.join(result.engines)}")

            lines.append("")  # Empty line between results

        return "\n".join(lines)

    async def run(self) -> None:
        """Run the MCP server with stdio transport."""
        try:
            logger.info("Starting SearXNG MCP server")
            logger.info(f"SearXNG URL: {self.config.searxng_base_url}")
            logger.info(f"Max results limit: {self.config.max_results_limit}")

            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options(),
                )
        finally:
            # Clean up client connection
            if self.client:
                await self.client.close()
                logger.info("Closed SearXNG client connection")


async def create_server(config: Config | None = None) -> SearXNGMCPServer:
    """Create and return a SearXNG MCP server instance.

    Args:
        config: Optional configuration object. If None, uses default config.

    Returns:
        Configured SearXNGMCPServer instance
    """
    if config is None:
        config = Config()

    return SearXNGMCPServer(config)
