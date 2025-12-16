"""Entry point for the SearXNG MCP server."""

import asyncio
import logging

from .config import Config
from .server import create_server


def main() -> None:
    """Run the SearXNG MCP server."""
    # Load configuration
    config = Config()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run the server
    asyncio.run(run_server(config))


async def run_server(config: Config) -> None:
    """Run the MCP server.

    Args:
        config: Configuration object
    """
    server = await create_server(config)
    await server.run()


if __name__ == "__main__":
    main()
