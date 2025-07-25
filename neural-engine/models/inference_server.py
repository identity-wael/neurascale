"""Real - time inference server for neural models."""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
import numpy as np
import json
from concurrent.futures import ThreadPoolExecutor
import time

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException

# from fastapi.responses import JSONResponse  # Unused import
from pydantic import BaseModel
import uvicorn

from .base_models import BaseNeuralModel

# from .movement_decoder import MovementDecoder, KalmanFilterDecoder  # Unused imports
# from .emotion_classifier import EmotionClassifier, ValenceArousalRegressor  # Unused imports

logger = logging.getLogger(__name__)


class InferenceRequest(BaseModel):
    """Schema for inference requests."""

    session_id: str
    data: List[List[float]]  # Neural data (n_samples, n_channels)
    model_name: str
    model_version: Optional[str] = "latest"
    metadata: Optional[Dict[str, Any]] = {}


class InferenceResponse(BaseModel):
    """Schema for inference responses."""

    session_id: str
    predictions: Union[List[float], List[List[float]]]
    model_name: str
    model_version: str
    inference_time_ms: float
    timestamp: str
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = {}


class ModelRegistry:
    """Registry for managing multiple models."""

    def __init__(self) -> None:
        self.models: Dict[str, Dict[str, BaseNeuralModel]] = {}
        self.model_metadata: Dict[str, Dict[str, Any]] = {}
        self.active_models: Dict[str, str] = {}  # model_name -> active_version

    def register_model(
        self,
        model: BaseNeuralModel,
        model_name: str,
        version: str = "v1",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Register a model in the registry."""
        if model_name not in self.models:
            self.models[model_name] = {}
            self.model_metadata[model_name] = {}

        self.models[model_name][version] = model
        self.model_metadata[model_name][version] = metadata or {}

        # Set as active if first version
        if len(self.models[model_name]) == 1:
            self.active_models[model_name] = version

        logger.info(f"Registered model: {model_name} version {version}")

    def get_model(
        self, model_name: str, version: Optional[str] = None
    ) -> BaseNeuralModel:
        """Get a model from the registry."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")

        version = version or self.active_models.get(model_name, "latest")

        if version == "latest":
            version = sorted(self.models[model_name].keys())[-1]

        if version not in self.models[model_name]:
            raise ValueError(f"Version {version} not found for model {model_name}")

        return self.models[model_name][version]

    def list_models(self) -> Dict[str, List[str]]:
        """List all registered models and versions."""
        return {
            model_name: list(versions.keys())
            for model_name, versions in self.models.items()
        }

    def set_active_version(self, model_name: str, version: str) -> None:
        """Set the active version for a model."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")

        if version not in self.models[model_name]:
            raise ValueError(f"Version {version} not found for model {model_name}")

        self.active_models[model_name] = version
        logger.info(f"Set active version for {model_name} to {version}")


class NeuralInferenceServer:
    """High - performance inference server for neural models."""

    def __init__(
        self, max_batch_size: int = 32, batch_timeout_ms: int = 50, num_workers: int = 4
    ):
        """
        Initialize inference server.

        Args:
            max_batch_size: Maximum batch size for inference
            batch_timeout_ms: Maximum wait time for batching
            num_workers: Number of worker threads
        """
        self.app = FastAPI(title="Neural Inference Server")
        self.registry = ModelRegistry()
        self.max_batch_size = max_batch_size
        self.batch_timeout_ms = batch_timeout_ms

        # Inference queue and batch processing
        self.inference_queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()
        self.executor = ThreadPoolExecutor(max_workers=num_workers)

        # WebSocket connections for streaming
        self.active_connections: Dict[str, WebSocket] = {}

        # Performance metrics
        self.metrics: Dict[str, Any] = {
            "total_requests": 0,
            "total_inference_time": 0.0,
            "model_request_counts": {},
        }

        # Setup routes
        self._setup_routes()

    def _setup_routes(self) -> None:  # noqa: C901
        """Setup FastAPI routes."""

        @self.app.get("/")
        async def root() -> Dict[str, str]:
            return {"message": "Neural Inference Server", "status": "running"}

        @self.app.get("/models")
        async def list_models() -> Dict[str, List[str]]:
            return self.registry.list_models()

        @self.app.post("/inference")
        async def inference(request: InferenceRequest) -> InferenceResponse:
            """Single inference endpoint."""
            start_time = time.time()

            try:
                # Get model
                model = self.registry.get_model(
                    request.model_name, request.model_version
                )

                # Prepare data
                data = np.array(request.data)
                if len(data.shape) == 2:
                    data = data[np.newaxis, :]  # Add batch dimension

                # Run inference
                predictions = await self._run_inference(model, data)

                # Calculate inference time
                inference_time = (time.time() - start_time) * 1000

                # Update metrics
                self.metrics["total_requests"] = int(self.metrics["total_requests"]) + 1
                self.metrics["total_inference_time"] = (
                    float(self.metrics["total_inference_time"]) + inference_time
                )
                if request.model_name not in self.metrics["model_request_counts"]:
                    self.metrics["model_request_counts"][request.model_name] = 0
                self.metrics["model_request_counts"][request.model_name] += 1

                # Prepare response
                response = InferenceResponse(
                    session_id=request.session_id,
                    predictions=predictions[0].tolist(),
                    model_name=request.model_name,
                    model_version=request.model_version or "latest",
                    inference_time_ms=inference_time,
                    timestamp=datetime.utcnow().isoformat(),
                    metadata=request.metadata,
                )

                return response

            except Exception as e:
                logger.error(f"Inference error: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/batch_inference")
        async def batch_inference(
            requests: List[InferenceRequest],
        ) -> List[InferenceResponse]:
            """Batch inference endpoint."""
            # Group requests by model
            model_groups: Dict[Tuple[str, Optional[str]], List[InferenceRequest]] = {}
            for req in requests:
                key = (req.model_name, req.model_version)
                if key not in model_groups:
                    model_groups[key] = []
                model_groups[key].append(req)

            # Process each group
            responses = []
            for (model_name, version), group_requests in model_groups.items():
                model = self.registry.get_model(model_name, version)

                # Prepare batch data
                batch_data = np.array([req.data for req in group_requests])

                # Run batch inference
                predictions = await self._run_inference(model, batch_data)

                # Create responses
                for i, req in enumerate(group_requests):
                    response = InferenceResponse(
                        session_id=req.session_id,
                        predictions=predictions[i].tolist(),
                        model_name=model_name,
                        model_version=version or "latest",
                        inference_time_ms=0,  # Will be updated
                        timestamp=datetime.utcnow().isoformat(),
                        metadata=req.metadata,
                    )
                    responses.append(response)

            return responses

        @self.app.websocket("/stream/{session_id}")
        async def websocket_endpoint(websocket: WebSocket, session_id: str) -> None:
            """WebSocket endpoint for streaming inference."""
            await websocket.accept()
            self.active_connections[session_id] = websocket

            try:
                while True:
                    # Receive data
                    data = await websocket.receive_json()

                    # Create inference request
                    request = InferenceRequest(**data)

                    # Get model
                    model = self.registry.get_model(
                        request.model_name, request.model_version
                    )

                    # Run inference
                    input_data = np.array(request.data)
                    if len(input_data.shape) == 2:
                        input_data = input_data[np.newaxis, :]

                    predictions = await self._run_inference(model, input_data)

                    # Send response
                    response = {
                        "predictions": predictions[0].tolist(),
                        "timestamp": datetime.utcnow().isoformat(),
                    }

                    await websocket.send_json(response)

            except WebSocketDisconnect:
                del self.active_connections[session_id]
                logger.info(f"WebSocket disconnected: {session_id}")

        @self.app.get("/metrics")
        async def get_metrics() -> Dict[str, Any]:
            """Get server metrics."""
            avg_inference_time = (
                float(self.metrics["total_inference_time"])
                / int(self.metrics["total_requests"])
                if int(self.metrics["total_requests"]) > 0
                else 0
            )

            return {
                "total_requests": self.metrics["total_requests"],
                "average_inference_time_ms": avg_inference_time,
                "model_request_counts": self.metrics["model_request_counts"],
                "active_connections": len(self.active_connections),
                "models_loaded": len(self.registry.models),
            }

        @self.app.post("/models / reload/{model_name}")
        async def reload_model(model_name: str, model_path: str) -> Dict[str, str]:
            """Reload a model from disk."""
            # This would load the model from the specified path
            # Implementation depends on model storage strategy
            return {"message": f"Model {model_name} reload initiated"}

    async def _run_inference(
        self, model: BaseNeuralModel, data: np.ndarray
    ) -> np.ndarray:
        """Run inference in executor to avoid blocking."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, model.predict, data)

    async def _batch_processor(self) -> None:
        """Background task for processing batched requests."""
        while True:
            batch: List[Dict[str, Any]] = []
            batch_start_time = time.time()

            # Collect batch
            while len(batch) < self.max_batch_size:
                try:
                    timeout = (self.batch_timeout_ms / 1000) - (
                        time.time() - batch_start_time
                    )
                    if timeout <= 0:
                        break

                    item = await asyncio.wait_for(
                        self.inference_queue.get(), timeout=timeout
                    )
                    batch.append(item)

                except asyncio.TimeoutError:
                    break

            if batch:
                # Process batch
                await self._process_batch(batch)

    async def _process_batch(self, batch: List[Dict[str, Any]]) -> None:
        """Process a batch of inference requests."""
        # Group by model
        model_batches: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
        for item in batch:
            model_key = (item["model_name"], item["model_version"])
            if model_key not in model_batches:
                model_batches[model_key] = []
            model_batches[model_key].append(item)

        # Process each model batch
        for (model_name, version), model_batch in model_batches.items():
            try:
                model = self.registry.get_model(model_name, version)

                # Prepare batch data
                batch_data = np.array([item["data"] for item in model_batch])

                # Run inference
                predictions = await self._run_inference(model, batch_data)

                # Send results
                for i, item in enumerate(model_batch):
                    item["future"].set_result(predictions[i])

            except Exception as e:
                # Set exception for all items in batch
                for item in model_batch:
                    item["future"].set_exception(e)

    def load_models_from_config(self, config_path: str) -> None:
        """Load models from configuration file."""
        with open(config_path, "r") as f:
            config = json.load(f)

        for model_config in config["models"]:
            # Load model based on configuration
            # This is a placeholder - actual implementation would load from disk
            logger.info(f"Loading model: {model_config['name']}")

    def run(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Run the inference server."""
        # Start batch processor
        asyncio.create_task(self._batch_processor())

        # Run FastAPI app
        uvicorn.run(self.app, host=host, port=port)


class ModelOptimizer:
    """Optimize models for inference."""

    @staticmethod
    def optimize_tensorflow_model(model_path: str, output_path: str) -> None:
        """Optimize TensorFlow model for inference."""
        try:
            import tensorflow as tf
        except ImportError:
            logger.error(
                "TensorFlow not installed. Please install with: pip install tensorflow"
            )
            return

        # Load model
        model = tf.keras.models.load_model(model_path)

        # Convert to TFLite for edge deployment
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.target_spec.supported_types = [tf.float16]

        tflite_model = converter.convert()

        # Save optimized model
        with open(output_path, "wb") as f:
            f.write(tflite_model)

        logger.info(f"Model optimized and saved to {output_path}")

    @staticmethod
    def quantize_pytorch_model(
        model: BaseNeuralModel, calibration_data: np.ndarray
    ) -> None:
        """Quantize PyTorch model for faster inference."""
        import torch
        import torch.quantization as quantization

        # Prepare model for quantization
        if model.model is None:
            raise ValueError("No model to quantize")
        model.model.eval()

        # Fuse modules
        model.model = torch.quantization.fuse_modules(
            model.model, [["conv", "bn", "relu"]]
        )

        # Prepare for quantization
        model.model.qconfig = quantization.get_default_qconfig("fbgemm")
        quantization.prepare(model.model, inplace=True)

        # Calibrate with sample data
        with torch.no_grad():
            for i in range(0, len(calibration_data), 32):
                batch = torch.FloatTensor(calibration_data[i : i + 32])
                model.model(batch)

        # Convert to quantized model
        quantization.convert(model.model, inplace=True)

        logger.info("Model quantized successfully")


def main() -> None:
    """Main entry point for the inference server."""
    import argparse

    parser = argparse.ArgumentParser(description="Neural Inference Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument(
        "--max - batch - size", type=int, default=32, help="Maximum batch size"
    )
    parser.add_argument(
        "--batch - timeout", type=int, default=50, help="Batch timeout in ms"
    )
    parser.add_argument(
        "--workers", type=int, default=4, help="Number of worker threads"
    )

    args = parser.parse_args()

    # Create server
    server = NeuralInferenceServer(
        max_batch_size=args.max_batch_size,
        batch_timeout_ms=args.batch_timeout,
        num_workers=args.workers,
    )

    # Load models from config if provided
    if args.config:
        server.load_models_from_config(args.config)

    # Run server
    logger.info(f"Starting Neural Inference Server on {args.host}:{args.port}")
    server.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
