"""Pagination utilities for REST API."""

from typing import TypeVar, Generic, List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import Query
import math

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = Field(Query(1, ge=1), description="Page number")
    size: int = Field(Query(50, ge=1, le=100), description="Page size")
    cursor: Optional[str] = Field(
        Query(None), description="Cursor for cursor-based pagination"
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None
    _links: Optional[Dict[str, Dict[str, str]]] = None


def paginate(
    items: List[T],
    params: PaginationParams,
    base_url: str,
    total_override: Optional[int] = None,
) -> PaginatedResponse[T]:
    """
    Apply pagination to a list of items.

    Args:
        items: List of items to paginate
        params: Pagination parameters
        base_url: Base URL for HATEOAS links
        total_override: Override total count (for DB queries)

    Returns:
        Paginated response
    """
    total = total_override or len(items)
    pages = math.ceil(total / params.size)

    # Calculate offset
    offset = (params.page - 1) * params.size

    # Slice items
    paginated_items = items[offset : offset + params.size]

    # Create response
    response = PaginatedResponse(
        items=paginated_items,
        total=total,
        page=params.page,
        size=params.size,
        pages=pages,
        has_next=params.page < pages,
        has_prev=params.page > 1,
    )

    # Add HATEOAS links
    links = {"self": {"href": f"{base_url}?page={params.page}&size={params.size}"}}

    if response.has_next:
        links["next"] = {
            "href": f"{base_url}?page={params.page + 1}&size={params.size}"
        }

    if response.has_prev:
        links["prev"] = {
            "href": f"{base_url}?page={params.page - 1}&size={params.size}"
        }

    links["first"] = {"href": f"{base_url}?page=1&size={params.size}"}
    links["last"] = {"href": f"{base_url}?page={pages}&size={params.size}"}

    response._links = links

    return response


class CursorPaginationParams(BaseModel):
    """Cursor-based pagination parameters."""

    cursor: Optional[str] = Field(Query(None), description="Pagination cursor")
    limit: int = Field(Query(50, ge=1, le=100), description="Number of items")
    direction: str = Field(
        Query("next", pattern="^(next|prev)$"), description="Pagination direction"
    )


def cursor_paginate(
    items: List[T],
    params: CursorPaginationParams,
    cursor_field: str,
    base_url: str,
) -> PaginatedResponse[T]:
    """
    Apply cursor-based pagination.

    Args:
        items: List of items to paginate
        params: Cursor pagination parameters
        cursor_field: Field to use for cursor
        base_url: Base URL for links

    Returns:
        Paginated response with cursor
    """
    # Parse cursor
    cursor_value = None
    if params.cursor:
        try:
            cursor_value = decode_cursor(params.cursor)
        except Exception:
            cursor_value = None

    # Filter items based on cursor
    if cursor_value:
        if params.direction == "next":
            filtered_items = [
                item for item in items if getattr(item, cursor_field) > cursor_value
            ]
        else:
            filtered_items = [
                item for item in items if getattr(item, cursor_field) < cursor_value
            ]
            filtered_items.reverse()
    else:
        filtered_items = items

    # Limit items
    has_more = len(filtered_items) > params.limit
    paginated_items = filtered_items[: params.limit]

    # Generate cursors
    next_cursor = None
    prev_cursor = None

    if paginated_items:
        if has_more or params.direction == "prev":
            last_item = paginated_items[-1]
            next_cursor = encode_cursor(getattr(last_item, cursor_field))

        if params.cursor or params.direction == "next":
            first_item = paginated_items[0]
            prev_cursor = encode_cursor(getattr(first_item, cursor_field))

    # Create response
    response = PaginatedResponse(
        items=paginated_items,
        total=len(items),  # Note: Total might not be accurate with cursor pagination
        page=1,  # Not applicable for cursor pagination
        size=params.limit,
        pages=1,  # Not applicable for cursor pagination
        has_next=bool(next_cursor),
        has_prev=bool(prev_cursor),
        next_cursor=next_cursor,
        prev_cursor=prev_cursor,
    )

    # Add HATEOAS links
    links = {"self": {"href": f"{base_url}?limit={params.limit}"}}

    if next_cursor:
        links["next"] = {
            "href": f"{base_url}?cursor={next_cursor}&limit={params.limit}"
        }

    if prev_cursor:
        links["prev"] = {
            "href": f"{base_url}?cursor={prev_cursor}&limit={params.limit}&direction=prev"
        }

    response._links = links

    return response


def encode_cursor(value: Any) -> str:
    """Encode cursor value."""
    import base64
    import json

    return base64.b64encode(json.dumps(value).encode()).decode()


def decode_cursor(cursor: str) -> Any:
    """Decode cursor value."""
    import base64
    import json

    return json.loads(base64.b64decode(cursor.encode()).decode())
