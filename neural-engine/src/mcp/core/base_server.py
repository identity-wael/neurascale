"""Base MCP server implementation for NeuraScale Neural Engine."""

import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

from .auth import MCPAuthManager
from .permissions import PermissionManager
from .rate_limiter import MCPRateLimiter
from .error_handler import MCPErrorHandler
from ..utils.logger import MCPLogger
from ..utils.validators import validate_tool_input


class BaseNeuralMCPServer(ABC):
    """Base class for all NeuraScale Neural Engine MCP servers."""

    def __init__(self, name: str, version: str, config: Dict[str, Any]):
        """Initialize base MCP server.

        Args:
            name: Server name identifier
            version: Server version
            config: Server configuration
        """
        self.name = name
        self.version = version
        self.config = config

        # Initialize core components
        self.auth_manager = MCPAuthManager(config.get("auth", {}))
        self.permission_manager = PermissionManager(config.get("permissions", {}))
        self.rate_limiter = MCPRateLimiter(config.get("rate_limits", {}))
        self.error_handler = MCPErrorHandler()
        self.logger = MCPLogger(name)

        # Tool registry
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.resources: Dict[str, Dict[str, Any]] = {}

        # Connection state
        self.clients: Dict[str, Dict[str, Any]] = {}
        self.is_running = False

    async def start(self, port: int = 8000) -> None:
        """Start the MCP server.

        Args:
            port: Port to listen on
        """
        try:
            self.logger.info(f"Starting {self.name} MCP server on port {port}")

            # Register tools and resources
            await self.register_tools()
            await self.register_resources()

            # Start WebSocket server
            import websockets

            self.server = await websockets.serve(
                self.handle_client, "0.0.0.0", port, ping_interval=30, ping_timeout=10
            )

            self.is_running = True
            self.logger.info(f"{self.name} MCP server started successfully")

        except Exception as e:
            self.logger.error(f"Failed to start MCP server: {e}")
            raise

    async def stop(self) -> None:
        """Stop the MCP server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()

        self.is_running = False
        self.logger.info(f"{self.name} MCP server stopped")

    async def handle_client(self, websocket, path):
        """Handle WebSocket client connections."""
        client_id = f"client_{id(websocket)}"
        self.clients[client_id] = {
            "websocket": websocket,
            "connected_at": datetime.utcnow(),
            "user": None,
        }

        try:
            self.logger.info(f"Client {client_id} connected")

            async for message in websocket:
                try:
                    request = json.loads(message)
                    response = await self.handle_request(client_id, request)
                    await websocket.send(json.dumps(response))

                except json.JSONDecodeError:
                    error_response = self.error_handler.create_error_response(
                        "parse_error", "Invalid JSON"
                    )
                    await websocket.send(json.dumps(error_response))

                except Exception as e:
                    self.logger.error(f"Error handling message from {client_id}: {e}")
                    error_response = self.error_handler.create_error_response(
                        "internal_error", str(e)
                    )
                    await websocket.send(json.dumps(error_response))

        except Exception as e:
            self.logger.error(f"Client {client_id} connection error: {e}")
        finally:
            if client_id in self.clients:
                del self.clients[client_id]
            self.logger.info(f"Client {client_id} disconnected")

    async def handle_request(
        self, client_id: str, request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle incoming MCP request with middleware.

        Args:
            client_id: Client identifier
            request: MCP request

        Returns:
            MCP response
        """
        try:
            # Extract request details
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

            # Rate limiting
            if not await self.rate_limiter.check_limit(client_id, method):
                return self.error_handler.create_error_response(
                    "rate_limit_exceeded", "Too many requests", request_id
                )

            # Authentication (for non-initialization methods)
            if method != "initialize":
                user = await self.authenticate_request(client_id, request)
                if not user:
                    return self.error_handler.create_error_response(
                        "unauthorized", "Authentication required", request_id
                    )
                self.clients[client_id]["user"] = user

            # Log request
            self.logger.log_request(client_id, method, params)

            # Route request
            if method == "initialize":
                response = await self.handle_initialize(params)
            elif method == "tools/list":
                response = await self.handle_list_tools(client_id)
            elif method == "tools/call":
                response = await self.handle_call_tool(client_id, params)
            elif method == "resources/list":
                response = await self.handle_list_resources(client_id)
            elif method == "resources/read":
                response = await self.handle_read_resource(client_id, params)
            else:
                response = self.error_handler.create_error_response(
                    "method_not_found", f"Unknown method: {method}", request_id
                )

            # Add request ID to response
            if request_id:
                response["id"] = request_id

            # Log response
            self.logger.log_response(client_id, response)

            return response

        except Exception as e:
            self.logger.error(f"Error handling request: {e}")
            return self.error_handler.create_error_response(
                "internal_error", str(e), request.get("id")
            )

    async def authenticate_request(
        self, client_id: str, request: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Authenticate MCP request.

        Args:
            client_id: Client identifier
            request: MCP request

        Returns:
            User information if authenticated, None otherwise
        """
        # Check for API key in headers/params
        api_key = request.get("params", {}).get("api_key") or request.get(
            "headers", {}
        ).get("authorization", "").replace("Bearer ", "")

        if api_key:
            return await self.auth_manager.authenticate_api_key(api_key)

        return None

    async def check_permission(
        self, client_id: str, permission: str, resource: str = None
    ) -> bool:
        """Check if client has required permission.

        Args:
            client_id: Client identifier
            permission: Required permission
            resource: Optional resource identifier

        Returns:
            True if permission granted
        """
        client = self.clients.get(client_id)
        if not client or not client.get("user"):
            return False

        user = client["user"]
        return await self.permission_manager.check_permission(
            user, permission, resource
        )

    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request."""
        return {
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": {"name": self.name, "version": self.version},
            },
        }

    async def handle_list_tools(self, client_id: str) -> Dict[str, Any]:
        """Handle tools/list request."""
        # Get user permissions
        client = self.clients.get(client_id)
        user_permissions = []
        if client and client.get("user"):
            user_permissions = await self.permission_manager.get_user_permissions(
                client["user"]
            )

        # Filter tools by permissions
        available_tools = []
        for tool_name, tool_info in self.tools.items():
            required_permissions = tool_info.get("permissions", [])
            if not required_permissions or any(
                p in user_permissions for p in required_permissions
            ):
                available_tools.append(
                    {
                        "name": tool_name,
                        "description": tool_info["description"],
                        "inputSchema": tool_info["input_schema"],
                    }
                )

        return {"jsonrpc": "2.0", "result": {"tools": available_tools}}

    async def handle_call_tool(
        self, client_id: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name not in self.tools:
            return self.error_handler.create_error_response(
                "tool_not_found", f"Tool not found: {tool_name}"
            )

        tool_info = self.tools[tool_name]

        # Check permissions
        required_permissions = tool_info.get("permissions", [])
        if required_permissions:
            has_permission = False
            for permission in required_permissions:
                if await self.check_permission(client_id, permission):
                    has_permission = True
                    break

            if not has_permission:
                return self.error_handler.create_error_response(
                    "forbidden", f"Insufficient permissions for tool: {tool_name}"
                )

        # Validate input
        try:
            validate_tool_input(arguments, tool_info["input_schema"])
        except ValueError as e:
            return self.error_handler.create_error_response("invalid_params", str(e))

        # Execute tool
        try:
            handler = tool_info["handler"]
            result = await handler(**arguments)

            return {
                "jsonrpc": "2.0",
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                },
            }

        except Exception as e:
            self.logger.error(f"Tool execution error: {e}")
            return self.error_handler.create_error_response(
                "execution_error", f"Tool execution failed: {str(e)}"
            )

    async def handle_list_resources(self, client_id: str) -> Dict[str, Any]:
        """Handle resources/list request."""
        # Implementation similar to list_tools but for resources
        return {"jsonrpc": "2.0", "result": {"resources": []}}

    async def handle_read_resource(
        self, client_id: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle resources/read request."""
        # Implementation for reading resources
        return {"jsonrpc": "2.0", "result": {"contents": []}}

    def register_tool(
        self,
        name: str,
        handler: Callable,
        description: str,
        input_schema: Dict[str, Any],
        permissions: List[str] = None,
    ):
        """Register a tool with the MCP server.

        Args:
            name: Tool name
            handler: Async function to handle tool calls
            description: Tool description
            input_schema: JSON schema for input validation
            permissions: Required permissions
        """
        self.tools[name] = {
            "handler": handler,
            "description": description,
            "input_schema": input_schema,
            "permissions": permissions or [],
        }

        self.logger.info(f"Registered tool: {name}")

    def register_resource(
        self,
        uri: str,
        name: str,
        mime_type: str,
        handler: Callable,
        permissions: List[str] = None,
    ):
        """Register a resource with the MCP server.

        Args:
            uri: Resource URI
            name: Resource name
            mime_type: MIME type
            handler: Async function to provide resource
            permissions: Required permissions
        """
        self.resources[uri] = {
            "name": name,
            "mime_type": mime_type,
            "handler": handler,
            "permissions": permissions or [],
        }

        self.logger.info(f"Registered resource: {uri}")

    @abstractmethod
    async def register_tools(self) -> None:
        """Register all tools for this server. Must be implemented by subclasses."""
        pass

    async def register_resources(self) -> None:
        """Register all resources for this server. Override in subclasses if needed."""
        pass

    def tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        permissions: List[str] = None,
    ):
        """Decorator to register tools.

        Args:
            name: Tool name
            description: Tool description
            input_schema: JSON schema for input validation
            permissions: Required permissions
        """

        def decorator(func: Callable):
            self.register_tool(name, func, description, input_schema, permissions)
            return func

        return decorator
