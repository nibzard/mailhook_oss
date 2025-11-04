"""Pagination utilities for API responses."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response.

    Used for all list endpoints that support pagination.
    """

    items: list[T] = Field(description="List of items")
    next: str | None = Field(
        default=None,
        description="Cursor for next page",
    )
    prev: str | None = Field(
        default=None,
        description="Cursor for previous page",
    )

    class Config:
        """Pydantic configuration."""

        from_attributes = True


def create_paginated_response(
    items: list[T],
    next_cursor: str | None,
    prev_cursor: str | None,
) -> PaginatedResponse[T]:
    """Create a paginated response.

    Args:
        items: List of items
        next_cursor: Next page cursor
        prev_cursor: Previous page cursor

    Returns:
        Paginated response
    """
    return PaginatedResponse(
        items=items,
        next=next_cursor,
        prev=prev_cursor,
    )
