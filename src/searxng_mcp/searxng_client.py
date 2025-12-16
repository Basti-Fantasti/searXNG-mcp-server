"""HTTP client for SearXNG API interaction."""

import logging
from typing import Optional

import httpx

from .config import Config
from .models import SearchResult, SearchResults

logger = logging.getLogger(__name__)


class SearXNGClientError(Exception):
    """Base exception for SearXNG client errors."""
    pass


class SearXNGConnectionError(SearXNGClientError):
    """Raised when unable to connect to SearXNG instance."""
    pass


class SearXNGTimeoutError(SearXNGClientError):
    """Raised when SearXNG request times out."""
    pass


class SearXNGResponseError(SearXNGClientError):
    """Raised when SearXNG returns invalid or malformed response."""
    pass


class SearXNGClient:
    """Async HTTP client for interacting with SearXNG API.

    Attributes:
        base_url: Base URL of the SearXNG instance
        timeout: Request timeout in seconds
        client: httpx AsyncClient instance
    """

    def __init__(self, config: Config):
        """Initialize SearXNG client.

        Args:
            config: Configuration object with SearXNG settings
        """
        self.base_url = config.searxng_base_url.rstrip("/")
        self.timeout = config.searxng_timeout
        self.max_results_limit = config.max_results_limit
        # Add headers that SearXNG might expect
        headers = {
            "User-Agent": "searxng-mcp-server/1.0",
            "Accept": "application/json",
        }
        self.client = httpx.AsyncClient(timeout=self.timeout, headers=headers)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def health_check(self) -> bool:
        """Check if SearXNG instance is reachable and healthy.

        Returns:
            True if SearXNG is reachable, False otherwise

        Raises:
            SearXNGConnectionError: If unable to connect to SearXNG
            SearXNGTimeoutError: If request times out
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/search",
                params={"q": "test", "format": "json"}
            )
            response.raise_for_status()
            logger.debug("SearXNG health check successful")
            return True
        except httpx.TimeoutException as e:
            logger.error(f"SearXNG health check timed out: {e}")
            raise SearXNGTimeoutError(
                f"SearXNG health check timed out after {self.timeout}s"
            ) from e
        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to SearXNG at {self.base_url}: {e}")
            raise SearXNGConnectionError(
                f"Unable to connect to SearXNG at {self.base_url}. "
                "Please ensure SearXNG is running."
            ) from e
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during health check: {e}")
            raise SearXNGConnectionError(
                f"HTTP error while connecting to SearXNG: {e}"
            ) from e

    async def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        categories: Optional[list[str]] = None,
        language: Optional[str] = None,
        time_range: Optional[str] = None,
    ) -> SearchResults:
        """Perform a search query against SearXNG.

        Args:
            query: Search query string
            max_results: Maximum number of results to return (optional)
            categories: List of SearXNG categories to search (e.g., ["general", "news"])
            language: ISO 639-1 language code (e.g., "en", "de")
            time_range: Time range filter (e.g., "day", "week", "month", "year")

        Returns:
            SearchResults object containing the search results

        Raises:
            ValueError: If max_results exceeds the configured limit
            SearXNGConnectionError: If unable to connect to SearXNG
            SearXNGTimeoutError: If request times out
            SearXNGResponseError: If response is malformed or invalid
        """
        # Validate max_results against configured limit
        if max_results is not None and max_results > self.max_results_limit:
            raise ValueError(
                f"max_results ({max_results}) exceeds the configured limit of {self.max_results_limit}"
            )

        # Build query parameters
        params = {
            "q": query,
            "format": "json",
        }

        if categories:
            params["categories"] = ",".join(categories)

        if language:
            params["language"] = language

        if time_range:
            params["time_range"] = time_range

        logger.debug(f"Searching SearXNG with query: {query}, params: {params}")

        try:
            response = await self.client.get(
                f"{self.base_url}/search",
                params=params
            )
            response.raise_for_status()
        except httpx.TimeoutException as e:
            logger.error(f"SearXNG search timed out for query '{query}': {e}")
            raise SearXNGTimeoutError(
                f"Search request timed out after {self.timeout}s"
            ) from e
        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to SearXNG at {self.base_url}: {e}")
            raise SearXNGConnectionError(
                f"Unable to connect to SearXNG at {self.base_url}. "
                "Please ensure SearXNG is running."
            ) from e
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during search: {e}")
            raise SearXNGConnectionError(
                f"HTTP error while searching: {e}"
            ) from e

        # Parse JSON response
        try:
            data = response.json()
        except Exception as e:
            logger.error(f"Failed to parse SearXNG response as JSON: {e}")
            raise SearXNGResponseError(
                "SearXNG returned malformed JSON response"
            ) from e

        # Validate required fields
        if "query" not in data:
            logger.error("SearXNG response missing 'query' field")
            raise SearXNGResponseError("Invalid SearXNG response: missing 'query' field")

        if "results" not in data:
            logger.error("SearXNG response missing 'results' field")
            raise SearXNGResponseError("Invalid SearXNG response: missing 'results' field")

        # Parse results
        try:
            results = []
            for result_data in data["results"]:
                # Skip results missing required fields
                if not all(k in result_data for k in ["title", "url", "content"]):
                    logger.warning(f"Skipping result with missing required fields: {result_data}")
                    continue

                result = SearchResult(
                    title=result_data["title"],
                    url=result_data["url"],
                    content=result_data["content"],
                    publishedDate=result_data.get("publishedDate"),
                    engines=result_data.get("engines", [])
                )
                results.append(result)

            # Limit results if max_results is specified
            if max_results is not None and max_results > 0:
                results = results[:max_results]

            search_results = SearchResults(
                query=data["query"],
                results=results,
                number_of_results=len(results)
            )

            logger.info(f"Successfully retrieved {len(results)} results for query '{query}'")
            return search_results

        except Exception as e:
            logger.error(f"Failed to parse SearXNG results into models: {e}")
            raise SearXNGResponseError(
                f"Failed to parse SearXNG response: {e}"
            ) from e
