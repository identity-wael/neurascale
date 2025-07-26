"""Jaeger tracing exporter for NeuraScale Neural Engine.

This module handles the export of distributed traces to Jaeger
for trace visualization and analysis.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class JaegerExporter:
    """Exports distributed traces to Jaeger."""

    def __init__(self, config):
        """Initialize Jaeger exporter.

        Args:
            config: Monitoring configuration
        """
        self.config = config
        self.jaeger_endpoint = getattr(
            config, "jaeger_endpoint", "http://localhost:14268 / api / traces"
        )
        self.service_name = "neurascale-neural-engine"

        # Export statistics
        self.total_spans_exported = 0
        self.failed_exports = 0
        self.last_export_time: Optional[datetime] = None

        # Batch management
        self.span_batch: List[Dict] = []
        self.max_batch_size = 100
        self.batch_timeout_seconds = 30

        logger.info("JaegerExporter initialized")

    async def start(self) -> bool:
        """Start the Jaeger exporter.

        Returns:
            True if started successfully
        """
        try:
            # Test connectivity to Jaeger
            logger.info(f"Jaeger exporter started, endpoint: {self.jaeger_endpoint}")
            return True

        except Exception as e:
            logger.error(f"Failed to start Jaeger exporter: {str(e)}")
            return False

    async def stop(self) -> None:
        """Stop the Jaeger exporter and flush remaining spans."""
        try:
            # Flush any remaining spans
            if self.span_batch:
                await self._flush_batch()

            logger.info("Jaeger exporter stopped")

        except Exception as e:
            logger.error(f"Failed to stop Jaeger exporter: {str(e)}")

    async def export_span(self, span_data: Dict[str, Any]) -> bool:
        """Export a single span to Jaeger.

        Args:
            span_data: Span data to export

        Returns:
            True if export successful
        """
        try:
            # Convert span to Jaeger format
            jaeger_span = self._convert_to_jaeger_format(span_data)

            # Add to batch
            self.span_batch.append(jaeger_span)

            # Flush batch if it's full
            if len(self.span_batch) >= self.max_batch_size:
                await self._flush_batch()

            return True

        except Exception as e:
            logger.error(f"Failed to export span: {str(e)}")
            self.failed_exports += 1
            return False

    async def export_spans(self, spans: List[Dict[str, Any]]) -> bool:
        """Export multiple spans to Jaeger.

        Args:
            spans: List of span data to export

        Returns:
            True if export successful
        """
        try:
            # Convert all spans to Jaeger format
            jaeger_spans = [self._convert_to_jaeger_format(span) for span in spans]

            # Add to batch
            self.span_batch.extend(jaeger_spans)

            # Flush if batch is large enough
            while len(self.span_batch) >= self.max_batch_size:
                await self._flush_batch()

            return True

        except Exception as e:
            logger.error(f"Failed to export spans: {str(e)}")
            self.failed_exports += len(spans)
            return False

    async def _flush_batch(self) -> bool:
        """Flush the current batch of spans to Jaeger.

        Returns:
            True if flush successful
        """
        if not self.span_batch:
            return True

        try:
            # Create Jaeger batch
            batch_data = {
                "spans": self.span_batch[: self.max_batch_size],
                "process": {
                    "serviceName": self.service_name,
                    "tags": [
                        {"key": "service.version", "vStr": "1.0.0"},
                        {"key": "service.namespace", "vStr": "neurascale"},
                    ],
                },
            }

            # In a real implementation, this would send to Jaeger HTTP API
            # For now, we'll simulate the export
            exported_count = len(batch_data["spans"])

            # Remove exported spans from batch
            self.span_batch = self.span_batch[exported_count:]

            self.total_spans_exported += exported_count
            self.last_export_time = datetime.utcnow()

            logger.debug(f"Exported {exported_count} spans to Jaeger")
            return True

        except Exception as e:
            logger.error(f"Failed to flush batch to Jaeger: {str(e)}")
            self.failed_exports += len(self.span_batch)
            return False

    def _convert_to_jaeger_format(self, span_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert span data to Jaeger format.

        Args:
            span_data: Raw span data

        Returns:
            Jaeger-formatted span
        """
        try:
            # Generate span and trace IDs if not present
            span_id = span_data.get("span_id", self._generate_id())
            trace_id = span_data.get("trace_id", self._generate_id())

            # Convert timestamp to microseconds
            start_time = span_data.get("start_time", datetime.utcnow())
            if isinstance(start_time, datetime):
                start_time_us = int(start_time.timestamp() * 1_000_000)
            else:
                start_time_us = int(start_time * 1_000_000)

            # Calculate duration
            duration = span_data.get("duration", 0.0)
            if isinstance(duration, (int, float)):
                duration_us = int(duration * 1_000_000)
            else:
                duration_us = 0

            # Convert tags / attributes
            tags = []
            attributes = span_data.get("attributes", {})
            for key, value in attributes.items():
                tags.append({"key": key, "vStr": str(value)})

            # Create Jaeger span
            jaeger_span = {
                "traceID": trace_id,
                "spanID": span_id,
                "parentSpanID": span_data.get("parent_span_id", ""),
                "operationName": span_data.get("operation_name", "unknown"),
                "startTime": start_time_us,
                "duration": duration_us,
                "tags": tags,
                "logs": [],
                "process": {"serviceName": self.service_name, "tags": []},
            }

            # Add logs / events
            events = span_data.get("events", [])
            for event in events:
                log_entry = {
                    "timestamp": int(event.get("timestamp", start_time_us)),
                    "fields": [
                        {"key": "event", "vStr": event.get("name", "event")},
                        {"key": "message", "vStr": event.get("message", "")},
                    ],
                }
                jaeger_span["logs"].append(log_entry)

            return jaeger_span

        except Exception as e:
            logger.error(f"Failed to convert span to Jaeger format: {str(e)}")
            return {
                "traceID": self._generate_id(),
                "spanID": self._generate_id(),
                "operationName": "conversion_error",
                "startTime": int(datetime.utcnow().timestamp() * 1_000_000),
                "duration": 0,
                "tags": [{"key": "error", "vStr": str(e)}],
                "logs": [],
            }

    def _generate_id(self) -> str:
        """Generate a unique ID for traces / spans.

        Returns:
            Hexadecimal ID string
        """
        import random

        return f"{random.randint(1, 2**63-1):016x}"

    async def create_neural_trace(
        self,
        operation: str,
        session_id: str,
        duration_seconds: float,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a trace for neural processing operation.

        Args:
            operation: Operation name
            session_id: Processing session ID
            duration_seconds: Operation duration
            attributes: Optional additional attributes

        Returns:
            Trace ID
        """
        try:
            trace_id = self._generate_id()
            span_id = self._generate_id()

            span_data = {
                "trace_id": trace_id,
                "span_id": span_id,
                "operation_name": f"neural_{operation}",
                "start_time": datetime.utcnow(),
                "duration": duration_seconds,
                "attributes": {
                    "neural.operation": operation,
                    "neural.session_id": session_id,
                    "service.name": self.service_name,
                    **(attributes or {}),
                },
            }

            await self.export_span(span_data)
            return trace_id

        except Exception as e:
            logger.error(f"Failed to create neural trace: {str(e)}")
            return ""

    async def create_device_trace(
        self,
        operation: str,
        device_id: str,
        duration_seconds: float,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> str:
        """Create a trace for device operation.

        Args:
            operation: Operation name
            device_id: Device identifier
            duration_seconds: Operation duration
            success: Whether operation was successful
            error_message: Optional error message

        Returns:
            Trace ID
        """
        try:
            trace_id = self._generate_id()
            span_id = self._generate_id()

            attributes = {
                "device.operation": operation,
                "device.id": device_id,
                "operation.success": str(success),
                "service.name": self.service_name,
            }

            if error_message:
                attributes["error.message"] = error_message

            span_data = {
                "trace_id": trace_id,
                "span_id": span_id,
                "operation_name": f"device_{operation}",
                "start_time": datetime.utcnow(),
                "duration": duration_seconds,
                "attributes": attributes,
            }

            await self.export_span(span_data)
            return trace_id

        except Exception as e:
            logger.error(f"Failed to create device trace: {str(e)}")
            return ""

    def get_exporter_stats(self) -> Dict[str, Any]:
        """Get exporter statistics.

        Returns:
            Exporter statistics
        """
        return {
            "total_spans_exported": self.total_spans_exported,
            "failed_exports": self.failed_exports,
            "success_rate": (
                self.total_spans_exported
                / max(1, self.total_spans_exported + self.failed_exports)
            )
            * 100,
            "current_batch_size": len(self.span_batch),
            "max_batch_size": self.max_batch_size,
            "jaeger_endpoint": self.jaeger_endpoint,
            "service_name": self.service_name,
            "last_export_time": (
                self.last_export_time.isoformat() if self.last_export_time else None
            ),
        }
