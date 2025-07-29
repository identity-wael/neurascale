"""
Base interfaces for classification components
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional

from .types import ClassificationResult, FeatureVector, ModelMetrics, NeuralData


class BaseClassifier(ABC):
    """Base interface for all classifiers"""

    @abstractmethod
    async def classify(self, features: FeatureVector) -> ClassificationResult:
        """Perform classification on extracted features"""
        pass

    @abstractmethod
    async def load_model(self, model_path: str) -> None:
        """Load model from path"""
        pass

    @abstractmethod
    async def update_model(self, feedback: Dict[str, Any]) -> None:
        """Update model with feedback (online learning)"""
        pass

    @abstractmethod
    def get_metrics(self) -> ModelMetrics:
        """Get current model performance metrics"""
        pass


class BaseFeatureExtractor(ABC):
    """Base interface for feature extraction"""

    @abstractmethod
    async def extract_features(self, data: NeuralData) -> FeatureVector:
        """Extract features from neural data"""
        pass

    @abstractmethod
    def get_feature_names(self) -> List[str]:
        """Get list of feature names"""
        pass

    @abstractmethod
    def get_required_window_size(self) -> float:
        """Get required window size in milliseconds"""
        pass


class BaseStreamProcessor(ABC):
    """Base interface for stream processing"""

    @abstractmethod
    async def process_stream(
        self, stream: AsyncIterator[NeuralData]
    ) -> AsyncIterator[ClassificationResult]:
        """Process neural data stream and yield classification results"""
        pass

    @abstractmethod
    async def add_classifier(
        self,
        name: str,
        classifier: BaseClassifier,
        feature_extractor: BaseFeatureExtractor,
    ) -> None:
        """Add a classifier to the pipeline"""
        pass

    @abstractmethod
    async def remove_classifier(self, name: str) -> None:
        """Remove a classifier from the pipeline"""
        pass

    @abstractmethod
    def get_active_classifiers(self) -> List[str]:
        """Get list of active classifier names"""
        pass


class BaseModelServer(ABC):
    """Base interface for model serving"""

    @abstractmethod
    async def predict(
        self, model_name: str, instances: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Get predictions from model"""
        pass

    @abstractmethod
    async def deploy_model(self, model: Any, model_name: str, version: str) -> str:
        """Deploy a model and return endpoint"""
        pass

    @abstractmethod
    async def undeploy_model(self, model_name: str, version: str) -> None:
        """Undeploy a model"""
        pass

    @abstractmethod
    async def get_model_metrics(self, model_name: str) -> ModelMetrics:
        """Get model performance metrics"""
        pass


class BaseBuffer(ABC):
    """Base interface for data buffering"""

    @abstractmethod
    async def add_data(self, data: NeuralData) -> None:
        """Add data to buffer"""
        pass

    @abstractmethod
    async def get_window(self, duration_ms: float) -> Optional[NeuralData]:
        """Get data window of specified duration"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear buffer"""
        pass

    @abstractmethod
    def get_buffer_size(self) -> int:
        """Get current buffer size in samples"""
        pass
