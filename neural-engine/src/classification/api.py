"""
API endpoints for real-time classification
"""

import logging
from datetime import datetime
from dataclasses import asdict
from typing import Any, AsyncIterator, Dict, List, Optional
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
import numpy as np
import json

from .stream_processor import StreamProcessor
from .types import (
    NeuralData,
    StreamMetadata,
    MentalStateResult,
    SleepStageResult,
    SeizurePrediction,
    MotorImageryResult,
)
from .classifiers import (
    MentalStateClassifier,
    SleepStageClassifier,
    SeizurePredictor,
    MotorImageryClassifier,
)
from .features import (
    MentalStateFeatureExtractor,
    SleepFeatureExtractor,
)

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1/classification", tags=["classification"])

# Global instances
stream_processor = StreamProcessor()
mental_state_classifier = MentalStateClassifier()
sleep_stage_classifier = SleepStageClassifier()
seizure_predictor = SeizurePredictor()
motor_imagery_classifier = MotorImageryClassifier()

# Feature extractors
mental_state_extractor = MentalStateFeatureExtractor()
sleep_extractor = SleepFeatureExtractor()

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}


# Request/Response Models
class ClassificationRequest(BaseModel):
    """Single classification request"""

    data: List[List[float]] = Field(..., description="Neural data (channels x samples)")
    sampling_rate: float = Field(..., description="Sampling rate in Hz")
    channels: List[str] = Field(..., description="Channel names")
    device_id: str = Field(..., description="Device identifier")
    classification_types: List[str] = Field(
        default=["mental_state"],
        description="Types of classification to perform",
    )
    patient_id: Optional[str] = Field(
        None, description="Patient ID for seizure prediction"
    )


class StreamConfigRequest(BaseModel):
    """Stream configuration request"""

    device_id: str
    subject_id: str
    sampling_rate: float
    channel_count: int
    channel_names: List[str]
    classification_types: List[str]
    buffer_size_ms: float = 1000.0
    overlap_ms: float = 500.0


class ClassificationResponse(BaseModel):
    """Classification response"""

    timestamp: datetime
    results: Dict[str, Any]
    latency_ms: float
    stream_id: Optional[str] = None


# HTTP Endpoints
@router.post("/classify", response_model=ClassificationResponse)
async def classify_data(request: ClassificationRequest) -> ClassificationResponse:
    """
    Perform one-shot classification on provided neural data

    Args:
        request: Classification request with neural data

    Returns:
        Classification results for requested types
    """
    try:
        start_time = datetime.now()

        # Create neural data object
        neural_data = NeuralData(
            data=np.array(request.data),
            sampling_rate=request.sampling_rate,
            channels=request.channels,
            timestamp=datetime.now(),
            device_id=request.device_id,
            metadata={"patient_id": request.patient_id} if request.patient_id else None,
        )

        results = {}

        # Perform requested classifications
        for classification_type in request.classification_types:
            if classification_type == "mental_state":
                # Extract features
                features = await mental_state_extractor.extract_features(neural_data)
                # Classify
                result = await mental_state_classifier.classify(features)
                results["mental_state"] = {
                    "state": result.state.value,
                    "confidence": result.confidence,
                    "arousal": result.arousal_level,
                    "valence": result.valence,
                    "attention": result.attention_score,
                    "probabilities": result.probabilities,
                }

            elif classification_type == "sleep_stage":
                # Extract features
                features = await sleep_extractor.extract_features(neural_data)
                # Classify
                sleep_result = await sleep_stage_classifier.classify(features)
                results["sleep_stage"] = {
                    "stage": sleep_result.stage.value,
                    "confidence": sleep_result.confidence,
                    "sleep_depth": sleep_result.sleep_depth,
                    "transition_probability": sleep_result.transition_probability,
                    "probabilities": sleep_result.probabilities,
                }

            elif classification_type == "seizure_prediction":
                if not request.patient_id:
                    raise HTTPException(
                        status_code=400,
                        detail="patient_id required for seizure prediction",
                    )
                # Extract features (using mental state extractor as base)
                features = await mental_state_extractor.extract_features(neural_data)
                # Classify
                seizure_result = await seizure_predictor.classify(features)
                results["seizure_prediction"] = {
                    "risk_level": seizure_result.risk_level.value,
                    "probability": seizure_result.probability,
                    "confidence": seizure_result.confidence,
                    "time_to_seizure_minutes": (
                        seizure_result.time_to_seizure_minutes
                        if seizure_result.time_to_seizure_minutes is not None
                        else None
                    ),
                    "spatial_focus": seizure_result.spatial_focus,
                }

            elif classification_type == "motor_imagery":
                # Extract features
                features = await mental_state_extractor.extract_features(neural_data)
                # Classify
                motor_result = await motor_imagery_classifier.classify(features)
                results["motor_imagery"] = {
                    "intent": motor_result.intent.value,
                    "confidence": motor_result.confidence,
                    "control_signal": motor_result.control_signal.tolist(),
                    "erd_ers_score": motor_result.erd_ers_score,
                    "probabilities": motor_result.probabilities,
                }

            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unknown classification type: {classification_type}",
                )

        # Calculate total latency
        total_latency = (datetime.now() - start_time).total_seconds() * 1000

        return ClassificationResponse(
            timestamp=datetime.now(),
            results=results,
            latency_ms=total_latency,
        )

    except Exception as e:
        logger.error(f"Classification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream/configure")
async def configure_stream(config: StreamConfigRequest) -> Dict[str, str]:
    """
    Configure a new classification stream

    Args:
        config: Stream configuration

    Returns:
        Stream ID for WebSocket connection
    """
    try:
        # Create stream metadata
        metadata = StreamMetadata(
            stream_id=f"{config.device_id}_{config.subject_id}_{datetime.now().timestamp()}",
            device_id=config.device_id,
            subject_id=config.subject_id,
            sampling_rate=config.sampling_rate,
            channel_count=config.channel_count,
            channel_names=config.channel_names,
            start_time=datetime.now(),
            classification_types=config.classification_types,
        )

        # Configure stream processor
        await stream_processor.configure_stream(
            metadata,
            buffer_size_ms=config.buffer_size_ms,
            overlap_ms=config.overlap_ms,
        )

        return {
            "stream_id": metadata.stream_id,
            "status": "configured",
            "websocket_url": f"/api/v1/classification/stream/{metadata.stream_id}",
        }

    except Exception as e:
        logger.error(f"Stream configuration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/status")
async def get_models_status() -> Dict[str, Any]:
    """Get status of all classification models"""
    return {
        "mental_state": {
            "status": "active",
            "metrics": asdict(mental_state_classifier.get_metrics()),
        },
        "sleep_stage": {
            "status": "active",
            "metrics": asdict(sleep_stage_classifier.get_metrics()),
        },
        "seizure_prediction": {
            "status": "active",
            "metrics": asdict(seizure_predictor.get_metrics()),
        },
        "motor_imagery": {
            "status": "active",
            "metrics": asdict(motor_imagery_classifier.get_metrics()),
        },
    }


@router.post("/models/{model_name}/feedback")
async def submit_feedback(model_name: str, feedback: Dict[str, Any]) -> Dict[str, str]:
    """Submit feedback for model improvement"""
    try:
        if model_name == "mental_state":
            await mental_state_classifier.update_model(feedback)
        elif model_name == "sleep_stage":
            await sleep_stage_classifier.update_model(feedback)
        elif model_name == "seizure_prediction":
            await seizure_predictor.update_model(feedback)
        elif model_name == "motor_imagery":
            await motor_imagery_classifier.update_model(feedback)
        else:
            raise HTTPException(status_code=404, detail=f"Model {model_name} not found")

        return {"status": "feedback_received", "model": model_name}

    except Exception as e:
        logger.error(f"Feedback submission error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket Endpoint
@router.websocket("/stream/{stream_id}")
async def websocket_stream(websocket: WebSocket, stream_id: str) -> None:  # noqa: C901
    """
    WebSocket endpoint for real-time classification streaming

    Protocol:
    - Client sends: {"data": [[...]], "timestamp": "..."}
    - Server responds: {"timestamp": "...", "results": {...}, "latency_ms": ...}
    """
    await websocket.accept()
    active_connections[stream_id] = websocket

    try:
        # Get stream configuration
        stream_config = stream_processor.get_stream_config(stream_id)
        if not stream_config:
            await websocket.send_json(
                {
                    "error": f"Stream {stream_id} not configured",
                }
            )
            await websocket.close()
            return

        logger.info(f"WebSocket connected for stream {stream_id}")

        # Create data generator
        async def data_generator() -> AsyncIterator[NeuralData]:
            while True:
                try:
                    message = await websocket.receive_text()
                    data = json.loads(message)

                    # Create neural data object
                    neural_data = NeuralData(
                        data=np.array(data["data"]),
                        sampling_rate=stream_config.sampling_rate,
                        channels=stream_config.channel_names,
                        timestamp=datetime.fromisoformat(
                            data.get("timestamp", datetime.now().isoformat())
                        ),
                        device_id=stream_config.device_id,
                        metadata={"subject_id": stream_config.subject_id},
                    )

                    yield neural_data

                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logger.error(f"WebSocket data error: {e}")
                    continue

        # Process stream
        async for result in stream_processor.process_stream(data_generator()):
            # Format result based on type
            formatted_result = {}

            if isinstance(result, MentalStateResult):
                formatted_result["mental_state"] = {
                    "state": result.state.value,
                    "confidence": result.confidence,
                    "arousal": result.arousal_level,
                    "valence": result.valence,
                    "attention": result.attention_score,
                }
            elif isinstance(result, SleepStageResult):
                formatted_result["sleep_stage"] = {
                    "stage": result.stage.value,
                    "confidence": result.confidence,
                    "sleep_depth": result.sleep_depth,
                    "transition_probability": result.transition_probability,
                }
            elif isinstance(result, SeizurePrediction):
                formatted_result["seizure_prediction"] = {
                    "risk_level": result.risk_level.value,
                    "probability": result.probability,
                    "time_to_seizure_minutes": (
                        result.time_to_seizure_minutes
                        if result.time_to_seizure_minutes is not None
                        else None
                    ),
                }
            elif isinstance(result, MotorImageryResult):
                formatted_result["motor_imagery"] = {
                    "intent": result.intent.value,
                    "confidence": result.confidence,
                    "control_signal": result.control_signal.tolist(),
                }

            # Send result
            await websocket.send_json(
                {
                    "timestamp": result.timestamp.isoformat(),
                    "results": formatted_result,
                    "latency_ms": result.latency_ms,
                }
            )

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for stream {stream_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({"error": str(e)})
    finally:
        if stream_id in active_connections:
            del active_connections[stream_id]
        await stream_processor.cleanup_stream(stream_id)


@router.get("/streams/active")
async def get_active_streams() -> Dict[str, Any]:
    """Get list of active classification streams"""
    return {
        "active_streams": list(active_connections.keys()),
        "total_count": len(active_connections),
    }


# Health check
@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "classification",
        "timestamp": datetime.now().isoformat(),
    }
