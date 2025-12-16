"""Configuration management for SearXNG MCP server."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Configuration for SearXNG MCP server.

    Settings can be configured via environment variables or a .env file.

    Attributes:
        searxng_base_url: Base URL of the SearXNG instance
        searxng_timeout: Request timeout in seconds
        log_level: Logging verbosity level
        max_results_limit: Maximum number of results allowed per query
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    searxng_base_url: str = Field(
        default="http://localhost:8080",
        description="Base URL of the SearXNG instance"
    )

    searxng_timeout: int = Field(
        default=10,
        gt=0,
        description="Request timeout in seconds"
    )

    log_level: str = Field(
        default="INFO",
        description="Logging verbosity level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    max_results_limit: int = Field(
        default=50,
        gt=0,
        le=100,
        description="Maximum number of results allowed per query"
    )


# Global config instance
config = Config()
