"""Processing API - FastAPI endpoints for signal processing.

This module provides REST API endpoints for signal processing operations
including batch processing, streaming, and quality monitoring.
"""

from fastapi import (
    APIRouter,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    BackgroundTasks,
)
from typing import Dict, List, Optional, Any
import numpy as np
from pydantic import BaseModel, Field
import logging

from ..processing.signal_processor import AdvancedSignalProcessor
from ..processing.stream_processor import StreamProcessor
from ..processing.quality_monitor import QualityMonitor
from ..core.dependencies import get_processor, get_stream_processor, get_quality_monitor

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/processing", tags=["signal_processing"])


# Request / Response models
class ProcessBatchRequest(BaseModel):
    """Request model for batch processing."""

    session_id: str = Field(..., description="Session identifier")
    data: List[List[float]] = Field(..., description="Signal data (channels x samples)")
    sampling_rate: float = Field(1000.0, description="Sampling rate in Hz")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    processing_steps: Optional[List[str]] = Field(
        None, description="Specific processing steps to apply"
    )
    feature_types: Optional[List[str]] = Field(
        None, description="Feature types to extract"
    )


class ProcessBatchResponse(BaseModel):
    """Response model for batch processing."""

    session_id: str
    success: bool
    processed_samples: int
    quality_score: float
    features: Dict[str, Any]
    quality_metrics: Dict[str, Any]
    processing_time_ms: float
    warnings: List[str] = []


class StreamStartRequest(BaseModel):
    """Request model for starting stream processing."""

    session_id: str = Field(..., description="Session identifier")
    n_channels: int = Field(..., description="Number of channels")
    sampling_rate: float = Field(1000.0, description="Sampling rate in Hz")
    buffer_size_seconds: float = Field(10.0, description="Buffer size in seconds")
    window_size_seconds: float = Field(2.0, description="Processing window size")
    window_overlap: float = Field(0.5, description="Window overlap (0-1)")
    quality_monitoring: bool = Field(True, description="Enable quality monitoring")


class StreamStartResponse(BaseModel):
    """Response model for stream start."""

    session_id: str
    success: bool
    message: str
    websocket_url: str


class QualityCheckRequest(BaseModel):
    """Request model for quality check."""

    data: List[List[float]] = Field(..., description="Signal data")
    sampling_rate: float = Field(1000.0, description="Sampling rate")
    detailed: bool = Field(False, description="Return detailed metrics")


class QualityCheckResponse(BaseModel):
    """Response model for quality check."""

    overall_score: float
    quality_rating: str
    snr_db: float
    noise_level_uv: float
    artifact_percentage: float
    bad_channels: List[int]
    recommendations: List[str]
    detailed_metrics: Optional[Dict[str, Any]] = None


class ConfigUpdateRequest(BaseModel):
    """Request model for configuration update."""

    parameters: Dict[str, Any] = Field(..., description="Parameters to update")
    component: str = Field("processor", description="Component to update")


# Batch processing endpoints
@router.post("/process/batch", response_model=ProcessBatchResponse)
async def process_batch(
    request: ProcessBatchRequest,
    processor: AdvancedSignalProcessor = Depends(get_processor),
) -> ProcessBatchResponse:
    """Process a batch of signal data.

    This endpoint processes a batch of neural signal data and extracts features.
    """
    try:
        # Convert data to numpy array
        data = np.array(request.data, dtype=np.float32)

        if data.ndim != 2:
            raise HTTPException(
                status_code=400, detail="Data must be 2D array (channels x samples)"
            )

        # Start timing
        import time

        start_time = time.perf_counter()

        # Process signal
        result = await processor.process_signal_batch(
            data,
            metadata={
                "session_id": request.session_id,
                "sampling_rate": request.sampling_rate,
                **(request.metadata or {}),
            },
        )

        if not result.success:
            raise HTTPException(
                status_code=500, detail=f"Processing failed: {result.error_message}"
            )

        # Extract features if requested
        features = {}
        if request.feature_types:
            # Features already extracted during processing
            features = result.features or {}

        # Calculate processing time
        processing_time = (time.perf_counter() - start_time) * 1000

        return ProcessBatchResponse(
            session_id=request.session_id,
            success=True,
            processed_samples=data.shape[1],
            quality_score=result.quality_score,
            features=features,
            quality_metrics={
                "snr_db": (
                    result.quality_metrics.snr_db if result.quality_metrics else 0
                ),
                "noise_level": (
                    result.quality_metrics.noise_level_rms
                    if result.quality_metrics
                    else 0
                ),
                "artifact_percentage": (
                    result.quality_metrics.artifact_percentage
                    if result.quality_metrics
                    else 0
                ),
            },
            processing_time_ms=processing_time,
            warnings=result.warnings,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Stream processing endpoints
@router.post("/stream/start", response_model=StreamStartResponse)
async def start_stream(
    request: StreamStartRequest,
    background_tasks: BackgroundTasks,
    stream_processor: StreamProcessor = Depends(get_stream_processor),
) -> StreamStartResponse:
    """Start a new streaming session.

    This initializes a streaming session for real-time signal processing.
    """
    try:
        # Configure stream
        stream_info = {
            "n_channels": request.n_channels,
            "sampling_rate": request.sampling_rate,
        }

        # Update stream config
        stream_processor.config.buffer_size_seconds = request.buffer_size_seconds
        stream_processor.config.window_size_seconds = request.window_size_seconds
        stream_processor.config.window_overlap = request.window_overlap

        # Start stream
        success = await stream_processor.start_stream(request.session_id, stream_info)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to start stream")

        # Start quality monitoring if requested
        if request.quality_monitoring:
            quality_monitor: QualityMonitor = await get_quality_monitor()
            await quality_monitor.start_monitoring(request.session_id)

        return StreamStartResponse(
            session_id=request.session_id,
            success=True,
            message="Stream started successfully",
            websocket_url=f"/api / v1 / processing / stream / ws/{request.session_id}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting stream: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/stream/{session_id}")
async def stop_stream(
    session_id: str,
    stream_processor: StreamProcessor = Depends(get_stream_processor),
    quality_monitor: QualityMonitor = Depends(get_quality_monitor),
) -> Dict[str, Any]:
    """Stop a streaming session.

    This stops the stream and returns final metrics.
    """
    try:
        # Stop stream processing
        metrics = await stream_processor.stop_stream()

        # Stop quality monitoring
        quality_report = await quality_monitor.stop_monitoring(session_id)

        return {
            "session_id": session_id,
            "processing_metrics": metrics,
            "quality_report": quality_report,
        }

    except Exception as e:
        logger.error(f"Error stopping stream: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stream/{session_id}/status")
async def get_stream_status(
    session_id: str, stream_processor: StreamProcessor = Depends(get_stream_processor)
) -> Dict[str, Any]:
    """Get current stream status and metrics."""

    if stream_processor.current_session_id != session_id:
        raise HTTPException(
            status_code=404, detail=f"Stream session {session_id} not found"
        )

    return stream_processor.get_stream_metrics()


# WebSocket endpoint for streaming
@router.websocket("/stream/ws/{session_id}")
async def stream_websocket(
    websocket: WebSocket,
    session_id: str,
    stream_processor: StreamProcessor = Depends(get_stream_processor),
):
    """WebSocket endpoint for real-time streaming.

    Accepts signal chunks and returns processed results.
    """
    await websocket.accept()

    try:
        # Verify session exists
        if stream_processor.current_session_id != session_id:
            await websocket.send_json({"error": f"Session {session_id} not found"})
            await websocket.close()
            return

        # Processing loop
        while True:
            # Receive data
            data = await websocket.receive_json()

            if data.get("type") == "chunk":
                # Process chunk
                chunk_data = np.array(data["data"], dtype=np.float32)
                timestamp = data.get("timestamp")

                success = await stream_processor.process_chunk(chunk_data, timestamp)

                if success:
                    # Get latest features
                    features = await stream_processor.get_latest_features()

                    # Send response
                    await websocket.send_json(
                        {
                            "type": "processed",
                            "session_id": session_id,
                            "features": features or {},
                            "metrics": stream_processor.get_stream_metrics(),
                        }
                    )
                else:
                    await websocket.send_json(
                        {"type": "error", "message": "Failed to process chunk"}
                    )

            elif data.get("type") == "ping":
                # Heartbeat
                await websocket.send_json({"type": "pong"})

            elif data.get("type") == "close":
                # Client requested close
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


# Quality monitoring endpoints
@router.post("/quality/check", response_model=QualityCheckResponse)
async def check_quality(
    request: QualityCheckRequest,
    quality_monitor: QualityMonitor = Depends(get_quality_monitor),
) -> QualityCheckResponse:
    """Check signal quality without full processing."""

    try:
        # Convert data
        data = np.array(request.data, dtype=np.float32)

        # Check quality
        metrics = await quality_monitor.assessment.calculate_signal_quality(
            data, request.sampling_rate
        )

        # Generate quality report
        report = await quality_monitor.assessment.generate_quality_report(metrics)

        # Determine rating
        if metrics.overall_score >= 0.8:
            rating = "excellent"
        elif metrics.overall_score >= 0.6:
            rating = "good"
        elif metrics.overall_score >= 0.4:
            rating = "acceptable"
        else:
            rating = "poor"

        response = QualityCheckResponse(
            overall_score=metrics.overall_score,
            quality_rating=rating,
            snr_db=metrics.snr_db,
            noise_level_uv=metrics.noise_level_rms,
            artifact_percentage=metrics.artifact_percentage,
            bad_channels=metrics.flatline_channels + metrics.clipping_channels,
            recommendations=metrics.recommendations,
        )

        if request.detailed:
            response.detailed_metrics = report

        return response

    except Exception as e:
        logger.error(f"Error checking quality: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quality/monitor/{session_id}")
async def get_quality_monitoring(
    session_id: str, quality_monitor: QualityMonitor = Depends(get_quality_monitor)
) -> Dict[str, Any]:
    """Get quality monitoring data for a session."""

    # Get active alerts
    alerts = await quality_monitor.get_active_alerts(session_id)

    # Get quality trends
    trends = await quality_monitor.get_quality_trends(session_id)

    # Get quality report
    report = await quality_monitor.generate_quality_report(session_id)

    return {
        "session_id": session_id,
        "active_alerts": [
            {
                "timestamp": alert.timestamp.isoformat(),
                "type": alert.alert_type,
                "metric": alert.metric_name,
                "value": alert.metric_value,
                "message": alert.message,
                "duration_seconds": alert.duration_seconds,
            }
            for alert in alerts
        ],
        "trends": trends,
        "report": report,
    }


# Configuration endpoints
@router.put("/config/update")
async def update_configuration(
    request: ConfigUpdateRequest,
    processor: AdvancedSignalProcessor = Depends(get_processor),
    stream_processor: StreamProcessor = Depends(get_stream_processor),
    quality_monitor: QualityMonitor = Depends(get_quality_monitor),
) -> Dict[str, Any]:
    """Update processing configuration."""

    try:
        if request.component == "processor":
            processor.update_config(request.parameters)
        elif request.component == "stream":
            stream_processor.update_config(request.parameters)
        elif request.component == "quality":
            quality_monitor.update_thresholds(request.parameters)
        else:
            raise HTTPException(
                status_code=400, detail=f"Unknown component: {request.component}"
            )

        return {
            "success": True,
            "component": request.component,
            "updated_parameters": request.parameters,
        }

    except Exception as e:
        logger.error(f"Error updating configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/current")
async def get_configuration(
    processor: AdvancedSignalProcessor = Depends(get_processor),
    stream_processor: StreamProcessor = Depends(get_stream_processor),
) -> Dict[str, Any]:
    """Get current processing configuration."""

    return {
        "processor": {
            "sampling_rate": processor.config.sampling_rate,
            "num_channels": processor.config.num_channels,
            "preprocessing_steps": processor.config.preprocessing_steps,
            "feature_types": processor.config.feature_types,
            "filter_specs": processor.config.filter_specs,
            "quality_threshold": processor.config.quality_threshold,
        },
        "stream": {
            "buffer_size_seconds": stream_processor.config.buffer_size_seconds,
            "window_size_seconds": stream_processor.config.window_size_seconds,
            "window_overlap": stream_processor.config.window_overlap,
            "process_interval_ms": stream_processor.config.process_interval_ms,
            "min_quality_score": stream_processor.config.min_quality_score,
        },
    }


# Feature extraction endpoints
@router.get("/features/available")
async def get_available_features() -> Dict[str, List[str]]:
    """Get list of available feature types."""

    return {
        "time_domain": [
            "mean",
            "std",
            "variance",
            "skewness",
            "kurtosis",
            "hjorth_activity",
            "hjorth_mobility",
            "hjorth_complexity",
            "sample_entropy",
            "approx_entropy",
            "hurst_exponent",
            "zero_crossing_rate",
            "line_length",
        ],
        "frequency_domain": [
            "band_power",
            "relative_power",
            "peak_frequency",
            "spectral_centroid",
            "spectral_entropy",
            "spectral_edge",
            "coherence",
            "phase_locking_value",
        ],
        "time_frequency": [
            "dwt_features",
            "cwt_features",
            "morlet_features",
            "hilbert_features",
            "stockwell_features",
        ],
        "spatial": [
            "spatial_complexity",
            "correlation_features",
            "pca_features",
            "topographical_features",
        ],
        "connectivity": [
            "coherence_matrix",
            "plv_matrix",
            "transfer_entropy",
            "mutual_information",
            "phase_amplitude_coupling",
        ],
    }


@router.post("/features/extract")
async def extract_features(
    data: List[List[float]],
    feature_types: List[str],
    sampling_rate: float = 1000.0,
    processor: AdvancedSignalProcessor = Depends(get_processor),
) -> Dict[str, Any]:
    """Extract specific features from signal data."""

    try:
        # Convert data
        signal_data = np.array(data, dtype=np.float32)

        # Configure processor for feature extraction only
        processor.config.preprocessing_steps = ["quality_assessment"]
        processor.config.feature_types = feature_types

        # Process to extract features
        result = await processor.process_signal_batch(signal_data)

        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Feature extraction failed: {result.error_message}",
            )

        return {
            "features": result.features or {},
            "quality_score": result.quality_score,
            "processing_time_ms": result.processing_time_ms,
        }

    except Exception as e:
        logger.error(f"Error extracting features: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
