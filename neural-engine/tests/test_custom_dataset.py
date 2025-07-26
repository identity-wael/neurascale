"""Tests for custom dataset loader."""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import tempfile
import h5py
import scipy.io
from unittest.mock import Mock, patch, MagicMock

from src.datasets import CustomDatasetLoader, CustomDatasetConfig, DataFormat
from src.datasets.dataset_converter import DatasetConverter


class TestCustomDatasetLoader:
    """Test custom dataset loading functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def sample_csv_data(self, temp_dir):
        """Create sample CSV data."""
        # Generate synthetic data
        n_samples = 1000
        n_channels = 4
        time = np.arange(n_samples) / 250.0

        data = {
            "time": time,
            "ch_0": np.sin(2 * np.pi * 10 * time) + 0.1 * np.random.randn(n_samples),
            "ch_1": np.sin(2 * np.pi * 15 * time) + 0.1 * np.random.randn(n_samples),
            "ch_2": np.sin(2 * np.pi * 20 * time) + 0.1 * np.random.randn(n_samples),
            "ch_3": np.sin(2 * np.pi * 25 * time) + 0.1 * np.random.randn(n_samples),
            "label": (time // 1).astype(int) % 2,  # Alternating labels
        }

        df = pd.DataFrame(data)
        csv_path = temp_dir / "test_data.csv"
        df.to_csv(csv_path, index=False)

        return csv_path, data

    @pytest.fixture
    def sample_hdf5_data(self, temp_dir):
        """Create sample HDF5 data."""
        # Generate epoched data
        n_epochs = 50
        n_samples = 500
        n_channels = 8

        data = np.random.randn(n_epochs, n_samples, n_channels).astype(np.float32)
        labels = np.random.randint(0, 3, n_epochs)

        h5_path = temp_dir / "test_data.h5"
        with h5py.File(h5_path, "w") as f:
            f.create_dataset("data", data=data)
            f.create_dataset("labels", data=labels)

            # Add metadata
            meta = f.create_group("metadata")
            meta.attrs["sampling_rate"] = 250.0
            meta.attrs["channel_names"] = [f"EEG_{i}" for i in range(n_channels)]

        return h5_path, data, labels

    @pytest.fixture
    def sample_mat_data(self, temp_dir):
        """Create sample MAT data."""
        # Generate continuous data
        n_samples = 2500
        n_channels = 16

        data = np.random.randn(n_channels, n_samples).astype(np.float32)
        labels = np.zeros(n_samples)
        labels[1000:1500] = 1  # Event in the middle

        mat_path = temp_dir / "test_data.mat"
        mat_data = {
            "EEG": data,
            "labels": labels,
            "fs": 500.0,
            "chanlocs": np.array(
                [{"labels": f"CH{i + 1}"} for i in range(n_channels)], dtype=object
            ),
        }
        scipy.io.savemat(mat_path, mat_data)

        return mat_path, data.T, labels  # Return in (samples, channels) format

    def test_csv_loading(self, sample_csv_data):
        """Test loading CSV data."""
        csv_path, original_data = sample_csv_data

        config = CustomDatasetConfig(
            name="test_csv",
            data_format=DataFormat.CSV,
            data_path=csv_path,
            csv_time_column="time",
            csv_label_column="label",
            csv_channel_columns=["ch_0", "ch_1", "ch_2", "ch_3"],
            sampling_rate=250.0,
        )

        loader = CustomDatasetLoader(config)
        data, labels = loader.load()

        # Check shapes
        assert data.shape[0] == len(original_data["time"])
        assert data.shape[1] == 4  # 4 channels
        assert len(labels) == len(original_data["label"])

        # Check metadata
        metadata = loader.get_metadata()
        assert metadata["format"] == "csv"
        assert metadata["n_channels"] == 4
        assert metadata["sampling_rate"] == 250.0

    def test_csv_with_epoching(self, sample_csv_data):
        """Test CSV loading with epoching."""
        csv_path, _ = sample_csv_data

        config = CustomDatasetConfig(
            name="test_csv_epoched",
            data_format=DataFormat.CSV,
            data_path=csv_path,
            csv_time_column="time",
            csv_label_column="label",
            csv_channel_columns=["ch_0", "ch_1", "ch_2", "ch_3"],
            sampling_rate=250.0,
            epoch_length=1.0,  # 1-second epochs
            epoch_overlap=0.5,  # 50% overlap
        )

        loader = CustomDatasetLoader(config)
        data, labels = loader.load()

        # Check epoched shape
        assert data.ndim == 3  # (epochs, samples, channels)
        assert data.shape[1] == 250  # 1 second at 250Hz
        assert data.shape[2] == 4  # 4 channels

    def test_hdf5_loading(self, sample_hdf5_data):
        """Test loading HDF5 data."""
        h5_path, original_data, original_labels = sample_hdf5_data

        config = CustomDatasetConfig(
            name="test_hdf5", data_format=DataFormat.HDF5, data_path=h5_path
        )

        loader = CustomDatasetLoader(config)
        data, labels = loader.load()

        # Check data matches
        np.testing.assert_array_equal(data, original_data)
        np.testing.assert_array_equal(labels, original_labels)

        # Check metadata
        metadata = loader.get_metadata()
        assert metadata["format"] == "hdf5"
        assert metadata["sampling_rate"] == 250.0
        assert len(metadata["channel_names"]) == 8

    def test_mat_loading(self, sample_mat_data):
        """Test loading MAT data."""
        mat_path, original_data, original_labels = sample_mat_data

        config = CustomDatasetConfig(
            name="test_mat",
            data_format=DataFormat.MAT,
            data_path=mat_path,
            data_key="EEG",
        )

        loader = CustomDatasetLoader(config)
        data, labels = loader.load()

        # Check shapes
        assert data.shape == original_data.shape
        assert len(labels) == len(original_labels)

        # Check sampling rate was loaded
        assert loader._original_sampling_rate == 500.0

    def test_custom_loader(self):
        """Test custom loader function."""

        def custom_loader_func(config):
            # Simple custom loader
            data = np.ones((100, 250, 4))  # 100 epochs, 250 samples, 4 channels
            labels = np.zeros(100)
            labels[50:] = 1

            return {
                "data": data,
                "labels": labels,
                "channel_names": ["A", "B", "C", "D"],
                "sampling_rate": 1000.0,
            }

        config = CustomDatasetConfig(
            name="test_custom",
            data_format=DataFormat.CUSTOM,
            custom_loader=custom_loader_func,
        )

        loader = CustomDatasetLoader(config)
        data, labels = loader.load()

        assert data.shape == (100, 250, 4)
        assert np.all(data == 1)
        assert np.sum(labels == 0) == 50
        assert np.sum(labels == 1) == 50

    def test_preprocessing(self, sample_csv_data):
        """Test preprocessing pipeline."""
        csv_path, _ = sample_csv_data

        config = CustomDatasetConfig(
            name="test_preprocess",
            data_format=DataFormat.CSV,
            data_path=csv_path,
            csv_channel_columns=["ch_0", "ch_1", "ch_2", "ch_3"],
            sampling_rate=250.0,
            filter_low=5.0,
            filter_high=30.0,
            notch_freq=50.0,
            reference="average",
        )

        loader = CustomDatasetLoader(config)
        data, _ = loader.load()

        # Check that preprocessing was applied (data should be modified)
        # Average reference should make mean across channels ~0
        channel_means = np.mean(data, axis=1)
        assert np.all(np.abs(channel_means) < 1e-10)

    def test_validation(self, temp_dir):
        """Test data validation."""
        # Create invalid data (all zeros)
        data = np.zeros((1000, 4))
        npy_path = temp_dir / "invalid_data.npy"
        np.save(npy_path, data)

        config = CustomDatasetConfig(
            name="test_invalid", data_format=DataFormat.NPY, data_path=npy_path
        )

        loader = CustomDatasetLoader(config)

        # Should load but validation should fail
        data, _ = loader.load()
        assert not loader.validate(data)  # Zero variance should fail

    def test_caching(self, sample_csv_data):
        """Test caching functionality."""
        csv_path, _ = sample_csv_data

        config = CustomDatasetConfig(
            name="test_cache",
            data_format=DataFormat.CSV,
            data_path=csv_path,
            csv_channel_columns=["ch_0", "ch_1", "ch_2", "ch_3"],
            sampling_rate=250.0,
        )

        loader = CustomDatasetLoader(config)

        # First load - should create cache
        data1, labels1 = loader.load()
        assert loader.cache_exists()

        # Second load - should use cache
        data2, labels2 = loader.load()

        # Data should be identical
        np.testing.assert_array_equal(data1, data2)
        np.testing.assert_array_equal(labels1, labels2)

    @patch("mne.io.read_raw_edf")
    def test_edf_loading(self, mock_read_edf, temp_dir):
        """Test EDF loading with mocked MNE."""
        # Create mock raw object
        mock_raw = MagicMock()
        mock_raw.ch_names = ["Fp1", "Fp2", "C3", "C4"]
        mock_raw.info = {"sfreq": 256.0}
        mock_raw.get_data.return_value = np.random.randn(4, 2560)  # 10 seconds
        mock_raw.annotations = []

        mock_read_edf.return_value = mock_raw

        edf_path = temp_dir / "test.edf"
        edf_path.touch()  # Create empty file

        config = CustomDatasetConfig(
            name="test_edf", data_format=DataFormat.EDF, data_path=edf_path
        )

        loader = CustomDatasetLoader(config)
        data, labels = loader.load()

        assert data.shape == (2560, 4)  # (samples, channels)
        assert loader._original_sampling_rate == 256.0

    def test_mne_conversion(self, sample_csv_data):
        """Test conversion to MNE format."""
        csv_path, _ = sample_csv_data

        config = CustomDatasetConfig(
            name="test_mne",
            data_format=DataFormat.CSV,
            data_path=csv_path,
            csv_channel_columns=["ch_0", "ch_1", "ch_2", "ch_3"],
            sampling_rate=250.0,
        )

        loader = CustomDatasetLoader(config)
        data, labels = loader.load()

        # Convert to MNE
        raw = loader.convert_to_mne(data, labels)

        assert raw.info["sfreq"] == 250.0
        assert len(raw.ch_names) == 4
        assert raw.n_times == len(data)


class TestDatasetConverter:
    """Test dataset conversion functionality."""

    @pytest.fixture
    def sample_data(self, tmp_path):
        """Create sample data for conversion tests."""
        data = np.random.randn(10, 500, 8).astype(np.float32)
        labels = np.random.randint(0, 2, 10)

        npy_path = tmp_path / "test_data.npy"
        np.save(npy_path, data)
        np.save(tmp_path / "test_data.labels.npy", labels)

        return npy_path, data, labels

    def test_npy_to_hdf5_conversion(self, sample_data, tmp_path):
        """Test NPY to HDF5 conversion."""
        npy_path, original_data, original_labels = sample_data
        hdf5_path = tmp_path / "converted.h5"

        DatasetConverter.convert(
            input_path=npy_path,
            output_path=hdf5_path,
            input_format=DataFormat.NPY,
            output_format=DataFormat.HDF5,
            labels_path=tmp_path / "test_data.labels.npy",
            channel_names=["CH1", "CH2", "CH3", "CH4", "CH5", "CH6", "CH7", "CH8"],
            sampling_rate=500.0,
        )

        # Verify conversion
        with h5py.File(hdf5_path, "r") as f:
            assert "data" in f
            assert "labels" in f
            assert "metadata" in f

            converted_data = f["data"][:]
            converted_labels = f["labels"][:]

            np.testing.assert_array_equal(converted_data, original_data)
            np.testing.assert_array_equal(converted_labels, original_labels)

    def test_hdf5_to_csv_conversion(self, tmp_path):
        """Test HDF5 to CSV conversion."""
        # Create HDF5 file
        data = np.random.randn(1000, 4)  # Continuous data
        labels = np.zeros(1000)
        labels[500:] = 1

        h5_path = tmp_path / "test.h5"
        with h5py.File(h5_path, "w") as f:
            f.create_dataset("data", data=data)
            f.create_dataset("labels", data=labels)
            meta = f.create_group("metadata")
            meta.attrs["sampling_rate"] = 250.0
            meta.attrs["channel_names"] = ["A", "B", "C", "D"]

        csv_path = tmp_path / "converted.csv"

        DatasetConverter.convert(
            input_path=h5_path,
            output_path=csv_path,
            input_format=DataFormat.HDF5,
            output_format=DataFormat.CSV,
        )

        # Verify CSV
        df = pd.read_csv(csv_path)
        assert "time" in df.columns
        assert "label" in df.columns
        assert len(df) == 1000
        assert list(df.columns[1:5]) == ["A", "B", "C", "D"]

    def test_batch_conversion(self, tmp_path):
        """Test batch conversion of multiple files."""
        # Create multiple NPY files
        for i in range(3):
            data = np.random.randn(100, 250, 4)
            np.save(tmp_path / f"data_{i}.npy", data)

        output_dir = tmp_path / "converted"

        DatasetConverter.batch_convert(
            input_dir=tmp_path,
            output_dir=output_dir,
            input_format=DataFormat.NPY,
            output_format=DataFormat.HDF5,
            pattern="data_*",
            channel_names=["CH1", "CH2", "CH3", "CH4"],
            sampling_rate=250.0,
        )

        # Check conversions
        assert len(list(output_dir.glob("*.h5"))) == 3

    def test_conversion_validation(self, sample_data, tmp_path):
        """Test conversion validation."""
        npy_path, _, _ = sample_data
        hdf5_path = tmp_path / "converted.h5"

        # Convert
        DatasetConverter.convert(
            input_path=npy_path,
            output_path=hdf5_path,
            input_format=DataFormat.NPY,
            output_format=DataFormat.HDF5,
            labels_path=tmp_path / "test_data.labels.npy",
        )

        # Validate
        is_valid = DatasetConverter.validate_conversion(
            original_path=npy_path,
            converted_path=hdf5_path,
            original_format=DataFormat.NPY,
            converted_format=DataFormat.HDF5,
        )

        assert is_valid


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
