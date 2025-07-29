"""MCP-specific logging utilities."""

import logging
from typing import Any, Dict, Optional
from datetime import datetime


class MCPLogger:
    """Specialized logger for MCP server operations."""

    def __init__(self, server_name: str):
        """Initialize MCP logger.

        Args:
            server_name: Name of the MCP server
        """
        self.server_name = server_name
        self.logger = logging.getLogger(f"mcp.{server_name}")

        # Configure logger if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def info(self, message: str, **kwargs) -> None:
        """Log info message.

        Args:
            message: Log message
            **kwargs: Additional context
        """
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message.

        Args:
            message: Log message
            **kwargs: Additional context
        """
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log error message.

        Args:
            message: Log message
            **kwargs: Additional context
        """
        self.logger.error(message, extra=kwargs)

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message.

        Args:
            message: Log message
            **kwargs: Additional context
        """
        self.logger.debug(message, extra=kwargs)

    def log_request(self, client_id: str, method: str, params: Dict[str, Any]) -> None:
        """Log incoming MCP request.

        Args:
            client_id: Client identifier
            method: MCP method
            params: Request parameters
        """
        # Sanitize sensitive parameters
        safe_params = self._sanitize_params(params)

        self.logger.info(
            f"MCP Request: {method}",
            extra={
                "event_type": "mcp_request",
                "client_id": client_id,
                "method": method,
                "params": safe_params,
                "server": self.server_name,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    def log_response(self, client_id: str, response: Dict[str, Any]) -> None:
        """Log MCP response.

        Args:
            client_id: Client identifier
            response: Response data
        """
        # Extract key information
        is_error = "error" in response
        response_type = "error" if is_error else "success"

        # Sanitize response data
        safe_response = self._sanitize_response(response)

        log_level = logging.ERROR if is_error else logging.INFO

        self.logger.log(
            log_level,
            f"MCP Response: {response_type}",
            extra={
                "event_type": "mcp_response",
                "client_id": client_id,
                "response_type": response_type,
                "response": safe_response,
                "server": self.server_name,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    def log_tool_execution(
        self,
        client_id: str,
        tool_name: str,
        execution_time: float,
        success: bool,
        error: Optional[str] = None,
    ) -> None:
        """Log tool execution.

        Args:
            client_id: Client identifier
            tool_name: Name of executed tool
            execution_time: Execution time in seconds
            success: Whether execution was successful
            error: Error message if failed
        """
        log_level = logging.INFO if success else logging.ERROR

        self.logger.log(
            log_level,
            f"Tool executed: {tool_name} ({'success' if success else 'failed'})",
            extra={
                "event_type": "tool_execution",
                "client_id": client_id,
                "tool_name": tool_name,
                "execution_time": execution_time,
                "success": success,
                "error": error,
                "server": self.server_name,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    def log_authentication(
        self,
        client_id: str,
        auth_method: str,
        success: bool,
        user_id: Optional[str] = None,
        failure_reason: Optional[str] = None,
    ) -> None:
        """Log authentication attempt.

        Args:
            client_id: Client identifier
            auth_method: Authentication method used
            success: Whether authentication was successful
            user_id: User ID if successful
            failure_reason: Reason for failure if failed
        """
        log_level = logging.INFO if success else logging.WARNING

        self.logger.log(
            log_level,
            f"Authentication {'successful' if success else 'failed'}: {auth_method}",
            extra={
                "event_type": "authentication",
                "client_id": client_id,
                "auth_method": auth_method,
                "success": success,
                "user_id": user_id,
                "failure_reason": failure_reason,
                "server": self.server_name,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    def log_rate_limit(
        self, client_id: str, limit_type: str, current_usage: int, limit: int
    ) -> None:
        """Log rate limit hit.

        Args:
            client_id: Client identifier
            limit_type: Type of rate limit
            current_usage: Current usage count
            limit: Rate limit threshold
        """
        self.logger.warning(
            f"Rate limit exceeded: {limit_type}",
            extra={
                "event_type": "rate_limit",
                "client_id": client_id,
                "limit_type": limit_type,
                "current_usage": current_usage,
                "limit": limit,
                "server": self.server_name,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    def log_connection(
        self,
        client_id: str,
        event: str,
        connection_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log client connection events.

        Args:
            client_id: Client identifier
            event: Connection event (connect, disconnect, error)
            connection_info: Additional connection information
        """
        self.logger.info(
            f"Client {event}: {client_id}",
            extra={
                "event_type": "connection",
                "client_id": client_id,
                "connection_event": event,
                "connection_info": connection_info or {},
                "server": self.server_name,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    def log_performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "seconds",
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log performance metric.

        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            context: Additional context
        """
        self.logger.info(
            f"Performance metric: {metric_name} = {value} {unit}",
            extra={
                "event_type": "performance_metric",
                "metric_name": metric_name,
                "value": value,
                "unit": unit,
                "context": context or {},
                "server": self.server_name,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    def _sanitize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize request parameters for logging.

        Args:
            params: Request parameters

        Returns:
            Sanitized parameters
        """
        sensitive_keys = {
            "api_key",
            "token",
            "password",
            "secret",
            "authorization",
            "private_key",
            "access_token",
            "refresh_token",
        }

        sanitized = {}

        for key, value in params.items():
            if key.lower() in sensitive_keys:
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_params(value)
            elif isinstance(value, str) and len(value) > 1000:
                # Truncate very long strings
                sanitized[key] = value[:1000] + "... [TRUNCATED]"
            else:
                sanitized[key] = value

        return sanitized

    def _sanitize_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize response data for logging.

        Args:
            response: Response data

        Returns:
            Sanitized response
        """
        # For responses, we mainly want to avoid logging huge data payloads
        sanitized = response.copy()

        # If result contains large data, summarize it
        if "result" in sanitized and isinstance(sanitized["result"], dict):
            result = sanitized["result"]

            # Check for large content arrays (common in MCP responses)
            if "content" in result and isinstance(result["content"], list):
                content = result["content"]
                if len(content) > 0:
                    # Summarize large content
                    first_item = content[0]
                    if isinstance(first_item, dict) and "text" in first_item:
                        text = first_item["text"]
                        if len(text) > 500:
                            sanitized["result"]["content"] = [
                                {
                                    **first_item,
                                    "text": text[:500]
                                    + f"... [TRUNCATED - {len(text)} chars total]",
                                }
                            ]
                            if len(content) > 1:
                                sanitized["result"]["content"].append(
                                    f"... and {len(content) - 1} more items"
                                )

        return sanitized

    def create_structured_log(self, event_type: str, **kwargs) -> None:
        """Create structured log entry.

        Args:
            event_type: Type of event
            **kwargs: Event data
        """
        self.logger.info(
            f"Structured event: {event_type}",
            extra={
                "event_type": event_type,
                "server": self.server_name,
                "timestamp": datetime.utcnow().isoformat(),
                **kwargs,
            },
        )

    def set_log_level(self, level: str) -> None:
        """Set log level.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(numeric_level)
