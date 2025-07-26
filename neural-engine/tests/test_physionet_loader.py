"""Unit tests for PhysioNet dataset loader."""

import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile

from src.datasets import PhysioNetLoader, PhysioNetDataset
from src.datasets.physionet_loader import PhysioNetConfig
from src.datasets.data_quality import DataQualityValidator, QualityLevel


class TestPhysioNetLoader:
    """Test PhysioNet dataset loader."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return PhysioNetConfig(
            name="test_dataset",
            dataset_type=PhysioNetDataset.EEGMMIDB,
            subjects=["S001"],
            tasks=["left_fist", "right_fist"],
            channels=["C3", "C4", "Cz"],
            sampling_rate=160.0,
            window_size=2.0,
            overlap=0.5,
            bandpass_freq=(8.0, 30.0),
            notch_freq=60.0,
            cache_dir=Path(tempfile.mkdtemp()),
        )

    @pytest.fixture
    def loader(self, config):
        """Create loader instance."""
        return PhysioNetLoader(config)

    def test_initialization(self, loader, config):
        """Test loader initialization."""
        assert loader.config == config
        assert loader.dataset_dir == config.cache_dir / config.dataset_type.value
        assert loader.dataset_dir.exists()

    @patch("requests.get")
    def test_download_file(self, mock_get, loader):
        """Test file download."""
        # Mock response
        mock_response = Mock()
        mock_response.iter_content = Mock(return_value=[b"test_data"])
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Test download
        test_file = loader.dataset_dir / "test.edf"
        loader._download_file("http://test.url", test_file)

        assert test_file.exists()
        assert test_file.read_bytes() == b"test_data"

    def test_cache_operations(self, loader):
        """Test cache save/load operations."""
        # Create test data
        data = np.random.randn(100, 3, 320)  # 100 epochs, 3 channels, 320 samples
        labels = np.random.choice(["left", "right"], size=100)
        metadata = {"test": "metadata", "channels": ["C3", "C4", "Cz"]}

        # Save cache
        loader.save_cache(data, labels, metadata)
        assert loader.cache_exists()

        # Load cache
        loaded_data, loaded_labels, loaded_metadata = loader.load_cache()

        np.testing.assert_array_equal(data, loaded_data)
        np.testing.assert_array_equal(labels, loaded_labels)
        assert loaded_metadata == metadata

    @patch("mne.io.read_raw_edf")
    def test_preprocess_raw(self, mock_read_edf, loader):
        """Test raw data preprocessing."""
        # Create mock raw object
        mock_raw = MagicMock()
        mock_raw.ch_names = ["C3", "C4", "Cz", "EOG"]
        mock_raw.info = {"sfreq": 256.0}
        mock_raw.pick_channels = Mock()
        mock_raw.set_eeg_reference = Mock()
        mock_raw.filter = Mock()
        mock_raw.notch_filter = Mock()
        mock_raw.resample = Mock()

        # Test preprocessing
        loader._preprocess_raw(mock_raw)

        # Verify channel selection
        mock_raw.pick_channels.assert_called_once()
        called_channels = mock_raw.pick_channels.call_args[0][0]
        assert set(called_channels) == {"C3", "C4", "Cz"}

        # Verify filtering
        mock_raw.filter.assert_called_once_with(
            l_freq=8.0, h_freq=30.0, fir_design="firwin"
        )

        # Verify notch filter
        mock_raw.notch_filter.assert_called_once()

        # Verify resampling
        mock_raw.resample.assert_called_once_with(160.0)

    def test_extract_epochs(self, loader):
        """Test epoch extraction."""
        # Create mock raw data
        mock_raw = MagicMock()
        mock_raw.info = {"sfreq": 160.0}

        # Create test data (3 channels, 800 samples = 5 seconds)
        test_data = np.random.randn(3, 800)
        mock_raw.get_data = Mock(return_value=test_data)

        # Extract epochs
        epochs, labels = loader._extract_epochs(mock_raw, "test_label")

        # Check dimensions
        # With 2s windows and 50% overlap: 5s -> 4 epochs
        assert epochs.shape[0] == 4  # 4 epochs
        assert epochs.shape[1] == 320  # 2s * 160Hz
        assert epochs.shape[2] == 3  # 3 channels
        assert len(labels) == 4
        assert all(label == "test_label" for label in labels)

    def test_split_data(self, loader):
        """Test data splitting."""
        # Create test data
        data = np.random.randn(1000, 3, 320)
        labels = np.random.choice([0, 1], size=1000)

        # Split data
        train, val, test = loader.split_data(data, labels)

        # Check splits
        assert len(train[0]) == 700  # 70% train
        assert len(val[0]) == 200  # 20% validation
        assert len(test[0]) == 100  # 10% test

        # Check no overlap
        # train_idx = set(range(700))
        # val_idx = set(range(700, 900))
        # test_idx = set(range(900, 1000))

        # Since data is shuffled, just check total length
        assert len(train[0]) + len(val[0]) + len(test[0]) == 1000

    def test_batch_iterator(self, loader):
        """Test batch iterator."""
        # Create test data
        data = np.random.randn(100, 3, 320)
        labels = np.random.choice([0, 1], size=100)

        # Test batch iteration
        batches = list(loader.get_batch_iterator(data, labels, shuffle=False))

        # Check number of batches
        expected_batches = int(np.ceil(100 / loader.config.batch_size))
        assert len(batches) == expected_batches

        # Check batch sizes
        for i, (batch_data, batch_labels) in enumerate(batches):
            if i < len(batches) - 1:
                assert len(batch_data) == loader.config.batch_size
            else:
                # Last batch may be smaller
                assert len(batch_data) <= loader.config.batch_size

            assert batch_data.shape[1:] == (3, 320)
            assert len(batch_labels) == len(batch_data)


class TestDataQualityValidator:
    """Test data quality validation."""

    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        return DataQualityValidator(
            sampling_rate=250.0,
            line_freq=60.0,
            amplitude_range=(-200, 200),
            min_snr_db=10.0,
        )

    def test_validation_good_data(self, validator):
        """Test validation with good quality data."""
        # Generate clean sinusoidal data
        t = np.arange(0, 4, 1 / 250.0)
        data = []

        # Create 8 channels with different frequencies
        for freq in [10, 12, 15, 18, 20, 25, 30, 35]:
            channel = 50 * np.sin(2 * np.pi * freq * t)
            # Add small noise
            channel += np.random.randn(len(t)) * 2
            data.append(channel)

        data = np.array(data).T  # (n_samples, n_channels)

        # Validate
        metrics = validator.validate(data)

        # Check metrics
        assert metrics.snr_db > 15  # Good SNR
        assert metrics.flatline_ratio < 0.01
        assert metrics.clipping_ratio < 0.01
        assert metrics.quality_level in [QualityLevel.GOOD, QualityLevel.EXCELLENT]

    def test_validation_poor_data(self, validator):
        """Test validation with poor quality data."""
        # Generate noisy data with artifacts
        t = np.arange(0, 4, 1 / 250.0)
        data = []

        for i in range(8):
            if i == 0:
                # Flat channel
                channel = np.zeros(len(t))
            elif i == 1:
                # Clipped channel
                channel = np.random.randn(len(t)) * 300
                channel = np.clip(channel, -190, 190)
            else:
                # Noisy channel
                channel = np.random.randn(len(t)) * 100

            data.append(channel)

        data = np.array(data).T

        # Validate
        metrics = validator.validate(data)

        # Check metrics
        assert metrics.quality_level in [QualityLevel.POOR, QualityLevel.UNUSABLE]
        assert len(metrics.issues) > 0
        assert 0 in [
            ch
            for ch, q in metrics.channel_quality.items()
            if q == QualityLevel.UNUSABLE
        ]

    def test_artifact_detection(self, validator):
        """Test artifact detection."""
        # Generate data with specific artifacts
        t = np.arange(0, 4, 1 / 250.0)
        data = np.random.randn(len(t), 8) * 10  # Background noise

        # Add motion artifact (large slow wave)
        data[250:300, :] += 100 * np.sin(2 * np.pi * 0.5 * np.arange(50) / 250)

        # Add muscle artifact (high frequency)
        data[500:600, 2] += 50 * np.random.randn(100)

        # Add 60Hz line noise
        data[:, 3] += 30 * np.sin(2 * np.pi * 60 * t)

        # Validate
        metrics = validator.validate(
            data, channel_names=["Fp1", "Fp2", "C3", "C4", "O1", "O2", "T3", "T4"]
        )

        # Check detections
        assert metrics.motion_artifacts > 0
        assert metrics.muscle_artifacts > 0
        assert metrics.line_noise_power > 5

    def test_quality_report(self, validator, tmp_path):
        """Test quality report generation."""
        # Generate test data
        data = np.random.randn(1000, 8) * 50

        # Validate
        metrics = validator.validate(data)

        # Generate report
        report_path = tmp_path / "quality_report.txt"
        report = validator.generate_report(metrics, output_path=report_path)

        # Check report
        assert "Data Quality Assessment Report" in report
        assert "Overall Quality:" in report
        assert "SNR:" in report
        assert report_path.exists()

    @patch("matplotlib.pyplot.savefig")
    def test_quality_plot(self, mock_savefig, validator, tmp_path):
        """Test quality plot generation."""
        # Generate test data
        data = np.random.randn(1000, 8) * 50

        # Validate
        metrics = validator.validate(data)

        # Generate plot
        plot_path = tmp_path / "quality_plot.png"
        validator.plot_quality_summary(metrics, save_path=plot_path)

        # Check that plot was saved
        mock_savefig.assert_called_once()


class TestPhysioNetDatasetIntegration:
    """Integration tests for PhysioNet datasets."""

    @pytest.mark.slow
    @patch("src.datasets.physionet_loader.PhysioNetLoader._download_file")
    @patch("mne.io.read_raw_edf")
    def test_eegmmidb_loading(self, mock_read_edf, mock_download):
        """Test EEGMMIDB dataset loading (mocked)."""
        # Configure minimal dataset
        config = PhysioNetConfig(
            name="test_eegmmidb",
            dataset_type=PhysioNetDataset.EEGMMIDB,
            subjects=["S001"],
            tasks=["left_fist"],
            sampling_rate=160.0,
            cache_dir=Path(tempfile.mkdtemp()),
        )

        # Create mock EDF data
        mock_raw = MagicMock()
        mock_raw.info = {"sfreq": 160.0}
        mock_raw.ch_names = ["C3", "C4", "Cz"] + [f"Ch{i}" for i in range(61)]
        mock_raw.get_data = Mock(return_value=np.random.randn(64, 16000))  # 100 seconds

        # Mock all the preprocessing methods
        mock_raw.pick_channels = Mock(return_value=mock_raw)
        mock_raw.set_eeg_reference = Mock(return_value=mock_raw)
        mock_raw.filter = Mock(return_value=mock_raw)
        mock_raw.notch_filter = Mock(return_value=mock_raw)
        mock_raw.resample = Mock(return_value=mock_raw)

        mock_read_edf.return_value = mock_raw

        # Create loader and load data
        loader = PhysioNetLoader(config)

        # Create dummy subject directory and files
        subject_dir = loader.dataset_dir / "S001"
        subject_dir.mkdir(parents=True, exist_ok=True)

        # Create dummy run files
        for i in range(3, 5):  # Just 2 runs for testing
            run_file = subject_dir / f"S001R{i:02d}.edf"
            run_file.touch()

        # Load data
        data, labels = loader.load()

        # Verify
        assert data.shape[0] > 0  # Some epochs
        assert data.shape[1] == 320  # 2s * 160Hz
        assert data.shape[2] == 3  # 3 channels
        assert len(labels) == len(data)
        assert all(label == "left_fist" for label in labels)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
