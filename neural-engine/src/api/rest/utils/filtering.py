"""Filtering utilities for REST API."""

from typing import TypeVar, List, Dict, Any, Optional, Callable
from pydantic import BaseModel, Field
from fastapi import Query
from datetime import datetime

T = TypeVar("T")


class FilterParams(BaseModel):
    """Base filter parameters."""

    search: Optional[str] = Field(Query(None), description="Search text")
    sort_by: Optional[str] = Field(Query(None), description="Sort field")
    sort_order: str = Field(
        Query("asc", pattern="^(asc|desc)$"), description="Sort order"
    )


def apply_filters(
    items: List[T],
    filters: Dict[str, Any],
    filter_functions: Dict[str, Callable[[T, Any], bool]],
) -> List[T]:
    """
    Apply filters to a list of items.

    Args:
        items: List of items to filter
        filters: Dictionary of filter values
        filter_functions: Dictionary of filter functions

    Returns:
        Filtered list of items
    """
    filtered_items = items

    for filter_name, filter_value in filters.items():
        if filter_value is not None and filter_name in filter_functions:
            filter_func = filter_functions[filter_name]
            filtered_items = [
                item for item in filtered_items if filter_func(item, filter_value)
            ]

    return filtered_items


def create_text_filter(field_names: List[str]) -> Callable[[T, str], bool]:
    """
    Create a text search filter for multiple fields.

    Args:
        field_names: List of field names to search in

    Returns:
        Filter function
    """

    def text_filter(item: T, search_text: str) -> bool:
        search_lower = search_text.lower()
        for field_name in field_names:
            value = getattr(item, field_name, None)
            if value and search_lower in str(value).lower():
                return True
        return False

    return text_filter


def create_exact_filter(field_name: str) -> Callable[[T, Any], bool]:
    """
    Create an exact match filter.

    Args:
        field_name: Field name to match

    Returns:
        Filter function
    """

    def exact_filter(item: T, value: Any) -> bool:
        return getattr(item, field_name, None) == value

    return exact_filter


def create_range_filter(
    field_name: str, min_value: Optional[Any] = None, max_value: Optional[Any] = None
) -> Callable[[T, Any], bool]:
    """
    Create a range filter.

    Args:
        field_name: Field name to check
        min_value: Minimum value (inclusive)
        max_value: Maximum value (inclusive)

    Returns:
        Filter function
    """

    def range_filter(item: T, value: Any) -> bool:
        item_value = getattr(item, field_name, None)
        if item_value is None:
            return False

        if min_value is not None and item_value < min_value:
            return False

        if max_value is not None and item_value > max_value:
            return False

        return True

    return range_filter


def create_date_range_filter(
    field_name: str,
) -> Callable[[T, Dict[str, datetime]], bool]:
    """
    Create a date range filter.

    Args:
        field_name: Field name containing the date

    Returns:
        Filter function
    """

    def date_filter(item: T, date_range: Dict[str, datetime]) -> bool:
        item_date = getattr(item, field_name, None)
        if not isinstance(item_date, datetime):
            return False

        start_date = date_range.get("start")
        end_date = date_range.get("end")

        if start_date and item_date < start_date:
            return False

        if end_date and item_date > end_date:
            return False

        return True

    return date_filter


def create_list_contains_filter(field_name: str) -> Callable[[T, Any], bool]:
    """
    Create a filter that checks if a list field contains a value.

    Args:
        field_name: Field name containing the list

    Returns:
        Filter function
    """

    def list_filter(item: T, value: Any) -> bool:
        item_list = getattr(item, field_name, None)
        if not isinstance(item_list, list):
            return False
        return value in item_list

    return list_filter


def create_nested_filter(
    path: str, condition: Callable[[Any], bool]
) -> Callable[[T, Any], bool]:
    """
    Create a filter for nested fields.

    Args:
        path: Dot-separated path to the nested field
        condition: Condition function to apply

    Returns:
        Filter function
    """

    def nested_filter(item: T, value: Any) -> bool:
        current = item
        for part in path.split("."):
            current = getattr(current, part, None)
            if current is None:
                return False
        return condition(current)

    return nested_filter
