"""Tests for neural data types."""

import pytest
import numpy as np
from datetime import datetime

from src.ingestion.data_types import (
    NeuralDataPacket,
    NeuralSignalType,
    DataSource,
    DeviceInfo,
    ChannelInfo,
    ValidationResult,
)


class TestNeuralDataPacket:
    """Test NeuralDataPacket class."""

    def test_packet_creation(self):
        """Test creating a valid neural data packet."""
        # Create test data
        n_channels = 8
        n_samples = 256
        data = np.random.randn(n_channels, n_samples)

        # Create device info
        channels = [
            ChannelInfo(
                channel_id=i,
                label=f"Ch{i + 1}",
                unit="microvolts",
                sampling_rate=256.0,
            )
            for i in range(n_channels)
        ]

        device_info = DeviceInfo(
            device_id="test_device_001",
            device_type="OpenBCI",
            manufacturer="OpenBCI",
            model="Cyton",
            channels=channels,
        )

        # Create packet
        packet = NeuralDataPacket(
            timestamp=datetime.utcnow(),
            data=data,
            signal_type=NeuralSignalType.EEG,
            source=DataSource.OPENBCI,
            device_info=device_info,
            session_id="test_session_001",
            sampling_rate=256.0,
        )

        # Verify properties
        assert packet.n_channels == n_channels
        assert packet.n_samples == n_samples
        assert packet.duration_seconds == pytest.approx(1.0)  # 256 samples at 256Hz

    def test_packet_validation_errors(self):
        """Test that invalid packets raise errors."""
        device_info = DeviceInfo(
            device_id="test_device",
            device_type="test",
        )

        # Test 1D data array
        with pytest.raises(ValueError, match="Data must be 2D array"):
            NeuralDataPacket(
                timestamp=datetime.utcnow(),
                data=np.array([1, 2, 3]),  # 1D array
                signal_type=NeuralSignalType.EEG,
                source=DataSource.SYNTHETIC,
                device_info=device_info,
                session_id="test",
            )

        # Test channel mismatch
        device_info.channels = [
            ChannelInfo(0, "Ch1"),
            ChannelInfo(1, "Ch2"),
        ]

        with pytest.raises(ValueError, match="Data channels.*don't match"):
            NeuralDataPacket(
                timestamp=datetime.utcnow(),
                data=np.zeros((3, 100)),  # 3 channels but device has 2
                signal_type=NeuralSignalType.EEG,
                source=DataSource.SYNTHETIC,
                device_info=device_info,
                session_id="test",
            )


class TestValidationResult:
    """Test ValidationResult class."""

    def test_validation_result_creation(self):
        """Test creating validation results."""
        result = ValidationResult(is_valid=True)

        assert result.is_valid
        assert result.errors == []
        assert result.warnings == []
        assert result.data_quality_score == 1.0

    def test_add_error(self):
        """Test adding errors invalidates result."""
        result = ValidationResult(is_valid=True)

        result.add_error("Test error")

        assert not result.is_valid
        assert "Test error" in result.errors

    def test_add_warning(self):
        """Test warnings don't invalidate result."""
        result = ValidationResult(is_valid=True)

        result.add_warning("Test warning")

        assert result.is_valid
        assert "Test warning" in result.warnings


class TestEnums:
    """Test enum types."""

    def test_neural_signal_types(self):
        """Test all neural signal types are defined."""
        expected_types = [
            "eeg",
            "ecog",
            "spikes",
            "lfp",
            "emg",
            "accelerometer",
            "custom",
        ]

        for expected in expected_types:
            assert any(t.value == expected for t in NeuralSignalType)

    def test_data_sources(self):
        """Test all data sources are defined."""
        expected_sources = [
            "lsl",
            "openbci",
            "brainflow",
            "file_upload",
            "synthetic",
            "custom_api",
        ]

        for expected in expected_sources:
            assert any(s.value == expected for s in DataSource)
