"""Prometheus metrics exporter for NeuraScale Neural Engine.

This module handles the export of collected metrics to Prometheus
format and serves them via HTTP endpoint.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from prometheus_client import (
    CollectorRegistry,
    generate_latest,
    start_http_server,
    CONTENT_TYPE_LATEST,
)
from aiohttp import web, ClientSession
import aiohttp

logger = logging.getLogger(__name__)


class PrometheusExporter:
    """Exports metrics to Prometheus format via HTTP endpoint."""

    def __init__(self, config):
        """Initialize Prometheus exporter.

        Args:
            config: Monitoring configuration
        """
        self.config = config
        self.registry = None
        self.http_server = None
        self.app = None
        self.runner = None
        self.site = None

        # Export statistics
        self.total_requests = 0
        self.failed_requests = 0
        self.last_export_time: Optional[datetime] = None

        logger.info("PrometheusExporter initialized")

    async def start(self) -> bool:
        """Start the Prometheus HTTP server.

        Returns:
            True if started successfully
        """
        try:
            if self.runner:
                logger.warning("Prometheus exporter already started")
                return True

            # Create web application
            self.app = web.Application()
            self.app.router.add_get("/metrics", self._handle_metrics_request)
            self.app.router.add_get("/health", self._handle_health_request)

            # Create and start runner
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()

            # Create site
            self.site = web.TCPSite(
                self.runner, "localhost", self.config.prometheus_port
            )
            await self.site.start()

            logger.info(
                f"Prometheus exporter started on port {self.config.prometheus_port}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to start Prometheus exporter: {str(e)}")
            return False

    async def stop(self) -> None:
        """Stop the Prometheus HTTP server."""
        try:
            if self.site:
                await self.site.stop()
                self.site = None

            if self.runner:
                await self.runner.cleanup()
                self.runner = None

            self.app = None

            logger.info("Prometheus exporter stopped")

        except Exception as e:
            logger.error(f"Failed to stop Prometheus exporter: {str(e)}")

    def set_registry(self, registry: CollectorRegistry) -> None:
        """Set the Prometheus registry to export.

        Args:
            registry: Prometheus CollectorRegistry
        """
        self.registry = registry
        logger.info("Prometheus registry configured")

    async def _handle_metrics_request(self, request: web.Request) -> web.Response:
        """Handle /metrics endpoint request.

        Args:
            request: HTTP request

        Returns:
            HTTP response with metrics
        """
        try:
            self.total_requests += 1

            if not self.registry:
                return web.Response(
                    text="No metrics registry configured",
                    status=503,
                    content_type="text/plain",
                )

            # Generate metrics text
            metrics_text = generate_latest(self.registry).decode("utf-8")

            # Add exporter metadata
            metadata = [
                f"# HELP neurascale_exporter_info Information about the NeuraScale Prometheus exporter",
                f"# TYPE neurascale_exporter_info gauge",
                f'neurascale_exporter_info{{version="1.0.0"}} 1',
                f"# HELP neurascale_exporter_requests_total Total number of requests to metrics endpoint",
                f"# TYPE neurascale_exporter_requests_total counter",
                f"neurascale_exporter_requests_total {self.total_requests}",
                f"# HELP neurascale_exporter_last_export_timestamp Unix timestamp of last export",
                f"# TYPE neurascale_exporter_last_export_timestamp gauge",
            ]

            if self.last_export_time:
                timestamp = int(self.last_export_time.timestamp())
                metadata.append(
                    f"neurascale_exporter_last_export_timestamp {timestamp}"
                )
            else:
                metadata.append(f"neurascale_exporter_last_export_timestamp 0")

            # Combine metadata and metrics
            full_metrics = "\n".join(metadata) + "\n\n" + metrics_text

            self.last_export_time = datetime.utcnow()

            return web.Response(text=full_metrics, content_type=CONTENT_TYPE_LATEST)

        except Exception as e:
            self.failed_requests += 1
            logger.error(f"Failed to handle metrics request: {str(e)}")
            return web.Response(
                text=f"Error generating metrics: {str(e)}",
                status=500,
                content_type="text/plain",
            )

    async def _handle_health_request(self, request: web.Request) -> web.Response:
        """Handle /health endpoint request.

        Args:
            request: HTTP request

        Returns:
            HTTP response with health status
        """
        try:
            health_data = {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "exporter": {
                    "total_requests": self.total_requests,
                    "failed_requests": self.failed_requests,
                    "registry_configured": self.registry is not None,
                    "last_export": (
                        self.last_export_time.isoformat()
                        if self.last_export_time
                        else None
                    ),
                },
            }

            return web.json_response(health_data)

        except Exception as e:
            logger.error(f"Failed to handle health request: {str(e)}")
            return web.Response(
                text=f"Health check failed: {str(e)}",
                status=500,
                content_type="text/plain",
            )

    async def push_metrics_to_gateway(
        self,
        gateway_url: str,
        job_name: str = "neural-engine",
        instance: str = "localhost",
    ) -> bool:
        """Push metrics to Prometheus Push Gateway.

        Args:
            gateway_url: Push Gateway URL
            job_name: Job name for metrics
            instance: Instance identifier

        Returns:
            True if push successful
        """
        try:
            if not self.registry:
                logger.warning("No registry configured for push")
                return False

            # Generate metrics
            metrics_data = generate_latest(self.registry)

            # Construct push URL
            push_url = f"{gateway_url}/metrics/job/{job_name}/instance/{instance}"

            # Push to gateway
            async with ClientSession() as session:
                async with session.post(
                    push_url,
                    data=metrics_data,
                    headers={"Content-Type": CONTENT_TYPE_LATEST},
                ) as response:
                    if response.status == 200:
                        logger.info(f"Successfully pushed metrics to {push_url}")
                        return True
                    else:
                        logger.error(f"Failed to push metrics: HTTP {response.status}")
                        return False

        except Exception as e:
            logger.error(f"Failed to push metrics to gateway: {str(e)}")
            return False

    def get_exporter_stats(self) -> Dict[str, Any]:
        """Get exporter statistics.

        Returns:
            Exporter statistics
        """
        return {
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
            "success_rate": (self.total_requests - self.failed_requests)
            / max(1, self.total_requests)
            * 100,
            "registry_configured": self.registry is not None,
            "server_running": self.runner is not None,
            "port": self.config.prometheus_port,
            "last_export_time": (
                self.last_export_time.isoformat() if self.last_export_time else None
            ),
        }
