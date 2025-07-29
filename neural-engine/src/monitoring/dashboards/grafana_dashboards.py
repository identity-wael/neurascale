"""
Grafana dashboard management and automation
"""

import logging
from typing import Dict, Optional, Any
import aiohttp

logger = logging.getLogger(__name__)


class GrafanaDashboardManager:
    """Manages Grafana dashboard creation and updates"""

    def __init__(
        self, grafana_url: str = "http://localhost:3000", api_key: Optional[str] = None
    ):
        """
        Initialize Grafana dashboard manager

        Args:
            grafana_url: Grafana server URL
            api_key: Grafana API key
        """
        self.grafana_url = grafana_url.rstrip("/")
        self.api_key = api_key

        # API headers
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

        logger.info(f"Grafana dashboard manager initialized for {grafana_url}")

    async def create_neural_processing_dashboard(self) -> Dict[str, Any]:
        """Create neural processing monitoring dashboard"""
        dashboard = {
            "dashboard": {
                "title": "Neural Engine - Processing Performance",
                "tags": ["neurascale", "neural-processing", "performance"],
                "timezone": "browser",
                "schemaVersion": 30,
                "version": 1,
                "panels": [
                    self._create_signal_latency_panel(1, 0, 0),
                    self._create_throughput_panel(2, 12, 0),
                    self._create_data_quality_panel(3, 0, 8),
                    self._create_feature_extraction_panel(4, 12, 8),
                    self._create_inference_latency_panel(5, 0, 16),
                    self._create_processing_accuracy_panel(6, 12, 16),
                ],
                "time": {"from": "now-6h", "to": "now"},
                "refresh": "5s",
            },
            "overwrite": True,
        }

        return await self._create_dashboard(dashboard)

    async def create_device_monitoring_dashboard(self) -> Dict[str, Any]:
        """Create device monitoring dashboard"""
        dashboard = {
            "dashboard": {
                "title": "Neural Engine - Device Monitoring",
                "tags": ["neurascale", "device", "bci"],
                "timezone": "browser",
                "schemaVersion": 30,
                "version": 1,
                "panels": [
                    self._create_device_status_panel(1, 0, 0),
                    self._create_connection_stability_panel(2, 8, 0),
                    self._create_signal_quality_panel(3, 16, 0),
                    self._create_device_data_rate_panel(4, 0, 8),
                    self._create_device_error_rate_panel(5, 12, 8),
                    self._create_device_latency_panel(6, 0, 16),
                    self._create_packet_loss_panel(7, 12, 16),
                ],
                "time": {"from": "now-1h", "to": "now"},
                "refresh": "10s",
            },
            "overwrite": True,
        }

        return await self._create_dashboard(dashboard)

    async def create_system_performance_dashboard(self) -> Dict[str, Any]:
        """Create system performance dashboard"""
        dashboard = {
            "dashboard": {
                "title": "Neural Engine - System Performance",
                "tags": ["neurascale", "system", "infrastructure"],
                "timezone": "browser",
                "schemaVersion": 30,
                "version": 1,
                "panels": [
                    self._create_cpu_usage_panel(1, 0, 0),
                    self._create_memory_usage_panel(2, 12, 0),
                    self._create_disk_usage_panel(3, 0, 8),
                    self._create_network_usage_panel(4, 12, 8),
                    self._create_api_latency_panel(5, 0, 16),
                    self._create_db_performance_panel(6, 12, 16),
                    self._create_service_health_panel(7, 0, 24),
                ],
                "time": {"from": "now-3h", "to": "now"},
                "refresh": "30s",
            },
            "overwrite": True,
        }

        return await self._create_dashboard(dashboard)

    async def create_alert_management_dashboard(self) -> Dict[str, Any]:
        """Create alert management dashboard"""
        dashboard = {
            "dashboard": {
                "title": "Neural Engine - Alert Management",
                "tags": ["neurascale", "alerts", "monitoring"],
                "timezone": "browser",
                "schemaVersion": 30,
                "version": 1,
                "panels": [
                    self._create_active_alerts_panel(1, 0, 0),
                    self._create_alert_history_panel(2, 0, 8),
                    self._create_alert_frequency_panel(3, 12, 8),
                    self._create_alert_severity_panel(4, 0, 16),
                    self._create_alert_response_time_panel(5, 12, 16),
                ],
                "time": {"from": "now-24h", "to": "now"},
                "refresh": "1m",
            },
            "overwrite": True,
        }

        return await self._create_dashboard(dashboard)

    def _create_signal_latency_panel(
        self, panel_id: int, x: int, y: int
    ) -> Dict[str, Any]:
        """Create signal processing latency panel"""
        return {
            "id": panel_id,
            "title": "Signal Processing Latency",
            "type": "graph",
            "gridPos": {"x": x, "y": y, "w": 12, "h": 8},
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
                {
                    "expr": "histogram_quantile(0.99, neural_signal_processing_duration_seconds_bucket)",
                    "legendFormat": "99th Percentile",
                    "refId": "C",
                },
            ],
            "yaxes": [{"format": "s", "label": "Latency"}, {"format": "short"}],
            "xaxis": {"mode": "time"},
        }

    def _create_throughput_panel(self, panel_id: int, x: int, y: int) -> Dict[str, Any]:
        """Create throughput monitoring panel"""
        return {
            "id": panel_id,
            "title": "Processing Throughput",
            "type": "graph",
            "gridPos": {"x": x, "y": y, "w": 12, "h": 8},
            "targets": [
                {
                    "expr": "neural_throughput_samples_per_second",
                    "legendFormat": "Samples/sec",
                    "refId": "A",
                }
            ],
            "yaxes": [{"format": "short", "label": "Samples/sec"}, {"format": "short"}],
        }

    def _create_data_quality_panel(
        self, panel_id: int, x: int, y: int
    ) -> Dict[str, Any]:
        """Create data quality monitoring panel"""
        return {
            "id": panel_id,
            "title": "Data Quality Score",
            "type": "gauge",
            "gridPos": {"x": x, "y": y, "w": 12, "h": 8},
            "targets": [{"expr": "avg(neural_data_quality_score)", "refId": "A"}],
            "options": {"showThresholdLabels": True, "showThresholdMarkers": True},
            "fieldConfig": {
                "defaults": {
                    "min": 0,
                    "max": 1,
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "red", "value": 0},
                            {"color": "yellow", "value": 0.7},
                            {"color": "green", "value": 0.9},
                        ],
                    },
                    "unit": "percentunit",
                }
            },
        }

    def _create_device_status_panel(
        self, panel_id: int, x: int, y: int
    ) -> Dict[str, Any]:
        """Create device status panel"""
        return {
            "id": panel_id,
            "title": "Connected Devices",
            "type": "stat",
            "gridPos": {"x": x, "y": y, "w": 8, "h": 8},
            "targets": [{"expr": "sum(neural_device_connected)", "refId": "A"}],
            "options": {
                "colorMode": "value",
                "graphMode": "area",
                "justifyMode": "center",
            },
            "fieldConfig": {
                "defaults": {
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "red", "value": 0},
                            {"color": "green", "value": 1},
                        ],
                    }
                }
            },
        }

    def _create_cpu_usage_panel(self, panel_id: int, x: int, y: int) -> Dict[str, Any]:
        """Create CPU usage panel"""
        return {
            "id": panel_id,
            "title": "CPU Usage",
            "type": "graph",
            "gridPos": {"x": x, "y": y, "w": 12, "h": 8},
            "targets": [
                {
                    "expr": "neural_cpu_usage_percent",
                    "legendFormat": "CPU %",
                    "refId": "A",
                }
            ],
            "yaxes": [
                {"format": "percent", "label": "Usage", "max": 100, "min": 0},
                {"format": "short"},
            ],
            "alert": {
                "conditions": [
                    {
                        "evaluator": {"params": [90], "type": "gt"},
                        "query": {"params": ["A", "5m", "now"]},
                        "type": "query",
                    }
                ],
                "name": "High CPU Usage",
                "noDataState": "no_data",
                "executionErrorState": "alerting",
            },
        }

    def _create_active_alerts_panel(
        self, panel_id: int, x: int, y: int
    ) -> Dict[str, Any]:
        """Create active alerts panel"""
        return {
            "id": panel_id,
            "title": "Active Alerts",
            "type": "table",
            "gridPos": {"x": x, "y": y, "w": 24, "h": 8},
            "targets": [
                {
                    "expr": 'ALERTS{alertstate="firing"}',
                    "format": "table",
                    "instant": True,
                    "refId": "A",
                }
            ],
            "options": {"showHeader": True},
            "fieldConfig": {
                "defaults": {"custom": {"align": "left"}},
                "overrides": [
                    {
                        "matcher": {"id": "byName", "options": "severity"},
                        "properties": [
                            {"id": "custom.displayMode", "value": "color-background"}
                        ],
                    }
                ],
            },
        }

    async def _create_dashboard(
        self, dashboard_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create dashboard in Grafana

        Args:
            dashboard_config: Dashboard configuration

        Returns:
            Dashboard creation response
        """
        try:
            url = f"{self.grafana_url}/api/dashboards/db"

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=dashboard_config,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(
                            f"Dashboard created: {dashboard_config['dashboard']['title']}"
                        )
                        return dict(result)
                    else:
                        error = await response.text()
                        logger.error(
                            f"Failed to create dashboard: {response.status} - {error}"
                        )
                        return {"error": error, "status": response.status}

        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            return {"error": str(e)}

    def update_config(
        self, grafana_url: Optional[str] = None, api_key: Optional[str] = None
    ) -> None:
        """
        Update Grafana configuration

        Args:
            grafana_url: New Grafana URL
            api_key: New API key
        """
        if grafana_url:
            self.grafana_url = grafana_url.rstrip("/")

        if api_key:
            self.api_key = api_key
            self.headers["Authorization"] = f"Bearer {api_key}"

        logger.info("Grafana configuration updated")

    # Additional panel creation methods

    def _create_feature_extraction_panel(
        self, panel_id: int, x: int, y: int
    ) -> Dict[str, Any]:
        """Create feature extraction time panel"""
        return {
            "id": panel_id,
            "title": "Feature Extraction Time",
            "type": "graph",
            "gridPos": {"x": x, "y": y, "w": 12, "h": 8},
            "targets": [
                {
                    "expr": "histogram_quantile(0.95, neural_feature_extraction_duration_seconds_bucket)",
                    "legendFormat": "95th Percentile",
                    "refId": "A",
                },
                {
                    "expr": "histogram_quantile(0.50, neural_feature_extraction_duration_seconds_bucket)",
                    "legendFormat": "Median",
                    "refId": "B",
                },
            ],
            "yaxes": [{"format": "s", "label": "Duration"}, {"format": "short"}],
        }

    def _create_inference_latency_panel(
        self, panel_id: int, x: int, y: int
    ) -> Dict[str, Any]:
        """Create model inference latency panel"""
        return {
            "id": panel_id,
            "title": "Model Inference Latency",
            "type": "graph",
            "gridPos": {"x": x, "y": y, "w": 12, "h": 8},
            "targets": [
                {
                    "expr": "histogram_quantile(0.95, neural_model_inference_duration_seconds_bucket) by (model_id)",
                    "legendFormat": "{{model_id}} - 95th",
                    "refId": "A",
                }
            ],
            "yaxes": [{"format": "s", "label": "Latency"}, {"format": "short"}],
        }

    def _create_processing_accuracy_panel(
        self, panel_id: int, x: int, y: int
    ) -> Dict[str, Any]:
        """Create processing accuracy panel"""
        return {
            "id": panel_id,
            "title": "Processing Accuracy",
            "type": "graph",
            "gridPos": {"x": x, "y": y, "w": 12, "h": 8},
            "targets": [
                {
                    "expr": "neural_processing_accuracy",
                    "legendFormat": "Accuracy",
                    "refId": "A",
                }
            ],
            "yaxes": [
                {"format": "percentunit", "label": "Accuracy", "max": 1, "min": 0},
                {"format": "short"},
            ],
        }

    def _create_connection_stability_panel(
        self, panel_id: int, x: int, y: int
    ) -> Dict[str, Any]:
        """Create connection stability panel"""
        return {
            "id": panel_id,
            "title": "Connection Stability",
            "type": "graph",
            "gridPos": {"x": x, "y": y, "w": 8, "h": 8},
            "targets": [
                {
                    "expr": "neural_device_connection_stability",
                    "legendFormat": "{{device_id}}",
                    "refId": "A",
                }
            ],
            "yaxes": [
                {"format": "percentunit", "label": "Stability", "max": 1, "min": 0},
                {"format": "short"},
            ],
        }

    def _create_signal_quality_panel(
        self, panel_id: int, x: int, y: int
    ) -> Dict[str, Any]:
        """Create signal quality panel"""
        return {
            "id": panel_id,
            "title": "Signal Quality",
            "type": "heatmap",
            "gridPos": {"x": x, "y": y, "w": 8, "h": 8},
            "targets": [
                {
                    "expr": "neural_device_signal_quality",
                    "format": "heatmap",
                    "refId": "A",
                }
            ],
            "options": {
                "calculate": True,
                "calculation": {"xBuckets": {"mode": "size", "value": "1min"}},
                "color": {"mode": "spectrum", "scheme": "Spectral"},
            },
        }

    def _create_device_data_rate_panel(
        self, panel_id: int, x: int, y: int
    ) -> Dict[str, Any]:
        """Create device data rate panel"""
        return {
            "id": panel_id,
            "title": "Device Data Rates",
            "type": "graph",
            "gridPos": {"x": x, "y": y, "w": 12, "h": 8},
            "targets": [
                {
                    "expr": "neural_device_data_rate_hz",
                    "legendFormat": "{{device_id}}",
                    "refId": "A",
                }
            ],
            "yaxes": [{"format": "Hz", "label": "Data Rate"}, {"format": "short"}],
        }

    def _create_device_error_rate_panel(
        self, panel_id: int, x: int, y: int
    ) -> Dict[str, Any]:
        """Create device error rate panel"""
        return {
            "id": panel_id,
            "title": "Device Error Rates",
            "type": "graph",
            "gridPos": {"x": x, "y": y, "w": 12, "h": 8},
            "targets": [
                {
                    "expr": "neural_device_error_rate",
                    "legendFormat": "{{device_id}}",
                    "refId": "A",
                }
            ],
            "yaxes": [{"format": "short", "label": "Errors/sec"}, {"format": "short"}],
            "alert": {
                "conditions": [
                    {
                        "evaluator": {"params": [0.01], "type": "gt"},
                        "query": {"params": ["A", "5m", "now"]},
                        "type": "query",
                    }
                ],
                "name": "High Device Error Rate",
            },
        }

    def _create_device_latency_panel(
        self, panel_id: int, x: int, y: int
    ) -> Dict[str, Any]:
        """Create device latency panel"""
        return {
            "id": panel_id,
            "title": "Device Communication Latency",
            "type": "graph",
            "gridPos": {"x": x, "y": y, "w": 12, "h": 8},
            "targets": [
                {
                    "expr": "neural_device_latency_milliseconds",
                    "legendFormat": "{{device_id}}",
                    "refId": "A",
                }
            ],
            "yaxes": [{"format": "ms", "label": "Latency"}, {"format": "short"}],
        }

    def _create_packet_loss_panel(
        self, panel_id: int, x: int, y: int
    ) -> Dict[str, Any]:
        """Create packet loss panel"""
        return {
            "id": panel_id,
            "title": "Packet Loss Rate",
            "type": "graph",
            "gridPos": {"x": x, "y": y, "w": 12, "h": 8},
            "targets": [
                {
                    "expr": "neural_device_packet_loss_rate",
                    "legendFormat": "{{device_id}}",
                    "refId": "A",
                }
            ],
            "yaxes": [
                {"format": "percentunit", "label": "Loss Rate", "max": 0.1, "min": 0},
                {"format": "short"},
            ],
        }

    def _create_memory_usage_panel(
        self, panel_id: int, x: int, y: int
    ) -> Dict[str, Any]:
        """Create memory usage panel"""
        return {
            "id": panel_id,
            "title": "Memory Usage",
            "type": "graph",
            "gridPos": {"x": x, "y": y, "w": 12, "h": 8},
            "targets": [
                {
                    "expr": "neural_memory_usage_bytes / 1024 / 1024 / 1024",
                    "legendFormat": "Memory (GB)",
                    "refId": "A",
                },
                {
                    "expr": "neural_memory_usage_percent",
                    "legendFormat": "Memory %",
                    "refId": "B",
                    "yaxis": 2,
                },
            ],
            "yaxes": [
                {"format": "decgbytes", "label": "Memory"},
                {"format": "percent", "label": "Percentage", "max": 100, "min": 0},
            ],
        }

    def _create_disk_usage_panel(self, panel_id: int, x: int, y: int) -> Dict[str, Any]:
        """Create disk usage panel"""
        return {
            "id": panel_id,
            "title": "Disk Usage",
            "type": "stat",
            "gridPos": {"x": x, "y": y, "w": 12, "h": 8},
            "targets": [{"expr": "neural_disk_usage_percent", "refId": "A"}],
            "options": {
                "colorMode": "background",
                "graphMode": "area",
                "justifyMode": "center",
            },
            "fieldConfig": {
                "defaults": {
                    "unit": "percent",
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "green", "value": 0},
                            {"color": "yellow", "value": 80},
                            {"color": "red", "value": 90},
                        ],
                    },
                }
            },
        }

    def _create_network_usage_panel(
        self, panel_id: int, x: int, y: int
    ) -> Dict[str, Any]:
        """Create network usage panel"""
        return {
            "id": panel_id,
            "title": "Network Usage",
            "type": "graph",
            "gridPos": {"x": x, "y": y, "w": 12, "h": 8},
            "targets": [
                {
                    "expr": "rate(neural_network_bytes_sent_total[5m])",
                    "legendFormat": "Sent",
                    "refId": "A",
                },
                {
                    "expr": "rate(neural_network_bytes_received_total[5m])",
                    "legendFormat": "Received",
                    "refId": "B",
                },
            ],
            "yaxes": [{"format": "Bps", "label": "Bytes/sec"}, {"format": "short"}],
        }

    def _create_api_latency_panel(
        self, panel_id: int, x: int, y: int
    ) -> Dict[str, Any]:
        """Create API latency panel"""
        return {
            "id": panel_id,
            "title": "API Response Time",
            "type": "graph",
            "gridPos": {"x": x, "y": y, "w": 12, "h": 8},
            "targets": [
                {
                    "expr": "histogram_quantile(0.95, neural_api_request_duration_seconds_bucket)",
                    "legendFormat": "95th Percentile",
                    "refId": "A",
                },
                {
                    "expr": "histogram_quantile(0.50, neural_api_request_duration_seconds_bucket)",
                    "legendFormat": "Median",
                    "refId": "B",
                },
            ],
            "yaxes": [{"format": "s", "label": "Response Time"}, {"format": "short"}],
        }

    def _create_db_performance_panel(
        self, panel_id: int, x: int, y: int
    ) -> Dict[str, Any]:
        """Create database performance panel"""
        return {
            "id": panel_id,
            "title": "Database Performance",
            "type": "graph",
            "gridPos": {"x": x, "y": y, "w": 12, "h": 8},
            "targets": [
                {
                    "expr": "histogram_quantile(0.95, neural_db_query_duration_seconds_bucket) by (query_type)",
                    "legendFormat": "{{query_type}}",
                    "refId": "A",
                }
            ],
            "yaxes": [{"format": "s", "label": "Query Time"}, {"format": "short"}],
        }

    def _create_service_health_panel(
        self, panel_id: int, x: int, y: int
    ) -> Dict[str, Any]:
        """Create service health status panel"""
        return {
            "id": panel_id,
            "title": "Service Health Status",
            "type": "stat",
            "gridPos": {"x": x, "y": y, "w": 24, "h": 8},
            "targets": [
                {
                    "expr": "neural_service_health",
                    "legendFormat": "{{service}}",
                    "refId": "A",
                }
            ],
            "options": {
                "colorMode": "background",
                "graphMode": "none",
                "justifyMode": "center",
                "orientation": "horizontal",
                "reduceOptions": {"calcs": ["lastNotNull"], "values": False},
            },
            "fieldConfig": {
                "defaults": {
                    "mappings": [
                        {
                            "options": {
                                "0": {"color": "red", "index": 0, "text": "Unhealthy"},
                                "1": {"color": "green", "index": 1, "text": "Healthy"},
                            },
                            "type": "value",
                        }
                    ],
                    "thresholds": {
                        "mode": "absolute",
                        "steps": [
                            {"color": "red", "value": 0},
                            {"color": "green", "value": 1},
                        ],
                    },
                    "unit": "none",
                }
            },
        }

    def _create_alert_history_panel(
        self, panel_id: int, x: int, y: int
    ) -> Dict[str, Any]:
        """Create alert history panel"""
        return {
            "id": panel_id,
            "title": "Alert History",
            "type": "table",
            "gridPos": {"x": x, "y": y, "w": 12, "h": 8},
            "targets": [
                {"expr": "increase(ALERTS[24h])", "format": "table", "refId": "A"}
            ],
            "options": {
                "showHeader": True,
                "sortBy": [{"desc": True, "displayName": "Time"}],
            },
        }

    def _create_alert_frequency_panel(
        self, panel_id: int, x: int, y: int
    ) -> Dict[str, Any]:
        """Create alert frequency panel"""
        return {
            "id": panel_id,
            "title": "Alert Frequency",
            "type": "graph",
            "gridPos": {"x": x, "y": y, "w": 12, "h": 8},
            "targets": [
                {
                    "expr": "sum(increase(ALERTS[1h])) by (alertname)",
                    "legendFormat": "{{alertname}}",
                    "refId": "A",
                }
            ],
            "yaxes": [{"format": "short", "label": "Alert Count"}, {"format": "short"}],
        }

    def _create_alert_severity_panel(
        self, panel_id: int, x: int, y: int
    ) -> Dict[str, Any]:
        """Create alert severity distribution panel"""
        return {
            "id": panel_id,
            "title": "Alert Severity Distribution",
            "type": "piechart",
            "gridPos": {"x": x, "y": y, "w": 12, "h": 8},
            "targets": [
                {
                    "expr": "sum(ALERTS) by (severity)",
                    "legendFormat": "{{severity}}",
                    "refId": "A",
                }
            ],
            "options": {
                "pieType": "pie",
                "displayLabels": ["name", "percent"],
                "legendDisplayMode": "list",
                "legendPlacement": "right",
            },
        }

    def _create_alert_response_time_panel(
        self, panel_id: int, x: int, y: int
    ) -> Dict[str, Any]:
        """Create alert response time panel"""
        return {
            "id": panel_id,
            "title": "Alert Response Time",
            "type": "graph",
            "gridPos": {"x": x, "y": y, "w": 12, "h": 8},
            "targets": [
                {
                    "expr": "histogram_quantile(0.95, alert_response_time_seconds_bucket)",
                    "legendFormat": "95th Percentile",
                    "refId": "A",
                },
                {
                    "expr": "histogram_quantile(0.50, alert_response_time_seconds_bucket)",
                    "legendFormat": "Median",
                    "refId": "B",
                },
            ],
            "yaxes": [{"format": "s", "label": "Response Time"}, {"format": "short"}],
        }
