"""Buffer Manager - Efficient circular buffer management for real-time streams.

This module implements thread-safe circular buffers for managing streaming
neural signal data with support for sliding windows and overflow handling.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
import threading
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class StreamBuffer:
    """Circular buffer for a single stream."""

    session_id: str
    n_channels: int
    sampling_rate: float
    max_samples: int

    # Circular buffer
    buffer: np.ndarray = field(init=False)

    # Buffer state
    write_pos: int = 0
    sample_count: int = 0
    total_samples_written: int = 0

    # Timestamps
    timestamps: deque = field(default_factory=lambda: deque(maxlen=1000))
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_write: Optional[datetime] = None

    # Window tracking
    last_window_end: int = 0

    def __post_init__(self):
        """Initialize the circular buffer."""
        self.buffer = np.zeros((self.n_channels, self.max_samples), dtype=np.float32)
        logger.debug(
            f"Created buffer for session {self.session_id}: "
            f"{self.n_channels} channels, {self.max_samples} samples"
        )

    def add_samples(self, data: np.ndarray, timestamp: Optional[float] = None) -> bool:
        """Add samples to the circular buffer.

        Args:
            data: Signal data (channels x samples)
            timestamp: Optional timestamp for synchronization

        Returns:
            True if successful, False if buffer would overflow
        """
        n_new_samples = data.shape[1]

        # Check if data would overflow buffer
        if n_new_samples > self.max_samples:
            logger.error(f"Data chunk ({n_new_samples} samples) exceeds buffer size")
            return False

        # Handle circular wrapping
        if self.write_pos + n_new_samples <= self.max_samples:
            # Simple case: no wrapping needed
            self.buffer[:, self.write_pos : self.write_pos + n_new_samples] = data
        else:
            # Need to wrap around
            first_part = self.max_samples - self.write_pos
            self.buffer[:, self.write_pos :] = data[:, :first_part]
            self.buffer[:, : n_new_samples - first_part] = data[:, first_part:]

        # Update state
        self.write_pos = (self.write_pos + n_new_samples) % self.max_samples
        self.sample_count = min(self.sample_count + n_new_samples, self.max_samples)
        self.total_samples_written += n_new_samples
        self.last_write = datetime.utcnow()

        # Store timestamp if provided
        if timestamp is not None:
            self.timestamps.append((self.total_samples_written, timestamp))

        return True

    def get_samples(
        self, n_samples: int, from_end: bool = True
    ) -> Optional[np.ndarray]:
        """Get samples from the buffer.

        Args:
            n_samples: Number of samples to retrieve
            from_end: If True, get most recent samples; if False, get oldest

        Returns:
            Signal data or None if not enough samples
        """
        if n_samples > self.sample_count:
            return None

        if from_end:
            # Get most recent samples
            start_pos = (self.write_pos - n_samples) % self.max_samples
        else:
            # Get oldest samples
            if self.sample_count < self.max_samples:
                start_pos = 0
            else:
                start_pos = self.write_pos

        # Extract samples handling circular wrap
        if start_pos + n_samples <= self.max_samples:
            # Simple case: no wrapping
            return self.buffer[:, start_pos : start_pos + n_samples].copy()
        else:
            # Need to handle wrap
            first_part = self.max_samples - start_pos
            result = np.empty((self.n_channels, n_samples), dtype=np.float32)
            result[:, :first_part] = self.buffer[:, start_pos:]
            result[:, first_part:] = self.buffer[:, : n_samples - first_part]
            return result

    def get_windows(
        self, window_size: int, step_size: int
    ) -> List[Tuple[np.ndarray, Dict[str, Any]]]:
        """Get sliding windows from the buffer.

        Args:
            window_size: Size of each window in samples
            step_size: Step between windows in samples

        Returns:
            List of (window_data, window_info) tuples
        """
        windows = []

        # Calculate available windows
        if self.sample_count < window_size:
            return windows

        # Start from last processed position
        current_pos = self.last_window_end

        while current_pos + window_size <= self.sample_count:
            # Get window data
            window_data = self.get_window_at_position(current_pos, window_size)

            if window_data is not None:
                # Create window info
                window_info = {
                    "start_sample": current_pos,
                    "end_sample": current_pos + window_size,
                    "window_size": window_size,
                    "timestamp": self._estimate_timestamp(current_pos),
                }

                windows.append((window_data, window_info))

            current_pos += step_size

        # Update last window position
        if windows:
            self.last_window_end = (
                windows[-1][1]["end_sample"] - window_size + step_size
            )

        return windows

    def get_window_at_position(
        self, position: int, window_size: int
    ) -> Optional[np.ndarray]:
        """Get a window at a specific position in the buffer.

        Args:
            position: Starting position (0 = oldest sample)
            window_size: Size of the window

        Returns:
            Window data or None
        """
        if position + window_size > self.sample_count:
            return None

        # Calculate actual buffer position
        if self.sample_count < self.max_samples:
            # Buffer not full yet
            buffer_pos = position
        else:
            # Buffer is full, adjust for circular nature
            buffer_pos = (self.write_pos + position) % self.max_samples

        # Extract window
        if buffer_pos + window_size <= self.max_samples:
            # Simple case
            return self.buffer[:, buffer_pos : buffer_pos + window_size].copy()
        else:
            # Handle wrap
            first_part = self.max_samples - buffer_pos
            result = np.empty((self.n_channels, window_size), dtype=np.float32)
            result[:, :first_part] = self.buffer[:, buffer_pos:]
            result[:, first_part:] = self.buffer[:, : window_size - first_part]
            return result

    def clear(self) -> None:
        """Clear the buffer."""
        self.buffer.fill(0)
        self.write_pos = 0
        self.sample_count = 0
        self.last_window_end = 0
        self.timestamps.clear()

    def _estimate_timestamp(self, sample_position: int) -> Optional[float]:
        """Estimate timestamp for a sample position.

        Args:
            sample_position: Position in samples from start

        Returns:
            Estimated timestamp or None
        """
        if not self.timestamps:
            return None

        # Find closest timestamp reference
        for total_samples, timestamp in reversed(self.timestamps):
            if (
                total_samples
                <= self.total_samples_written - self.sample_count + sample_position
            ):
                # Extrapolate from this reference
                sample_diff = (
                    self.total_samples_written
                    - self.sample_count
                    + sample_position
                    - total_samples
                )
                time_diff = sample_diff / self.sampling_rate
                return timestamp + time_diff

        return None


class BufferManager:
    """Manages multiple stream buffers."""

    def __init__(self, max_duration: float = 10.0, sampling_rate: float = 1000.0):
        """Initialize buffer manager.

        Args:
            max_duration: Maximum buffer duration in seconds
            sampling_rate: Default sampling rate
        """
        self.max_duration = max_duration
        self.default_sampling_rate = sampling_rate

        # Stream buffers
        self.buffers: Dict[str, StreamBuffer] = {}
        self._buffer_lock = threading.RLock()

        logger.info(f"BufferManager initialized: max duration {max_duration}s")

    async def create_stream_buffer(
        self, session_id: str, stream_info: Dict[str, Any]
    ) -> bool:
        """Create a new stream buffer.

        Args:
            session_id: Unique session identifier
            stream_info: Stream metadata

        Returns:
            Success status
        """
        try:
            with self._buffer_lock:
                if session_id in self.buffers:
                    logger.warning(f"Buffer already exists for session {session_id}")
                    return False

                # Extract stream parameters
                n_channels = stream_info.get("n_channels", 1)
                sampling_rate = stream_info.get(
                    "sampling_rate", self.default_sampling_rate
                )

                # Calculate buffer size
                max_samples = int(self.max_duration * sampling_rate)

                # Create buffer
                buffer = StreamBuffer(
                    session_id=session_id,
                    n_channels=n_channels,
                    sampling_rate=sampling_rate,
                    max_samples=max_samples,
                )

                self.buffers[session_id] = buffer

                logger.info(
                    f"Created buffer for session {session_id}: "
                    f"{n_channels} channels, {max_samples} samples"
                )

                return True

        except Exception as e:
            logger.error(f"Error creating stream buffer: {str(e)}")
            return False

    async def add_samples(
        self, session_id: str, data: np.ndarray, timestamp: Optional[float] = None
    ) -> bool:
        """Add samples to a stream buffer.

        Args:
            session_id: Session identifier
            data: Signal data (channels x samples)
            timestamp: Optional timestamp

        Returns:
            Success status
        """
        with self._buffer_lock:
            buffer = self.buffers.get(session_id)
            if not buffer:
                logger.error(f"No buffer found for session {session_id}")
                return False

            # Validate data shape
            if data.shape[0] != buffer.n_channels:
                logger.error(
                    f"Channel mismatch: expected {buffer.n_channels}, "
                    f"got {data.shape[0]}"
                )
                return False

            return buffer.add_samples(data, timestamp)

    async def get_samples(
        self, session_id: str, n_samples: int, from_end: bool = True
    ) -> Optional[np.ndarray]:
        """Get samples from a stream buffer.

        Args:
            session_id: Session identifier
            n_samples: Number of samples to retrieve
            from_end: Get most recent (True) or oldest (False) samples

        Returns:
            Signal data or None
        """
        with self._buffer_lock:
            buffer = self.buffers.get(session_id)
            if not buffer:
                return None

            return buffer.get_samples(n_samples, from_end)

    async def get_windows(
        self, session_id: str, window_size: int, step_size: int
    ) -> List[Tuple[np.ndarray, Dict[str, Any]]]:
        """Get sliding windows from a stream buffer.

        Args:
            session_id: Session identifier
            window_size: Window size in samples
            step_size: Step between windows

        Returns:
            List of windows with metadata
        """
        with self._buffer_lock:
            buffer = self.buffers.get(session_id)
            if not buffer:
                return []

            return buffer.get_windows(window_size, step_size)

    def get_stream_buffer(self, session_id: str) -> Optional[StreamBuffer]:
        """Get stream buffer instance.

        Args:
            session_id: Session identifier

        Returns:
            StreamBuffer or None
        """
        with self._buffer_lock:
            return self.buffers.get(session_id)

    def get_buffer_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get buffer status information.

        Args:
            session_id: Session identifier

        Returns:
            Status dictionary or None
        """
        with self._buffer_lock:
            buffer = self.buffers.get(session_id)
            if not buffer:
                return None

            return {
                "session_id": session_id,
                "n_channels": buffer.n_channels,
                "sampling_rate": buffer.sampling_rate,
                "max_samples": buffer.max_samples,
                "current_samples": buffer.sample_count,
                "total_samples_written": buffer.total_samples_written,
                "buffer_fill_percent": (buffer.sample_count / buffer.max_samples) * 100,
                "created_at": buffer.created_at.isoformat(),
                "last_write": (
                    buffer.last_write.isoformat() if buffer.last_write else None
                ),
            }

    def get_all_sessions(self) -> List[str]:
        """Get list of all active sessions.

        Returns:
            List of session IDs
        """
        with self._buffer_lock:
            return list(self.buffers.keys())

    async def clear_buffer(self, session_id: str) -> bool:
        """Clear a stream buffer.

        Args:
            session_id: Session identifier

        Returns:
            Success status
        """
        with self._buffer_lock:
            buffer = self.buffers.get(session_id)
            if not buffer:
                return False

            buffer.clear()
            logger.info(f"Cleared buffer for session {session_id}")
            return True

    async def remove_stream_buffer(self, session_id: str) -> bool:
        """Remove a stream buffer.

        Args:
            session_id: Session identifier

        Returns:
            Success status
        """
        with self._buffer_lock:
            if session_id in self.buffers:
                del self.buffers[session_id]
                logger.info(f"Removed buffer for session {session_id}")
                return True
            return False

    def cleanup_old_buffers(self, max_age_seconds: float = 3600) -> int:
        """Remove buffers older than specified age.

        Args:
            max_age_seconds: Maximum age in seconds

        Returns:
            Number of buffers removed
        """
        removed = 0
        current_time = datetime.utcnow()

        with self._buffer_lock:
            sessions_to_remove = []

            for session_id, buffer in self.buffers.items():
                age = (current_time - buffer.created_at).total_seconds()
                if age > max_age_seconds:
                    sessions_to_remove.append(session_id)

            for session_id in sessions_to_remove:
                del self.buffers[session_id]
                removed += 1

        if removed > 0:
            logger.info(f"Cleaned up {removed} old buffers")

        return removed
