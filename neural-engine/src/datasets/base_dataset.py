"""Base dataset interface for neural data."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, Tuple, Generator
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class DatasetConfig:
    """Configuration for dataset loading."""

    name: str
    version: str = "1.0"
    cache_dir: Path = Path.home() / ".neurascale" / "datasets"
    download_if_missing: bool = True
    preprocessing_params: Dict[str, Any] = field(default_factory=dict)
    validation_split: float = 0.2
    test_split: float = 0.1
    random_seed: int = 42
    batch_size: int = 32
    lazy_loading: bool = True
    max_cache_size_gb: float = 10.0


class BaseDataset(ABC):
    """Abstract base class for neural datasets."""

    def __init__(self, config: DatasetConfig):
        """
        Initialize dataset.

        Args:
            config: Dataset configuration
        """
        self.config = config
        self.cache_dir = config.cache_dir / config.name / config.version
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._metadata: Dict[str, Any] = {}
        self._is_loaded = False
        self._cached_data: Optional[Dict[str, np.ndarray]] = None

    @abstractmethod
    def download(self) -> None:
        """Download dataset if not present locally."""
        pass

    @abstractmethod
    def load(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load dataset.

        Returns:
            Tuple of (data, labels) arrays
        """
        pass

    @abstractmethod
    def preprocess(self, data: np.ndarray) -> np.ndarray:
        """
        Apply dataset-specific preprocessing.

        Args:
            data: Raw data array

        Returns:
            Preprocessed data
        """
        pass

    @abstractmethod
    def validate(self, data: np.ndarray) -> bool:
        """
        Validate data quality.

        Args:
            data: Data to validate

        Returns:
            True if data passes validation
        """
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """Get dataset metadata."""
        return self._metadata

    def split_data(self, data: np.ndarray, labels: np.ndarray) -> Tuple[
        Tuple[np.ndarray, np.ndarray],
        Tuple[np.ndarray, np.ndarray],
        Tuple[np.ndarray, np.ndarray],
    ]:
        """
        Split data into train, validation, and test sets.

        Args:
            data: Data array
            labels: Labels array

        Returns:
            Tuple of (train, val, test) where each is (data, labels)
        """
        np.random.seed(self.config.random_seed)
        n_samples = len(data)
        indices = np.random.permutation(n_samples)

        # Calculate split points
        val_size = int(n_samples * self.config.validation_split)
        test_size = int(n_samples * self.config.test_split)
        train_size = n_samples - val_size - test_size

        # Split indices
        train_idx = indices[:train_size]
        val_idx = indices[train_size : train_size + val_size]
        test_idx = indices[train_size + val_size :]

        # Split data and labels
        train_data = (data[train_idx], labels[train_idx])
        val_data = (data[val_idx], labels[val_idx])
        test_data = (data[test_idx], labels[test_idx])

        logger.info(
            f"Data split - Train: {len(train_idx)}, Val: {len(val_idx)}, Test: {len(test_idx)}"
        )

        return train_data, val_data, test_data

    def get_batch_iterator(
        self, data: np.ndarray, labels: np.ndarray, shuffle: bool = True
    ) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
        """
        Create batch iterator for data.

        Args:
            data: Data array
            labels: Labels array
            shuffle: Whether to shuffle data

        Yields:
            Batches of (data, labels)
        """
        n_samples = len(data)
        indices = np.arange(n_samples)

        if shuffle:
            np.random.shuffle(indices)

        for start_idx in range(0, n_samples, self.config.batch_size):
            end_idx = min(start_idx + self.config.batch_size, n_samples)
            batch_idx = indices[start_idx:end_idx]

            yield data[batch_idx], labels[batch_idx]

    def cache_exists(self) -> bool:
        """Check if cached data exists."""
        cache_file = self.cache_dir / "data.npz"
        metadata_file = self.cache_dir / "metadata.json"
        return cache_file.exists() and metadata_file.exists()

    def save_cache(
        self, data: np.ndarray, labels: np.ndarray, metadata: Dict[str, Any]
    ) -> None:
        """Save data to cache."""
        import json

        # Save data
        cache_file = self.cache_dir / "data.npz"
        np.savez_compressed(cache_file, data=data, labels=labels)

        # Save metadata
        metadata_file = self.cache_dir / "metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Saved cache to {self.cache_dir}")

    def load_cache(self) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """Load data from cache."""
        import json

        # Load data
        cache_file = self.cache_dir / "data.npz"
        with np.load(cache_file) as npz:
            data = npz["data"]
            labels = npz["labels"]

        # Load metadata
        metadata_file = self.cache_dir / "metadata.json"
        with open(metadata_file, "r") as f:
            metadata = json.load(f)

        logger.info(f"Loaded cache from {self.cache_dir}")

        return data, labels, metadata
