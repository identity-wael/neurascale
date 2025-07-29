"""Response serialization middleware."""

from typing import Any, Dict, List, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import json
from pydantic import BaseModel
import numpy as np


class ResponseSerializer:
    """Custom response serializer for complex data types."""

    @staticmethod
    def serialize(data: Any) -> Any:
        """
        Serialize data for JSON response.

        Args:
            data: Data to serialize

        Returns:
            JSON-serializable data
        """
        if isinstance(data, BaseModel):
            return data.dict()
        elif isinstance(data, dict):
            return {k: ResponseSerializer.serialize(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            return [ResponseSerializer.serialize(item) for item in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, date):
            return data.isoformat()
        elif isinstance(data, Decimal):
            return float(data)
        elif isinstance(data, Enum):
            return data.value
        elif isinstance(data, np.ndarray):
            return data.tolist()
        elif isinstance(data, np.generic):
            return data.item()
        elif hasattr(data, "__dict__"):
            # Custom objects
            return ResponseSerializer.serialize(data.__dict__)
        else:
            return data


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for complex types."""

    def default(self, obj):
        """Encode object."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.generic):
            return obj.item()
        elif isinstance(obj, BaseModel):
            return obj.dict()
        elif hasattr(obj, "__dict__"):
            return obj.__dict__

        return super().default(obj)


def create_response_model(
    data: Any,
    message: Optional[str] = None,
    success: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create standardized response model.

    Args:
        data: Response data
        message: Optional message
        success: Success status
        metadata: Optional metadata

    Returns:
        Standardized response
    """
    response = {
        "success": success,
        "data": ResponseSerializer.serialize(data),
    }

    if message:
        response["message"] = message

    if metadata:
        response["metadata"] = metadata

    return response


def create_error_response(
    error: str,
    code: str,
    details: Optional[Any] = None,
    status_code: int = 400,
) -> Dict[str, Any]:
    """
    Create standardized error response.

    Args:
        error: Error message
        code: Error code
        details: Optional error details
        status_code: HTTP status code

    Returns:
        Error response
    """
    response = {
        "success": False,
        "error": {
            "message": error,
            "code": code,
            "status_code": status_code,
        },
    }

    if details:
        response["error"]["details"] = details

    return response
