"""Example demonstrating enhanced device interface features."""

import asyncio
import logging
from datetime import datetime

from src.devices.device_manager import DeviceManager
from src.devices.device_api import router, initialize_device_manager
from fastapi import FastAPI, WebSocket
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def impedance_check_demo(manager: DeviceManager, device_id: str):
    """Demonstrate impedance checking."""
    logger.info("=== Impedance Check Demo ===")

    try:
        # Check impedance for all channels
        logger.info("Checking impedance for all channels...")
        impedance_results = await manager.check_device_impedance(device_id)

        # Display results
        logger.info(f"Impedance check complete for {len(impedance_results)} channels:")
        for channel_id, impedance in impedance_results.items():
            quality = (
                "Good" if impedance < 10000 else "Fair" if impedance < 20000 else "Poor"
            )
            logger.info(
                f"  Channel {channel_id}: {impedance / 1000:.1f} kΩ ({quality})"
            )

        # Check specific channels
        logger.info("\nChecking impedance for channels 0-3...")
        specific_results = await manager.check_device_impedance(device_id, [0, 1, 2, 3])

        avg_impedance = sum(specific_results.values()) / len(specific_results)
        logger.info(
            f"Average impedance for channels 0-3: {avg_impedance / 1000:.1f} kΩ"
        )

    except Exception as e:
        logger.error(f"Impedance check failed: {e}")


async def signal_quality_demo(manager: DeviceManager, device_id: str):
    """Demonstrate signal quality monitoring."""
    logger.info("\n=== Signal Quality Monitoring Demo ===")

    device = manager.get_device(device_id)
    if not device:
        logger.error("Device not found")
        return

    try:
        # Start streaming to enable signal quality monitoring
        logger.info("Starting data streaming...")
        await manager.start_streaming([device_id])

        # Wait for data to accumulate
        await asyncio.sleep(2)

        # Get signal quality metrics
        if hasattr(device, "get_signal_quality"):
            logger.info("Checking signal quality...")
            quality_metrics = await device.get_signal_quality()

            logger.info(f"Signal quality for {len(quality_metrics)} channels:")
            for channel_id, metrics in quality_metrics.items():
                logger.info(f"  Channel {channel_id}:")
                logger.info(f"    SNR: {metrics.snr_db:.1f} dB")
                logger.info(f"    RMS: {metrics.rms_amplitude:.2f} µV")
                logger.info(f"    Quality: {metrics.quality_level.value}")
                logger.info(f"    Artifacts: {metrics.artifacts_detected}")

        # Stop streaming
        await manager.stop_streaming([device_id])

    except Exception as e:
        logger.error(f"Signal quality monitoring failed: {e}")


async def device_discovery_demo(manager: DeviceManager):
    """Demonstrate device discovery."""
    logger.info("\n=== Device Discovery Demo ===")

    logger.info("Scanning for neural devices (10 seconds)...")

    try:
        # Discover devices
        discovered_devices = await manager.auto_discover_devices(timeout=10.0)

        if discovered_devices:
            logger.info(f"Found {len(discovered_devices)} device(s):")
            for device in discovered_devices:
                logger.info(f"\n  Device: {device['name']}")
                logger.info(f"    Type: {device['device_type']}")
                logger.info(f"    Protocol: {device['protocol']}")
                logger.info(f"    Connection info: {device['connection_info']}")
        else:
            logger.info(
                "No devices found. Make sure devices are powered on and in range."
            )

    except Exception as e:
        logger.error(f"Device discovery failed: {e}")


async def websocket_client_demo():
    """Demonstrate WebSocket notifications."""
    logger.info("\n=== WebSocket Notifications Demo ===")

    import websockets
    import json

    uri = "ws://localhost:8000/devices/notifications"

    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Connected to notification service")

            # Subscribe to notifications
            await websocket.send(
                json.dumps({"type": "subscribe", "notification_types": ["all"]})
            )

            # Listen for notifications
            logger.info("Listening for device notifications...")

            # Set a timeout for the demo
            try:
                while True:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    notification = json.loads(message)

                    logger.info("Notification received:")
                    logger.info(f"  Type: {notification.get('type')}")
                    logger.info(f"  Device: {notification.get('device_id')}")
                    logger.info(f"  Severity: {notification.get('severity')}")

                    if notification.get("type") == "impedance_check_complete":
                        data = notification.get("data", {})
                        logger.info(
                            f"  Channels checked: {data.get('channels_checked')}"
                        )
                        logger.info(
                            f"  Good channels: {data.get('quality_summary', {}).get('good_channels')}"
                        )

            except asyncio.TimeoutError:
                logger.info("Demo timeout reached")

    except Exception as e:
        logger.error(f"WebSocket connection failed: {e}")


async def main():
    """Main demo function."""
    logger.info("=== NeuraScale Device Interface Enhancement Demo ===\n")

    # Create device manager
    async with DeviceManager() as manager:
        # Start services
        await manager.start_notification_service()
        await manager.start_health_monitoring()

        # 1. Device Discovery Demo
        await device_discovery_demo(manager)

        # 2. Add a synthetic device for testing
        logger.info("\n=== Setting up synthetic device ===")
        device_id = "demo_device"

        try:
            device = await manager.add_device(
                device_id=device_id, device_type="brainflow", board_name="synthetic"
            )
            logger.info(f"Added device: {device.device_name}")

            # Connect to device
            logger.info("Connecting to device...")
            success = await manager.connect_device(device_id)

            if success:
                logger.info("Device connected successfully")

                # Get device capabilities
                capabilities = device.get_capabilities()
                logger.info("Device capabilities:")
                logger.info(f"  Max channels: {capabilities.max_channels}")
                logger.info(
                    f"  Sampling rates: {capabilities.supported_sampling_rates}"
                )
                logger.info(
                    f"  Has impedance check: {capabilities.has_impedance_check}"
                )
                logger.info(
                    f"  Has battery monitor: {capabilities.has_battery_monitor}"
                )

                # 3. Impedance Check Demo
                await asyncio.sleep(1)
                await impedance_check_demo(manager, device_id)

                # 4. Signal Quality Demo
                await asyncio.sleep(1)
                await signal_quality_demo(manager, device_id)

                # 5. Health monitoring
                await asyncio.sleep(1)
                logger.info("\n=== Device Health Monitoring ===")
                health_info = manager.get_device_health(device_id)
                logger.info(f"Device health status: {health_info['status']}")

                # Disconnect device
                await manager.disconnect_device(device_id)
                logger.info("Device disconnected")

        except Exception as e:
            logger.error(f"Demo error: {e}")

        # 6. Show telemetry statistics
        logger.info("\n=== Telemetry Statistics ===")
        stats = manager.get_telemetry_statistics()
        logger.info(f"Telemetry statistics: {stats}")


async def run_api_server():
    """Run the FastAPI server with WebSocket support."""
    app = FastAPI(title="NeuraScale Device API")

    # Create and initialize device manager
    manager = DeviceManager()
    await manager.start_notification_service()
    await manager.start_health_monitoring()

    # Initialize API with device manager
    initialize_device_manager(manager)

    # Include device routes
    app.include_router(router)

    # Add WebSocket demo endpoint
    @app.websocket("/ws-demo")
    async def websocket_demo(websocket: WebSocket):
        await websocket.accept()
        await websocket.send_json(
            {
                "message": "Connected to NeuraScale Device API",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        try:
            while True:
                data = await websocket.receive_text()
                await websocket.send_text(f"Echo: {data}")
        except Exception:
            await websocket.close()

    # Run server
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())

    # Uncomment to run the API server instead
    # asyncio.run(run_api_server())
