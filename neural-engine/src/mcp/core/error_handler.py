"""Error handling for MCP servers."""

import logging
import traceback
from typing import Dict, Any, Optional
from datetime import datetime


class MCPErrorHandler:
    """Handles errors and creates standardized error responses for MCP servers."""

    def __init__(self):
        """Initialize error handler."""
        self.logger = logging.getLogger(__name__)

        # Standard MCP error codes
        self.error_codes = {
            # Standard JSON-RPC errors
            "parse_error": -32700,
            "invalid_request": -32600,
            "method_not_found": -32601,
            "invalid_params": -32602,
            "internal_error": -32603,
            # MCP-specific errors
            "unauthorized": -32000,
            "forbidden": -32001,
            "rate_limit_exceeded": -32002,
            "tool_not_found": -32003,
            "resource_not_found": -32004,
            "execution_error": -32005,
            "validation_error": -32006,
            "connection_error": -32007,
            "timeout_error": -32008,
            "not_implemented": -32009,
        }

    def create_error_response(
        self,
        error_type: str,
        message: str,
        request_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create standardized error response.

        Args:
            error_type: Type of error (must be in error_codes)
            message: Human-readable error message
            request_id: Optional request identifier
            data: Optional additional error data

        Returns:
            Standardized error response
        """
        error_code = self.error_codes.get(
            error_type, -32603
        )  # Default to internal_error

        error_response = {
            "jsonrpc": "2.0",
            "error": {
                "code": error_code,
                "message": message,
                "type": error_type,
                "timestamp": datetime.utcnow().isoformat(),
            },
        }

        if request_id is not None:
            error_response["id"] = request_id

        if data:
            error_response["error"]["data"] = data

        # Log the error
        self.logger.error(
            f"MCP Error [{error_type}]: {message}",
            extra={
                "error_code": error_code,
                "error_type": error_type,
                "request_id": request_id,
                "error_data": data,
            },
        )

        return error_response

    def handle_exception(
        self,
        exception: Exception,
        request_id: Optional[str] = None,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Handle unexpected exceptions and create appropriate error responses.

        Args:
            exception: The exception that occurred
            request_id: Optional request identifier
            context: Optional context information

        Returns:
            Error response based on exception type
        """
        # Log the full exception with traceback
        self.logger.exception(
            f"Unhandled exception in MCP server: {exception}",
            extra={
                "exception_type": type(exception).__name__,
                "request_id": request_id,
                "context": context,
            },
        )

        # Map specific exception types to MCP error types
        if isinstance(exception, PermissionError):
            return self.create_error_response(
                "forbidden",
                str(exception),
                request_id,
                {"exception_type": type(exception).__name__},
            )

        elif isinstance(exception, ValueError):
            return self.create_error_response(
                "validation_error",
                str(exception),
                request_id,
                {"exception_type": type(exception).__name__},
            )

        elif isinstance(exception, KeyError):
            return self.create_error_response(
                "invalid_params",
                f"Missing required parameter: {str(exception)}",
                request_id,
                {"exception_type": type(exception).__name__},
            )

        elif isinstance(exception, TimeoutError):
            return self.create_error_response(
                "timeout_error",
                str(exception),
                request_id,
                {"exception_type": type(exception).__name__},
            )

        elif isinstance(exception, ConnectionError):
            return self.create_error_response(
                "connection_error",
                str(exception),
                request_id,
                {"exception_type": type(exception).__name__},
            )

        elif isinstance(exception, NotImplementedError):
            return self.create_error_response(
                "not_implemented",
                str(exception),
                request_id,
                {"exception_type": type(exception).__name__},
            )

        else:
            # Generic internal error
            return self.create_error_response(
                "internal_error",
                f"An unexpected error occurred: {str(exception)}",
                request_id,
                {
                    "exception_type": type(exception).__name__,
                    "traceback": (
                        traceback.format_exc()
                        if self.logger.isEnabledFor(logging.DEBUG)
                        else None
                    ),
                },
            )

    def create_validation_error(
        self, field: str, message: str, request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create validation error for specific field.

        Args:
            field: Field name that failed validation
            message: Validation error message
            request_id: Optional request identifier

        Returns:
            Validation error response
        """
        return self.create_error_response(
            "validation_error",
            f"Validation failed for field '{field}': {message}",
            request_id,
            {"field": field, "validation_message": message},
        )

    def create_permission_error(
        self,
        permission: str,
        resource: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create permission error.

        Args:
            permission: Required permission
            resource: Optional resource identifier
            request_id: Optional request identifier

        Returns:
            Permission error response
        """
        message = f"Permission denied: requires '{permission}'"
        if resource:
            message += f" for resource '{resource}'"

        return self.create_error_response(
            "forbidden",
            message,
            request_id,
            {"required_permission": permission, "resource": resource},
        )

    def create_rate_limit_error(
        self,
        limit_type: str,
        reset_time: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create rate limit error.

        Args:
            limit_type: Type of rate limit exceeded
            reset_time: When the limit resets
            request_id: Optional request identifier

        Returns:
            Rate limit error response
        """
        message = f"Rate limit exceeded: {limit_type}"
        data = {"limit_type": limit_type}

        if reset_time:
            message += f". Resets at {reset_time}"
            data["reset_time"] = reset_time

        return self.create_error_response(
            "rate_limit_exceeded", message, request_id, data
        )

    def create_tool_error(
        self, tool_name: str, error_message: str, request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create tool execution error.

        Args:
            tool_name: Name of the tool that failed
            error_message: Error message from tool execution
            request_id: Optional request identifier

        Returns:
            Tool execution error response
        """
        return self.create_error_response(
            "execution_error",
            f"Tool '{tool_name}' failed: {error_message}",
            request_id,
            {"tool_name": tool_name, "tool_error": error_message},
        )

    def create_resource_error(
        self, resource_uri: str, error_message: str, request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create resource access error.

        Args:
            resource_uri: URI of the resource that failed
            error_message: Error message from resource access
            request_id: Optional request identifier

        Returns:
            Resource error response
        """
        return self.create_error_response(
            "resource_not_found",
            f"Resource '{resource_uri}' error: {error_message}",
            request_id,
            {"resource_uri": resource_uri, "resource_error": error_message},
        )

    def is_client_error(self, error_code: int) -> bool:
        """Check if error code represents a client error.

        Args:
            error_code: Error code to check

        Returns:
            True if client error (4xx equivalent)
        """
        # Client errors are typically -32600 to -32099
        return -32099 <= error_code <= -32600

    def is_server_error(self, error_code: int) -> bool:
        """Check if error code represents a server error.

        Args:
            error_code: Error code to check

        Returns:
            True if server error (5xx equivalent)
        """
        # Server errors are typically -32000 to -32099 and -32603
        return error_code == -32603 or (-32099 <= error_code <= -32000)

    def should_retry(self, error_code: int) -> bool:
        """Determine if an error is retryable.

        Args:
            error_code: Error code to check

        Returns:
            True if error is potentially retryable
        """
        retryable_errors = [
            self.error_codes["timeout_error"],
            self.error_codes["connection_error"],
            self.error_codes["internal_error"],
            self.error_codes["rate_limit_exceeded"],
        ]

        return error_code in retryable_errors

    def get_retry_delay(self, error_code: int, attempt: int = 1) -> float:
        """Get suggested retry delay for an error.

        Args:
            error_code: Error code
            attempt: Retry attempt number

        Returns:
            Suggested delay in seconds
        """
        if error_code == self.error_codes["rate_limit_exceeded"]:
            # Exponential backoff for rate limits, starting at 1 second
            return min(60, 1 * (2 ** (attempt - 1)))

        elif error_code == self.error_codes["timeout_error"]:
            # Linear increase for timeouts
            return min(30, 5 * attempt)

        elif error_code == self.error_codes["connection_error"]:
            # Quick retry for connection errors
            return min(10, 1 + attempt)

        else:
            # Default exponential backoff
            return min(30, 2 ** (attempt - 1))
