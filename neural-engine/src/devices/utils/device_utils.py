"""Utilities for device interface layer."""

import logging
from typing import Dict, List, Optional, Any
import numpy as np
from datetime import datetime, timezone
import asyncio

from ..interfaces.base_device import BaseDevice
from ...ingestion.data_types import NeuralDataPacket, NeuralSignalType

logger = logging.getLogger(__name__)


class DeviceRecorder:
    """Records data from devices to files."""

    def __init__(self, output_dir: str = "./recordings"):
        """Initialize recorder."""
        self.output_dir = output_dir
        self.recording_sessions: Dict[str, Dict[str, Any]] = {}
        self.is_recording = False

        # Create output directory if needed
        import os
        os.makedirs(output_dir, exist_ok=True)

    def start_recording(self, session_id: str, device_ids: List[str]) -> None:
        """Start recording session."""
        import h5py

        self.is_recording = True
        timestamp = datetime.utcnow()

        for device_id in device_ids:
            filename = f"{self.output_dir}/{session_id}_{device_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.h5"

            # Create HDF5 file
            h5file = h5py.File(filename, 'w')

            # Create groups
            h5file.create_group('data')
            h5file.create_group('metadata')
            h5file.create_group('timestamps')

            self.recording_sessions[device_id] = {
                'file': h5file,
                'filename': filename,
                'packet_count': 0,
                'start_time': timestamp
            }

            logger.info(f"Started recording for device {device_id}: {filename}")

    def record_packet(self, device_id: str, packet: NeuralDataPacket) -> None:
        """Record a data packet."""
        if not self.is_recording or device_id not in self.recording_sessions:
            return

        session = self.recording_sessions[device_id]
        h5file = session['file']
        packet_idx = session['packet_count']

        # Store data
        data_group = h5file['data']
        data_group.create_dataset(f'packet_{packet_idx}', data=packet.data)

        # Store timestamp
        ts_group = h5file['timestamps']
        ts_group.create_dataset(f'packet_{packet_idx}',
                                data=packet.timestamp.timestamp())

        # Store metadata on first packet
        if packet_idx == 0:
            meta_group = h5file['metadata']
            meta_group.attrs['device_id'] = packet.device_info.device_id
            meta_group.attrs['device_type'] = packet.device_info.device_type
            meta_group.attrs['n_channels'] = packet.n_channels
            meta_group.attrs['sampling_rate'] = packet.sampling_rate
            meta_group.attrs['signal_type'] = packet.signal_type.value
            meta_group.attrs['session_id'] = packet.session_id

            # Store channel info
            if packet.device_info.channels:
                for i, channel in enumerate(packet.device_info.channels):
                    ch_group = meta_group.create_group(f'channel_{i}')
                    ch_group.attrs['label'] = channel.label
                    ch_group.attrs['unit'] = channel.unit
                    ch_group.attrs['sampling_rate'] = channel.sampling_rate

        session['packet_count'] += 1

        # Flush periodically
        if packet_idx % 100 == 0:
            h5file.flush()

    def stop_recording(self) -> Dict[str, str]:
        """Stop recording and return filenames."""
        self.is_recording = False
        filenames = {}

        for device_id, session in self.recording_sessions.items():
            h5file = session['file']

            # Add final metadata
            meta_group = h5file['metadata']
            meta_group.attrs['total_packets'] = session['packet_count']
            meta_group.attrs['duration_seconds'] = (
                datetime.utcnow() - session['start_time']
            ).total_seconds()

            # Close file
            h5file.close()
            filenames[device_id] = session['filename']

            logger.info(f"Stopped recording for device {device_id}: "
                        f"{session['packet_count']} packets recorded")

        self.recording_sessions.clear()
        return filenames


class DeviceMonitor:
    """Monitors device health and performance."""

    def __init__(self, check_interval: float = 1.0):
        """Initialize monitor."""
        self.check_interval = check_interval
        self.device_stats: Dict[str, Dict[str, Any]] = {}
        self._monitoring_task: Optional[asyncio.Task] = None
        self._stop_monitoring = asyncio.Event()

    def add_device(self, device_id: str, device: BaseDevice) -> None:
        """Add device to monitor."""
        self.device_stats[device_id] = {
            'device': device,
            'packets_received': 0,
            'last_packet_time': None,
            'data_rate': 0.0,
            'dropped_packets': 0,
            'errors': [],
            'impedance_history': [],
            'battery_history': []
        }

    def update_packet_stats(self, device_id: str) -> None:
        """Update packet statistics."""
        if device_id not in self.device_stats:
            return

        stats = self.device_stats[device_id]
        stats['packets_received'] += 1

        now = datetime.utcnow()
        if stats['last_packet_time']:
            # Calculate data rate
            time_diff = (now - stats['last_packet_time']).total_seconds()
            if time_diff > 0:
                stats['data_rate'] = 1.0 / time_diff

        stats['last_packet_time'] = now

    async def start_monitoring(self) -> None:
        """Start monitoring devices."""
        self._stop_monitoring.clear()
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started device monitoring")

    async def stop_monitoring(self) -> None:
        """Stop monitoring devices."""
        self._stop_monitoring.set()
        if self._monitoring_task:
            await self._monitoring_task
            self._monitoring_task = None
        logger.info("Stopped device monitoring")

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while not self._stop_monitoring.is_set():
            for device_id, stats in self.device_stats.items():
                device = stats['device']

                # Check device state
                if not device.is_connected():
                    continue

                # Check data flow
                if stats['last_packet_time']:
                    time_since_last = (
                        datetime.utcnow() - stats['last_packet_time']
                    ).total_seconds()

                    if time_since_last > 2.0 and device.is_streaming():
                        logger.warning(f"Device {device_id}: No data for {time_since_last:.1f}s")

                # Check battery if available
                capabilities = device.get_capabilities()
                if capabilities.has_battery_monitor:
                    try:
                        battery_level = await device.get_battery_level()
                        stats['battery_history'].append({
                            'timestamp': datetime.utcnow(),
                            'level': battery_level
                        })

                        if battery_level < 20:
                            logger.warning(f"Device {device_id}: Low battery ({battery_level}%)")
                    except Exception as e:
                        logger.error(f"Error checking battery for {device_id}: {e}")

            await asyncio.sleep(self.check_interval)

    def get_device_stats(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a device."""
        if device_id not in self.device_stats:
            return None

        stats = self.device_stats[device_id].copy()
        # Remove device object from returned stats
        stats.pop('device', None)
        return stats

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all devices."""
        all_stats: Dict[str, Dict[str, Any]] = {}
        for device_id in self.device_stats:
            stats = self.get_device_stats(device_id)
            if stats is not None:
                all_stats[device_id] = stats
        return all_stats


class SignalQualityAnalyzer:
    """Analyzes signal quality from devices."""

    @staticmethod
    def analyze_packet(packet: NeuralDataPacket) -> Dict[str, Any]:
        """Analyze signal quality of a data packet."""
        data = packet.data
        quality_metrics = {}

        # Basic statistics
        quality_metrics['mean'] = np.mean(data)
        quality_metrics['std'] = np.std(data)
        quality_metrics['min'] = np.min(data)
        quality_metrics['max'] = np.max(data)

        # Check for saturation
        saturation_threshold = 0.95
        if packet.signal_type in [NeuralSignalType.EEG, NeuralSignalType.EMG]:
            # Assume ±200µV range for EEG
            max_expected = 200.0
            saturation_ratio = np.sum(np.abs(data) > saturation_threshold * max_expected) / data.size
            quality_metrics['saturation_ratio'] = saturation_ratio
            quality_metrics['is_saturated'] = saturation_ratio > 0.01

        # Check for flat lines
        flat_threshold = 0.1  # µV
        channel_stds = np.std(data, axis=1)
        flat_channels = np.sum(channel_stds < flat_threshold)
        quality_metrics['flat_channels'] = int(flat_channels)
        quality_metrics['has_flat_lines'] = flat_channels > 0

        # Signal-to-noise ratio estimation (simplified)
        if packet.signal_type == NeuralSignalType.EEG:
            # Estimate noise from high frequencies
            from scipy import signal

            # Design highpass filter
            fs = packet.sampling_rate
            b, a = signal.butter(4, 40.0 / (fs / 2), 'high')

            # Filter each channel
            noise_power = []
            signal_power = []
            for ch in range(data.shape[0]):
                # High frequency content (noise)
                noise = signal.filtfilt(b, a, data[ch])
                noise_power.append(np.var(noise))

                # Total signal power
                signal_power.append(np.var(data[ch]))

            # Average SNR across channels
            snr_values = []
            for s, n in zip(signal_power, noise_power):
                if n > 0:
                    snr_values.append(10 * np.log10(s / n))

            if snr_values:
                quality_metrics['snr_db'] = np.mean(snr_values)
                quality_metrics['snr_good'] = quality_metrics['snr_db'] > 10

        # Overall quality score (0-1)
        quality_score = 1.0
        if quality_metrics.get('is_saturated', False):
            quality_score *= 0.5
        if quality_metrics.get('has_flat_lines', False):
            quality_score *= 0.7
        if quality_metrics.get('snr_db', 20) < 10:
            quality_score *= 0.8

        quality_metrics['quality_score'] = quality_score
        quality_metrics['quality_good'] = quality_score > 0.7

        return quality_metrics


def create_device_from_config(config: Dict[str, Any]) -> BaseDevice:
    """Create a device instance from configuration."""
    device_type = config.get('type', 'synthetic')

    if device_type == 'lsl':
        from ..implementations.lsl_device import LSLDevice
        return LSLDevice(
            stream_name=config.get('stream_name'),
            stream_type=config.get('stream_type'),
            timeout=config.get('timeout', 5.0)
        )
    elif device_type == 'openbci':
        from ..implementations.openbci_device import OpenBCIDevice
        return OpenBCIDevice(
            port=config.get('port'),
            board_type=config.get('board_type', 'cyton'),
            daisy=config.get('daisy', False)
        )
    elif device_type == 'brainflow':
        from ..implementations.brainflow_device import BrainFlowDevice
        return BrainFlowDevice(
            board_name=config.get('board_name', 'synthetic'),
            serial_port=config.get('serial_port'),
            mac_address=config.get('mac_address'),
            ip_address=config.get('ip_address'),
            ip_port=config.get('ip_port'),
            serial_number=config.get('serial_number')
        )
    elif device_type == 'synthetic':
        from ..implementations.synthetic_device import SyntheticDevice
        signal_type_str = config.get('signal_type', 'EEG')
        signal_type = NeuralSignalType[signal_type_str.upper()]
        return SyntheticDevice(
            signal_type=signal_type,
            config=config.get('config', {})
        )
    else:
        raise ValueError(f"Unknown device type: {device_type}")


async def test_device_latency(device: BaseDevice, duration: float = 10.0) -> Dict[str, float]:
    """Test device streaming latency."""
    latencies = []
    packet_count = 0

    def latency_callback(packet: NeuralDataPacket) -> None:
        nonlocal packet_count
        packet_count += 1

        # Calculate latency
        now = datetime.now(timezone.utc)
        latency = (now - packet.timestamp).total_seconds() * 1000  # ms
        latencies.append(latency)

    # Set callback
    original_callback = device._data_callback
    device.set_data_callback(latency_callback)

    try:
        # Start streaming
        await device.start_streaming()

        # Collect data
        await asyncio.sleep(duration)

        # Stop streaming
        await device.stop_streaming()

    finally:
        # Restore original callback
        if original_callback:
            device.set_data_callback(original_callback)

    # Calculate statistics
    if latencies:
        return {
            'mean_latency_ms': float(np.mean(latencies)),
            'std_latency_ms': float(np.std(latencies)),
            'min_latency_ms': float(np.min(latencies)),
            'max_latency_ms': float(np.max(latencies)),
            'packet_count': packet_count,
            'packet_rate': packet_count / duration
        }
    else:
        return {
            'mean_latency_ms': 0,
            'std_latency_ms': 0,
            'min_latency_ms': 0,
            'max_latency_ms': 0,
            'packet_count': 0,
            'packet_rate': 0
        }
