"""Lab Streaming Layer (LSL) Integration for NeuraScale Neural Engine.

This module provides comprehensive LSL stream management capabilities
for real-time data streaming and device integration.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import threading
import time

try:
    import pylsl

    LSL_AVAILABLE = True
except ImportError:
    LSL_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("pylsl not available, LSL integration disabled")

from .base import DeviceInfo, DataSample, DeviceEvent

logger = logging.getLogger(__name__)


class LSLStreamType(Enum):
    """LSL stream data types."""

    EEG = "EEG"
    MARKER = "Markers"
    ACCELEROMETER = "Accelerometer"
    GYROSCOPE = "Gyroscope"
    IMPEDANCE = "Impedance"
    CUSTOM = "Custom"


@dataclass
class LSLStreamInfo:
    """LSL stream information and metadata."""

    # Core stream properties
    name: str
    stream_type: LSLStreamType
    channel_count: int
    sampling_rate: float
    channel_format: str = "float32"
    source_id: str = ""

    # Stream metadata
    device_info: Optional[DeviceInfo] = None
    channel_labels: List[str] = field(default_factory=list)
    channel_units: List[str] = field(default_factory=list)
    manufacturer: str = ""

    # Stream state
    stream_id: Optional[int] = None
    is_active: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_data_time: Optional[datetime] = None

    # Performance metrics
    data_rate_hz: float = 0.0
    latency_ms: float = 0.0
    packet_loss_rate: float = 0.0


@dataclass
class LSLInletInfo:
    """LSL inlet connection information."""

    stream_info: LSLStreamInfo
    inlet: Optional[Any] = None  # pylsl.StreamInlet
    buffer_size: int = 1000
    timeout_seconds: float = 1.0

    # Connection state
    is_connected: bool = False
    samples_received: int = 0
    last_sample_time: Optional[datetime] = None

    # Data buffers
    data_buffer: List[np.ndarray] = field(default_factory=list)
    timestamp_buffer: List[float] = field(default_factory=list)


@dataclass
class LSLOutletInfo:
    """LSL outlet streaming information."""

    stream_info: LSLStreamInfo
    outlet: Optional[Any] = None  # pylsl.StreamOutlet

    # Streaming state
    is_streaming: bool = False
    samples_sent: int = 0
    last_send_time: Optional[datetime] = None


@dataclass
class LSLIntegrationConfig:
    """Configuration for LSL integration."""

    # Discovery settings
    discovery_timeout_seconds: float = 2.0
    auto_discovery_enabled: bool = True
    discovery_interval_seconds: int = 30

    # Stream management
    max_concurrent_inlets: int = 10
    max_concurrent_outlets: int = 5
    default_buffer_size: int = 1000
    default_timeout_seconds: float = 1.0

    # Data processing
    chunk_size: int = 32
    enable_data_validation: bool = True
    enable_timestamp_correction: bool = True

    # Performance monitoring
    enable_performance_monitoring: bool = True
    performance_update_interval_seconds: int = 5


class LSLIntegration:
    """Comprehensive Lab Streaming Layer integration service."""

    def __init__(self, config: LSLIntegrationConfig = None):
        """Initialize LSL integration.

        Args:
            config: LSL integration configuration
        """
        if not LSL_AVAILABLE:
            raise ImportError("pylsl is required for LSL integration")

        self.config = config or LSLIntegrationConfig()

        # Stream management
        self.discovered_streams: Dict[str, LSLStreamInfo] = {}
        self.active_inlets: Dict[str, LSLInletInfo] = {}
        self.active_outlets: Dict[str, LSLOutletInfo] = {}

        # Event callbacks
        self.stream_callbacks: List[Callable[[str, LSLStreamInfo], None]] = []
        self.data_callbacks: List[Callable[[str, DataSample], None]] = []
        self.event_callbacks: List[Callable[[DeviceEvent], None]] = []

        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        self.is_running = False
        self._shutdown_event = asyncio.Event()

        # Threading for LSL operations
        self._lsl_thread: Optional[threading.Thread] = None
        self._lsl_running = False

        # Performance tracking
        self.stats = {
            "streams_discovered": 0,
            "inlets_created": 0,
            "outlets_created": 0,
            "samples_received": 0,
            "samples_sent": 0,
            "data_rate_hz": 0.0,
        }

        logger.info("LSLIntegration initialized")

    async def start(self) -> None:
        """Start LSL integration services."""
        if self.is_running:
            logger.warning("LSLIntegration already running")
            return

        logger.info("Starting LSLIntegration...")
        self.is_running = True
        self._shutdown_event.clear()

        # Start background tasks
        if self.config.auto_discovery_enabled:
            task = asyncio.create_task(self._discovery_loop())
            self.background_tasks.append(task)

        task = asyncio.create_task(self._data_processing_loop())
        self.background_tasks.append(task)

        if self.config.enable_performance_monitoring:
            task = asyncio.create_task(self._performance_monitoring_loop())
            self.background_tasks.append(task)

        # Start LSL processing thread
        self._lsl_running = True
        self._lsl_thread = threading.Thread(
            target=self._lsl_processing_thread, daemon=True
        )
        self._lsl_thread.start()

        logger.info("LSLIntegration started successfully")

    async def stop(self) -> None:
        """Stop LSL integration services."""
        if not self.is_running:
            return

        logger.info("Stopping LSLIntegration...")
        self.is_running = False
        self._shutdown_event.set()

        # Stop LSL thread
        self._lsl_running = False
        if self._lsl_thread and self._lsl_thread.is_alive():
            self._lsl_thread.join(timeout=5.0)

        # Disconnect all streams
        await self.disconnect_all_inlets()
        await self.stop_all_outlets()

        # Cancel background tasks
        for task in self.background_tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)

        self.background_tasks.clear()
        logger.info("LSLIntegration stopped")

    async def discover_streams(self, timeout: float = None) -> List[LSLStreamInfo]:
        """Discover available LSL streams.

        Args:
            timeout: Discovery timeout in seconds

        Returns:
            List of discovered stream information
        """
        timeout = timeout or self.config.discovery_timeout_seconds

        try:
            # Run LSL discovery in thread to avoid blocking
            loop = asyncio.get_event_loop()
            streams = await loop.run_in_executor(
                None, self._discover_streams_sync, timeout
            )

            # Update discovered streams
            for stream_info in streams:
                stream_id = f"{stream_info.name}_{stream_info.source_id}"
                self.discovered_streams[stream_id] = stream_info

            self.stats["streams_discovered"] = len(self.discovered_streams)

            self._emit_event(
                "streams_discovered",
                {"count": len(streams), "streams": [s.name for s in streams]},
            )

            logger.info(f"Discovered {len(streams)} LSL streams")
            return streams

        except Exception as e:
            logger.error(f"Error discovering LSL streams: {str(e)}")
            return []

    async def create_inlet(
        self, stream_name: str, buffer_size: int = None, timeout: float = None
    ) -> bool:
        """Create LSL inlet for receiving data.

        Args:
            stream_name: Name or ID of the stream
            buffer_size: Buffer size for inlet
            timeout: Timeout for operations

        Returns:
            True if inlet created successfully
        """
        if len(self.active_inlets) >= self.config.max_concurrent_inlets:
            logger.error(
                f"Maximum concurrent inlets ({self.config.max_concurrent_inlets}) reached"
            )
            return False

        # Find stream info
        stream_info = None
        for stream_id, info in self.discovered_streams.items():
            if info.name == stream_name or stream_id == stream_name:
                stream_info = info
                break

        if not stream_info:
            logger.error(f"Stream not found: {stream_name}")
            return False

        try:
            # Create inlet in thread
            loop = asyncio.get_event_loop()
            inlet = await loop.run_in_executor(
                None, self._create_inlet_sync, stream_info, buffer_size, timeout
            )

            if inlet:
                inlet_info = LSLInletInfo(
                    stream_info=stream_info,
                    inlet=inlet,
                    buffer_size=buffer_size or self.config.default_buffer_size,
                    timeout_seconds=timeout or self.config.default_timeout_seconds,
                    is_connected=True,
                )

                stream_id = f"{stream_info.name}_{stream_info.source_id}"
                self.active_inlets[stream_id] = inlet_info
                self.stats["inlets_created"] += 1

                self._emit_event("inlet_created", {"stream_name": stream_name})
                logger.info(f"Created LSL inlet for stream: {stream_name}")
                return True

        except Exception as e:
            logger.error(f"Error creating LSL inlet for {stream_name}: {str(e)}")

        return False

    async def disconnect_inlet(self, stream_name: str) -> bool:
        """Disconnect LSL inlet.

        Args:
            stream_name: Name or ID of the stream

        Returns:
            True if disconnection successful
        """
        stream_id = None
        for sid, inlet_info in self.active_inlets.items():
            if inlet_info.stream_info.name == stream_name or sid == stream_name:
                stream_id = sid
                break

        if not stream_id:
            logger.warning(f"Inlet not found: {stream_name}")
            return False

        try:
            inlet_info = self.active_inlets[stream_id]

            # Close inlet
            if inlet_info.inlet:
                inlet_info.inlet.close_stream()

            # Remove from active inlets
            del self.active_inlets[stream_id]

            self._emit_event("inlet_disconnected", {"stream_name": stream_name})
            logger.info(f"Disconnected LSL inlet: {stream_name}")
            return True

        except Exception as e:
            logger.error(f"Error disconnecting LSL inlet {stream_name}: {str(e)}")
            return False

    async def disconnect_all_inlets(self) -> None:
        """Disconnect all active inlets."""
        inlet_names = list(self.active_inlets.keys())

        for stream_id in inlet_names:
            stream_name = self.active_inlets[stream_id].stream_info.name
            await self.disconnect_inlet(stream_name)

        logger.info("Disconnected all LSL inlets")

    async def create_outlet(
        self, stream_info: LSLStreamInfo, chunk_size: int = None
    ) -> bool:
        """Create LSL outlet for sending data.

        Args:
            stream_info: Stream information
            chunk_size: Chunk size for outlet

        Returns:
            True if outlet created successfully
        """
        if len(self.active_outlets) >= self.config.max_concurrent_outlets:
            logger.error(
                f"Maximum concurrent outlets ({self.config.max_concurrent_outlets}) reached"
            )
            return False

        try:
            # Create outlet in thread
            loop = asyncio.get_event_loop()
            outlet = await loop.run_in_executor(
                None, self._create_outlet_sync, stream_info, chunk_size
            )

            if outlet:
                outlet_info = LSLOutletInfo(
                    stream_info=stream_info, outlet=outlet, is_streaming=True
                )

                stream_id = f"{stream_info.name}_{stream_info.source_id}"
                self.active_outlets[stream_id] = outlet_info
                self.stats["outlets_created"] += 1

                self._emit_event("outlet_created", {"stream_name": stream_info.name})
                logger.info(f"Created LSL outlet for stream: {stream_info.name}")
                return True

        except Exception as e:
            logger.error(f"Error creating LSL outlet for {stream_info.name}: {str(e)}")

        return False

    async def stop_outlet(self, stream_name: str) -> bool:
        """Stop LSL outlet.

        Args:
            stream_name: Name of the stream

        Returns:
            True if stop successful
        """
        stream_id = None
        for sid, outlet_info in self.active_outlets.items():
            if outlet_info.stream_info.name == stream_name or sid == stream_name:
                stream_id = sid
                break

        if not stream_id:
            logger.warning(f"Outlet not found: {stream_name}")
            return False

        try:
            outlet_info = self.active_outlets[stream_id]
            outlet_info.is_streaming = False

            # Remove from active outlets
            del self.active_outlets[stream_id]

            self._emit_event("outlet_stopped", {"stream_name": stream_name})
            logger.info(f"Stopped LSL outlet: {stream_name}")
            return True

        except Exception as e:
            logger.error(f"Error stopping LSL outlet {stream_name}: {str(e)}")
            return False

    async def stop_all_outlets(self) -> None:
        """Stop all active outlets."""
        outlet_names = list(self.active_outlets.keys())

        for stream_id in outlet_names:
            stream_name = self.active_outlets[stream_id].stream_info.name
            await self.stop_outlet(stream_name)

        logger.info("Stopped all LSL outlets")

    async def send_data(
        self, stream_name: str, data: np.ndarray, timestamp: float = None
    ) -> bool:
        """Send data through LSL outlet.

        Args:
            stream_name: Name of the stream
            data: Data to send
            timestamp: Timestamp for data (optional)

        Returns:
            True if data sent successfully
        """
        outlet_info = None
        for outlet in self.active_outlets.values():
            if outlet.stream_info.name == stream_name:
                outlet_info = outlet
                break

        if not outlet_info or not outlet_info.is_streaming:
            logger.error(f"No active outlet found for stream: {stream_name}")
            return False

        try:
            # Send data in thread
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                None, self._send_data_sync, outlet_info.outlet, data, timestamp
            )

            if success:
                outlet_info.samples_sent += 1
                outlet_info.last_send_time = datetime.utcnow()
                self.stats["samples_sent"] += 1
                return True

        except Exception as e:
            logger.error(f"Error sending data to {stream_name}: {str(e)}")

        return False

    def add_stream_callback(
        self, callback: Callable[[str, LSLStreamInfo], None]
    ) -> None:
        """Add callback for stream events.

        Args:
            callback: Function to call when stream events occur
        """
        self.stream_callbacks.append(callback)

    def add_data_callback(self, callback: Callable[[str, DataSample], None]) -> None:
        """Add callback for data samples.

        Args:
            callback: Function to call when data is received
        """
        self.data_callbacks.append(callback)

    def add_event_callback(self, callback: Callable[[DeviceEvent], None]) -> None:
        """Add callback for LSL events.

        Args:
            callback: Function to call when LSL events occur
        """
        self.event_callbacks.append(callback)

    async def get_stream_info(self, stream_name: str) -> Optional[LSLStreamInfo]:
        """Get information about a stream.

        Args:
            stream_name: Name of the stream

        Returns:
            Stream information or None if not found
        """
        for stream_info in self.discovered_streams.values():
            if stream_info.name == stream_name:
                return stream_info
        return None

    async def get_active_streams(self) -> Dict[str, LSLStreamInfo]:
        """Get all active streams.

        Returns:
            Dictionary of active stream information
        """
        active_streams = {}

        # Add inlet streams
        for stream_id, inlet_info in self.active_inlets.items():
            active_streams[stream_id] = inlet_info.stream_info

        # Add outlet streams
        for stream_id, outlet_info in self.active_outlets.items():
            active_streams[stream_id] = outlet_info.stream_info

        return active_streams

    async def get_statistics(self) -> Dict[str, Any]:
        """Get LSL integration statistics.

        Returns:
            Statistics dictionary
        """
        return {
            **self.stats,
            "active_inlets": len(self.active_inlets),
            "active_outlets": len(self.active_outlets),
            "discovered_streams": len(self.discovered_streams),
            "lsl_available": LSL_AVAILABLE,
        }

    # Private methods

    def _discover_streams_sync(self, timeout: float) -> List[LSLStreamInfo]:
        """Synchronous stream discovery (runs in thread).

        Args:
            timeout: Discovery timeout

        Returns:
            List of discovered streams
        """
        streams = []

        try:
            # Discover streams
            stream_infos = pylsl.resolve_streams(timeout)

            for stream_info in stream_infos:
                # Convert to our format
                lsl_info = LSLStreamInfo(
                    name=stream_info.name(),
                    stream_type=LSLStreamType(stream_info.type()),
                    channel_count=stream_info.channel_count(),
                    sampling_rate=stream_info.nominal_srate(),
                    channel_format=stream_info.channel_format(),
                    source_id=stream_info.source_id(),
                    manufacturer=stream_info.desc()
                    .child("acquisition")
                    .child("manufacturer")
                    .first_child()
                    .value(),
                )

                # Extract channel labels
                channels = stream_info.desc().child("channels").child("channel")
                for i in range(lsl_info.channel_count):
                    if channels:
                        label = channels.child("label").first_child().value()
                        unit = channels.child("unit").first_child().value()

                        lsl_info.channel_labels.append(label or f"Ch{i + 1}")
                        lsl_info.channel_units.append(unit or "uV")

                        channels = channels.next_sibling()
                    else:
                        lsl_info.channel_labels.append(f"Ch{i + 1}")
                        lsl_info.channel_units.append("uV")

                streams.append(lsl_info)

        except Exception as e:
            logger.error(f"Error in synchronous stream discovery: {str(e)}")

        return streams

    def _create_inlet_sync(
        self,
        stream_info: LSLStreamInfo,
        buffer_size: Optional[int],
        timeout: Optional[float],
    ) -> Optional[Any]:
        """Create inlet synchronously (runs in thread).

        Args:
            stream_info: Stream information
            buffer_size: Buffer size
            timeout: Timeout

        Returns:
            pylsl.StreamInlet or None
        """
        try:
            # Find the stream
            streams = pylsl.resolve_stream("name", stream_info.name, timeout or 2.0)

            if not streams:
                logger.error(f"Stream not found: {stream_info.name}")
                return None

            # Create inlet
            inlet = pylsl.StreamInlet(
                streams[0],
                max_buflen=buffer_size or self.config.default_buffer_size,
                processing_flags=pylsl.proc_clocksync | pylsl.proc_dejitter,
            )

            # Open stream
            inlet.open_stream(timeout or self.config.default_timeout_seconds)

            return inlet

        except Exception as e:
            logger.error(f"Error creating inlet: {str(e)}")
            return None

    def _create_outlet_sync(
        self, stream_info: LSLStreamInfo, chunk_size: Optional[int]
    ) -> Optional[Any]:
        """Create outlet synchronously (runs in thread).

        Args:
            stream_info: Stream information
            chunk_size: Chunk size

        Returns:
            pylsl.StreamOutlet or None
        """
        try:
            # Create stream info
            info = pylsl.StreamInfo(
                stream_info.name,
                stream_info.stream_type.value,
                stream_info.channel_count,
                stream_info.sampling_rate,
                stream_info.channel_format,
                stream_info.source_id,
            )

            # Add channel descriptions
            channels = info.desc().append_child("channels")
            for i in range(stream_info.channel_count):
                ch = channels.append_child("channel")
                ch.append_child_value(
                    "label",
                    (
                        stream_info.channel_labels[i]
                        if i < len(stream_info.channel_labels)
                        else f"Ch{i + 1}"
                    ),
                )
                ch.append_child_value(
                    "unit",
                    (
                        stream_info.channel_units[i]
                        if i < len(stream_info.channel_units)
                        else "uV"
                    ),
                )
                ch.append_child_value("type", stream_info.stream_type.value)

            # Create outlet
            outlet = pylsl.StreamOutlet(info, chunk_size or self.config.chunk_size)

            return outlet

        except Exception as e:
            logger.error(f"Error creating outlet: {str(e)}")
            return None

    def _send_data_sync(
        self, outlet: Any, data: np.ndarray, timestamp: Optional[float]
    ) -> bool:
        """Send data synchronously (runs in thread).

        Args:
            outlet: pylsl.StreamOutlet
            data: Data to send
            timestamp: Timestamp

        Returns:
            True if successful
        """
        try:
            if timestamp is not None:
                outlet.push_sample(data.tolist(), timestamp)
            else:
                outlet.push_sample(data.tolist())
            return True

        except Exception as e:
            logger.error(f"Error sending data: {str(e)}")
            return False

    def _lsl_processing_thread(self) -> None:
        """Background thread for LSL data processing."""
        logger.info("Starting LSL processing thread")

        while self._lsl_running:
            try:
                # Process data from all active inlets
                for stream_id, inlet_info in list(self.active_inlets.items()):
                    self._process_inlet_data(stream_id, inlet_info)

                time.sleep(0.01)  # Small delay to prevent excessive CPU usage

            except Exception as e:
                logger.error(f"Error in LSL processing thread: {str(e)}")
                time.sleep(0.1)

        logger.info("LSL processing thread stopped")

    def _process_inlet_data(self, stream_id: str, inlet_info: LSLInletInfo) -> None:
        """Process data from an LSL inlet.

        Args:
            stream_id: Stream identifier
            inlet_info: Inlet information
        """
        if not inlet_info.inlet or not inlet_info.is_connected:
            return

        try:
            # Pull data chunk
            samples, timestamps = inlet_info.inlet.pull_chunk(
                timeout=0.0, max_samples=self.config.chunk_size  # Non-blocking
            )

            if samples:
                # Convert to numpy array
                # data = np.array(samples).T  # Transpose to get channels x samples
                # Process samples directly without intermediate variable

                # Process each sample
                for i, sample in enumerate(samples):
                    sample_data = np.array(sample)
                    timestamp = timestamps[i] if i < len(timestamps) else time.time()

                    # Create data sample
                    data_sample = DataSample(
                        timestamp=timestamp,
                        channel_data=sample_data,
                        sample_number=inlet_info.samples_received,
                        device_id=stream_id,
                        sampling_rate=inlet_info.stream_info.sampling_rate,
                    )

                    # Update metrics
                    inlet_info.samples_received += 1
                    inlet_info.last_sample_time = datetime.utcnow()
                    self.stats["samples_received"] += 1

                    # Call data callbacks
                    for callback in self.data_callbacks:
                        try:
                            callback(stream_id, data_sample)
                        except Exception as e:
                            logger.error(f"Error in LSL data callback: {str(e)}")

        except Exception as e:
            logger.error(f"Error processing inlet data for {stream_id}: {str(e)}")

    async def _discovery_loop(self) -> None:
        """Background task for periodic stream discovery."""
        logger.info("Starting LSL discovery loop")

        while not self._shutdown_event.is_set():
            try:
                await self.discover_streams()

            except Exception as e:
                logger.error(f"Error in LSL discovery loop: {str(e)}")

            # Wait for next discovery cycle
            try:
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=self.config.discovery_interval_seconds,
                )
                break  # Shutdown requested
            except asyncio.TimeoutError:
                continue  # Continue discovery

        logger.info("LSL discovery loop stopped")

    async def _data_processing_loop(self) -> None:
        """Background task for data processing coordination."""
        logger.info("Starting LSL data processing loop")

        while not self._shutdown_event.is_set():
            try:
                # Update stream performance metrics
                for inlet_info in self.active_inlets.values():
                    if inlet_info.last_sample_time:
                        time_diff = (
                            datetime.utcnow() - inlet_info.last_sample_time
                        ).total_seconds()
                        if time_diff > 0:
                            inlet_info.stream_info.data_rate_hz = 1.0 / time_diff

                await asyncio.sleep(0.1)  # Process every 100ms

            except Exception as e:
                logger.error(f"Error in LSL data processing loop: {str(e)}")
                await asyncio.sleep(1.0)

        logger.info("LSL data processing loop stopped")

    async def _performance_monitoring_loop(self) -> None:
        """Background task for performance monitoring."""
        logger.info("Starting LSL performance monitoring loop")

        while not self._shutdown_event.is_set():
            try:
                # Calculate overall data rate
                total_samples = (
                    self.stats["samples_received"] + self.stats["samples_sent"]
                )
                uptime = (datetime.utcnow() - datetime.utcnow()).total_seconds() or 1
                self.stats["data_rate_hz"] = total_samples / uptime

            except Exception as e:
                logger.error(f"Error in LSL performance monitoring: {str(e)}")

            # Wait for next monitoring cycle
            try:
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=self.config.performance_update_interval_seconds,
                )
                break  # Shutdown requested
            except asyncio.TimeoutError:
                continue  # Continue monitoring

        logger.info("LSL performance monitoring loop stopped")

    def _emit_event(self, event_type: str, data: Dict[str, Any] = None) -> None:
        """Emit LSL integration event.

        Args:
            event_type: Type of event
            data: Event data
        """
        event = DeviceEvent(
            event_type=event_type,
            device_id="lsl_integration",
            timestamp=datetime.utcnow(),
            data=data or {},
            severity="info",
        )

        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in LSL event callback: {str(e)}")
