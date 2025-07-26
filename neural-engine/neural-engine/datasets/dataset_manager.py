"""Dataset manager and registry for neural datasets.

This module provides centralized management of datasets including registration,
loading, caching, and metadata management.
"""

import logging
import json
from typing import Dict, List, Optional, Type, Any, Callable
from pathlib import Path
from datetime import datetime
import threading
import pickle
import hashlib

from .base_dataset import BaseDataset, DatasetInfo, DatasetSplit, DataSample

logger = logging.getLogger(__name__)


class DatasetRegistry:
    """Registry for dataset classes."""

    def __init__(self):
        """Initialize dataset registry."""
        self._datasets: Dict[str, Type[BaseDataset]] = {}
        self._loaders: Dict[str, Callable] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()

    def register(
        self,
        name: str,
        dataset_class: Type[BaseDataset],
        loader: Optional[Callable] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Register a dataset class.

        Args:
            name: Dataset name
            dataset_class: Dataset class (must inherit from BaseDataset)
            loader: Optional custom loader function
            metadata: Optional metadata about the dataset
        """
        with self._lock:
            if name in self._datasets:
                logger.warning(f"Dataset '{name}' already registered. Overwriting.")

            if not issubclass(dataset_class, BaseDataset):
                raise ValueError(
                    f"Dataset class must inherit from BaseDataset, got {dataset_class}"
                )

            self._datasets[name] = dataset_class

            if loader is not None:
                self._loaders[name] = loader

            if metadata is not None:
                self._metadata[name] = metadata

            logger.info(f"Registered dataset: {name}")

    def unregister(self, name: str):
        """Unregister a dataset."""
        with self._lock:
            if name not in self._datasets:
                raise ValueError(f"Dataset '{name}' not found in registry")

            del self._datasets[name]
            self._loaders.pop(name, None)
            self._metadata.pop(name, None)

            logger.info(f"Unregistered dataset: {name}")

    def get(self, name: str) -> Type[BaseDataset]:
        """Get dataset class by name."""
        with self._lock:
            if name not in self._datasets:
                raise ValueError(
                    f"Dataset '{name}' not found in registry. "
                    f"Available datasets: {list(self._datasets.keys())}"
                )
            return self._datasets[name]

    def get_loader(self, name: str) -> Optional[Callable]:
        """Get custom loader for dataset."""
        with self._lock:
            return self._loaders.get(name)

    def get_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for dataset."""
        with self._lock:
            return self._metadata.get(name)

    def list_datasets(self) -> List[str]:
        """List all registered datasets."""
        with self._lock:
            return list(self._datasets.keys())

    def __contains__(self, name: str) -> bool:
        """Check if dataset is registered."""
        with self._lock:
            return name in self._datasets

    def __repr__(self) -> str:
        """String representation."""
        return f"DatasetRegistry(datasets={self.list_datasets()})"


class DatasetManager:
    """Manager for loading and caching datasets."""

    def __init__(
        self,
        data_root: Optional[Path] = None,
        cache_root: Optional[Path] = None,
        registry: Optional[DatasetRegistry] = None,
    ):
        """
        Initialize dataset manager.

        Args:
            data_root: Root directory for dataset storage
            cache_root: Root directory for cache storage
            registry: Dataset registry (creates new one if None)
        """
        self.data_root = Path(data_root) if data_root else self._default_data_root()
        self.cache_root = Path(cache_root) if cache_root else self._default_cache_root()
        self.registry = registry if registry else DatasetRegistry()

        # Create directories
        self.data_root.mkdir(parents=True, exist_ok=True)
        self.cache_root.mkdir(parents=True, exist_ok=True)

        # Loaded datasets cache
        self._loaded_datasets: Dict[str, BaseDataset] = {}
        self._dataset_info_cache: Dict[str, DatasetInfo] = {}

        # Metadata storage
        self._metadata_file = self.cache_root / "dataset_metadata.json"
        self._load_metadata()

        # Lazy loading configuration
        self._lazy_loading = True
        self._preload_info = True

    def _default_data_root(self) -> Path:
        """Get default data root directory."""
        return Path.home() / ".neurascale" / "datasets"

    def _default_cache_root(self) -> Path:
        """Get default cache root directory."""
        return Path.home() / ".neurascale" / "cache"

    def _load_metadata(self):
        """Load dataset metadata from disk."""
        if self._metadata_file.exists():
            try:
                with open(self._metadata_file, 'r') as f:
                    metadata = json.load(f)

                # Convert back to DatasetInfo objects
                for name, info_dict in metadata.items():
                    self._dataset_info_cache[name] = DatasetInfo.from_dict(info_dict)

                logger.info(f"Loaded metadata for {len(metadata)} datasets")
            except Exception as e:
                logger.error(f"Failed to load metadata: {e}")

    def _save_metadata(self):
        """Save dataset metadata to disk."""
        metadata = {}
        for name, info in self._dataset_info_cache.items():
            metadata[name] = info.to_dict()

        try:
            with open(self._metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")

    def register_dataset(
        self,
        name: str,
        dataset_class: Type[BaseDataset],
        loader: Optional[Callable] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Register a dataset with the manager.

        Args:
            name: Dataset name
            dataset_class: Dataset class
            loader: Optional custom loader
            metadata: Optional metadata
        """
        self.registry.register(name, dataset_class, loader, metadata)

    def load_dataset(
        self,
        name: str,
        split: Optional[DatasetSplit] = None,
        download: bool = True,
        transform: Optional[Any] = None,
        target_transform: Optional[Any] = None,
        force_reload: bool = False,
        **kwargs,
    ) -> BaseDataset:
        """
        Load a dataset.

        Args:
            name: Dataset name
            split: Dataset split to load
            download: Whether to download if not found
            transform: Data transform
            target_transform: Target transform
            force_reload: Force reload even if cached
            **kwargs: Additional arguments for dataset constructor

        Returns:
            Loaded dataset
        """
        # Generate cache key
        cache_key = self._generate_cache_key(name, split, kwargs)

        # Check if already loaded
        if not force_reload and cache_key in self._loaded_datasets:
            logger.info(f"Using cached dataset: {name}")
            return self._loaded_datasets[cache_key]

        # Get dataset class
        dataset_class = self.registry.get(name)

        # Check for custom loader
        loader = self.registry.get_loader(name)
        if loader is not None:
            logger.info(f"Using custom loader for dataset: {name}")
            dataset = loader(
                data_dir=self.data_root / name,
                cache_dir=self.cache_root / name,
                download=download,
                transform=transform,
                target_transform=target_transform,
                **kwargs,
            )
        else:
            # Use default constructor
            logger.info(f"Loading dataset: {name}")
            dataset = dataset_class(
                data_dir=self.data_root / name,
                cache_dir=self.cache_root / name,
                download=download,
                transform=transform,
                target_transform=target_transform,
                **kwargs,
            )

        # Get specific split if requested
        if split is not None and split != DatasetSplit.ALL:
            dataset = dataset.get_split(split)

        # Cache dataset
        if self._lazy_loading:
            self._loaded_datasets[cache_key] = dataset

        # Cache dataset info
        if name not in self._dataset_info_cache:
            self._dataset_info_cache[name] = dataset.info
            self._save_metadata()

        return dataset

    def _generate_cache_key(
        self,
        name: str,
        split: Optional[DatasetSplit],
        kwargs: Dict[str, Any],
    ) -> str:
        """Generate cache key for dataset configuration."""
        key_data = {
            "name": name,
            "split": split.value if split else None,
            "kwargs": kwargs,
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get_dataset_info(self, name: str) -> DatasetInfo:
        """
        Get dataset information without loading the full dataset.

        Args:
            name: Dataset name

        Returns:
            Dataset information
        """
        # Check cache first
        if name in self._dataset_info_cache:
            return self._dataset_info_cache[name]

        # Load minimal dataset to get info
        dataset = self.load_dataset(name, download=False)
        info = dataset.info

        # Cache for future use
        self._dataset_info_cache[name] = info
        self._save_metadata()

        # Unload dataset if lazy loading is enabled
        if self._lazy_loading:
            cache_key = self._generate_cache_key(name, None, {})
            self._loaded_datasets.pop(cache_key, None)

        return info

    def list_available_datasets(self) -> List[Dict[str, Any]]:
        """
        List all available datasets with their information.

        Returns:
            List of dataset information dictionaries
        """
        datasets = []

        for name in self.registry.list_datasets():
            try:
                info = self.get_dataset_info(name)
                dataset_dict = info.to_dict()
                dataset_dict["registered_name"] = name
                dataset_dict["is_downloaded"] = self.is_downloaded(name)
                datasets.append(dataset_dict)
            except Exception as e:
                logger.warning(f"Failed to get info for dataset {name}: {e}")
                datasets.append({
                    "registered_name": name,
                    "error": str(e),
                })

        return datasets

    def is_downloaded(self, name: str) -> bool:
        """
        Check if a dataset is downloaded.

        Args:
            name: Dataset name

        Returns:
            True if dataset is downloaded
        """
        dataset_dir = self.data_root / name
        return dataset_dir.exists() and any(dataset_dir.iterdir())

    def delete_dataset(self, name: str, delete_cache: bool = True):
        """
        Delete a downloaded dataset.

        Args:
            name: Dataset name
            delete_cache: Whether to also delete cached data
        """
        # Remove from loaded datasets
        keys_to_remove = [
            key for key in self._loaded_datasets
            if key.startswith(name)
        ]
        for key in keys_to_remove:
            del self._loaded_datasets[key]

        # Delete data directory
        dataset_dir = self.data_root / name
        if dataset_dir.exists():
            import shutil
            shutil.rmtree(dataset_dir)
            logger.info(f"Deleted dataset data: {dataset_dir}")

        # Delete cache if requested
        if delete_cache:
            cache_dir = self.cache_root / name
            if cache_dir.exists():
                import shutil
                shutil.rmtree(cache_dir)
                logger.info(f"Deleted dataset cache: {cache_dir}")

        # Remove from info cache
        self._dataset_info_cache.pop(name, None)
        self._save_metadata()

    def clear_cache(self, name: Optional[str] = None):
        """
        Clear cached data.

        Args:
            name: Dataset name (clears all if None)
        """
        if name is None:
            # Clear all caches
            self._loaded_datasets.clear()
            for dataset in self._loaded_datasets.values():
                dataset.clear_cache()
            logger.info("Cleared all dataset caches")
        else:
            # Clear specific dataset cache
            keys_to_remove = [
                key for key in self._loaded_datasets
                if key.startswith(name)
            ]
            for key in keys_to_remove:
                dataset = self._loaded_datasets.pop(key)
                dataset.clear_cache()
            logger.info(f"Cleared cache for dataset: {name}")

    def preload_datasets(self, names: List[str], splits: Optional[List[DatasetSplit]] = None):
        """
        Preload multiple datasets for faster access.

        Args:
            names: List of dataset names
            splits: List of splits to load (loads all if None)
        """
        if splits is None:
            splits = [DatasetSplit.ALL]

        for name in names:
            for split in splits:
                try:
                    self.load_dataset(name, split=split)
                    logger.info(f"Preloaded dataset: {name} ({split.value})")
                except Exception as e:
                    logger.error(f"Failed to preload {name} ({split.value}): {e}")

    def get_statistics(self, name: str) -> Dict[str, Any]:
        """
        Get dataset statistics.

        Args:
            name: Dataset name

        Returns:
            Dictionary with statistics
        """
        dataset = self.load_dataset(name)
        return dataset.compute_statistics()

    def enable_lazy_loading(self):
        """Enable lazy loading of datasets."""
        self._lazy_loading = True
        logger.info("Enabled lazy loading")

    def disable_lazy_loading(self):
        """Disable lazy loading (keeps all datasets in memory)."""
        self._lazy_loading = False
        logger.info("Disabled lazy loading")

    def save_state(self, filepath: Path):
        """
        Save manager state to disk.

        Args:
            filepath: Path to save state
        """
        state = {
            "data_root": str(self.data_root),
            "cache_root": str(self.cache_root),
            "registry": self.registry.list_datasets(),
            "dataset_info": {
                name: info.to_dict()
                for name, info in self._dataset_info_cache.items()
            },
            "lazy_loading": self._lazy_loading,
        }

        with open(filepath, 'wb') as f:
            pickle.dump(state, f)

        logger.info(f"Saved manager state to: {filepath}")

    def load_state(self, filepath: Path):
        """
        Load manager state from disk.

        Args:
            filepath: Path to load state from
        """
        with open(filepath, 'rb') as f:
            state = pickle.load(f)

        self.data_root = Path(state["data_root"])
        self.cache_root = Path(state["cache_root"])
        self._lazy_loading = state["lazy_loading"]

        # Restore dataset info
        self._dataset_info_cache = {
            name: DatasetInfo.from_dict(info_dict)
            for name, info_dict in state["dataset_info"].items()
        }

        logger.info(f"Loaded manager state from: {filepath}")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"DatasetManager("
            f"data_root='{self.data_root}', "
            f"datasets={self.registry.list_datasets()}, "
            f"loaded={list(self._loaded_datasets.keys())}"
            f")"
        )
