#!/usr/bin/env python3
"""Main entry point for NeuraScale MCP servers."""

import asyncio
import logging
import argparse
import signal
import sys
from typing import List
import uvloop
from aiohttp import web

from .config import load_config
from .servers.neural_data.server import NeuralDataMCPServer
from .servers.device_control.server import DeviceControlMCPServer
from .servers.clinical.server import ClinicalMCPServer
from .servers.analysis.server import AnalysisMCPServer


class MCPServerManager:
    """Manages multiple MCP servers."""

    def __init__(self, config):
        """Initialize server manager.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.servers = {}
        self.running = False
        self.http_app = None
        self.http_runner = None

        # Setup logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)

    def _setup_logging(self):
        """Setup logging configuration."""
        log_config = self.config.get("logging", {})
        level = getattr(logging, log_config.get("level", "INFO"))
        format_str = log_config.get(
            "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        logging.basicConfig(level=level, format=format_str)

    async def health_check(self, request):
        """Health check endpoint."""
        status = {
            "status": "healthy",
            "servers": {},
            "timestamp": asyncio.get_event_loop().time(),
        }

        for server_type, server in self.servers.items():
            # Simple health check - server exists and is running
            status["servers"][server_type] = {
                "status": "running" if server else "stopped",
                "port": self.config["servers"]
                .get(server_type, {})
                .get("port", "unknown"),
            }

        return web.json_response(status)

    async def setup_http_server(self, port: int = 8080):
        """Setup HTTP server for health checks."""
        self.http_app = web.Application()
        self.http_app.router.add_get("/health", self.health_check)
        self.http_app.router.add_get(
            "/healthz", self.health_check
        )  # Alternative endpoint

        self.http_runner = web.AppRunner(self.http_app)
        await self.http_runner.setup()

        site = web.TCPSite(self.http_runner, "0.0.0.0", port)
        await site.start()

        self.logger.info(f"HTTP health server started on port {port}")

    async def start_servers(
        self, server_types: List[str] = None, http_port: int = 8080
    ):
        """Start MCP servers.

        Args:
            server_types: List of server types to start (None for all)
            http_port: Port for HTTP health server
        """
        if server_types is None:
            server_types = ["neural_data", "device_control", "clinical", "analysis"]

        self.logger.info(f"Starting MCP servers: {server_types}")

        # Start HTTP health server first
        await self.setup_http_server(http_port)

        # Initialize servers
        for server_type in server_types:
            await self._start_server(server_type)

        self.running = True
        self.logger.info("All MCP servers started successfully")

    async def _start_server(self, server_type: str):
        """Start a specific server type.

        Args:
            server_type: Type of server to start
        """
        server_config = self.config["servers"].get(server_type)
        if not server_config:
            raise ValueError(f"No configuration found for server type: {server_type}")

        # Create server instance
        if server_type == "neural_data":
            server = NeuralDataMCPServer(self.config)
        elif server_type == "device_control":
            server = DeviceControlMCPServer(self.config)
        elif server_type == "clinical":
            server = ClinicalMCPServer(self.config)
        elif server_type == "analysis":
            server = AnalysisMCPServer(self.config)
        else:
            raise ValueError(f"Unknown server type: {server_type}")

        # Start server
        port = server_config["port"]
        await server.start(port)

        self.servers[server_type] = server
        self.logger.info(f"Started {server_type} MCP server on port {port}")

    async def stop_servers(self):
        """Stop all MCP servers."""
        self.logger.info("Stopping MCP servers")

        for server_type, server in self.servers.items():
            try:
                await server.stop()
                self.logger.info(f"Stopped {server_type} MCP server")
            except Exception as e:
                self.logger.error(f"Error stopping {server_type} server: {e}")

        # Stop HTTP server
        if self.http_runner:
            try:
                await self.http_runner.cleanup()
                self.logger.info("Stopped HTTP health server")
            except Exception as e:
                self.logger.error(f"Error stopping HTTP server: {e}")

        self.servers.clear()
        self.running = False
        self.logger.info("All MCP servers stopped")

    async def run_forever(self):
        """Run servers until interrupted."""
        try:
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        finally:
            await self.stop_servers()

    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(signame):
            self.logger.info(f"Received {signame}")
            self.running = False

        for signame in {"SIGINT", "SIGTERM"}:
            if hasattr(signal, signame):
                loop = asyncio.get_event_loop()
                loop.add_signal_handler(
                    getattr(signal, signame), lambda: signal_handler(signame)
                )


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="NeuraScale MCP Server Manager")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    parser.add_argument(
        "--servers",
        nargs="+",
        choices=["neural_data", "device_control", "clinical", "analysis"],
        help="Server types to start (default: all)",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Log level",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="HTTP health check server port",
    )

    args = parser.parse_args()

    # Load configuration
    try:
        config = load_config(args.config)

        # Override log level if specified
        if args.log_level:
            config.setdefault("logging", {})["level"] = args.log_level

    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)

    # Create server manager
    manager = MCPServerManager(config)

    # Setup signal handlers for graceful shutdown
    manager.setup_signal_handlers()

    try:
        # Start servers
        await manager.start_servers(args.servers, args.port)

        # Run until interrupted
        await manager.run_forever()

    except Exception as e:
        logging.error(f"Error running MCP servers: {e}")
        sys.exit(1)


def cli_neural_data():
    """CLI entry point for neural data server only."""

    async def run_neural_data():
        config = load_config()
        manager = MCPServerManager(config)
        manager.setup_signal_handlers()
        await manager.start_servers(["neural_data"])
        await manager.run_forever()

    # Use uvloop for better performance
    if hasattr(asyncio, "set_event_loop_policy"):
        try:
            import uvloop

            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        except ImportError:
            pass

    asyncio.run(run_neural_data())


def cli_device_control():
    """CLI entry point for device control server only."""

    async def run_device_control():
        config = load_config()
        manager = MCPServerManager(config)
        manager.setup_signal_handlers()
        await manager.start_servers(["device_control"])
        await manager.run_forever()

    # Use uvloop for better performance
    if hasattr(asyncio, "set_event_loop_policy"):
        try:
            import uvloop

            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        except ImportError:
            pass

    asyncio.run(run_device_control())


def cli_clinical():
    """CLI entry point for clinical server only."""

    async def run_clinical():
        config = load_config()
        manager = MCPServerManager(config)
        manager.setup_signal_handlers()
        await manager.start_servers(["clinical"])
        await manager.run_forever()

    # Use uvloop for better performance
    if hasattr(asyncio, "set_event_loop_policy"):
        try:
            import uvloop

            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        except ImportError:
            pass

    asyncio.run(run_clinical())


def cli_analysis():
    """CLI entry point for analysis server only."""

    async def run_analysis():
        config = load_config()
        manager = MCPServerManager(config)
        manager.setup_signal_handlers()
        await manager.start_servers(["analysis"])
        await manager.run_forever()

    # Use uvloop for better performance
    if hasattr(asyncio, "set_event_loop_policy"):
        try:
            import uvloop

            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        except ImportError:
            pass

    asyncio.run(run_analysis())


if __name__ == "__main__":
    # Use uvloop for better performance
    if hasattr(asyncio, "set_event_loop_policy"):
        try:
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        except ImportError:
            pass

    asyncio.run(main())
