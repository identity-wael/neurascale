"""GraphQL subscription resolvers."""

import strawberry
from typing import AsyncGenerator, Optional, List
import asyncio
from datetime import datetime
import random

from .types import Device, Session, NeuralData, Analysis


@strawberry.type
class DeviceStatusUpdate:
    """Device status update."""

    device_id: str
    status: str
    timestamp: datetime
    metrics: Optional[strawberry.scalars.JSON] = None


@strawberry.type
class SessionUpdate:
    """Session update."""

    session: Session
    event_type: str  # started, paused, resumed, stopped, data_available
    timestamp: datetime


@strawberry.type
class NeuralDataFrame:
    """Real-time neural data frame."""

    session_id: str
    timestamp: float
    channels: List[int]
    data: List[List[float]]  # [channels][samples]
    sampling_rate: int


@strawberry.type
class AnalysisProgress:
    """Analysis progress update."""

    analysis_id: str
    progress: float  # 0-100
    status: str
    message: Optional[str] = None
    timestamp: datetime


@strawberry.type
class SystemAlert:
    """System alert."""

    id: str
    level: str  # info, warning, error, critical
    message: str
    source: str
    timestamp: datetime
    metadata: Optional[strawberry.scalars.JSON] = None


@strawberry.type
class Subscription:
    """Root subscription type."""

    @strawberry.subscription
    async def device_status(
        self, device_ids: Optional[List[str]] = None
    ) -> AsyncGenerator[DeviceStatusUpdate, None]:
        """Subscribe to device status updates."""
        while True:
            # Mock device status updates
            device_id = (
                random.choice(device_ids)
                if device_ids
                else f"dev_{random.randint(1, 10):03d}"
            )

            yield DeviceStatusUpdate(
                device_id=device_id,
                status=random.choice(["ONLINE", "OFFLINE", "MAINTENANCE", "ERROR"]),
                timestamp=datetime.utcnow(),
                metrics={
                    "temperature": random.uniform(20, 40),
                    "battery": random.uniform(0, 100),
                    "signal_quality": random.uniform(0, 1),
                },
            )

            await asyncio.sleep(random.uniform(2, 5))

    @strawberry.subscription
    async def session_updates(
        self, session_id: Optional[str] = None
    ) -> AsyncGenerator[SessionUpdate, None]:
        """Subscribe to session updates."""
        while True:
            # Mock session updates
            session = Session(
                id=session_id or f"ses_{random.randint(1, 100):06d}",
                patient_id=f"pat_{random.randint(1, 50):03d}",
                device_id=f"dev_{random.randint(1, 10):03d}",
                start_time=datetime.utcnow(),
                end_time=None,
                duration=None,
                status="RECORDING",  # type: ignore
                channel_count=32,
                sampling_rate=256,
                data_size=random.randint(1000000, 10000000),
            )

            yield SessionUpdate(
                session=session,
                event_type=random.choice(
                    ["started", "data_available", "paused", "resumed", "stopped"]
                ),
                timestamp=datetime.utcnow(),
            )

            await asyncio.sleep(random.uniform(3, 10))

    @strawberry.subscription
    async def neural_data_stream(
        self, session_id: str, channels: Optional[List[int]] = None
    ) -> AsyncGenerator[NeuralDataFrame, None]:
        """Subscribe to real-time neural data stream."""
        # Default channels if not specified
        if not channels:
            channels = list(range(32))

        sampling_rate = 256
        samples_per_frame = 64  # 250ms at 256Hz

        while True:
            # Generate mock neural data
            data = []
            for ch in channels:
                # Generate realistic EEG-like signal
                samples = []
                for _ in range(samples_per_frame):
                    # Mix of frequencies typical in EEG
                    sample = (
                        10 * random.gauss(0, 1)  # Baseline noise
                        + 5 * random.gauss(0, 1) * random.uniform(0.8, 1.2)  # Alpha
                        + 3 * random.gauss(0, 1) * random.uniform(0.5, 0.8)  # Beta
                    )
                    samples.append(sample)
                data.append(samples)

            yield NeuralDataFrame(
                session_id=session_id,
                timestamp=datetime.utcnow().timestamp(),
                channels=channels,
                data=data,
                sampling_rate=sampling_rate,
            )

            # Stream at approximately real-time rate
            await asyncio.sleep(samples_per_frame / sampling_rate)

    @strawberry.subscription
    async def analysis_progress(
        self, analysis_id: str
    ) -> AsyncGenerator[AnalysisProgress, None]:
        """Subscribe to analysis progress updates."""
        progress = 0.0

        while progress < 100:
            # Simulate analysis progress
            progress += random.uniform(5, 15)
            progress = min(progress, 100)

            status = "processing"
            if progress >= 100:
                status = "completed"

            yield AnalysisProgress(
                analysis_id=analysis_id,
                progress=progress,
                status=status,
                message=f"Processing step {int(progress / 20) + 1} of 5",
                timestamp=datetime.utcnow(),
            )

            if progress < 100:
                await asyncio.sleep(random.uniform(1, 3))

    @strawberry.subscription
    async def system_alerts(
        self, severity_filter: Optional[List[str]] = None
    ) -> AsyncGenerator[SystemAlert, None]:
        """Subscribe to system alerts."""
        alert_messages = [
            ("info", "Device calibration recommended", "device_manager"),
            ("warning", "High CPU usage detected", "system_monitor"),
            ("error", "Failed to save session data", "storage_service"),
            ("info", "New ML model available", "ml_engine"),
            ("warning", "Low disk space", "storage_service"),
        ]

        while True:
            level, message, source = random.choice(alert_messages)

            # Apply severity filter
            if severity_filter and level not in severity_filter:
                await asyncio.sleep(random.uniform(5, 15))
                continue

            yield SystemAlert(
                id=f"alert_{datetime.utcnow().timestamp():.0f}",
                level=level,
                message=message,
                source=source,
                timestamp=datetime.utcnow(),
                metadata={
                    "affected_components": random.randint(1, 5),
                    "auto_resolved": random.choice([True, False]),
                },
            )

            await asyncio.sleep(random.uniform(10, 30))

    @strawberry.subscription
    async def model_training_updates(
        self, job_id: str
    ) -> AsyncGenerator[strawberry.scalars.JSON, None]:
        """Subscribe to ML model training updates."""
        epoch = 0
        max_epochs = 50

        while epoch < max_epochs:
            epoch += 1

            # Simulate training metrics
            metrics = {
                "job_id": job_id,
                "epoch": epoch,
                "total_epochs": max_epochs,
                "loss": 2.5 * (0.95**epoch) + random.uniform(-0.1, 0.1),
                "accuracy": min(0.95, 0.5 + epoch * 0.01 + random.uniform(-0.02, 0.02)),
                "validation_loss": 2.8 * (0.94**epoch) + random.uniform(-0.15, 0.15),
                "validation_accuracy": min(
                    0.92, 0.45 + epoch * 0.01 + random.uniform(-0.03, 0.03)
                ),
                "learning_rate": 0.001 * (0.95 ** (epoch // 10)),
                "timestamp": datetime.utcnow().isoformat(),
            }

            yield metrics

            # Training gets faster as it progresses
            await asyncio.sleep(random.uniform(0.5, 2))
