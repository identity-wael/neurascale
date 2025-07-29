"""Request validation middleware."""

from typing import Dict, Callable
from pydantic import ValidationError
from fastapi import Request, HTTPException
import logging

logger = logging.getLogger(__name__)


class RequestValidator:
    """Request validation middleware."""

    def __init__(self):
        """Initialize validator."""
        self.validators: Dict[str, Callable] = {}

    def register_validator(self, path: str, validator: Callable) -> None:
        """Register a validator for a path."""
        self.validators[path] = validator

    async def validate_request(self, request: Request) -> None:
        """Validate request based on path."""
        path = request.url.path

        # Find matching validator
        validator = self.validators.get(path)
        if not validator:
            # Try pattern matching
            for pattern, val_func in self.validators.items():
                if self._match_pattern(path, pattern):
                    validator = val_func
                    break

        if validator:
            try:
                await validator(request)
            except ValidationError as e:
                raise HTTPException(
                    status_code=422,
                    detail={"error": "Validation failed", "details": e.errors()},
                )
            except Exception as e:
                logger.error(f"Validation error: {e}")
                raise HTTPException(
                    status_code=400,
                    detail={"error": "Invalid request"},
                )

    def _match_pattern(self, path: str, pattern: str) -> bool:
        """Match path against pattern with wildcards."""
        # Simple pattern matching with * wildcard
        pattern_parts = pattern.split("/")
        path_parts = path.split("/")

        if len(pattern_parts) != len(path_parts):
            return False

        for pattern_part, path_part in zip(pattern_parts, path_parts):
            if pattern_part == "*":
                continue
            if pattern_part != path_part:
                return False

        return True


# Common validators
async def validate_json_content_type(request: Request) -> None:
    """Validate JSON content type."""
    content_type = request.headers.get("content-type", "")
    if request.method in ["POST", "PUT", "PATCH"] and not content_type.startswith(
        "application/json"
    ):
        raise HTTPException(
            status_code=415,
            detail="Content-Type must be application/json",
        )


async def validate_pagination_params(request: Request) -> None:
    """Validate pagination parameters."""
    params = request.query_params

    # Validate page
    page = params.get("page")
    if page is not None:
        try:
            page_num = int(page)
            if page_num < 1:
                raise ValueError("Page must be >= 1")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid page parameter",
            )

    # Validate size
    size = params.get("size")
    if size is not None:
        try:
            size_num = int(size)
            if size_num < 1 or size_num > 100:
                raise ValueError("Size must be between 1 and 100")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid size parameter",
            )


async def validate_date_range(request: Request) -> None:
    """Validate date range parameters."""
    params = request.query_params
    start_date = params.get("start_date")
    end_date = params.get("end_date")

    if start_date and end_date:
        # Validate date format and order
        try:
            from datetime import datetime

            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)

            if start > end:
                raise HTTPException(
                    status_code=400,
                    detail="start_date must be before end_date",
                )
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use ISO format (YYYY-MM-DD)",
            )
