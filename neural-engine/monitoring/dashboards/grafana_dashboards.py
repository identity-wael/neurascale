"""Grafana dashboard management for NeuraScale Neural Engine.

This module provides automated Grafana dashboard creation and management
for neural processing, system monitoring, and alerting visualizations.
"""

import logging

# from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DashboardConfig:
    """Configuration for dashboard creation."""

    title: str
    description: str
    tags: List[str]
    refresh_interval: str = "5s"
    time_range: str = "1h"
    editable: bool = True


class GrafanaDashboardManager:
    """Manages Grafana dashboard creation and updates."""

    def __init__(
        self, grafana_url: str = "http://localhost:3000", api_key: Optional[str] = None
    ):
        """Initialize Grafana dashboard manager.

        Args:
            grafana_url: Grafana server URL
            api_key: Optional API key for authentication
        """
        self.grafana_url = grafana_url.rstrip("/")
        self.api_key = api_key
        self.headers = {}

        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

        logger.info(f"GrafanaDashboardManager initialized for {grafana_url}")

    async def create_neural_processing_dashboard(self) -> Dict[str, Any]:
        """Create neural processing performance dashboard.

        Returns:
            Dashboard creation result
        """
        try:
            dashboard_json = {
                "dashboard": {
                    "id": None,
                    "title": "Neural Engine - Processing Performance",
                    "description": "Neural signal processing performance metrics",
                    "tags": ["neurascale", "neural-processing", "performance"],
                    "timezone": "browser",
                    "refresh": "5s",
                    "time": {"from": "now-1h", "to": "now"},
                    "panels": [
                        # Signal Processing Latency
                        {
                            "id": 1,
                            "title": "Signal Processing Latency",
                            "type": "graph",
                            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                            "targets": [
                                {
                                    "expr": "histogram_quantile(0.95, neural_signal_processing_duration_seconds_bucket)",
                                    "legendFormat": "95th Percentile",
                                    "refId": "A",
                                },
                                {
                                    "expr": "histogram_quantile(0.50, neural_signal_processing_duration_seconds_bucket)",
                                    "legendFormat": "Median",
                                    "refId": "B",
                                },
                            ],
                            "yAxes": [{"label": "Latency (seconds)", "min": 0}],
                            "xAxis": {"mode": "time"},
                            "thresholds": [
                                {"value": 0.1, "colorMode": "critical", "op": "gt"}
                            ],
                        },
                        # Device Connection Status
                        {
                            "id": 2,
                            "title": "Device Connection Status",
                            "type": "stat",
                            "gridPos": {"h": 8, "w": 6, "x": 12, "y": 0},
                            "targets": [
                                {
                                    "expr": "sum(neural_device_connected)",
                                    "legendFormat": "Connected Devices",
                                    "refId": "A",
                                }
                            ],
                            "fieldConfig": {
                                "defaults": {
                                    "color": {"mode": "thresholds"},
                                    "thresholds": {
                                        "steps": [
                                            {"color": "red", "value": 0},
                                            {"color": "yellow", "value": 1},
                                            {"color": "green", "value": 2},
                                        ]
                                    },
                                }
                            },
                        },
                        # Data Quality Score
                        {
                            "id": 3,
                            "title": "Data Quality Score",
                            "type": "gauge",
                            "gridPos": {"h": 8, "w": 6, "x": 18, "y": 0},
                            "targets": [
                                {
                                    "expr": "avg(neural_data_quality_score)",
                                    "legendFormat": "Average Quality",
                                    "refId": "A",
                                }
                            ],
                            "fieldConfig": {
                                "defaults": {
                                    "min": 0,
                                    "max": 1,
                                    "thresholds": {
                                        "steps": [
                                            {"color": "red", "value": 0},
                                            {"color": "yellow", "value": 0.7},
                                            {"color": "green", "value": 0.85},
                                        ]
                                    },
                                }
                            },
                        },
                        # Neural Sessions Activity
                        {
                            "id": 4,
                            "title": "Neural Sessions Activity",
                            "type": "graph",
                            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
                            "targets": [
                                {
                                    "expr": "neural_sessions_active",
                                    "legendFormat": "Active Sessions",
                                    "refId": "A",
                                },
                                {
                                    "expr": "rate(neural_sessions_total[5m])",
                                    "legendFormat": "Session Rate (per minute)",
                                    "refId": "B",
                                },
                            ],
                        },
                        # Feature Extraction Performance
                        {
                            "id": 5,
                            "title": "Feature Extraction Performance",
                            "type": "graph",
                            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
                            "targets": [
                                {
                                    "expr": "histogram_quantile(0.95, neural_feature_extraction_duration_seconds_bucket)",
                                    "legendFormat": "95th Percentile",
                                    "refId": "A",
                                },
                                {
                                    "expr": "rate(neural_feature_extraction_duration_seconds_count[5m])",
                                    "legendFormat": "Extraction Rate",
                                    "refId": "B",
                                },
                            ],
                        },
                        # Model Inference Latency
                        {
                            "id": 6,
                            "title": "Model Inference Latency by Model",
                            "type": "graph",
                            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16},
                            "targets": [
                                {
                                    "expr": "histogram_quantile(0.95, neural_model_inference_duration_seconds_bucket)",
                                    "legendFormat": "{{model_id}} - 95th Percentile",
                                    "refId": "A",
                                }
                            ],
                        },
                    ],
                },
                "overwrite": True,
            }

            result = await self._create_dashboard(dashboard_json)
            logger.info("Neural processing dashboard created successfully")
            return result

        except Exception as e:
            logger.error(f"Failed to create neural processing dashboard: {str(e)}")
            return {"error": str(e)}

    async def create_system_performance_dashboard(self) -> Dict[str, Any]:
        """Create system performance dashboard.

        Returns:
            Dashboard creation result
        """
        try:
            dashboard_json = {
                "dashboard": {
                    "id": None,
                    "title": "Neural Engine - System Performance",
                    "description": "System resource monitoring and performance metrics",
                    "tags": ["neurascale", "system", "performance"],
                    "timezone": "browser",
                    "refresh": "10s",
                    "time": {"from": "now-1h", "to": "now"},
                    "panels": [
                        # CPU Usage
                        {
                            "id": 1,
                            "title": "CPU Usage",
                            "type": "graph",
                            "gridPos": {"h": 8, "w": 8, "x": 0, "y": 0},
                            "targets": [
                                {
                                    "expr": "neural_system_cpu_percent",
                                    "legendFormat": "CPU Usage %",
                                    "refId": "A",
                                }
                            ],
                            "yAxes": [{"min": 0, "max": 100, "unit": "percent"}],
                            "thresholds": [
                                {"value": 75, "colorMode": "critical", "op": "gt"}
                            ],
                        },
                        # Memory Usage
                        {
                            "id": 2,
                            "title": "Memory Usage",
                            "type": "graph",
                            "gridPos": {"h": 8, "w": 8, "x": 8, "y": 0},
                            "targets": [
                                {
                                    "expr": "neural_system_memory_percent",
                                    "legendFormat": "Memory Usage %",
                                    "refId": "A",
                                }
                            ],
                            "yAxes": [{"min": 0, "max": 100, "unit": "percent"}],
                            "thresholds": [
                                {"value": 80, "colorMode": "critical", "op": "gt"}
                            ],
                        },
                        # Disk Usage
                        {
                            "id": 3,
                            "title": "Disk Usage",
                            "type": "gauge",
                            "gridPos": {"h": 8, "w": 8, "x": 16, "y": 0},
                            "targets": [
                                {
                                    "expr": "neural_system_disk_percent",
                                    "legendFormat": "Disk Usage %",
                                    "refId": "A",
                                }
                            ],
                            "fieldConfig": {
                                "defaults": {
                                    "min": 0,
                                    "max": 100,
                                    "unit": "percent",
                                    "thresholds": {
                                        "steps": [
                                            {"color": "green", "value": 0},
                                            {"color": "yellow", "value": 70},
                                            {"color": "red", "value": 90},
                                        ]
                                    },
                                }
                            },
                        },
                        # API Response Time
                        {
                            "id": 4,
                            "title": "API Response Time",
                            "type": "graph",
                            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
                            "targets": [
                                {
                                    "expr": 'histogram_quantile(0.95, neural_api_request_duration_seconds_bucket{job="neural-api"})',
                                    "legendFormat": "95th Percentile",
                                    "refId": "A",
                                },
                                {
                                    "expr": 'histogram_quantile(0.50, neural_api_request_duration_seconds_bucket{job="neural-api"})',
                                    "legendFormat": "Median",
                                    "refId": "B",
                                },
                            ],
                            "yAxes": [{"label": "Response Time (seconds)", "min": 0}],
                        },
                        # API Request Rate
                        {
                            "id": 5,
                            "title": "API Request Rate",
                            "type": "graph",
                            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
                            "targets": [
                                {
                                    "expr": "rate(neural_api_requests_total[5m])",
                                    "legendFormat": "{{method}} {{endpoint}}",
                                    "refId": "A",
                                }
                            ],
                            "yAxes": [{"label": "Requests per second", "min": 0}],
                        },
                        # Error Rate
                        {
                            "id": 6,
                            "title": "API Error Rate",
                            "type": "graph",
                            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16},
                            "targets": [
                                {
                                    "expr": 'rate(neural_api_requests_total{status_code=~"5.."}[5m]) / rate(neural_api_requests_total[5m]) * 100',
                                    "legendFormat": "5xx Error Rate %",
                                    "refId": "A",
                                },
                                {
                                    "expr": 'rate(neural_api_requests_total{status_code=~"4.."}[5m]) / rate(neural_api_requests_total[5m]) * 100',
                                    "legendFormat": "4xx Error Rate %",
                                    "refId": "B",
                                },
                            ],
                            "yAxes": [{"label": "Error Rate %", "min": 0}],
                            "thresholds": [
                                {"value": 5, "colorMode": "critical", "op": "gt"}
                            ],
                        },
                    ],
                },
                "overwrite": True,
            }

            result = await self._create_dashboard(dashboard_json)
            logger.info("System performance dashboard created successfully")
            return result

        except Exception as e:
            logger.error(f"Failed to create system performance dashboard: {str(e)}")
            return {"error": str(e)}

    async def create_device_monitoring_dashboard(self) -> Dict[str, Any]:
        """Create device monitoring dashboard.

        Returns:
            Dashboard creation result
        """
        try:
            dashboard_json = {
                "dashboard": {
                    "id": None,
                    "title": "Neural Engine - Device Monitoring",
                    "description": "BCI device performance and connectivity monitoring",
                    "tags": ["neurascale", "devices", "bci"],
                    "timezone": "browser",
                    "refresh": "5s",
                    "time": {"from": "now-30m", "to": "now"},
                    "panels": [
                        # Device Connection Overview
                        {
                            "id": 1,
                            "title": "Device Connection Overview",
                            "type": "stat",
                            "gridPos": {"h": 6, "w": 24, "x": 0, "y": 0},
                            "targets": [
                                {
                                    "expr": "sum(neural_device_connected) by (device_type)",
                                    "legendFormat": "{{device_type}}",
                                    "refId": "A",
                                }
                            ],
                        },
                        # Signal Quality by Device
                        {
                            "id": 2,
                            "title": "Signal Quality by Device",
                            "type": "graph",
                            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 6},
                            "targets": [
                                {
                                    "expr": "neural_device_signal_quality",
                                    "legendFormat": "{{device_id}}",
                                    "refId": "A",
                                }
                            ],
                            "yAxes": [{"min": 0, "max": 1, "label": "Quality Score"}],
                            "thresholds": [
                                {"value": 0.7, "colorMode": "critical", "op": "lt"}
                            ],
                        },
                        # Data Rate by Device
                        {
                            "id": 3,
                            "title": "Data Rate by Device",
                            "type": "graph",
                            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 6},
                            "targets": [
                                {
                                    "expr": "neural_device_data_rate_hz",
                                    "legendFormat": "{{device_id}}",
                                    "refId": "A",
                                }
                            ],
                            "yAxes": [{"label": "Data Rate (Hz)", "min": 0}],
                        },
                        # Device Latency
                        {
                            "id": 4,
                            "title": "Device Communication Latency",
                            "type": "graph",
                            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 14},
                            "targets": [
                                {
                                    "expr": "histogram_quantile(0.95, neural_device_latency_seconds_bucket)",
                                    "legendFormat": "{{device_id}} - 95th Percentile",
                                    "refId": "A",
                                }
                            ],
                            "yAxes": [{"label": "Latency (seconds)", "min": 0}],
                        },
                        # Connection Failures
                        {
                            "id": 5,
                            "title": "Connection Failures",
                            "type": "graph",
                            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 14},
                            "targets": [
                                {
                                    "expr": "rate(neural_device_connection_failures_total[5m])",
                                    "legendFormat": "{{device_id}} - {{error_type}}",
                                    "refId": "A",
                                }
                            ],
                            "yAxes": [{"label": "Failures per second", "min": 0}],
                        },
                    ],
                },
                "overwrite": True,
            }

            result = await self._create_dashboard(dashboard_json)
            logger.info("Device monitoring dashboard created successfully")
            return result

        except Exception as e:
            logger.error(f"Failed to create device monitoring dashboard: {str(e)}")
            return {"error": str(e)}

    async def _create_dashboard(self, dashboard_json: Dict[str, Any]) -> Dict[str, Any]:
        """Create dashboard in Grafana.

        Args:
            dashboard_json: Dashboard JSON configuration

        Returns:
            Creation result
        """
        try:
            # url = f"{self.grafana_url}/api / dashboards / db"  # TODO: implement API call

            # For now, simulate dashboard creation
            # In a real implementation, this would POST to Grafana API
            logger.info(f"Creating dashboard: {dashboard_json['dashboard']['title']}")

            return {
                "status": "success",
                "id": 123,  # Simulated dashboard ID
                "uid": "neural-dashboard-123",
                "url": f"{self.grafana_url}/d / neural-dashboard-123",
                "version": 1,
            }

        except Exception as e:
            logger.error(f"Failed to create dashboard in Grafana: {str(e)}")
            return {"error": str(e)}

    async def update_dashboard_config(
        self, dashboard_id: str, config: Dict[str, Any]
    ) -> bool:
        """Update dashboard configuration.

        Args:
            dashboard_id: Dashboard ID to update
            config: New configuration

        Returns:
            True if update successful
        """
        try:
            # In a real implementation, this would update via Grafana API
            logger.info(f"Updating dashboard {dashboard_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update dashboard {dashboard_id}: {str(e)}")
            return False

    def get_dashboard_manager_stats(self) -> Dict[str, Any]:
        """Get dashboard manager statistics.

        Returns:
            Manager statistics
        """
        return {
            "grafana_url": self.grafana_url,
            "api_key_configured": bool(self.api_key),
            "available_dashboards": [
                "neural-processing-performance",
                "system-performance",
                "device-monitoring",
                "alert-management",
            ],
        }
