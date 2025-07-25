"""Device manager for handling multiple neural data acquisition devices."""

import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any, Type, Tuple
from datetime import datetime
import uuid

from .interfaces.base_device import BaseDevice, DeviceState
from .implementations.lsl_device import LSLDevice
from .implementations.openbci_device import OpenBCIDevice
from .implementations.brainflow_device import BrainFlowDevice
from .implementations.synthetic_device import SyntheticDevice
from ..ingestion.data_types import NeuralDataPacket

logger = logging.getLogger(__name__)


class DeviceManager:
    """Manages multiple neural data acquisition devices."""

    # Device type registry
    DEVICE_TYPES: Dict[str, Type[BaseDevice]] = {
        'lsl': LSLDevice,
        'openbci': OpenBCIDevice,
        'brainflow': BrainFlowDevice,
        'synthetic': SyntheticDevice,
    }

    def __init__(self) -> None:
        """Initialize device manager."""
        self.devices: Dict[str, BaseDevice] = {}
        self.active_session_id: Optional[str] = None
        self._data_callback: Optional[Callable[[str, NeuralDataPacket], None]] = None
        self._state_callback: Optional[Callable[[str, DeviceState], None]] = None
        self._error_callback: Optional[Callable[[str, Exception], None]] = None
        self._aggregation_task: Optional[asyncio.Task] = None
        self._aggregation_queue: asyncio.Queue[Tuple[str, NeuralDataPacket]] = asyncio.Queue()

    def register_device_type(self, device_type: str, device_class: Type[BaseDevice]) -> None:
        """Register a custom device type."""
        self.DEVICE_TYPES[device_type] = device_class
        logger.info(f"Registered device type: {device_type}")

    async def add_device(self,
                         device_id: str,
                         device_type: str,
                         **device_kwargs: Any) -> BaseDevice:
        """
        Add a new device to the manager.

        Args:
            device_id: Unique identifier for the device
            device_type: Type of device from DEVICE_TYPES
            **device_kwargs: Device - specific initialization parameters

        Returns:
            The created device instance
        """
        if device_id in self.devices:
            raise ValueError(f"Device {device_id} already exists")

        if device_type not in self.DEVICE_TYPES:
            raise ValueError(f"Unknown device type: {device_type}. "
                             f"Available types: {list(self.DEVICE_TYPES.keys())}")

        # Create device instance
        device_class = self.DEVICE_TYPES[device_type]
        device = device_class(**device_kwargs)

        # Set up callbacks
        device.set_data_callback(lambda packet: self._handle_device_data(device_id, packet))
        device.set_state_callback(lambda state: self._handle_device_state(device_id, state))
        device.set_error_callback(lambda error: self._handle_device_error(device_id, error))

        # Set session ID if active
        if self.active_session_id:
            device.set_session_id(self.active_session_id)

        self.devices[device_id] = device
        logger.info(f"Added device: {device_id} (type: {device_type})")

        return device

    async def remove_device(self, device_id: str) -> None:
        """Remove a device from the manager."""
        if device_id not in self.devices:
            return

        device = self.devices[device_id]

        # Stop and disconnect if necessary
        if device.is_streaming():
            await device.stop_streaming()
        if device.is_connected():
            await device.disconnect()

        del self.devices[device_id]
        logger.info(f"Removed device: {device_id}")

    def get_device(self, device_id: str) -> Optional[BaseDevice]:
        """Get a device by ID."""
        return self.devices.get(device_id)

    def list_devices(self) -> List[Dict[str, Any]]:
        """List all devices with their status."""
        device_list = []
        for device_id, device in self.devices.items():
            device_list.append({
                'device_id': device_id,
                'device_name': device.device_name,
                'state': device.state.value,
                'connected': device.is_connected(),
                'streaming': device.is_streaming(),
                'capabilities': device.get_capabilities() if device.is_connected() else None
            })
        return device_list

    async def connect_device(self, device_id: str, **connect_kwargs: Any) -> bool:
        """Connect to a specific device."""
        device = self.devices.get(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")

        return await device.connect(**connect_kwargs)

    async def disconnect_device(self, device_id: str) -> None:
        """Disconnect a specific device."""
        device = self.devices.get(device_id)
        if device:
            await device.disconnect()

    async def start_streaming(self, device_ids: Optional[List[str]] = None) -> None:
        """
        Start streaming from specified devices.

        Args:
            device_ids: List of device IDs to start streaming, or None for all connected devices
        """
        if device_ids is None:
            device_ids = [dev_id for dev_id, dev in self.devices.items() if dev.is_connected()]

        # Start session if not active
        if not self.active_session_id:
            self.start_session()

        # Start streaming for each device
        tasks = []
        for device_id in device_ids:
            device = self.devices.get(device_id)
            if device and device.is_connected() and not device.is_streaming():
                tasks.append(device.start_streaming())

        if tasks:
            await asyncio.gather(*tasks)
            logger.info(f"Started streaming from {len(tasks)} devices")

    async def stop_streaming(self, device_ids: Optional[List[str]] = None) -> None:
        """
        Stop streaming from specified devices.

        Args:
            device_ids: List of device IDs to stop streaming, or None for all streaming devices
        """
        if device_ids is None:
            device_ids = [dev_id for dev_id, dev in self.devices.items() if dev.is_streaming()]

        # Stop streaming for each device
        tasks = []
        for device_id in device_ids:
            device = self.devices.get(device_id)
            if device and device.is_streaming():
                tasks.append(device.stop_streaming())

        if tasks:
            await asyncio.gather(*tasks)
            logger.info(f"Stopped streaming from {len(tasks)} devices")

    def start_session(self, session_id: Optional[str] = None) -> str:
        """
        Start a new recording session.

        Args:
            session_id: Optional session ID, will be generated if not provided

        Returns:
            The session ID
        """
        self.active_session_id = session_id or f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        # Update all devices with new session ID
        for device in self.devices.values():
            device.set_session_id(self.active_session_id)

        logger.info(f"Started session: {self.active_session_id}")
        return self.active_session_id

    def end_session(self) -> None:
        """End the current recording session."""
        if self.active_session_id:
            logger.info(f"Ended session: {self.active_session_id}")
            self.active_session_id = None

    def set_data_callback(self, callback: Callable[[str, NeuralDataPacket], None]) -> None:
        """Set callback for data packets from any device."""
        self._data_callback = callback

    def set_state_callback(self, callback: Callable[[str, DeviceState], None]) -> None:
        """Set callback for device state changes."""
        self._state_callback = callback

    def set_error_callback(self, callback: Callable[[str, Exception], None]) -> None:
        """Set callback for device errors."""
        self._error_callback = callback

    def _handle_device_data(self, device_id: str, packet: NeuralDataPacket) -> None:
        """Handle data packet from a device."""
        # Add device ID to packet metadata
        if packet.metadata is None:
            packet.metadata = {}
        packet.metadata['device_id'] = device_id

        # Add to aggregation queue if aggregation is active
        if self._aggregation_task and not self._aggregation_task.done():
            try:
                self._aggregation_queue.put_nowait((device_id, packet))
            except asyncio.QueueFull:
                logger.warning(f"Aggregation queue full, dropping packet from {device_id}")

        # Call user callback
        if self._data_callback:
            try:
                self._data_callback(device_id, packet)
            except Exception as e:
                logger.error(f"Error in data callback: {e}")

    def _handle_device_state(self, device_id: str, state: DeviceState) -> None:
        """Handle device state change."""
        if self._state_callback:
            try:
                self._state_callback(device_id, state)
            except Exception as e:
                logger.error(f"Error in state callback: {e}")

    def _handle_device_error(self, device_id: str, error: Exception) -> None:
        """Handle device error."""
        logger.error(f"Device {device_id} error: {error}")
        if self._error_callback:
            try:
                self._error_callback(device_id, error)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")

    async def start_aggregation(self,
                                window_size_ms: int = 50,
                                callback: Optional[Callable[[Dict[str, NeuralDataPacket]], None]] = None) -> None:
        """
        Start aggregating data from multiple devices into synchronized windows.

        Args:
            window_size_ms: Window size in milliseconds
            callback: Callback for aggregated data windows
        """
        if self._aggregation_task and not self._aggregation_task.done():
            logger.warning("Aggregation already running")
            return

        self._aggregation_task = asyncio.create_task(
            self._aggregation_loop(window_size_ms, callback)
        )
        logger.info(f"Started data aggregation with {window_size_ms}ms windows")

    async def stop_aggregation(self) -> None:
        """Stop data aggregation."""
        if self._aggregation_task:
            self._aggregation_task.cancel()
            try:
                await self._aggregation_task
            except asyncio.CancelledError:
                pass
            self._aggregation_task = None
            logger.info("Stopped data aggregation")

    async def _aggregation_loop(self,
                                window_size_ms: int,
                                callback: Optional[Callable[[Dict[str, NeuralDataPacket]], None]]) -> None:
        """Main aggregation loop."""
        window_duration = window_size_ms / 1000.0
        window_data: Dict[str, List[NeuralDataPacket]] = {}
        window_start = asyncio.get_event_loop().time()

        try:
            while True:
                try:
                    # Get packet with timeout
                    remaining_time = window_duration - (asyncio.get_event_loop().time() - window_start)
                    if remaining_time <= 0:
                        # Window complete, process data
                        if window_data and callback:
                            # Get latest packet from each device
                            aggregated = {
                                device_id: packets[-1]
                                for device_id, packets in window_data.items()
                            }
                            callback(aggregated)

                        # Reset window
                        window_data.clear()
                        window_start = asyncio.get_event_loop().time()
                        continue

                    # Get next packet
                    device_id, packet = await asyncio.wait_for(
                        self._aggregation_queue.get(),
                        timeout=remaining_time
                    )

                    # Add to window
                    if device_id not in window_data:
                        window_data[device_id] = []
                    window_data[device_id].append(packet)

                except asyncio.TimeoutError:
                    # Window timeout, process what we have
                    if window_data and callback:
                        aggregated = {
                            device_id: packets[-1]
                            for device_id, packets in window_data.items()
                        }
                        callback(aggregated)

                    # Reset window
                    window_data.clear()
                    window_start = asyncio.get_event_loop().time()

        except asyncio.CancelledError:
            logger.info("Aggregation loop cancelled")
            raise

    async def auto_discover_devices(self, timeout: float = 5.0) -> List[Dict[str, Any]]:
        """
        Auto - discover available devices.

        Args:
            timeout: Discovery timeout in seconds

        Returns:
            List of discovered devices
        """
        discovered = []

        # Try LSL discovery
        try:
            lsl_device = LSLDevice(timeout=timeout)
            lsl_streams = await lsl_device.get_available_streams()
            for stream in lsl_streams:
                discovered.append({
                    'device_type': 'lsl',
                    'device_id': f"lsl_{stream['uid']}",
                    'name': stream['name'],
                    'info': stream
                })
        except Exception as e:
            logger.warning(f"LSL discovery failed: {e}")

        # Try serial port discovery for OpenBCI
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            for port in ports:
                if any(id_str in str(port.description).lower() for id_str in ['openbci', 'ftdi', 'serial']):
                    discovered.append({
                        'device_type': 'openbci',
                        'device_id': f"openbci_{port.device}",
                        'name': f"OpenBCI on {port.device}",
                        'info': {
                            'port': port.device,
                            'description': port.description
                        }
                    })
        except Exception as e:
            logger.warning(f"Serial port discovery failed: {e}")

        # Always include synthetic device option
        discovered.append({
            'device_type': 'synthetic',
            'device_id': 'synthetic_eeg',
            'name': 'Synthetic EEG Device',
            'info': {'signal_type': 'EEG'}
        })

        logger.info(f"Discovered {len(discovered)} devices")
        return discovered

    async def __aenter__(self) -> 'DeviceManager':
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit - cleanup all devices."""
        # Stop aggregation if running
        await self.stop_aggregation()

        # Stop all streaming
        await self.stop_streaming()

        # Disconnect all devices
        disconnect_tasks = []
        for device in self.devices.values():
            if device.is_connected():
                disconnect_tasks.append(device.disconnect())

        if disconnect_tasks:
            await asyncio.gather(*disconnect_tasks)

        # Clear devices
        self.devices.clear()
