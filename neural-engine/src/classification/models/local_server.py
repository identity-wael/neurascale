"""
Local model server for development and testing
"""

import logging
from datetime import datetime
from typing import Any, Dict, List
import numpy as np
import pickle
import os

from ..interfaces import BaseModelServer
from ..types import ModelMetrics

logger = logging.getLogger(__name__)


class LocalModelServer(BaseModelServer):
    """
    Local model server for development and edge deployment.

    Features:
    - In-memory model storage
    - Fast local inference
    - Model hot-swapping
    - Minimal latency for real-time applications
    """

    def __init__(self, model_dir: str = "./models"):
        """
        Initialize local model server

        Args:
            model_dir: Directory to store model files
        """
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)

        # In-memory model registry
        self.models: Dict[str, Any] = {}
        self.model_info: Dict[str, Dict[str, Any]] = {}
        self.model_metrics: Dict[str, ModelMetrics] = {}

        # Performance tracking
        self.inference_times: Dict[str, List[float]] = {}

    async def predict(
        self, model_name: str, instances: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Get predictions from local model

        Args:
            model_name: Name of the model
            instances: List of instances to predict

        Returns:
            List of predictions
        """
        start_time = datetime.now()

        try:
            # Check if model is loaded
            if model_name not in self.models:
                # Try to load from disk
                await self._load_model_from_disk(model_name)

            model = self.models[model_name]
            predictions = []

            # Process each instance
            for instance in instances:
                # Convert instance to appropriate format
                features = self._prepare_features(instance)

                # Make prediction
                if hasattr(model, "predict_proba"):
                    # Scikit-learn style model
                    proba = model.predict_proba(features.reshape(1, -1))[0]
                    pred_class = model.classes_[np.argmax(proba)]

                    prediction = {
                        "class": pred_class,
                        "confidence": float(np.max(proba)),
                        "probabilities": {
                            str(cls): float(p) for cls, p in zip(model.classes_, proba)
                        },
                    }
                elif hasattr(model, "predict"):
                    # Simple predict method
                    pred = model.predict(features.reshape(1, -1))[0]
                    prediction = {
                        "class": str(pred),
                        "confidence": 0.9,  # Default confidence
                    }
                else:
                    # Custom model - call directly
                    prediction = await model(features)

                predictions.append(prediction)

            # Track performance
            latency_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._track_inference_time(model_name, latency_ms)

            # Update metrics
            if model_name in self.model_metrics:
                metrics = self.model_metrics[model_name]
                metrics.inference_count += len(instances)
                metrics.last_updated = datetime.now()

            return predictions

        except Exception as e:
            logger.error(f"Prediction error for {model_name}: {e}")
            if model_name in self.model_metrics:
                self.model_metrics[model_name].error_count += 1
            raise

    async def deploy_model(self, model: Any, model_name: str, version: str) -> str:
        """
        Deploy model locally

        Args:
            model: Model object
            model_name: Name for the model
            version: Model version

        Returns:
            Local endpoint (file path)
        """
        try:
            # Store model in memory
            self.models[model_name] = model

            # Save model to disk
            model_path = os.path.join(self.model_dir, f"{model_name}_{version}.pkl")
            with open(model_path, "wb") as f:
                pickle.dump(model, f)

            # Store model info
            self.model_info[model_name] = {
                "version": version,
                "path": model_path,
                "deployed_at": datetime.now(),
                "model_type": type(model).__name__,
                "status": "serving",
            }

            # Initialize metrics
            self.model_metrics[model_name] = ModelMetrics(
                model_name=model_name,
                accuracy=0.0,
                precision=0.0,
                recall=0.0,
                f1_score=0.0,
                latency_p50=0.0,
                latency_p95=0.0,
                latency_p99=0.0,
                inference_count=0,
                error_count=0,
                last_updated=datetime.now(),
            )

            # Initialize performance tracking
            self.inference_times[model_name] = []

            logger.info(
                f"Model {model_name} v{version} deployed locally at {model_path}"
            )
            return f"local://{model_path}"

        except Exception as e:
            logger.error(f"Local deployment failed: {e}")
            raise

    async def undeploy_model(self, model_name: str, version: str) -> None:
        """
        Remove model from local server

        Args:
            model_name: Name of the model
            version: Model version
        """
        try:
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not deployed")

            # Remove from memory
            del self.models[model_name]

            # Remove model file
            if model_name in self.model_info:
                model_path = self.model_info[model_name]["path"]
                if os.path.exists(model_path):
                    os.remove(model_path)

                del self.model_info[model_name]

            # Clean up metrics
            if model_name in self.model_metrics:
                del self.model_metrics[model_name]

            if model_name in self.inference_times:
                del self.inference_times[model_name]

            logger.info(f"Model {model_name} v{version} undeployed")

        except Exception as e:
            logger.error(f"Undeployment failed: {e}")
            raise

    async def get_model_metrics(self, model_name: str) -> ModelMetrics:
        """
        Get model performance metrics

        Args:
            model_name: Name of the model

        Returns:
            Model metrics
        """
        if model_name not in self.model_metrics:
            raise ValueError(f"No metrics for model {model_name}")

        metrics = self.model_metrics[model_name]

        # Update latency percentiles
        if model_name in self.inference_times and self.inference_times[model_name]:
            latencies = np.array(self.inference_times[model_name][-1000:])  # Last 1000
            metrics.latency_p50 = float(np.percentile(latencies, 50))
            metrics.latency_p95 = float(np.percentile(latencies, 95))
            metrics.latency_p99 = float(np.percentile(latencies, 99))

        return metrics

    async def _load_model_from_disk(self, model_name: str) -> Any:
        """Load model from disk if available"""
        # Find latest version
        model_files = [
            f
            for f in os.listdir(self.model_dir)
            if f.startswith(f"{model_name}_") and f.endswith(".pkl")
        ]

        if not model_files:
            raise ValueError(f"No saved model found for {model_name}")

        # Load latest version
        latest_file = sorted(model_files)[-1]
        model_path = os.path.join(self.model_dir, latest_file)

        with open(model_path, "rb") as f:
            model = pickle.load(f)

        self.models[model_name] = model
        logger.info(f"Loaded model {model_name} from {model_path}")

    def _prepare_features(self, instance: Dict[str, Any]) -> np.ndarray:
        """Convert instance dict to feature array"""
        if "features" in instance:
            # Direct feature array
            return np.array(instance["features"])
        elif "data" in instance:
            # Raw data that needs feature extraction
            return np.array(instance["data"]).flatten()
        else:
            # Try to extract all numeric values
            features = []
            for key, value in instance.items():
                if isinstance(value, (int, float)):
                    features.append(value)
                elif isinstance(value, list) and all(
                    isinstance(v, (int, float)) for v in value
                ):
                    features.extend(value)

            return np.array(features)

    def _track_inference_time(self, model_name: str, latency_ms: float) -> None:
        """Track inference time for performance monitoring"""
        if model_name not in self.inference_times:
            self.inference_times[model_name] = []

        self.inference_times[model_name].append(latency_ms)

        # Keep only recent times
        if len(self.inference_times[model_name]) > 10000:
            self.inference_times[model_name] = self.inference_times[model_name][-5000:]

    async def update_model(self, model_name: str, new_model: Any) -> None:
        """Hot-swap model without downtime"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not deployed")

        # Keep old model reference
        old_model = self.models[model_name]

        try:
            # Swap models
            self.models[model_name] = new_model

            # Update version
            if model_name in self.model_info:
                old_version = self.model_info[model_name]["version"]
                new_version = (
                    f"{old_version}_updated_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
                self.model_info[model_name]["version"] = new_version

                # Save new model
                model_path = os.path.join(
                    self.model_dir, f"{model_name}_{new_version}.pkl"
                )
                with open(model_path, "wb") as f:
                    pickle.dump(new_model, f)

                self.model_info[model_name]["path"] = model_path

            logger.info(f"Model {model_name} updated successfully")

        except Exception as e:
            # Rollback on error
            self.models[model_name] = old_model
            logger.error(f"Model update failed, rolled back: {e}")
            raise

    def get_loaded_models(self) -> List[str]:
        """Get list of currently loaded models"""
        return list(self.models.keys())

    async def benchmark_model(
        self,
        model_name: str,
        test_instances: List[Dict[str, Any]],
        iterations: int = 100,
    ) -> Dict[str, float]:
        """
        Benchmark model performance

        Args:
            model_name: Name of the model
            test_instances: Test data
            iterations: Number of iterations

        Returns:
            Benchmark results
        """
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not loaded")

        latencies = []

        for _ in range(iterations):
            start = datetime.now()
            await self.predict(model_name, test_instances)
            latency = (datetime.now() - start).total_seconds() * 1000
            latencies.append(latency)

        return {
            "mean_latency_ms": float(np.mean(latencies)),
            "std_latency_ms": float(np.std(latencies)),
            "min_latency_ms": float(np.min(latencies)),
            "max_latency_ms": float(np.max(latencies)),
            "p50_latency_ms": float(np.percentile(latencies, 50)),
            "p95_latency_ms": float(np.percentile(latencies, 95)),
            "p99_latency_ms": float(np.percentile(latencies, 99)),
            "throughput_per_second": float(
                1000.0 / np.mean(latencies) * len(test_instances)
            ),
        }
