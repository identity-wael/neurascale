"""Unit tests for signal quality monitoring."""

import pytest
import numpy as np

from src.devices.signal_quality import (
    SignalQualityMonitor,
    SignalQualityMetrics,
    SignalQualityLevel,
    ImpedanceResult,
)


class TestSignalQualityMonitor:
    """Test suite for SignalQualityMonitor."""

    @pytest.fixture
    def monitor(self):
        """Create a signal quality monitor instance."""
        return SignalQualityMonitor(sampling_rate=256.0, line_freq=60.0)

    def test_initialization(self, monitor):
        """Test monitor initialization."""
        assert monitor.sampling_rate == 256.0
        assert monitor.line_freq == 60.0
        assert monitor.window_duration == 1.0
        assert monitor.window_size == 256

    def test_assess_signal_quality_good(self, monitor):
        """Test signal quality assessment with good signal."""
        # Generate clean sinusoidal signal (10 Hz)
        t = np.linspace(0, 1, 256)
        signal = np.sin(2 * np.pi * 10 * t)

        # Add small amount of noise
        signal += np.random.normal(0, 0.1, len(signal))

        metrics = monitor.assess_signal_quality(signal, channel_id=0)

        assert isinstance(metrics, SignalQualityMetrics)
        assert metrics.channel_id == 0
        assert metrics.snr_db > 10  # Should have decent SNR
        assert metrics.rms_amplitude > 0
        assert metrics.quality_level in [
            SignalQualityLevel.EXCELLENT,
            SignalQualityLevel.GOOD,
            SignalQualityLevel.FAIR,
        ]
        assert metrics.is_acceptable

    def test_assess_signal_quality_poor(self, monitor):
        """Test signal quality assessment with poor signal."""
        # Generate very noisy signal
        signal = np.random.normal(0, 1, 256)

        metrics = monitor.assess_signal_quality(signal, channel_id=1)

        assert metrics.channel_id == 1
        assert metrics.snr_db < 10  # Should have poor SNR
        assert metrics.quality_level in [
            SignalQualityLevel.POOR,
            SignalQualityLevel.BAD,
        ]

    def test_assess_signal_quality_with_artifacts(self, monitor):
        """Test signal quality with artifacts."""
        # Generate signal with spikes
        signal = np.random.normal(0, 0.5, 256)
        # Add artifacts (large spikes)
        signal[50] = 10
        signal[100] = -10
        signal[150] = 15

        metrics = monitor.assess_signal_quality(signal, channel_id=2)

        assert metrics.artifacts_detected > 0

    def test_assess_signal_quality_with_line_noise(self, monitor):
        """Test signal quality with line noise."""
        # Generate signal with 60 Hz line noise
        t = np.linspace(0, 1, 256)
        signal = np.sin(2 * np.pi * 10 * t)  # 10 Hz base signal
        signal += 0.5 * np.sin(2 * np.pi * 60 * t)  # Add 60 Hz noise

        metrics = monitor.assess_signal_quality(signal, channel_id=3)

        assert metrics.line_noise_power > 0.1  # Should detect line noise

    def test_assess_impedance_excellent(self, monitor):
        """Test impedance assessment for excellent quality."""
        result = monitor.assess_impedance(3000, channel_id=0)  # 3 kOhm

        assert isinstance(result, ImpedanceResult)
        assert result.channel_id == 0
        assert result.impedance_ohms == 3000
        assert result.impedance_kohms == 3.0
        assert result.quality_level == SignalQualityLevel.EXCELLENT

    def test_assess_impedance_good(self, monitor):
        """Test impedance assessment for good quality."""
        result = monitor.assess_impedance(8000, channel_id=1)  # 8 kOhm

        assert result.quality_level == SignalQualityLevel.GOOD

    def test_assess_impedance_fair(self, monitor):
        """Test impedance assessment for fair quality."""
        result = monitor.assess_impedance(15000, channel_id=2)  # 15 kOhm

        assert result.quality_level == SignalQualityLevel.FAIR

    def test_assess_impedance_poor(self, monitor):
        """Test impedance assessment for poor quality."""
        result = monitor.assess_impedance(35000, channel_id=3)  # 35 kOhm

        assert result.quality_level == SignalQualityLevel.POOR

    def test_assess_impedance_bad(self, monitor):
        """Test impedance assessment for bad quality."""
        result = monitor.assess_impedance(100000, channel_id=4)  # 100 kOhm

        assert result.quality_level == SignalQualityLevel.BAD

    def test_assess_multi_channel(self, monitor):
        """Test multi-channel signal quality assessment."""
        # Generate 4 channels with different quality
        channels = []

        # Channel 0: Good quality
        t = np.linspace(0, 1, 256)
        channels.append(np.sin(2 * np.pi * 10 * t) + np.random.normal(0, 0.1, 256))

        # Channel 1: Poor quality (very noisy)
        channels.append(np.random.normal(0, 2, 256))

        # Channel 2: With artifacts
        signal = np.random.normal(0, 0.5, 256)
        signal[50] = 20
        channels.append(signal)

        # Channel 3: With line noise
        channels.append(np.sin(2 * np.pi * 10 * t) + 0.8 * np.sin(2 * np.pi * 60 * t))

        signals = np.array(channels)

        metrics = monitor.assess_multi_channel(signals)

        assert len(metrics) == 4
        assert all(isinstance(m, SignalQualityMetrics) for m in metrics)
        assert metrics[0].quality_level in [
            SignalQualityLevel.EXCELLENT,
            SignalQualityLevel.GOOD,
        ]
        assert metrics[1].quality_level in [
            SignalQualityLevel.POOR,
            SignalQualityLevel.BAD,
        ]
        assert metrics[2].artifacts_detected > 0
        assert metrics[3].line_noise_power > 0.1

    def test_get_overall_quality(self, monitor):
        """Test overall quality assessment."""
        # Create metrics with different quality levels
        metrics = [
            SignalQualityMetrics(
                channel_id=0,
                snr_db=25.0,
                rms_amplitude=1.0,
                line_noise_power=0.05,
                artifacts_detected=0,
                quality_level=SignalQualityLevel.EXCELLENT,
            ),
            SignalQualityMetrics(
                channel_id=1,
                snr_db=18.0,
                rms_amplitude=1.2,
                line_noise_power=0.08,
                artifacts_detected=2,
                quality_level=SignalQualityLevel.GOOD,
            ),
            SignalQualityMetrics(
                channel_id=2,
                snr_db=12.0,
                rms_amplitude=0.8,
                line_noise_power=0.15,
                artifacts_detected=5,
                quality_level=SignalQualityLevel.FAIR,
            ),
            SignalQualityMetrics(
                channel_id=3,
                snr_db=3.0,
                rms_amplitude=2.0,
                line_noise_power=0.4,
                artifacts_detected=20,
                quality_level=SignalQualityLevel.BAD,
            ),
        ]

        overall_quality, summary = monitor.get_overall_quality(metrics)

        # Overall quality should be worst case (BAD)
        assert overall_quality == SignalQualityLevel.BAD

        # Check summary statistics
        assert "avg_snr_db" in summary
        assert "min_snr_db" in summary
        assert summary["n_excellent"] == 1
        assert summary["n_good"] == 1
        assert summary["n_fair"] == 1
        assert summary["n_bad"] == 1
        assert summary["n_poor"] == 0

    def test_empty_signal_handling(self, monitor):
        """Test handling of empty signals."""
        empty_signal = np.array([])

        # Should handle empty signal gracefully
        metrics = monitor.assess_signal_quality(empty_signal, channel_id=0)
        assert isinstance(metrics, SignalQualityMetrics)

    def test_constant_signal(self, monitor):
        """Test handling of constant (DC) signal."""
        # Constant signal (no variation)
        signal = np.ones(256) * 5.0

        metrics = monitor.assess_signal_quality(signal, channel_id=0)

        # Should detect as poor quality (no signal variation)
        assert metrics.quality_level in [
            SignalQualityLevel.POOR,
            SignalQualityLevel.BAD,
        ]

    def test_different_sampling_rates(self):
        """Test monitor with different sampling rates."""
        # Test with common sampling rates
        for rate in [128.0, 256.0, 512.0, 1000.0]:
            monitor = SignalQualityMonitor(sampling_rate=rate)
            assert monitor.sampling_rate == rate
            assert monitor.window_size == int(rate * monitor.window_duration)

    def test_different_line_frequencies(self):
        """Test monitor with different line frequencies."""
        # Test 50 Hz (European) and 60 Hz (US)
        monitor_50 = SignalQualityMonitor(sampling_rate=256.0, line_freq=50.0)
        monitor_60 = SignalQualityMonitor(sampling_rate=256.0, line_freq=60.0)

        assert monitor_50.line_freq == 50.0
        assert monitor_60.line_freq == 60.0

    def test_quality_level_ordering(self):
        """Test quality level ordering."""
        levels = list(SignalQualityLevel)

        # Ensure levels are in expected order
        assert levels.index(SignalQualityLevel.EXCELLENT) < levels.index(
            SignalQualityLevel.GOOD
        )
        assert levels.index(SignalQualityLevel.GOOD) < levels.index(
            SignalQualityLevel.FAIR
        )
        assert levels.index(SignalQualityLevel.FAIR) < levels.index(
            SignalQualityLevel.POOR
        )
        assert levels.index(SignalQualityLevel.POOR) < levels.index(
            SignalQualityLevel.BAD
        )
