"""Unit tests for base dataset functionality."""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

from neural_engine.datasets.base_dataset import (
    BaseDataset,
    DatasetInfo,
    DatasetSplit,
    DataSample,
)


class MockDataset(BaseDataset):
    """Mock dataset for testing."""

    @property
    def name(self) -> str:
        return "mock_dataset"

    @property
    def version(self) -> str:
        return "1.0.0"

    def _check_exists(self) -> bool:
        """Check if dataset exists."""
        marker_file = self.data_dir / "mock_data.npz"
        return marker_file.exists()

    def _download(self):
        """Simulate dataset download."""
        # Create mock data
        n_samples = 100
        n_channels = 8

        data = []
        labels = []

        for i in range(n_samples):
            # Generate random neural data
            sample_data = np.random.randn(n_channels, 1000)
            data.append(sample_data)
            labels.append(i % 2)  # Binary classification

        # Save to disk
        marker_file = self.data_dir / "mock_data.npz"
        np.savez_compressed(
            marker_file,
            data=np.array(data),
            labels=np.array(labels),
        )

    def _load_info(self) -> DatasetInfo:
        """Load dataset information."""
        return DatasetInfo(
            name=self.name,
            version=self.version,
            description="Mock dataset for testing",
            n_samples=100,
            n_channels=8,
            sampling_rate=250.0,
            duration_seconds=4.0,
            signal_types=["EEG"],
            n_subjects=10,
            subject_ids=[f"S{i:02d}" for i in range(10)],
            task_type="binary_classification",
            n_classes=2,
            class_names=["class_0", "class_1"],
            total_size_mb=10.0,
            format="npz",
        )

    def __len__(self) -> int:
        """Number of samples."""
        return 100

    def __getitem__(self, idx: int) -> DataSample:
        """Get a single sample."""
        if idx < 0 or idx >= len(self):
            raise IndexError(f"Index {idx} out of range [0, {len(self)})")

        # Load data if not cached
        if not hasattr(self, "_data"):
            data_file = self.data_dir / "mock_data.npz"
            loaded = np.load(data_file)
            self._data = loaded["data"]
            self._labels = loaded["labels"]

        # Apply transforms if any
        data = self._data[idx]
        label = self._labels[idx]

        if self.transform:
            data = self.transform(data)

        if self.target_transform:
            label = self.target_transform(label)

        return DataSample(
            data=data,
            label=label,
            sample_id=f"sample_{idx:04d}",
            subject_id=f"S{idx // 10:02d}",
            trial_id=idx % 10,
            sampling_rate=250.0,
            duration_seconds=4.0,
        )

    def get_split(self, split: DatasetSplit) -> "MockDataset":
        """Get dataset split."""
        if split == DatasetSplit.TRAIN:
            indices = list(range(0, 70))
        elif split == DatasetSplit.VALIDATION:
            indices = list(range(70, 85))
        elif split == DatasetSplit.TEST:
            indices = list(range(85, 100))
        else:
            indices = list(range(100))

        # Create subset dataset
        subset = MockDatasetSubset(self, indices)
        return subset


class MockDatasetSubset(MockDataset):
    """Subset of mock dataset."""

    def __init__(self, parent: MockDataset, indices: list):
        """Initialize subset."""
        self.parent = parent
        self.indices = indices

        # Copy attributes
        self.data_dir = parent.data_dir
        self.cache_dir = parent.cache_dir
        self.transform = parent.transform
        self.target_transform = parent.target_transform
        self._info = parent._info

    def __len__(self) -> int:
        return len(self.indices)

    def __getitem__(self, idx: int) -> DataSample:
        if idx < 0 or idx >= len(self):
            raise IndexError(f"Index {idx} out of range [0, {len(self)})")

        parent_idx = self.indices[idx]
        return self.parent[parent_idx]


class TestDatasetInfo:
    """Test DatasetInfo class."""

    def test_dataset_info_creation(self):
        """Test creating dataset info."""
        info = DatasetInfo(
            name="test_dataset",
            version="1.0",
            description="Test dataset",
            n_samples=100,
            n_channels=8,
            sampling_rate=250.0,
        )

        assert info.name == "test_dataset"
        assert info.version == "1.0"
        assert info.n_samples == 100
        assert info.n_channels == 8
        assert info.sampling_rate == 250.0

    def test_dataset_info_serialization(self):
        """Test dataset info serialization."""
        info = DatasetInfo(
            name="test_dataset",
            version="1.0",
            description="Test dataset",
            signal_types=["EEG", "EMG"],
            metadata={"custom": "value"},
        )

        # Convert to dict
        info_dict = info.to_dict()
        assert isinstance(info_dict, dict)
        assert info_dict["name"] == "test_dataset"
        assert info_dict["signal_types"] == ["EEG", "EMG"]
        assert info_dict["metadata"]["custom"] == "value"

        # Convert back
        info2 = DatasetInfo.from_dict(info_dict)
        assert info2.name == info.name
        assert info2.version == info.version
        assert info2.signal_types == info.signal_types
        assert info2.metadata == info.metadata


class TestDataSample:
    """Test DataSample class."""

    def test_data_sample_creation(self):
        """Test creating data sample."""
        data = np.random.randn(8, 1000)
        sample = DataSample(
            data=data,
            label=1,
            sample_id="test_001",
            subject_id="S01",
            sampling_rate=250.0,
        )

        assert sample.n_channels == 8
        assert sample.n_samples == 1000
        assert sample.label == 1
        assert sample.sample_id == "test_001"
        assert sample.subject_id == "S01"


class TestBaseDataset:
    """Test BaseDataset functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_dataset_initialization(self, temp_dir):
        """Test dataset initialization."""
        dataset = MockDataset(
            data_dir=temp_dir / "data",
            cache_dir=temp_dir / "cache",
            download=True,
        )

        # Check that directories were created
        assert dataset.data_dir.exists()
        assert dataset.cache_dir.exists()

        # Check that data was downloaded
        assert (dataset.data_dir / "mock_data.npz").exists()

    def test_dataset_loading(self, temp_dir):
        """Test loading dataset samples."""
        dataset = MockDataset(
            data_dir=temp_dir / "data",
            cache_dir=temp_dir / "cache",
            download=True,
        )

        # Test length
        assert len(dataset) == 100

        # Test getting samples
        sample = dataset[0]
        assert isinstance(sample, DataSample)
        assert sample.data.shape == (8, 1000)
        assert sample.label in [0, 1]

        # Test invalid index
        with pytest.raises(IndexError):
            _ = dataset[100]

    def test_dataset_info(self, temp_dir):
        """Test dataset info."""
        dataset = MockDataset(
            data_dir=temp_dir / "data",
            cache_dir=temp_dir / "cache",
            download=True,
        )

        info = dataset.info
        assert info.name == "mock_dataset"
        assert info.version == "1.0.0"
        assert info.n_samples == 100
        assert info.n_channels == 8
        assert info.sampling_rate == 250.0

    def test_dataset_splits(self, temp_dir):
        """Test dataset splits."""
        dataset = MockDataset(
            data_dir=temp_dir / "data",
            cache_dir=temp_dir / "cache",
            download=True,
        )

        # Get splits
        train_set = dataset.get_split(DatasetSplit.TRAIN)
        val_set = dataset.get_split(DatasetSplit.VALIDATION)
        test_set = dataset.get_split(DatasetSplit.TEST)

        # Check sizes
        assert len(train_set) == 70
        assert len(val_set) == 15
        assert len(test_set) == 15

        # Check that samples are different
        train_sample = train_set[0]
        test_sample = test_set[0]
        assert train_sample.sample_id != test_sample.sample_id

    def test_dataset_transforms(self, temp_dir):
        """Test dataset transforms."""
        # Define simple transforms
        def data_transform(x):
            return x * 2.0

        def target_transform(y):
            return y + 10

        dataset = MockDataset(
            data_dir=temp_dir / "data",
            cache_dir=temp_dir / "cache",
            download=True,
            transform=data_transform,
            target_transform=target_transform,
        )

        # Get transformed sample
        sample = dataset[0]

        # Verify transforms were applied
        # Note: We can't directly check the multiplication because
        # the transform is applied to the loaded data
        assert sample.label >= 10  # Original labels are 0 or 1

    def test_dataset_caching(self, temp_dir):
        """Test dataset caching functionality."""
        dataset = MockDataset(
            data_dir=temp_dir / "data",
            cache_dir=temp_dir / "cache",
            download=True,
        )

        # Test cache key generation
        key = dataset.cache_key("test", 123, {"param": "value"})
        assert isinstance(key, str)
        assert len(key) == 32  # MD5 hash length

        # Test caching
        test_data = {"test": "data"}
        dataset.set_cached("test_key", test_data)

        cached = dataset.get_cached("test_key")
        assert cached == test_data

        # Test cache clearing
        dataset.clear_cache()
        assert dataset.get_cached("test_key") is None

    def test_dataset_statistics(self, temp_dir):
        """Test computing dataset statistics."""
        dataset = MockDataset(
            data_dir=temp_dir / "data",
            cache_dir=temp_dir / "cache",
            download=True,
        )

        stats = dataset.compute_statistics()

        assert "mean" in stats
        assert "std" in stats
        assert "min" in stats
        assert "max" in stats
        assert "median" in stats

        # Check that statistics have correct shape
        assert len(stats["mean"]) == 8  # 8 channels
        assert len(stats["std"]) == 8

    def test_batch_iteration(self, temp_dir):
        """Test batch iteration."""
        dataset = MockDataset(
            data_dir=temp_dir / "data",
            cache_dir=temp_dir / "cache",
            download=True,
        )

        # Test batch iteration
        batch_size = 10
        batches = list(dataset.iter_batches(batch_size=batch_size))

        assert len(batches) == 10  # 100 samples / 10 batch size
        assert len(batches[0]) == batch_size
        assert all(isinstance(sample, DataSample) for sample in batches[0])

        # Test with drop_last
        batches = list(dataset.iter_batches(batch_size=15, drop_last=True))
        assert len(batches) == 6  # 90 samples / 15 batch size

        # Test with shuffle
        batches1 = list(dataset.iter_batches(batch_size=10, shuffle=True))
        batches2 = list(dataset.iter_batches(batch_size=10, shuffle=True))

        # Check that shuffled batches are different (with high probability)
        first_ids_1 = [b[0].sample_id for b in batches1]
        first_ids_2 = [b[0].sample_id for b in batches2]
        assert first_ids_1 != first_ids_2  # May fail rarely

    def test_subject_data_retrieval(self, temp_dir):
        """Test getting data for specific subject."""
        dataset = MockDataset(
            data_dir=temp_dir / "data",
            cache_dir=temp_dir / "cache",
            download=True,
        )

        # Get data for subject S01
        subject_data = dataset.get_subject_data("S01")

        # Should have 10 samples (indices 10-19)
        assert len(subject_data) == 10
        assert all(sample.subject_id == "S01" for sample in subject_data)
