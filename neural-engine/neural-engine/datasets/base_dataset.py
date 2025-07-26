"""Base dataset infrastructure for neural data.

This module provides abstract base classes and common functionality for all
neural datasets in the NeuraScale system.
"""

import abc
import logging
from typing import Dict, List, Optional, Any, Iterator, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum
import numpy as np
import hashlib
import json

logger = logging.getLogger(__name__)


class DatasetSplit(Enum):
    """Standard dataset splits."""

    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"
    ALL = "all"


@dataclass
class DatasetInfo:
    """Metadata information about a dataset."""

    name: str
    version: str
    description: str
    source_url: Optional[str] = None
    license: Optional[str] = None
    citation: Optional[str] = None

    # Data characteristics
    n_samples: int = 0
    n_channels: int = 0
    sampling_rate: float = 0.0
    duration_seconds: float = 0.0

    # Signal types
    signal_types: List[str] = field(default_factory=list)

    # Subject information
    n_subjects: int = 0
    subject_ids: List[str] = field(default_factory=list)

    # Task information
    task_type: Optional[str] = None
    n_classes: Optional[int] = None
    class_names: Optional[List[str]] = None

    # Storage information
    total_size_mb: float = 0.0
    format: str = "unknown"

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.utcnow())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "source_url": self.source_url,
            "license": self.license,
            "citation": self.citation,
            "n_samples": self.n_samples,
            "n_channels": self.n_channels,
            "sampling_rate": self.sampling_rate,
            "duration_seconds": self.duration_seconds,
            "signal_types": self.signal_types,
            "n_subjects": self.n_subjects,
            "subject_ids": self.subject_ids,
            "task_type": self.task_type,
            "n_classes": self.n_classes,
            "class_names": self.class_names,
            "total_size_mb": self.total_size_mb,
            "format": self.format,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DatasetInfo":
        """Create from dictionary representation."""
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


@dataclass
class DataSample:
    """Single sample from a dataset."""

    data: np.ndarray  # Shape: (n_channels, n_samples)
    label: Optional[Union[int, np.ndarray]] = None

    # Metadata
    sample_id: Optional[str] = None
    subject_id: Optional[str] = None
    session_id: Optional[str] = None
    trial_id: Optional[int] = None

    # Timing information
    timestamp: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    sampling_rate: Optional[float] = None

    # Additional info
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def n_channels(self) -> int:
        """Number of channels."""
        return self.data.shape[0]

    @property
    def n_samples(self) -> int:
        """Number of time samples."""
        return self.data.shape[1]


class BaseDataset(abc.ABC):
    """Abstract base class for all neural datasets."""

    def __init__(
        self,
        data_dir: Optional[Path] = None,
        cache_dir: Optional[Path] = None,
        download: bool = True,
        transform: Optional[Any] = None,
        target_transform: Optional[Any] = None,
    ):
        """
        Initialize dataset.

        Args:
            data_dir: Directory containing the dataset
            cache_dir: Directory for caching processed data
            download: Whether to download the dataset if not found
            transform: Transform to apply to data
            target_transform: Transform to apply to labels
        """
        self.data_dir = Path(data_dir) if data_dir else self._default_data_dir()
        self.cache_dir = Path(cache_dir) if cache_dir else self._default_cache_dir()
        self.download = download
        self.transform = transform
        self.target_transform = target_transform

        # Dataset info
        self._info: Optional[DatasetInfo] = None

        # Cache for loaded data
        self._cache: Dict[str, Any] = {}
        self._cache_enabled = True

        # Initialize dataset
        self._initialize()

    def _default_data_dir(self) -> Path:
        """Get default data directory."""
        return Path.home() / ".neurascale" / "datasets" / self.name

    def _default_cache_dir(self) -> Path:
        """Get default cache directory."""
        return Path.home() / ".neurascale" / "cache" / self.name

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Dataset name."""
        pass

    @property
    @abc.abstractmethod
    def version(self) -> str:
        """Dataset version."""
        pass

    @property
    def info(self) -> DatasetInfo:
        """Get dataset information."""
        if self._info is None:
            self._info = self._load_info()
        return self._info

    def _initialize(self):
        """Initialize dataset (download if needed)."""
        # Create directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Check if dataset exists
        if not self._check_exists():
            if self.download:
                logger.info(f"Dataset {self.name} not found. Downloading...")
                self._download()
            else:
                raise RuntimeError(
                    f"Dataset {self.name} not found at {self.data_dir}. "
                    "Set download=True to download it."
                )

        # Verify integrity
        if not self._verify_integrity():
            raise RuntimeError(
                f"Dataset {self.name} integrity check failed. "
                "Try deleting the dataset and downloading again."
            )

    @abc.abstractmethod
    def _check_exists(self) -> bool:
        """Check if dataset exists."""
        pass

    @abc.abstractmethod
    def _download(self):
        """Download the dataset."""
        pass

    def _verify_integrity(self) -> bool:
        """Verify dataset integrity."""
        # Default implementation - can be overridden
        return True

    @abc.abstractmethod
    def _load_info(self) -> DatasetInfo:
        """Load dataset information."""
        pass

    @abc.abstractmethod
    def __len__(self) -> int:
        """Number of samples in the dataset."""
        pass

    @abc.abstractmethod
    def __getitem__(self, idx: int) -> DataSample:
        """Get a single sample."""
        pass

    def get_split(self, split: DatasetSplit) -> "BaseDataset":
        """
        Get a specific split of the dataset.

        Args:
            split: Dataset split to retrieve

        Returns:
            Dataset subset for the specified split
        """
        raise NotImplementedError(
            f"Dataset {self.name} does not implement split functionality"
        )

    def get_subject_data(self, subject_id: str) -> List[DataSample]:
        """
        Get all data for a specific subject.

        Args:
            subject_id: Subject identifier

        Returns:
            List of data samples for the subject
        """
        samples = []
        for i in range(len(self)):
            sample = self[i]
            if sample.subject_id == subject_id:
                samples.append(sample)
        return samples

    def iter_batches(
        self,
        batch_size: int,
        shuffle: bool = False,
        drop_last: bool = False,
    ) -> Iterator[List[DataSample]]:
        """
        Iterate over batches of samples.

        Args:
            batch_size: Number of samples per batch
            shuffle: Whether to shuffle the data
            drop_last: Whether to drop the last incomplete batch

        Yields:
            Batches of data samples
        """
        indices = list(range(len(self)))

        if shuffle:
            import random

            random.shuffle(indices)

        for i in range(0, len(indices), batch_size):
            batch_indices = indices[i : i + batch_size]

            if len(batch_indices) < batch_size and drop_last:
                break

            batch = [self[idx] for idx in batch_indices]
            yield batch

    def cache_key(self, *args) -> str:
        """Generate cache key from arguments."""
        key_data = json.dumps(args, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()

    def get_cached(self, key: str) -> Optional[Any]:
        """Get cached data."""
        if self._cache_enabled and key in self._cache:
            logger.debug(f"Cache hit for key: {key}")
            return self._cache[key]

        # Check disk cache
        cache_file = self.cache_dir / f"{key}.npz"
        if cache_file.exists():
            logger.debug(f"Loading from disk cache: {cache_file}")
            data = np.load(cache_file, allow_pickle=True)
            return data

        return None

    def set_cached(self, key: str, value: Any, persist: bool = False):
        """Set cached data."""
        if self._cache_enabled:
            self._cache[key] = value

            if persist:
                # Save to disk
                cache_file = self.cache_dir / f"{key}.npz"
                np.savez_compressed(cache_file, data=value)
                logger.debug(f"Saved to disk cache: {cache_file}")

    def clear_cache(self):
        """Clear memory cache."""
        self._cache.clear()
        logger.info(f"Cleared memory cache for dataset {self.name}")

    def enable_cache(self):
        """Enable caching."""
        self._cache_enabled = True

    def disable_cache(self):
        """Disable caching."""
        self._cache_enabled = False
        self.clear_cache()

    def compute_statistics(self) -> Dict[str, Any]:
        """
        Compute dataset statistics.

        Returns:
            Dictionary with statistics (mean, std, etc.)
        """
        # Check cache
        cache_key = self.cache_key("statistics", self.version)
        cached = self.get_cached(cache_key)
        if cached is not None:
            return cached.item()

        logger.info(f"Computing statistics for dataset {self.name}...")

        # Compute statistics
        all_data = []
        for i in range(min(1000, len(self))):  # Sample first 1000 items
            sample = self[i]
            all_data.append(sample.data)

        all_data = np.concatenate(all_data, axis=1)

        stats = {
            "mean": np.mean(all_data, axis=1).tolist(),
            "std": np.std(all_data, axis=1).tolist(),
            "min": np.min(all_data, axis=1).tolist(),
            "max": np.max(all_data, axis=1).tolist(),
            "median": np.median(all_data, axis=1).tolist(),
        }

        # Cache results
        self.set_cached(cache_key, stats, persist=True)

        return stats

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"version='{self.version}', "
            f"n_samples={len(self)}, "
            f"data_dir='{self.data_dir}'"
            f")"
        )
