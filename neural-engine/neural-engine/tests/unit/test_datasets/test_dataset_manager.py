"""Unit tests for dataset manager and registry."""

import pytest
import tempfile
import shutil
from pathlib import Path
import json

from neural_engine.datasets.dataset_manager import DatasetManager, DatasetRegistry
from neural_engine.datasets.base_dataset import BaseDataset, DatasetInfo, DatasetSplit
from .test_base_dataset import MockDataset


class AnotherMockDataset(BaseDataset):
    """Another mock dataset for testing multiple datasets."""

    @property
    def name(self) -> str:
        return "another_mock"

    @property
    def version(self) -> str:
        return "2.0.0"

    def _check_exists(self) -> bool:
        return True  # Always exists for testing

    def _download(self):
        pass  # No download needed

    def _load_info(self) -> DatasetInfo:
        return DatasetInfo(
            name=self.name,
            version=self.version,
            description="Another mock dataset",
            n_samples=50,
            n_channels=4,
            sampling_rate=128.0,
        )

    def __len__(self) -> int:
        return 50

    def __getitem__(self, idx: int):
        return None  # Simplified for testing


class TestDatasetRegistry:
    """Test DatasetRegistry functionality."""

    def test_registry_initialization(self):
        """Test registry initialization."""
        registry = DatasetRegistry()
        assert isinstance(registry, DatasetRegistry)
        assert len(registry.list_datasets()) == 0

    def test_register_dataset(self):
        """Test registering datasets."""
        registry = DatasetRegistry()

        # Register dataset
        registry.register("mock", MockDataset)

        assert "mock" in registry
        assert len(registry.list_datasets()) == 1
        assert registry.get("mock") == MockDataset

    def test_register_with_metadata(self):
        """Test registering with metadata."""
        registry = DatasetRegistry()

        metadata = {
            "paper": "Test Paper 2023",
            "url": "https://example.com",
        }

        registry.register("mock", MockDataset, metadata=metadata)

        assert registry.get_metadata("mock") == metadata

    def test_register_with_loader(self):
        """Test registering with custom loader."""
        registry = DatasetRegistry()

        def custom_loader(**kwargs):
            return MockDataset(**kwargs)

        registry.register("mock", MockDataset, loader=custom_loader)

        assert registry.get_loader("mock") == custom_loader

    def test_unregister_dataset(self):
        """Test unregistering datasets."""
        registry = DatasetRegistry()

        registry.register("mock", MockDataset)
        assert "mock" in registry

        registry.unregister("mock")
        assert "mock" not in registry
        assert len(registry.list_datasets()) == 0

    def test_invalid_dataset_class(self):
        """Test registering invalid dataset class."""
        registry = DatasetRegistry()

        class NotADataset:
            pass

        with pytest.raises(ValueError, match="must inherit from BaseDataset"):
            registry.register("invalid", NotADataset)

    def test_get_nonexistent_dataset(self):
        """Test getting non-existent dataset."""
        registry = DatasetRegistry()

        with pytest.raises(ValueError, match="not found in registry"):
            registry.get("nonexistent")


class TestDatasetManager:
    """Test DatasetManager functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def manager(self, temp_dir):
        """Create dataset manager."""
        manager = DatasetManager(
            data_root=temp_dir / "data",
            cache_root=temp_dir / "cache",
        )

        # Register mock datasets
        manager.register_dataset("mock", MockDataset)
        manager.register_dataset("another", AnotherMockDataset)

        return manager

    def test_manager_initialization(self, temp_dir):
        """Test manager initialization."""
        manager = DatasetManager(
            data_root=temp_dir / "data",
            cache_root=temp_dir / "cache",
        )

        assert manager.data_root == temp_dir / "data"
        assert manager.cache_root == temp_dir / "cache"
        assert manager.data_root.exists()
        assert manager.cache_root.exists()

    def test_load_dataset(self, manager):
        """Test loading dataset."""
        dataset = manager.load_dataset("mock", download=True)

        assert isinstance(dataset, MockDataset)
        assert len(dataset) == 100
        assert dataset.name == "mock_dataset"

    def test_load_dataset_with_split(self, manager):
        """Test loading dataset with split."""
        train_set = manager.load_dataset("mock", split=DatasetSplit.TRAIN)

        assert len(train_set) == 70

    def test_dataset_caching(self, manager):
        """Test dataset caching in manager."""
        # Load dataset twice
        dataset1 = manager.load_dataset("mock")
        dataset2 = manager.load_dataset("mock")

        # Should be the same instance (cached)
        assert dataset1 is dataset2

        # Force reload
        dataset3 = manager.load_dataset("mock", force_reload=True)
        assert dataset3 is not dataset1

    def test_get_dataset_info(self, manager):
        """Test getting dataset info without loading full dataset."""
        info = manager.get_dataset_info("mock")

        assert info.name == "mock_dataset"
        assert info.version == "1.0.0"
        assert info.n_samples == 100

    def test_list_available_datasets(self, manager):
        """Test listing available datasets."""
        datasets = manager.list_available_datasets()

        assert len(datasets) == 2

        # Find mock dataset
        mock_info = next(d for d in datasets if d["registered_name"] == "mock")
        assert mock_info["name"] == "mock_dataset"
        assert mock_info["version"] == "1.0.0"
        assert "is_downloaded" in mock_info

    def test_delete_dataset(self, manager):
        """Test deleting dataset."""
        # Load dataset first
        dataset = manager.load_dataset("mock")
        assert manager.is_downloaded("mock")

        # Delete it
        manager.delete_dataset("mock")
        assert not manager.is_downloaded("mock")

    def test_clear_cache(self, manager):
        """Test clearing cache."""
        # Load datasets
        dataset1 = manager.load_dataset("mock")
        dataset2 = manager.load_dataset("another")

        # Clear all caches
        manager.clear_cache()

        # Load again - should create new instances
        dataset3 = manager.load_dataset("mock")
        assert dataset3 is not dataset1

    def test_clear_specific_cache(self, manager):
        """Test clearing specific dataset cache."""
        # Load datasets
        dataset1 = manager.load_dataset("mock")
        dataset2 = manager.load_dataset("another")

        # Clear only mock cache
        manager.clear_cache("mock")

        # Load again
        dataset3 = manager.load_dataset("mock")
        dataset4 = manager.load_dataset("another")

        assert dataset3 is not dataset1  # Mock was cleared
        assert dataset4 is dataset2  # Another was not cleared

    def test_preload_datasets(self, manager):
        """Test preloading multiple datasets."""
        manager.preload_datasets(["mock", "another"])

        # Check that datasets are loaded
        assert len(manager._loaded_datasets) >= 2

    def test_lazy_loading(self, manager):
        """Test lazy loading control."""
        # Disable lazy loading
        manager.disable_lazy_loading()

        dataset = manager.load_dataset("mock")

        # Should not be cached
        assert len(manager._loaded_datasets) == 0

        # Enable lazy loading
        manager.enable_lazy_loading()

        dataset = manager.load_dataset("mock")

        # Should be cached
        assert len(manager._loaded_datasets) > 0

    def test_metadata_persistence(self, manager):
        """Test metadata persistence."""
        # Load dataset to generate metadata
        info = manager.get_dataset_info("mock")

        # Check metadata file exists
        assert manager._metadata_file.exists()

        # Load metadata manually
        with open(manager._metadata_file, "r") as f:
            metadata = json.load(f)

        assert "mock" in metadata
        assert metadata["mock"]["name"] == "mock_dataset"

    def test_save_and_load_state(self, manager, temp_dir):
        """Test saving and loading manager state."""
        # Load some datasets
        manager.load_dataset("mock")
        manager.get_dataset_info("another")

        # Save state
        state_file = temp_dir / "manager_state.pkl"
        manager.save_state(state_file)

        # Create new manager
        new_manager = DatasetManager()

        # Load state
        new_manager.load_state(state_file)

        # Check state was restored
        assert new_manager.data_root == manager.data_root
        assert new_manager.cache_root == manager.cache_root
        assert "mock" in new_manager._dataset_info_cache
        assert "another" in new_manager._dataset_info_cache

    def test_custom_transform(self, manager):
        """Test loading dataset with custom transforms."""

        def transform(x):
            return x * 2.0

        dataset = manager.load_dataset(
            "mock",
            transform=transform,
            download=True,
        )

        assert dataset.transform == transform

    def test_get_statistics(self, manager):
        """Test getting dataset statistics."""
        stats = manager.get_statistics("mock")

        assert "mean" in stats
        assert "std" in stats
        assert len(stats["mean"]) == 8  # 8 channels


class TestIntegration:
    """Integration tests for dataset system."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_full_workflow(self, temp_dir):
        """Test full dataset workflow."""
        # Create manager
        manager = DatasetManager(
            data_root=temp_dir / "data",
            cache_root=temp_dir / "cache",
        )

        # Register dataset
        manager.register_dataset(
            "test_dataset",
            MockDataset,
            metadata={"source": "test"},
        )

        # Load dataset
        dataset = manager.load_dataset("test_dataset", download=True)
        assert len(dataset) == 100

        # Get specific split
        train_set = manager.load_dataset(
            "test_dataset",
            split=DatasetSplit.TRAIN,
        )
        assert len(train_set) == 70

        # Get info
        info = manager.get_dataset_info("test_dataset")
        assert info.n_samples == 100

        # List datasets
        datasets = manager.list_available_datasets()
        assert len(datasets) == 1
        assert datasets[0]["registered_name"] == "test_dataset"

        # Clear cache
        manager.clear_cache()

        # Delete dataset
        manager.delete_dataset("test_dataset")
        assert not manager.is_downloaded("test_dataset")
