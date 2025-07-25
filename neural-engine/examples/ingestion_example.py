"""Example of using the Neural Data Ingestion system."""

import asyncio
import numpy as np
from datetime import datetime, timezone
import os

# Add parent directory to path for imports
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion import NeuralDataIngestion  # noqa: E402
from src.ingestion.data_types import (  # noqa: E402
    NeuralDataPacket,
    NeuralSignalType,
    DataSource,
    DeviceInfo,
    ChannelInfo,
)


async def main() -> None:
    """Example of ingesting neural data."""

    # Initialize ingestion system
    # Note: In production, use real project ID and enable GCP services
    ingestion = NeuralDataIngestion(
        project_id="neurascale",
        enable_pubsub=False,  # Disabled for local testing
        enable_bigtable=False,  # Disabled for local testing
    )

    # Create sample device info
    n_channels = 8
    channels = [
        ChannelInfo(
            channel_id=i,
            label=f"Ch{i + 1}",
            unit="microvolts",
            sampling_rate=256.0,
        )
        for i in range(n_channels)
    ]

    device_info = DeviceInfo(
        device_id="openbci_synthetic_001",
        device_type="OpenBCI_Synthetic",
        manufacturer="OpenBCI",
        model="Synthetic Board",
        channels=channels,
    )

    # Simulate ingesting 10 packets
    for packet_idx in range(10):
        # Generate synthetic EEG data
        # Real implementation would get data from actual device
        duration_seconds = 1.0
        n_samples = int(256 * duration_seconds)

        # Simulate EEG signals with different frequency components
        t = np.linspace(0, duration_seconds, n_samples)
        data = np.zeros((n_channels, n_samples))

        for ch in range(n_channels):
            # Add different frequency components per channel
            # Alpha (8-12 Hz)
            data[ch] += 20 * np.sin(2 * np.pi * 10 * t)
            # Beta (12-30 Hz)
            data[ch] += 10 * np.sin(2 * np.pi * 20 * t)
            # Noise
            data[ch] += 5 * np.random.randn(n_samples)

        # Create packet
        packet = NeuralDataPacket(
            timestamp=datetime.now(timezone.utc),
            data=data,
            signal_type=NeuralSignalType.EEG,
            source=DataSource.SYNTHETIC,
            device_info=device_info,
            session_id="example_session_001",
            subject_id="test_subject_001",  # Will be anonymized
            sampling_rate=256.0,
            data_quality=0.95,
        )

        # Ingest packet
        success = await ingestion.ingest_packet(packet)

        if success:
            print(f"✓ Packet {packet_idx + 1} ingested successfully")
        else:
            print(f"✗ Failed to ingest packet {packet_idx + 1}")

        # Small delay between packets
        await asyncio.sleep(0.1)

    # Print metrics
    metrics = ingestion.get_metrics()
    print("\nIngestion Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")

    # Clean up
    await ingestion.close()


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
