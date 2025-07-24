"""Tests for neural data validators."""

import pytest
import numpy as np
from datetime import datetime, timezone

from src.ingestion.validators import DataValidator
from src.ingestion.data_types import (
    NeuralDataPacket,
    NeuralSignalType,
    DataSource,
    DeviceInfo,
    ChannelInfo,
)


class TestDataValidator:
    """Test DataValidator class."""

    @pytest.fixture
    def validator(self):
        """Create a DataValidator instance."""
        return DataValidator()

    @pytest.fixture
    def valid_packet(self):
        """Create a valid test packet."""
        n_channels = 8
        n_samples = 256

        # Create realistic EEG data with lower noise
        # Generate smooth signals with some frequency components
        t = np.linspace(0, 1, n_samples)
        data = np.zeros((n_channels, n_samples))
        for i in range(n_channels):
            # Add alpha wave (10 Hz) and beta wave (20 Hz)
            data[i] = 30 * np.sin(2 * np.pi * 10 * t) + 20 * np.sin(2 * np.pi * 20 * t)
            # Add small amount of noise
            data[i] += np.random.randn(n_samples) * 5

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
            device_id="test_device",
            device_type="OpenBCI",
            channels=channels,
        )

        return NeuralDataPacket(
            timestamp=datetime.now(timezone.utc),
            data=data,
            signal_type=NeuralSignalType.EEG,
            source=DataSource.OPENBCI,
            device_info=device_info,
            session_id="test_session",
            sampling_rate=256.0,
            data_quality=0.95,
        )

    def test_validate_valid_packet(self, validator, valid_packet):
        """Test validation of a valid packet."""
        result = validator.validate_packet(valid_packet)

        assert result.is_valid
        assert len(result.errors) == 0
        # Quality score is affected by noise warnings
        assert result.data_quality_score > 0.5

    def test_validate_empty_data(self, validator, valid_packet):
        """Test validation with empty data."""
        valid_packet.data = np.array([]).reshape(0, 0)  # Empty 2D array

        result = validator.validate_packet(valid_packet)

        assert not result.is_valid
        assert any("empty" in error.lower() for error in result.errors)

    def test_validate_nan_data(self, validator, valid_packet):
        """Test validation with NaN values."""
        valid_packet.data[0, 0] = np.nan

        result = validator.validate_packet(valid_packet)

        assert not result.is_valid
        assert any("nan" in error.lower() for error in result.errors)

    def test_validate_inf_data(self, validator, valid_packet):
        """Test validation with infinite values."""
        valid_packet.data[0, 0] = np.inf

        result = validator.validate_packet(valid_packet)

        assert not result.is_valid
        assert any("infinite" in error.lower() for error in result.errors)

    def test_validate_out_of_range_eeg(self, validator, valid_packet):
        """Test validation with out-of-range EEG values."""
        # EEG should be in range -200 to 200 μV
        valid_packet.data[0, :] = 1000  # Too high

        result = validator.validate_packet(valid_packet)

        # Should get warning, not error
        assert result.is_valid
        assert any("range" in warning.lower() for warning in result.warnings)

    def test_validate_sampling_rate(self, validator, valid_packet):
        """Test validation of sampling rate."""
        # Test unusual sampling rate
        valid_packet.sampling_rate = 10.0  # Unusual for EEG

        result = validator.validate_packet(valid_packet)

        # Should get warning, not error
        assert result.is_valid
        assert any("sampling rate" in warning.lower() for warning in result.warnings)

    def test_validate_ecog_signal(self, validator, valid_packet):
        """Test validation of ECoG signal."""
        valid_packet.signal_type = NeuralSignalType.ECOG
        valid_packet.data = np.random.randn(8, 1000) * 200  # ECoG has higher amplitude
        valid_packet.sampling_rate = 1000.0  # Higher sampling rate

        result = validator.validate_packet(valid_packet)

        assert result.is_valid

    def test_validate_spikes_signal(self, validator):
        """Test validation of spike signal."""
        # Spikes have very high sampling rate and short duration
        data = np.random.randn(32, 30000) * 100  # 1 second at 30kHz

        device_info = DeviceInfo(
            device_id="test_device",
            device_type="NeuroPixels",
        )

        packet = NeuralDataPacket(
            timestamp=datetime.now(timezone.utc),
            data=data,
            signal_type=NeuralSignalType.SPIKES,
            source=DataSource.CUSTOM_API,
            device_info=device_info,
            session_id="test_session",
            sampling_rate=30000.0,
        )

        result = validator.validate_packet(packet)

        assert result.is_valid

    def test_calculate_quality_score(self, validator, valid_packet):
        """Test quality score calculation."""
        # Good quality data (but has some noise warnings)
        result = validator.validate_packet(valid_packet)
        assert result.data_quality_score > 0.5

        # Add extreme values that cause warnings
        valid_packet.data[0, :] = (
            190 + np.random.randn(256) * 2
        )  # Near max for EEG with small variation
        result = validator.validate_packet(valid_packet)
        # Should have more warnings which reduce quality score
        assert (
            result.data_quality_score < 0.9
        )  # Adjusted expectation based on improved validator

        # Multiple warnings should reduce score more
        valid_packet.sampling_rate = 999  # Unusual rate
        valid_packet.data[1, :] = (
            -190 + np.random.randn(256) * 2
        )  # Another channel near limit with variation
        result = validator.validate_packet(valid_packet)
        assert (
            result.data_quality_score < 0.8
        )  # Adjusted expectation based on improved validator

    def test_validate_accelerometer(self, validator):
        """Test validation of accelerometer data."""
        # Accelerometer has 3 channels (X, Y, Z)
        data = np.random.randn(3, 100) * 2  # ±2g range

        channels = [
            ChannelInfo(0, "AccX", "g", 100.0),
            ChannelInfo(1, "AccY", "g", 100.0),
            ChannelInfo(2, "AccZ", "g", 100.0),
        ]

        device_info = DeviceInfo(
            device_id="test_device",
            device_type="IMU",
            channels=channels,
        )

        packet = NeuralDataPacket(
            timestamp=datetime.now(timezone.utc),
            data=data,
            signal_type=NeuralSignalType.ACCELEROMETER,
            source=DataSource.OPENBCI,
            device_info=device_info,
            session_id="test_session",
            sampling_rate=100.0,
            data_quality=0.95,
        )

        result = validator.validate_packet(packet)

        assert result.is_valid

        # Test out of range
        packet.data[0, :] = 25  # Way too high for accelerometer
        result = validator.validate_packet(packet)

        # Should get warning, not error
        assert result.is_valid
        assert any("range" in warning.lower() for warning in result.warnings)
