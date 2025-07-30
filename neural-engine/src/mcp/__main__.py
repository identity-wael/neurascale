#!/usr/bin/env python3
"""Allow running MCP module directly with python -m mcp."""

from .main import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
