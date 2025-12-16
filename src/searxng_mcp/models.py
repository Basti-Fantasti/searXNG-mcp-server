"""Pydantic models for SearXNG API responses."""

from typing import Optional

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """A single search result from SearXNG.

    Attributes:
        title: The title of the search result
        url: The URL of the search result
        content: Description/snippet of the search result
        publishedDate: Optional publication date of the result
        engines: List of search engines that returned this result
    """

    title: str = Field(..., description="Title of the search result")
    url: str = Field(..., description="URL of the search result")
    content: str = Field(..., description="Description/snippet of the search result")
    publishedDate: Optional[str] = Field(
        None,
        description="Publication date of the result (may be None)"
    )
    engines: list[str] = Field(
        default_factory=list,
        description="List of search engines that returned this result"
    )


class SearchResults(BaseModel):
    """Collection of search results from SearXNG.

    Attributes:
        query: The original search query
        results: List of search results
        number_of_results: Total number of results returned
    """

    query: str = Field(..., description="The original search query")
    results: list[SearchResult] = Field(
        default_factory=list,
        description="List of search results"
    )
    number_of_results: int = Field(
        ...,
        ge=0,
        description="Total number of results returned"
    )
