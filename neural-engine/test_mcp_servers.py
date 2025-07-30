#!/usr/bin/env python3
"""Test MCP servers functionality."""

import asyncio
import websockets
import json


async def test_mcp_server(host="localhost", port=8100, server_name="neural-data"):
    """Test MCP server connection and basic functionality."""
    uri = f"ws://{host}:{port}"

    try:
        async with websockets.connect(uri) as websocket:
            # Send initialize request
            initialize_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "1.0",
                    "capabilities": {"tools": {"supports": True}},
                    "clientInfo": {"name": "test-client", "version": "1.0"},
                },
                "id": 1,
            }

            await websocket.send(json.dumps(initialize_request))
            response = await websocket.recv()
            print(f"\n{server_name} server initialize response:")
            print(json.dumps(json.loads(response), indent=2))

            # List tools
            list_tools_request = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 2,
            }

            await websocket.send(json.dumps(list_tools_request))
            response = await websocket.recv()
            tools_response = json.loads(response)
            print(f"\n{server_name} server available tools:")
            if "result" in tools_response and "tools" in tools_response["result"]:
                for tool in tools_response["result"]["tools"]:
                    print(f"  - {tool['name']}: {tool['description']}")

            return True

    except Exception as e:
        print(f"Error connecting to {server_name} server on port {port}: {e}")
        return False


async def main():
    """Test all MCP servers."""
    servers = [
        ("neural-data", 8100),
        ("device-control", 8101),
        ("clinical", 8102),
        ("analysis", 8103),
    ]

    print("Testing MCP servers...")

    results = []
    for server_name, port in servers:
        result = await test_mcp_server(port=port, server_name=server_name)
        results.append((server_name, result))

    print("\n\nTest Summary:")
    print("-" * 40)
    for server_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{server_name:20} {status}")

    # Test health endpoint
    try:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8080/health") as resp:
                if resp.status == 200:
                    health_data = await resp.json()
                    print("\nHealth check endpoint: ✓ PASSED")
                    print(f"Servers status: {health_data.get('servers', {})}")
                else:
                    print(f"\nHealth check endpoint: ✗ FAILED (status: {resp.status})")
    except Exception as e:
        print(f"\nHealth check endpoint: ✗ FAILED ({e})")


if __name__ == "__main__":
    asyncio.run(main())
