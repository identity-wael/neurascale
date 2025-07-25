"""Example of using the device interface layer."""

import asyncio
import logging
import sys
import os
from typing import Dict

import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.devices import DeviceManager  # noqa: E402
from src.devices.interfaces.base_device import DeviceState  # noqa: E402
from src.ingestion.data_types import NeuralDataPacket, NeuralSignalType, ChannelInfo  # noqa: E402

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataProcessor:
    """Simple data processor for demonstration."""

    def __init__(self) -> None:
        self.packet_count = 0
        self.channel_means: Dict[str, np.ndarray] = {}

    def process_packet(self, device_id: str, packet: NeuralDataPacket) -> None:
        """Process incoming data packet."""
        self.packet_count += 1

        # Calculate channel means
        means = np.mean(packet.data, axis=1)
        self.channel_means[device_id] = means

        # Log every 20th packet
        if self.packet_count % 20 == 0:
            logger.info(
                f"Device {device_id}: Packet {self.packet_count}, "
                f"Channels: {packet.n_channels}, "
                f"Samples: {packet.n_samples}, "
                f"Mean amplitude: {np.mean(means):.2f}µV"
            )


def device_state_handler(device_id: str, state: DeviceState) -> None:
    """Handle device state changes."""
    logger.info(f"Device {device_id} state changed to: {state.value}")


def device_error_handler(device_id: str, error: Exception) -> None:
    """Handle device errors."""
    logger.error(f"Device {device_id} error: {error}")


async def main() -> None:
    """Main example demonstrating device usage."""

    # Create device manager
    manager = DeviceManager()
    processor = DataProcessor()

    # Set callbacks
    manager.set_data_callback(processor.process_packet)
    manager.set_state_callback(device_state_handler)
    manager.set_error_callback(device_error_handler)

    try:
        # Example 1: Add and use a synthetic EEG device
        logger.info("=== Example 1: Synthetic EEG Device ===")

        eeg_device = await manager.add_device(
            device_id="synthetic_eeg_001",
            device_type="synthetic",
            signal_type=NeuralSignalType.EEG,
            config={
                'n_channels': 8,
                'sampling_rate': 256.0
            }
        )

        # Connect to device
        connected = await manager.connect_device("synthetic_eeg_001")
        if connected:
            logger.info("Successfully connected to synthetic EEG device")

            # Check capabilities
            capabilities = eeg_device.get_capabilities()
            logger.info(
                f"Device capabilities: {capabilities.max_channels} channels, "
                f"sampling rates: {capabilities.supported_sampling_rates}"
            )

            # Start streaming
            await manager.start_streaming(["synthetic_eeg_001"])

            # Stream for 5 seconds
            await asyncio.sleep(5)

            # Stop streaming
            await manager.stop_streaming(["synthetic_eeg_001"])

            # Check impedance
            impedances = await eeg_device.check_impedance()
            logger.info(f"Impedance check results: {impedances}")

        # Example 2: Multiple devices with aggregation
        logger.info("\n=== Example 2: Multiple Devices with Aggregation ===")

        # Add EMG device
        await manager.add_device(
            device_id="synthetic_emg_001",
            device_type="synthetic",
            signal_type=NeuralSignalType.EMG,
            config={
                'n_channels': 4,
                'sampling_rate': 1000.0
            }
        )

        # Add accelerometer device
        await manager.add_device(
            device_id="synthetic_accel_001",
            device_type="synthetic",
            signal_type=NeuralSignalType.ACCELEROMETER,
            config={
                'n_channels': 3,
                'sampling_rate': 100.0
            }
        )

        # Connect all devices
        await manager.connect_device("synthetic_emg_001")
        await manager.connect_device("synthetic_accel_001")

        # Define aggregation callback
        def aggregation_callback(packets: Dict[str, NeuralDataPacket]) -> None:
            logger.info(f"Aggregated window with data from {len(packets)} devices:")
            for device_id, packet in packets.items():
                logger.info(f"  {device_id}: {packet.n_samples} samples")

        # Start aggregation with 100ms windows
        await manager.start_aggregation(
            window_size_ms=100,
            callback=aggregation_callback
        )

        # Start streaming from all devices
        await manager.start_streaming()

        # Stream for 3 seconds
        await asyncio.sleep(3)

        # Stop everything
        await manager.stop_streaming()
        await manager.stop_aggregation()

        # Example 3: Auto - discovery (if LSL is available)
        logger.info("\n=== Example 3: Device Discovery ===")

        discovered = await manager.auto_discover_devices(timeout=2.0)
        logger.info(f"Discovered {len(discovered)} devices:")
        for device in discovered:
            logger.info(f"  - {device['name']} ({device['device_type']})")

        # List all devices
        logger.info("\n=== Device Summary ===")
        devices = manager.list_devices()
        for device in devices:
            logger.info(f"Device: {device['device_id']}")
            logger.info(f"  Name: {device['device_name']}")
            logger.info(f"  State: {device['state']}")
            logger.info(f"  Connected: {device['connected']}")
            logger.info(f"  Streaming: {device['streaming']}")

        # Final statistics
        logger.info(f"\nTotal packets processed: {processor.packet_count}")

    except Exception as e:
        logger.error(f"Example error: {e}")
        raise

    finally:
        # Cleanup - disconnect all devices
        await manager.stop_streaming()
        for device_id in list(manager.devices.keys()):
            await manager.disconnect_device(device_id)
            await manager.remove_device(device_id)


async def lsl_example() -> None:
    """Example using LSL device (requires pylsl and active LSL stream)."""
    manager = DeviceManager()

    try:
        # Try to find LSL streams
        await manager.add_device(
            device_id="lsl_any",
            device_type="lsl",
            stream_type="EEG",  # Look for EEG streams
            timeout=5.0
        )

        # Connect to first available stream
        connected = await manager.connect_device("lsl_any")
        if connected:
            logger.info("Connected to LSL stream")

            # Stream for 10 seconds
            await manager.start_streaming(["lsl_any"])
            await asyncio.sleep(10)
            await manager.stop_streaming(["lsl_any"])
        else:
            logger.warning("No LSL streams found")

    except ImportError:
        logger.warning("pylsl not installed, skipping LSL example")
    except Exception as e:
        logger.error(f"LSL example error: {e}")
    finally:
        await manager.disconnect_device("lsl_any")


async def openbci_example() -> None:
    """Example using OpenBCI device (requires physical device)."""
    manager = DeviceManager()

    try:
        # Add OpenBCI device
        device = await manager.add_device(
            device_id="openbci_cyton",
            device_type="openbci",
            board_type="cyton",
            port=None  # Auto - detect
        )

        # Try to connect
        connected = await manager.connect_device("openbci_cyton")
        if connected:
            logger.info("Connected to OpenBCI device")

            # Configure channels (turn off channels 5 - 8)
            channels = [
                ChannelInfo(channel_id=i, label=f"Ch{i + 1}", unit="microvolts", sampling_rate=250.0)
                for i in range(4)  # Only use first 4 channels
            ]
            device.configure_channels(channels)

            # Stream for 30 seconds
            await manager.start_streaming(["openbci_cyton"])
            await asyncio.sleep(30)
            await manager.stop_streaming(["openbci_cyton"])
        else:
            logger.warning("Could not connect to OpenBCI device")

    except Exception as e:
        logger.error(f"OpenBCI example error: {e}")
    finally:
        await manager.disconnect_device("openbci_cyton")


if __name__ == "__main__":
    # Run main example
    asyncio.run(main())

    # Uncomment to run LSL example
    # asyncio.run(lsl_example())

    # Uncomment to run OpenBCI example (requires device)
    # asyncio.run(openbci_example())
