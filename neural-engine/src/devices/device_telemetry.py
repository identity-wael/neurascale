"""Device telemetry collection and export."""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Callable, Protocol, IO
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import gzip
from pathlib import Path

logger = logging.getLogger(__name__)


class TelemetryType(Enum):
    """Types of telemetry data."""

    DEVICE_INFO = "device_info"
    CONNECTION = "connection"
    DATA_FLOW = "data_flow"
    SIGNAL_QUALITY = "signal_quality"
    PERFORMANCE = "performance"
    ERROR = "error"
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"


@dataclass
class TelemetryEvent:
    """Single telemetry event."""

    event_id: str
    device_id: str
    event_type: TelemetryType
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "device_id": self.device_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "metadata": self.metadata,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


class TelemetryExporter(Protocol):
    """Protocol for telemetry exporters."""

    async def export(self, events: List[TelemetryEvent]) -> bool:
        """Export telemetry events."""
        ...

    async def close(self) -> None:
        """Close exporter resources."""
        ...


class FileTelemetryExporter:
    """Export telemetry to local files."""

    def __init__(
        self,
        output_dir: Path,
        compress: bool = True,
        max_file_size_mb: int = 100,
    ):
        """
        Initialize file exporter.

        Args:
            output_dir: Directory to write telemetry files
            compress: Whether to compress files with gzip
            max_file_size_mb: Maximum file size before rotation
        """
        self.output_dir = Path(output_dir)
        self.compress = compress
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Current file
        self._current_file: Optional[IO[bytes]] = None
        self._current_size: int = 0
        self._file_counter = 0

    async def export(self, events: List[TelemetryEvent]) -> bool:
        """Export events to file."""
        try:
            for event in events:
                await self._write_event(event)
            return True
        except Exception as e:
            logger.error(f"Failed to export telemetry to file: {e}")
            return False

    async def _write_event(self, event: TelemetryEvent) -> None:
        """Write single event to file."""
        # Get or create file
        if self._current_file is None or self._current_size >= self.max_file_size_bytes:
            await self._rotate_file()

        # Write event
        event_json = event.to_json() + "\n"
        event_bytes = event_json.encode("utf-8")

        if self.compress:
            event_bytes = gzip.compress(event_bytes)

        self._current_file.write(event_bytes)
        self._current_size += len(event_bytes)

    async def _rotate_file(self) -> None:
        """Rotate to new file."""
        # Close current file
        if self._current_file:
            self._current_file.close()

        # Generate new filename
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self._file_counter += 1

        if self.compress:
            filename = f"telemetry_{timestamp}_{self._file_counter:04d}.jsonl.gz"
            mode = "wb"
        else:
            filename = f"telemetry_{timestamp}_{self._file_counter:04d}.jsonl"
            mode = "w"

        filepath = self.output_dir / filename
        self._current_file = open(filepath, mode + "b")  # Open in binary mode
        self._current_size = 0

        logger.info(f"Rotated telemetry file to: {filename}")

    async def close(self) -> None:
        """Close file resources."""
        if self._current_file:
            self._current_file.close()
            self._current_file = None


class CloudTelemetryExporter:
    """Export telemetry to cloud storage (placeholder for GCP integration)."""

    def __init__(self, project_id: str, dataset_id: str, table_id: str):
        """
        Initialize cloud exporter.

        Args:
            project_id: GCP project ID
            dataset_id: BigQuery dataset ID
            table_id: BigQuery table ID
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id

        # TODO: Initialize BigQuery client when GCP integration is ready
        logger.info(
            f"Cloud telemetry exporter initialized for "
            f"{project_id}.{dataset_id}.{table_id}"
        )

    async def export(self, events: List[TelemetryEvent]) -> bool:
        """Export events to cloud."""
        # TODO: Implement BigQuery streaming insert
        logger.debug(f"Would export {len(events)} events to BigQuery")
        return True

    async def close(self) -> None:
        """Close cloud resources."""
        pass


class DeviceTelemetryCollector:
    """Collect and manage device telemetry."""

    def __init__(
        self,
        buffer_size: int = 1000,
        flush_interval: float = 60.0,
        exporters: Optional[List[TelemetryExporter]] = None,
    ):
        """
        Initialize telemetry collector.

        Args:
            buffer_size: Maximum events to buffer before flush
            flush_interval: Interval to flush buffer in seconds
            exporters: List of telemetry exporters
        """
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self.exporters = exporters or []

        # Event buffer
        self._buffer: List[TelemetryEvent] = []
        self._buffer_lock = asyncio.Lock()

        # Event counter for IDs
        self._event_counter = 0

        # Flush task
        self._flush_task: Optional[asyncio.Task] = None
        self._stop_flushing = asyncio.Event()

        # Telemetry filters
        self._filters: List[Callable[[TelemetryEvent], bool]] = []

        # Statistics
        self._stats = {
            "events_collected": 0,
            "events_exported": 0,
            "events_filtered": 0,
            "export_failures": 0,
        }

    def add_exporter(self, exporter: TelemetryExporter) -> None:
        """Add a telemetry exporter."""
        self.exporters.append(exporter)

    def add_filter(self, filter_func: Callable[[TelemetryEvent], bool]) -> None:
        """Add a filter function (returns True to keep event)."""
        self._filters.append(filter_func)

    async def start(self) -> None:
        """Start telemetry collection."""
        if self._flush_task and not self._flush_task.done():
            logger.warning("Telemetry collection already started")
            return

        self._stop_flushing.clear()
        self._flush_task = asyncio.create_task(self._flush_loop())
        logger.info("Started telemetry collection")

    async def stop(self) -> None:
        """Stop telemetry collection."""
        self._stop_flushing.set()

        # Flush remaining events
        await self._flush_buffer()

        if self._flush_task:
            await self._flush_task
            self._flush_task = None

        # Close exporters
        for exporter in self.exporters:
            await exporter.close()

        logger.info(f"Stopped telemetry collection. Stats: {self._stats}")

    async def _flush_loop(self) -> None:
        """Periodic flush loop."""
        while not self._stop_flushing.is_set():
            try:
                await asyncio.sleep(self.flush_interval)
                await self._flush_buffer()
            except Exception as e:
                logger.error(f"Error in telemetry flush loop: {e}")

    async def _flush_buffer(self):
        """Flush buffer to exporters."""
        async with self._buffer_lock:
            if not self._buffer:
                return

            events_to_export = self._buffer.copy()
            self._buffer.clear()

        # Export to all exporters
        export_tasks = []
        for exporter in self.exporters:
            export_tasks.append(exporter.export(events_to_export))

        if export_tasks:
            results = await asyncio.gather(*export_tasks, return_exceptions=True)

            # Count successes and failures
            successes = sum(1 for r in results if r is True)
            failures = len(results) - successes

            if successes > 0:
                self._stats["events_exported"] += len(events_to_export)
            if failures > 0:
                self._stats["export_failures"] += failures
                logger.warning(f"Failed to export to {failures} exporters")

    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        self._event_counter += 1
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"evt_{timestamp}_{self._event_counter:06d}"

    async def collect_event(
        self,
        device_id: str,
        event_type: TelemetryType,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Collect a telemetry event.

        Args:
            device_id: Device identifier
            event_type: Type of telemetry event
            data: Event data
            metadata: Optional event metadata
        """
        event = TelemetryEvent(
            event_id=self._generate_event_id(),
            device_id=device_id,
            event_type=event_type,
            data=data,
            metadata=metadata or {},
        )

        # Apply filters
        for filter_func in self._filters:
            try:
                if not filter_func(event):
                    self._stats["events_filtered"] += 1
                    return
            except Exception as e:
                logger.error(f"Error in telemetry filter: {e}")

        # Add to buffer
        async with self._buffer_lock:
            self._buffer.append(event)
            self._stats["events_collected"] += 1

            # Flush if buffer is full
            if len(self._buffer) >= self.buffer_size:
                asyncio.create_task(self._flush_buffer())

    # Convenience methods for common telemetry events

    async def collect_device_info(self, device_id: str, info: Dict[str, Any]):
        """Collect device information telemetry."""
        await self.collect_event(
            device_id=device_id,
            event_type=TelemetryType.DEVICE_INFO,
            data=info,
        )

    async def collect_connection_event(
        self,
        device_id: str,
        event: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Collect connection event telemetry."""
        await self.collect_event(
            device_id=device_id,
            event_type=TelemetryType.CONNECTION,
            data={
                "event": event,
                "details": details or {},
            },
        )

    async def collect_data_flow(
        self,
        device_id: str,
        packets_received: int,
        packets_dropped: int,
        data_rate_hz: float,
        latency_ms: float,
    ):
        """Collect data flow telemetry."""
        await self.collect_event(
            device_id=device_id,
            event_type=TelemetryType.DATA_FLOW,
            data={
                "packets_received": packets_received,
                "packets_dropped": packets_dropped,
                "data_rate_hz": data_rate_hz,
                "latency_ms": latency_ms,
            },
        )

    async def collect_signal_quality(
        self,
        device_id: str,
        channel_id: int,
        snr_db: float,
        quality_level: str,
        impedance_ohms: Optional[float] = None,
    ):
        """Collect signal quality telemetry."""
        await self.collect_event(
            device_id=device_id,
            event_type=TelemetryType.SIGNAL_QUALITY,
            data={
                "channel_id": channel_id,
                "snr_db": snr_db,
                "quality_level": quality_level,
                "impedance_ohms": impedance_ohms,
            },
        )

    async def collect_error(
        self,
        device_id: str,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
    ):
        """Collect error telemetry."""
        await self.collect_event(
            device_id=device_id,
            event_type=TelemetryType.ERROR,
            data={
                "error_type": error_type,
                "error_message": error_message,
                "stack_trace": stack_trace,
            },
        )

    async def collect_user_action(
        self,
        device_id: str,
        action: str,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        """Collect user action telemetry."""
        await self.collect_event(
            device_id=device_id,
            event_type=TelemetryType.USER_ACTION,
            data={
                "action": action,
                "parameters": parameters or {},
            },
        )

    def get_statistics(self) -> Dict[str, int]:
        """Get telemetry statistics."""
        return self._stats.copy()
