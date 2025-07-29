"""Neural data access REST API endpoints."""

from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import numpy as np
import logging

from ...rest.middleware.auth import get_current_user, check_permission

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models
class NeuralDataSegment(BaseModel):
    """Neural data segment."""

    session_id: str
    start_time: float  # seconds from session start
    end_time: float
    channels: List[int]
    sampling_rate: int
    data_shape: List[int]  # [samples, channels]
    data_url: Optional[str] = None  # URL for binary data
    statistics: Optional[Dict[str, Any]] = None


class NeuralDataQuery(BaseModel):
    """Neural data query parameters."""

    start_time: Optional[float] = Field(None, ge=0, description="Start time in seconds")
    end_time: Optional[float] = Field(None, ge=0, description="End time in seconds")
    channels: Optional[List[int]] = Field(None, description="Channel indices")
    downsample: Optional[int] = Field(
        None, ge=1, le=100, description="Downsampling factor"
    )
    format: str = Field(
        "json", pattern="^(json|binary|numpy)$", description="Response format"
    )


class ChannelInfo(BaseModel):
    """Channel information."""

    index: int
    name: str
    type: str  # EEG, EMG, EOG, etc.
    unit: str  # µV, mV, etc.
    sampling_rate: int
    reference: Optional[str] = None
    location: Optional[Dict[str, float]] = None  # 3D coordinates


class DataStatistics(BaseModel):
    """Data statistics."""

    mean: float
    std: float
    min: float
    max: float
    rms: float
    zero_crossings: int
    peak_frequency: Optional[float] = None


class SpectralAnalysis(BaseModel):
    """Spectral analysis results."""

    frequencies: List[float]
    power_spectrum: List[float]
    dominant_frequency: float
    band_powers: Dict[str, float]  # delta, theta, alpha, beta, gamma


@router.get("/sessions/{session_id}", response_model=NeuralDataSegment)
async def get_neural_data(
    session_id: str,
    query: NeuralDataQuery = Depends(),
    user: Dict[str, Any] = Depends(get_current_user),
) -> NeuralDataSegment:
    """
    Get neural data for a session.

    - **start_time**: Start time in seconds from session start
    - **end_time**: End time in seconds
    - **channels**: List of channel indices to retrieve
    - **downsample**: Downsampling factor for data reduction
    - **format**: Response format (json, binary, numpy)
    """
    if not await check_permission(user, "neural_data.read", session_id):
        raise HTTPException(403, "Insufficient permissions")

    # Mock implementation
    # In production, would fetch from data storage

    # Validate time range
    session_duration = 300.0  # 5 minutes mock session
    start = query.start_time or 0
    end = query.end_time or session_duration

    if start >= end:
        raise HTTPException(400, "Invalid time range")

    if end > session_duration:
        raise HTTPException(
            400, f"End time exceeds session duration ({session_duration}s)"
        )

    # Default channels
    total_channels = 32
    channels = query.channels or list(range(total_channels))

    # Validate channels
    if any(ch >= total_channels or ch < 0 for ch in channels):
        raise HTTPException(400, "Invalid channel indices")

    # Calculate data shape
    sampling_rate = 256
    downsample = query.downsample or 1
    effective_rate = sampling_rate // downsample
    num_samples = int((end - start) * effective_rate)

    # Create response
    segment = NeuralDataSegment(
        session_id=session_id,
        start_time=start,
        end_time=end,
        channels=channels,
        sampling_rate=effective_rate,
        data_shape=[num_samples, len(channels)],
    )

    # Add data URL for binary format
    if query.format == "binary":
        segment.data_url = f"/api/v2/neural-data/sessions/{session_id}/download?start={start}&end={end}"

    # Add statistics
    segment.statistics = {
        "duration": end - start,
        "total_samples": num_samples,
        "data_size_bytes": num_samples * len(channels) * 4,  # float32
    }

    return segment


@router.get("/sessions/{session_id}/channels", response_model=List[ChannelInfo])
async def get_channel_info(
    session_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
) -> List[ChannelInfo]:
    """Get channel information for a session."""
    if not await check_permission(user, "neural_data.read", session_id):
        raise HTTPException(403, "Insufficient permissions")

    # Mock channel data
    channels = []
    channel_types = ["EEG"] * 19 + ["EOG"] * 2 + ["EMG"] * 2 + ["ECG"] * 1 + ["REF"] * 8

    for i in range(32):
        channels.append(
            ChannelInfo(
                index=i,
                name=f"CH{i + 1:02d}",
                type=channel_types[i % len(channel_types)],
                unit="µV",
                sampling_rate=256,
                reference=(
                    "Cz" if channel_types[i % len(channel_types)] == "EEG" else None
                ),
                location=(
                    {
                        "x": np.random.randn(),
                        "y": np.random.randn(),
                        "z": np.random.randn(),
                    }
                    if channel_types[i % len(channel_types)] == "EEG"
                    else None
                ),
            )
        )

    return channels


@router.post(
    "/sessions/{session_id}/statistics", response_model=Dict[int, DataStatistics]
)
async def calculate_statistics(
    session_id: str,
    query: NeuralDataQuery,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[int, DataStatistics]:
    """Calculate statistics for neural data."""
    if not await check_permission(user, "neural_data.analyze", session_id):
        raise HTTPException(403, "Insufficient permissions")

    # Mock statistics calculation
    channels = query.channels or list(range(32))
    stats = {}

    for ch in channels:
        # Generate mock statistics
        stats[ch] = DataStatistics(
            mean=np.random.randn() * 0.1,
            std=abs(np.random.randn()) * 10 + 5,
            min=-100 + np.random.randn() * 10,
            max=100 + np.random.randn() * 10,
            rms=abs(np.random.randn()) * 15 + 10,
            zero_crossings=int(np.random.randint(100, 1000)),
            peak_frequency=np.random.uniform(8, 12),  # Alpha range
        )

    return stats


@router.post(
    "/sessions/{session_id}/spectral", response_model=Dict[int, SpectralAnalysis]
)
async def spectral_analysis(
    session_id: str,
    channels: List[int],
    window_size: float = Query(4.0, description="Window size in seconds"),
    overlap: float = Query(0.5, description="Overlap ratio (0-1)"),
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[int, SpectralAnalysis]:
    """Perform spectral analysis on neural data."""
    if not await check_permission(user, "neural_data.analyze", session_id):
        raise HTTPException(403, "Insufficient permissions")

    # Mock spectral analysis
    results = {}

    for ch in channels:
        # Generate mock frequency spectrum
        frequencies = np.linspace(0, 128, 129)  # 0-128 Hz
        power_spectrum = np.random.exponential(1, 129) * np.exp(-frequencies / 30)

        # Calculate band powers
        band_powers = {
            "delta": np.sum(power_spectrum[1:4]),  # 1-4 Hz
            "theta": np.sum(power_spectrum[4:8]),  # 4-8 Hz
            "alpha": np.sum(power_spectrum[8:13]),  # 8-13 Hz
            "beta": np.sum(power_spectrum[13:30]),  # 13-30 Hz
            "gamma": np.sum(power_spectrum[30:50]),  # 30-50 Hz
        }

        results[ch] = SpectralAnalysis(
            frequencies=frequencies.tolist(),
            power_spectrum=power_spectrum.tolist(),
            dominant_frequency=frequencies[np.argmax(power_spectrum)],
            band_powers=band_powers,
        )

    return results


@router.get("/sessions/{session_id}/stream")
async def stream_neural_data(
    session_id: str,
    channels: Optional[str] = Query(
        None, description="Comma-separated channel indices"
    ),
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get WebSocket URL for real-time data streaming."""
    if not await check_permission(user, "neural_data.stream", session_id):
        raise HTTPException(403, "Insufficient permissions")

    # Parse channels
    channel_list = []
    if channels:
        try:
            channel_list = [int(ch) for ch in channels.split(",")]
        except ValueError:
            raise HTTPException(400, "Invalid channel format")

    # Generate streaming token
    stream_token = f"stream_{session_id}_{int(datetime.utcnow().timestamp())}"

    return {
        "websocket_url": f"wss://api.neurascale.com/ws/neural-data/{stream_token}",
        "token": stream_token,
        "channels": channel_list or "all",
        "expires_in": 3600,  # 1 hour
        "_links": {
            "self": {"href": f"/api/v2/neural-data/sessions/{session_id}/stream"},
            "session": {"href": f"/api/v2/sessions/{session_id}"},
        },
    }


@router.post("/batch/statistics")
async def batch_statistics(
    session_ids: List[str],
    query: NeuralDataQuery,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Dict[int, DataStatistics]]:
    """Calculate statistics for multiple sessions."""
    if not await check_permission(user, "neural_data.analyze"):
        raise HTTPException(403, "Insufficient permissions")

    results = {}

    for session_id in session_ids[:10]:  # Limit to 10 sessions
        # Check individual session permission
        if await check_permission(user, "neural_data.read", session_id):
            # Reuse single session statistics
            stats = await calculate_statistics(session_id, query, user)
            results[session_id] = stats

    return results
