"""
Circular buffer implementation for real-time data streaming
"""

import asyncio
from datetime import datetime
from typing import List, Optional
import numpy as np

from ..types import NeuralData


class CircularBuffer:
    """
    Thread-safe circular buffer for neural data with time-based windowing
    """

    def __init__(self, channels: int, buffer_duration_ms: float, sampling_rate: float):
        """
        Initialize circular buffer

        Args:
            channels: Number of channels
            buffer_duration_ms: Buffer duration in milliseconds
            sampling_rate: Sampling rate in Hz
        """
        self.channels = channels
        self.sampling_rate = sampling_rate
        self.buffer_duration_ms = buffer_duration_ms

        # Calculate buffer size in samples
        self.buffer_size = int((buffer_duration_ms / 1000.0) * sampling_rate)

        # Initialize circular buffer
        self.buffer = np.zeros((channels, self.buffer_size), dtype=np.float32)
        self.timestamps = np.zeros(self.buffer_size, dtype=np.float64)

        # Buffer position tracking
        self.write_pos = 0
        self.samples_written = 0

        # Thread safety
        self._lock = asyncio.Lock()

        # Metadata
        self.device_id: Optional[str] = None
        self.channel_names: Optional[List[str]] = None
        self.last_update: Optional[datetime] = None

    async def add_data(self, data: NeuralData) -> None:
        """
        Add data to circular buffer

        Args:
            data: Neural data to add
        """
        async with self._lock:
            # Store metadata on first write
            if self.device_id is None:
                self.device_id = data.device_id
                self.channel_names = data.channels

            # Get number of samples
            n_samples = data.data.shape[1]

            # Calculate positions
            start_pos = self.write_pos
            end_pos = (start_pos + n_samples) % self.buffer_size

            # Handle wraparound
            if end_pos > start_pos:
                # No wraparound
                self.buffer[:, start_pos:end_pos] = data.data
                self.timestamps[start_pos:end_pos] = np.linspace(
                    data.timestamp.timestamp(),
                    data.timestamp.timestamp() + (n_samples - 1) / self.sampling_rate,
                    n_samples,
                )
            else:
                # Wraparound occurred
                split_point = self.buffer_size - start_pos

                # Fill to end of buffer
                self.buffer[:, start_pos:] = data.data[:, :split_point]
                self.timestamps[start_pos:] = np.linspace(
                    data.timestamp.timestamp(),
                    data.timestamp.timestamp() + (split_point - 1) / self.sampling_rate,
                    split_point,
                )

                # Fill from beginning
                self.buffer[:, :end_pos] = data.data[:, split_point:]
                self.timestamps[:end_pos] = np.linspace(
                    data.timestamp.timestamp() + split_point / self.sampling_rate,
                    data.timestamp.timestamp() + (n_samples - 1) / self.sampling_rate,
                    n_samples - split_point,
                )

            # Update position and counters
            self.write_pos = end_pos
            self.samples_written += n_samples
            self.last_update = datetime.now()

    async def get_window(self, duration_ms: float) -> Optional[NeuralData]:
        """
        Get a window of data from the buffer

        Args:
            duration_ms: Duration of window in milliseconds

        Returns:
            Neural data for the requested window, or None if insufficient data
        """
        async with self._lock:
            # Calculate number of samples needed
            n_samples = int((duration_ms / 1000.0) * self.sampling_rate)

            # Check if we have enough data
            if self.samples_written < n_samples:
                return None

            # Calculate start position
            if self.samples_written >= self.buffer_size:
                # Buffer is full, use circular logic
                start_pos = (self.write_pos - n_samples) % self.buffer_size
            else:
                # Buffer not full yet
                start_pos = max(0, self.write_pos - n_samples)

            # Extract data
            if start_pos < self.write_pos:
                # No wraparound
                window_data = self.buffer[:, start_pos : self.write_pos].copy()
                window_timestamps = self.timestamps[start_pos : self.write_pos].copy()
            else:
                # Wraparound
                window_data = np.hstack(
                    [self.buffer[:, start_pos:], self.buffer[:, : self.write_pos]]
                )
                window_timestamps = np.hstack(
                    [self.timestamps[start_pos:], self.timestamps[: self.write_pos]]
                )

            # Create NeuralData object
            return NeuralData(
                data=window_data,
                sampling_rate=self.sampling_rate,
                channels=self.channel_names
                or [f"ch_{i}" for i in range(self.channels)],
                timestamp=datetime.fromtimestamp(window_timestamps[0]),
                device_id=self.device_id or "unknown",
                metadata={
                    "window_duration_ms": duration_ms,
                    "actual_samples": window_data.shape[1],
                    "buffer_fullness": min(
                        1.0, self.samples_written / self.buffer_size
                    ),
                },
            )

    def clear(self) -> None:
        """Clear the buffer"""
        self.buffer.fill(0)
        self.timestamps.fill(0)
        self.write_pos = 0
        self.samples_written = 0
        self.last_update = None

    def get_buffer_size(self) -> int:
        """Get current buffer size in samples"""
        return min(self.samples_written, self.buffer_size)

    def get_duration_ms(self) -> float:
        """Get current buffer duration in milliseconds"""
        return (self.get_buffer_size() / self.sampling_rate) * 1000.0

    def is_full(self) -> bool:
        """Check if buffer is full"""
        return self.samples_written >= self.buffer_size
