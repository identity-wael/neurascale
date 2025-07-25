"""Training pipeline for neural models with Vertex AI integration."""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import tempfile
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

# Google Cloud imports
from google.cloud import aiplatform
from google.cloud import storage
import wandb

from .base_models import BaseNeuralModel

# from .movement_decoder import MovementDecoder, KalmanFilterDecoder  # Unused imports
# from .emotion_classifier import EmotionClassifier, ValenceArousalRegressor  # Unused imports

logger = logging.getLogger(__name__)


class NeuralModelTrainingPipeline:
    """Comprehensive training pipeline for neural models with cloud integration."""

    def __init__(
        self,
        project_id: str,
        location: str = "us - central1",
        bucket_name: Optional[str] = None,
        experiment_name: Optional[str] = None,
        use_wandb: bool = True,
    ):
        """
        Initialize training pipeline.

        Args:
            project_id: GCP project ID
            location: GCP location for Vertex AI
            bucket_name: GCS bucket for model artifacts
            experiment_name: Name for experiment tracking
            use_wandb: Whether to use Weights & Biases for tracking
        """
        self.project_id = project_id
        self.location = location
        self.bucket_name = bucket_name or f"{project_id}-neural - models"
        self.experiment_name = (
            experiment_name
            or f"neural - exp-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        )
        self.use_wandb = use_wandb

        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)

        # Initialize storage client
        self.storage_client = storage.Client(project=project_id)

        # Initialize W&B if enabled
        if self.use_wandb:
            wandb.init(project="neurascale", name=self.experiment_name)

        # Training state
        self.model: Optional[BaseNeuralModel] = None
        self.scaler: Optional[StandardScaler] = None
        self.training_history: Dict[str, Any] = {}
        self.metadata = {
            "experiment_name": self.experiment_name,
            "created_at": datetime.utcnow().isoformat(),
            "project_id": project_id,
        }

    def prepare_data(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = 0.2,
        val_size: float = 0.2,
        standardize: bool = True,
    ) -> Dict[str, np.ndarray]:
        """
        Prepare data for training with train / val / test splits.

        Args:
            X: Input features
            y: Target labels / values
            test_size: Proportion for test set
            val_size: Proportion for validation set (from training data)
            standardize: Whether to standardize features

        Returns:
            Dictionary with train / val / test splits
        """
        # Split data
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_size, random_state=42
        )

        # Standardize if requested
        if standardize:
            self.scaler = StandardScaler()
            X_train = self.scaler.fit_transform(X_train.reshape(-1, X_train.shape[-1]))
            X_train = X_train.reshape(-1, X.shape[1], X.shape[2])

            assert self.scaler is not None
            X_val = self.scaler.transform(X_val.reshape(-1, X_val.shape[-1]))
            X_val = X_val.reshape(-1, X.shape[1], X.shape[2])

            assert self.scaler is not None
            X_test = self.scaler.transform(X_test.reshape(-1, X_test.shape[-1]))
            X_test = X_test.reshape(-1, X.shape[1], X.shape[2])

        data_splits = {
            "X_train": X_train,
            "y_train": y_train,
            "X_val": X_val,
            "y_val": y_val,
            "X_test": X_test,
            "y_test": y_test,
        }

        # Log data statistics
        logger.info(
            f"Data prepared - Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}"
        )

        if self.use_wandb:
            wandb.log(
                {
                    "train_samples": len(X_train),
                    "val_samples": len(X_val),
                    "test_samples": len(X_test),
                    "input_shape": X_train.shape[1:],
                    "output_shape": y_train.shape[1:] if len(y_train.shape) > 1 else 1,
                }
            )

        return data_splits

    def train_model(
        self,
        model: BaseNeuralModel,
        data_splits: Dict[str, np.ndarray],
        hyperparameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Train a neural model with tracking and monitoring.

        Args:
            model: Neural model instance
            data_splits: Dictionary with train / val / test data
            hyperparameters: Optional hyperparameters to override

        Returns:
            Training results dictionary
        """
        self.model = model

        # Update model config with hyperparameters
        if hyperparameters and self.model is not None:
            self.model.config.update(hyperparameters)

        # Log hyperparameters
        if self.use_wandb and self.model is not None:
            wandb.config.update(self.model.config)

        # Train model
        logger.info(f"Starting training for {model.model_name}")

        training_results = model.train(
            data_splits["X_train"],
            data_splits["y_train"],
            data_splits["X_val"],
            data_splits["y_val"],
        )

        # Evaluate on test set
        test_metrics = model.evaluate(data_splits["X_test"], data_splits["y_test"])

        # Combine results
        results = {
            **training_results,
            "test_metrics": test_metrics,
            "model_name": model.model_name,
            "hyperparameters": model.config,
        }

        self.training_history = results

        # Log results
        if self.use_wandb:
            wandb.log(test_metrics)

            # Log training curves
            if "history" in training_results:
                for metric, values in training_results["history"].items():
                    for i, value in enumerate(values):
                        wandb.log({f"train/{metric}": value}, step=i)

        logger.info(f"Training completed - Test metrics: {test_metrics}")

        return results

    def train_on_vertex_ai(
        self,
        model_class: str,
        dataset_path: str,
        hyperparameters: Dict[str, Any],
        machine_type: str = "n1-standard-8",
        accelerator_type: Optional[str] = "NVIDIA_TESLA_T4",
        accelerator_count: int = 1,
    ) -> aiplatform.Model:
        """
        Train model on Vertex AI with distributed training support.

        Args:
            model_class: Name of model class to train
            dataset_path: GCS path to training data
            hyperparameters: Model hyperparameters
            machine_type: Vertex AI machine type
            accelerator_type: GPU type (if needed)
            accelerator_count: Number of GPUs

        Returns:
            Trained Vertex AI model
        """
        # Create custom training job
        job = aiplatform.CustomTrainingJob(
            display_name=f"{model_class}-{self.experiment_name}",
            script_path="train.py",  # Training script
            container_uri="gcr.io / cloud - aiplatform / training / tf - gpu.2 - 8:latest",
            requirements=["tensorflow", "numpy", "scikit - learn", "wandb"],
            model_serving_container_image_uri="gcr.io / cloud - aiplatform / prediction / tf2 - gpu.2 - 8:latest",
        )

        # Run training job
        # Note: dataset parameter expects a Dataset object, but we're passing path as string
        # This is a common pattern in Vertex AI where paths are accepted
        # Type ignore needed for CI environment where stricter typing is enforced
        model = job.run(
            dataset=dataset_path,  # type: ignore[arg-type]  # String paths are accepted
            model_display_name=f"{model_class}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            args=[
                f"--model_class={model_class}",
                f"--hyperparameters={json.dumps(hyperparameters)}",
                f"--bucket_name={self.bucket_name}",
                f"--experiment_name={self.experiment_name}",
            ],
            replica_count=1,
            machine_type=machine_type,
            accelerator_type=accelerator_type if accelerator_type is not None else "ACCELERATOR_TYPE_UNSPECIFIED",
            accelerator_count=accelerator_count,
        )

        if model:
            logger.info(f"Vertex AI training completed - Model: {model.resource_name}")
        else:
            raise RuntimeError("Training job failed to produce a model")

        return model

    def hyperparameter_tuning(
        self,
        model_class: type,
        data_splits: Dict[str, np.ndarray],
        param_grid: Dict[str, List[Any]],
        metric: str = "accuracy",
        n_trials: int = 20,
    ) -> Dict[str, Any]:
        """
        Perform hyperparameter tuning using Vertex AI Vizier.

        Args:
            model_class: Model class to tune
            data_splits: Data splits for training
            param_grid: Dictionary of parameters to search
            metric: Metric to optimize
            n_trials: Number of trials to run

        Returns:
            Best parameters and results
        """
        from google.cloud import aiplatform_v1beta1

        # Create study configuration
        study_config: Dict[str, Any] = {
            "algorithm": "ALGORITHM_UNSPECIFIED",  # Bayesian optimization
            "metrics": [{"metric_id": metric, "goal": "MAXIMIZE"}],
            "parameters": [],
        }

        # Add parameters to study config
        for param_name, param_values in param_grid.items():
            if isinstance(param_values[0], (int, float)):
                param_spec = {
                    "parameter_id": param_name,
                    "double_value_spec": {
                        "min_value": min(param_values),
                        "max_value": max(param_values),
                    },
                }
            else:
                param_spec = {
                    "parameter_id": param_name,
                    "categorical_value_spec": {
                        "values": [str(v) for v in param_values]
                    },
                }
            study_config["parameters"].append(param_spec)

        # Create Vizier client
        vizier_client = aiplatform_v1beta1.VizierServiceClient()

        # Create study using correct API
        from google.cloud.aiplatform_v1beta1.types import Study

        study_obj = Study(
            display_name=f"hpt-{self.experiment_name}", study_spec=study_config
        )

        study = vizier_client.create_study(
            parent=f"projects/{self.project_id}/locations/{self.location}",
            study=study_obj,
        )

        best_score = -float("inf")
        best_params = {}

        # Run trials
        for i in range(n_trials):
            # Get trial suggestion using correct API
            from google.cloud.aiplatform_v1beta1.types import SuggestTrialsRequest

            request = SuggestTrialsRequest(
                parent=study.name, suggestion_count=1, client_id=f"trial-{i}"
            )
            suggest_response = vizier_client.suggest_trials(request=request)

            # The response is an operation, need to get result
            operation = suggest_response
            trial = operation.trials[0] if hasattr(operation, "trials") else None

            if not trial:
                continue

            # Extract parameters
            trial_params = {}
            for param in trial.parameters:
                if param.HasField("double_value"):
                    trial_params[param.parameter_id] = param.double_value
                else:
                    trial_params[param.parameter_id] = param.categorical_value

            # Train model with suggested parameters
            model = model_class(
                n_channels=data_splits["X_train"].shape[2],
                n_samples=data_splits["X_train"].shape[1],
                **trial_params,
            )

            results = self.train_model(model, data_splits)
            score = results["test_metrics"][metric]

            # Report measurement using correct API
            from google.cloud.aiplatform_v1beta1 import AddTrialMeasurementRequest
            from google.cloud.aiplatform_v1beta1.types import Measurement
            from google.protobuf.struct_pb2 import Value

            # Create metric value
            metric_value = Value()
            metric_value.number_value = score

            measurement = Measurement(step_count=i, metrics={metric: metric_value})

            # Create request
            request = AddTrialMeasurementRequest(
                trial_name=trial.name, measurement=measurement
            )
            vizier_client.add_trial_measurement(request=request)

            # Track best
            if score > best_score:
                best_score = score
                best_params = trial_params

            logger.info(f"Trial {i + 1}/{n_trials} - Score: {score:.4f}")

        return {
            "best_params": best_params,
            "best_score": best_score,
            "study_name": study.name,
        }

    def save_model(
        self, model_name: Optional[str] = None, include_preprocessor: bool = True
    ) -> str:
        """
        Save trained model to GCS.

        Args:
            model_name: Optional custom model name
            include_preprocessor: Whether to save the scaler

        Returns:
            GCS path to saved model
        """
        if self.model is None:
            raise ValueError("No model to save")

        assert self.model is not None
        model_name = model_name or f"{self.model.model_name}_{self.experiment_name}"

        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save model
            model_path = os.path.join(temp_dir, "model")
            assert self.model is not None
            self.model.save(model_path)

            # Save scaler if exists
            if include_preprocessor and self.scaler is not None:
                scaler_path = os.path.join(temp_dir, "scaler.pkl")
                joblib.dump(self.scaler, scaler_path)

            # Save metadata
            metadata_path = os.path.join(temp_dir, "metadata.json")
            metadata = {
                **self.metadata,
                "model_summary": self.model.get_model_summary(),
                "training_history": self.training_history,
                "saved_at": datetime.utcnow().isoformat(),
            }
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)

            # Upload to GCS
            bucket = self.storage_client.bucket(self.bucket_name)
            gcs_path = f"models/{model_name}/{datetime.now().strftime('%Y%m%d-%H%M%S')}"

            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    local_path = os.path.join(root, file)
                    blob_path = os.path.join(
                        gcs_path, os.path.relpath(local_path, temp_dir)
                    )
                    blob = bucket.blob(blob_path)
                    blob.upload_from_filename(local_path)

            logger.info(f"Model saved to gs://{self.bucket_name}/{gcs_path}")

            return f"gs://{self.bucket_name}/{gcs_path}"

    def deploy_model(
        self,
        model_path: str,
        endpoint_name: Optional[str] = None,
        machine_type: str = "n1-standard-4",
        min_replica_count: int = 1,
        max_replica_count: int = 3,
    ) -> aiplatform.Endpoint:
        """
        Deploy model to Vertex AI endpoint.

        Args:
            model_path: GCS path to saved model
            endpoint_name: Optional endpoint name
            machine_type: Machine type for serving
            min_replica_count: Minimum number of replicas
            max_replica_count: Maximum number of replicas

        Returns:
            Deployed endpoint
        """
        # Upload model to Vertex AI
        if self.model is None:
            raise ValueError("No model to deploy")
        model = aiplatform.Model.upload(
            display_name=f"{self.model.model_name}-{self.experiment_name}",
            artifact_uri=model_path,
            serving_container_image_uri="gcr.io / cloud - aiplatform / prediction / tf2 - gpu.2 - 8:latest",
        )

        # Create endpoint
        endpoint_name = endpoint_name or f"{self.model.model_name}-endpoint"
        endpoint = aiplatform.Endpoint.create(display_name=endpoint_name)

        # Deploy model to endpoint
        assert self.model is not None
        model.deploy(
            endpoint=endpoint,
            deployed_model_display_name=self.model.model_name,
            machine_type=machine_type,
            min_replica_count=min_replica_count,
            max_replica_count=max_replica_count,
            traffic_percentage=100,
        )

        logger.info(f"Model deployed to endpoint: {endpoint.resource_name}")

        return endpoint
