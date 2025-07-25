"""Neural models package for BCI applications."""

from .base_models import (
    BaseNeuralModel,
    TensorFlowBaseModel,
    PyTorchBaseModel,
    EEGNet,
    CNNLSTMModel,
    TransformerModel,
)

from .movement_decoder import MovementDecoder, KalmanFilterDecoder, CursorControlDecoder

from .emotion_classifier import (
    EmotionClassifier,
    ValenceArousalRegressor,
    EmotionFeatureExtractor,
)

from .training_pipeline import NeuralModelTrainingPipeline

from .inference_server import NeuralInferenceServer, ModelRegistry, ModelOptimizer

__all__ = [
    # Base models
    "BaseNeuralModel",
    "TensorFlowBaseModel",
    "PyTorchBaseModel",
    "EEGNet",
    "CNNLSTMModel",
    "TransformerModel",
    # Movement decoders
    "MovementDecoder",
    "KalmanFilterDecoder",
    "CursorControlDecoder",
    # Emotion classifiers
    "EmotionClassifier",
    "ValenceArousalRegressor",
    "EmotionFeatureExtractor",
    # Training and inference
    "NeuralModelTrainingPipeline",
    "NeuralInferenceServer",
    "ModelRegistry",
    "ModelOptimizer",
]
