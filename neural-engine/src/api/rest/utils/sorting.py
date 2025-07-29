"""Sorting utilities for REST API."""

from typing import TypeVar, List, Optional, Callable, Any
from pydantic import BaseModel, Field
from fastapi import Query
import operator

T = TypeVar("T")


class SortParams(BaseModel):
    """Sort parameters."""

    sort_by: Optional[str] = Field(Query(None), description="Field to sort by")
    sort_order: str = Field(
        Query("asc", pattern="^(asc|desc)$"), description="Sort order"
    )


def apply_sorting(
    items: List[T],
    sort_params: SortParams,
    allowed_fields: Optional[List[str]] = None,
    custom_sorts: Optional[dict[str, Callable[[T], Any]]] = None,
) -> List[T]:
    """
    Apply sorting to a list of items.

    Args:
        items: List of items to sort
        sort_params: Sort parameters
        allowed_fields: List of allowed sort fields
        custom_sorts: Dictionary of custom sort functions

    Returns:
        Sorted list of items
    """
    if not sort_params.sort_by:
        return items

    # Check if field is allowed
    if allowed_fields and sort_params.sort_by not in allowed_fields:
        # Silently ignore invalid sort fields
        return items

    # Use custom sort function if available
    if custom_sorts and sort_params.sort_by in custom_sorts:
        key_func = custom_sorts[sort_params.sort_by]
    else:
        # Default to attribute getter
        key_func = operator.attrgetter(sort_params.sort_by)

    try:
        sorted_items = sorted(
            items,
            key=key_func,
            reverse=(sort_params.sort_order == "desc"),
        )
        return sorted_items
    except (AttributeError, TypeError):
        # If sorting fails, return original list
        return items


def create_multi_field_sort(*fields: str) -> Callable[[T], tuple]:
    """
    Create a sort function for multiple fields.

    Args:
        fields: Field names in order of priority

    Returns:
        Sort key function
    """

    def sort_key(item: T) -> tuple:
        return tuple(getattr(item, field, None) for field in fields)

    return sort_key


def create_nested_sort(path: str) -> Callable[[T], Any]:
    """
    Create a sort function for nested fields.

    Args:
        path: Dot-separated path to the nested field

    Returns:
        Sort key function
    """

    def sort_key(item: T) -> Any:
        current = item
        for part in path.split("."):
            current = getattr(current, part, None)
            if current is None:
                return None
        return current

    return sort_key


def create_custom_order_sort(field: str, custom_order: List[Any]) -> Callable[[T], int]:
    """
    Create a sort function with custom ordering.

    Args:
        field: Field name to sort by
        custom_order: List defining the custom order

    Returns:
        Sort key function
    """

    def sort_key(item: T) -> int:
        value = getattr(item, field, None)
        try:
            return custom_order.index(value)
        except ValueError:
            # Put unknown values at the end
            return len(custom_order)

    return sort_key


def create_null_last_sort(field: str) -> Callable[[T], tuple]:
    """
    Create a sort function that puts null values last.

    Args:
        field: Field name to sort by

    Returns:
        Sort key function
    """

    def sort_key(item: T) -> tuple:
        value = getattr(item, field, None)
        return (value is None, value)

    return sort_key


class SortBuilder:
    """Builder for complex sort operations."""

    def __init__(self):
        self.sorts: List[tuple[str, bool]] = []

    def add_field(self, field: str, descending: bool = False) -> "SortBuilder":
        """Add a field to sort by."""
        self.sorts.append((field, descending))
        return self

    def add_custom(
        self, key_func: Callable[[T], Any], descending: bool = False
    ) -> "SortBuilder":
        """Add a custom sort function."""
        self.sorts.append((key_func, descending))  # type: ignore
        return self

    def build(self) -> Callable[[List[T]], List[T]]:
        """Build the sort function."""

        def sort_function(items: List[T]) -> List[T]:
            # Apply sorts in reverse order (last added is primary sort)
            sorted_items = items
            for sort_spec in reversed(self.sorts):
                field_or_func, descending = sort_spec
                if isinstance(field_or_func, str):
                    key_func = operator.attrgetter(field_or_func)
                else:
                    key_func = field_or_func

                sorted_items = sorted(sorted_items, key=key_func, reverse=descending)

            return sorted_items

        return sort_function
