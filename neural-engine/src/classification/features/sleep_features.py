"""
Feature extraction for sleep stage classification
"""

import logging
from typing import Dict, List, Optional
import numpy as np
from scipy import signal

from ..interfaces import BaseFeatureExtractor
from ..types import FeatureVector, NeuralData

logger = logging.getLogger(__name__)


class SleepFeatureExtractor(BaseFeatureExtractor):
    """
    Extract features for sleep stage classification from polysomnographic signals.

    Features include:
    - EEG spectral features (delta, theta, alpha, beta power)
    - Sleep-specific events (spindles, K-complexes, slow waves)
    - EOG features (eye movements, REM density)
    - EMG features (muscle tone)
    - Cross-channel coherence
    """

    def __init__(
        self,
        window_size_ms: float = 30000.0,  # 30 seconds (standard epoch)
        eeg_channels: Optional[List[str]] = None,
        eog_channels: Optional[List[str]] = None,
        emg_channels: Optional[List[str]] = None,
    ):
        """
        Initialize sleep feature extractor

        Args:
            window_size_ms: Window size (typically 30s for sleep staging)
            eeg_channels: EEG channel names (e.g., ['C3', 'C4'])
            eog_channels: EOG channel names (e.g., ['LOC', 'ROC'])
            emg_channels: EMG channel names (e.g., ['EMG'])
        """
        self.window_size_ms = window_size_ms

        # Default channel configurations
        self.eeg_channels = eeg_channels or ["C3", "C4", "O1", "O2"]
        self.eog_channels = eog_channels or ["LOC", "ROC"]
        self.emg_channels = emg_channels or ["EMG"]

        # Frequency bands for sleep
        self.bands = {
            "delta": (0.5, 4),  # Deep sleep
            "theta": (4, 8),  # Light sleep, REM
            "alpha": (8, 13),  # Relaxed wakefulness
            "sigma": (11, 15),  # Sleep spindles
            "beta": (15, 30),  # Active wakefulness
            "gamma": (30, 45),  # High frequency
        }

        self.feature_names: List[str] = []
        self._build_feature_names()

    def _build_feature_names(self) -> None:
        """Build list of feature names"""
        # Spectral features
        for band in self.bands:
            self.feature_names.extend([f"{band}_power", f"{band}_relative_power"])

        # Sleep-specific features
        self.feature_names.extend(
            [
                "spindle_density",
                "k_complex_presence",
                "slow_wave_amplitude",
                "delta_percentage",
                "vertex_waves",
                "emg_power",
                "eye_movements",
                "rem_density",
                "spectral_edge_frequency",
                "spectral_entropy",
                "hjorth_mobility",
                "hjorth_complexity",
            ]
        )

    async def extract_features(self, data: NeuralData) -> FeatureVector:
        """
        Extract sleep-specific features from polysomnographic data

        Args:
            data: Neural data containing EEG, EOG, and EMG signals

        Returns:
            Extracted feature vector
        """
        try:
            features = {}
            channel_indices = self._get_channel_indices(data.channels)

            # Extract EEG features
            if channel_indices["eeg"]:
                eeg_features = self._extract_eeg_features(
                    data.data[channel_indices["eeg"], :], data.sampling_rate
                )
                features.update(eeg_features)

            # Extract EOG features
            if channel_indices["eog"]:
                eog_features = self._extract_eog_features(
                    data.data[channel_indices["eog"], :], data.sampling_rate
                )
                features.update(eog_features)

            # Extract EMG features
            if channel_indices["emg"]:
                emg_features = self._extract_emg_features(
                    data.data[channel_indices["emg"], :], data.sampling_rate
                )
                features.update(emg_features)

            # Cross-modal features
            if channel_indices["eeg"] and channel_indices["emg"]:
                cross_features = self._extract_cross_modal_features(
                    data.data, channel_indices, data.sampling_rate
                )
                features.update(cross_features)

            return FeatureVector(
                features=features,
                timestamp=data.timestamp,
                window_size_ms=self.window_size_ms,
                metadata={
                    "epoch_duration_s": self.window_size_ms / 1000,
                    "n_samples": data.data.shape[1],
                    "channels_used": {
                        "eeg": len(channel_indices["eeg"]),
                        "eog": len(channel_indices["eog"]),
                        "emg": len(channel_indices["emg"]),
                    },
                },
            )

        except Exception as e:
            logger.error(f"Sleep feature extraction error: {e}")
            raise

    def _get_channel_indices(self, channels: List[str]) -> Dict[str, List[int]]:
        """Map channel names to indices"""
        indices: Dict[str, List[int]] = {"eeg": [], "eog": [], "emg": []}

        for i, ch in enumerate(channels):
            ch_upper = ch.upper()

            # Check EEG channels
            if any(eeg_ch in ch_upper for eeg_ch in self.eeg_channels):
                indices["eeg"].append(i)
            # Check EOG channels
            elif any(eog_ch in ch_upper for eog_ch in self.eog_channels):
                indices["eog"].append(i)
            # Check EMG channels
            elif any(emg_ch in ch_upper for emg_ch in self.emg_channels):
                indices["emg"].append(i)

        return indices

    def _extract_eeg_features(
        self, eeg_data: np.ndarray, fs: float
    ) -> Dict[str, np.ndarray]:
        """Extract EEG-specific sleep features"""
        features = {}

        # Average across EEG channels
        eeg_avg = eeg_data.mean(axis=0)

        # 1. Spectral features
        freqs, psd = signal.welch(eeg_avg, fs=fs, nperseg=min(512, len(eeg_avg) // 4))
        total_power = np.trapz(psd, freqs)

        for band_name, (low_freq, high_freq) in self.bands.items():
            band_mask = (freqs >= low_freq) & (freqs <= high_freq)
            band_power = np.trapz(psd[band_mask], freqs[band_mask])

            features[f"{band_name}_power"] = np.array([band_power])
            features[f"{band_name}_relative_power"] = np.array(
                [band_power / (total_power + 1e-10)]
            )

        # 2. Sleep spindle detection (11-15 Hz)
        spindles = self._detect_sleep_spindles(eeg_avg, fs)
        features["spindle_density"] = np.array([spindles["density"]])

        # 3. K-complex detection
        k_complexes = self._detect_k_complexes(eeg_avg, fs)
        features["k_complex_presence"] = np.array(
            [k_complexes["count"] / (len(eeg_avg) / fs)]
        )

        # 4. Slow wave detection
        slow_waves = self._detect_slow_waves(eeg_avg, fs)
        features["slow_wave_amplitude"] = np.array([slow_waves["mean_amplitude"]])

        # 5. Delta percentage (for N3 detection)
        delta_mask = (freqs >= 0.5) & (freqs <= 4)
        delta_power = np.trapz(psd[delta_mask], freqs[delta_mask])
        low_freq_mask = (freqs >= 0.5) & (freqs <= 30)
        low_freq_power = np.trapz(psd[low_freq_mask], freqs[low_freq_mask])
        features["delta_percentage"] = np.array(
            [delta_power / (low_freq_power + 1e-10)]
        )

        # 6. Vertex waves (for N1)
        vertex_waves = self._detect_vertex_waves(eeg_avg, fs)
        features["vertex_waves"] = np.array(
            [vertex_waves["count"] / (len(eeg_avg) / fs)]
        )

        # 7. Spectral edge frequency (95% of power)
        cumsum_psd = np.cumsum(psd)
        sef_idx = np.where(cumsum_psd >= 0.95 * cumsum_psd[-1])[0]
        sef = freqs[sef_idx[0]] if len(sef_idx) > 0 else freqs[-1]
        features["spectral_edge_frequency"] = np.array([sef])

        # 8. Spectral entropy
        psd_norm = psd / (np.sum(psd) + 1e-10)
        spectral_entropy = -np.sum(psd_norm * np.log2(psd_norm + 1e-10))
        features["spectral_entropy"] = np.array([spectral_entropy])

        # 9. Hjorth parameters
        hjorth_params = self._calculate_hjorth_parameters(eeg_avg)
        features["hjorth_mobility"] = np.array([hjorth_params["mobility"]])
        features["hjorth_complexity"] = np.array([hjorth_params["complexity"]])

        return features

    def _extract_eog_features(
        self, eog_data: np.ndarray, fs: float
    ) -> Dict[str, np.ndarray]:
        """Extract EOG-specific features for REM detection"""
        features = {}

        # Difference between left and right EOG (if available)
        if eog_data.shape[0] >= 2:
            eog_diff = eog_data[0, :] - eog_data[1, :]
        else:
            eog_diff = eog_data[0, :]

        # 1. Eye movement detection
        eye_movements = self._detect_eye_movements(eog_diff, fs)
        features["eye_movements"] = np.array([eye_movements["rate"]])

        # 2. REM density (rapid eye movements per minute)
        rem_events = self._detect_rem_events(eog_diff, fs)
        features["rem_density"] = np.array([rem_events["density"]])

        return features

    def _extract_emg_features(
        self, emg_data: np.ndarray, fs: float
    ) -> Dict[str, np.ndarray]:
        """Extract EMG features for muscle tone assessment"""
        features = {}

        # Average EMG channels
        emg_avg = emg_data.mean(axis=0)

        # 1. EMG power (muscle tone indicator)
        emg_power = np.mean(emg_avg**2)
        features["emg_power"] = np.array([emg_power])

        # 2. EMG variance
        emg_variance = np.var(emg_avg)
        features["emg_variance"] = np.array([emg_variance])

        return features

    def _extract_cross_modal_features(
        self, data: np.ndarray, indices: Dict[str, List[int]], fs: float
    ) -> Dict[str, np.ndarray]:
        """Extract features combining multiple signal types"""
        features = {}

        # EEG-EMG coupling (for REM detection)
        if indices["eeg"] and indices["emg"]:
            eeg_avg = data[indices["eeg"], :].mean(axis=0)
            emg_avg = data[indices["emg"], :].mean(axis=0)

            # Coherence between EEG and EMG
            f, Cxy = signal.coherence(
                eeg_avg, emg_avg, fs=fs, nperseg=min(256, len(eeg_avg) // 4)
            )

            # Low frequency coherence (should be low in REM)
            low_freq_mask = f < 10
            low_freq_coherence = np.mean(Cxy[low_freq_mask])
            features["eeg_emg_coherence"] = np.array([low_freq_coherence])

        return features

    def _detect_sleep_spindles(
        self, eeg_signal: np.ndarray, fs: float
    ) -> Dict[str, float]:
        """Detect sleep spindles (11-15 Hz bursts lasting 0.5-2s)"""
        # Bandpass filter for spindle frequency
        nyquist = fs / 2
        low = 11 / nyquist
        high = 15 / nyquist
        b, a = signal.butter(4, [low, high], btype="band")
        spindle_filtered = signal.filtfilt(b, a, eeg_signal)

        # Calculate envelope using Hilbert transform
        analytic = signal.hilbert(spindle_filtered)
        envelope = np.abs(analytic)

        # Threshold for spindle detection
        threshold = np.percentile(envelope, 85)

        # Find spindle events
        above_threshold = envelope > threshold

        # Group consecutive samples above threshold
        spindle_events = []
        in_spindle = False
        start_idx = 0

        for i, above in enumerate(above_threshold):
            if above and not in_spindle:
                start_idx = i
                in_spindle = True
            elif not above and in_spindle:
                duration = (i - start_idx) / fs
                # Spindles last 0.5-2 seconds
                if 0.5 <= duration <= 2.0:
                    spindle_events.append(
                        {
                            "start": start_idx / fs,
                            "duration": duration,
                            "amplitude": np.max(envelope[start_idx:i]),
                        }
                    )
                in_spindle = False

        # Calculate spindle density (spindles per minute)
        epoch_duration_min = len(eeg_signal) / fs / 60
        density = (
            len(spindle_events) / epoch_duration_min if epoch_duration_min > 0 else 0
        )

        return {
            "count": len(spindle_events),
            "density": density,
            "mean_duration": (
                np.mean([s["duration"] for s in spindle_events])
                if spindle_events
                else 0
            ),
        }

    def _detect_k_complexes(
        self, eeg_signal: np.ndarray, fs: float
    ) -> Dict[str, float]:
        """Detect K-complexes (large biphasic waves)"""
        # Low-pass filter for K-complex detection
        nyquist = fs / 2
        cutoff = 10 / nyquist
        b, a = signal.butter(4, cutoff, btype="low")
        filtered = signal.filtfilt(b, a, eeg_signal)

        # Find large amplitude deflections
        amplitude_threshold = 2.5 * np.std(filtered)

        # Detect negative peaks followed by positive peaks
        k_complex_count = 0
        min_separation = int(0.5 * fs)  # 0.5 seconds minimum between K-complexes

        i = 0
        while i < len(filtered) - int(0.5 * fs):
            # Look for negative peak
            if filtered[i] < -amplitude_threshold:
                # Check for following positive peak within 0.5s
                window_end = min(i + int(0.5 * fs), len(filtered))
                window = filtered[i:window_end]

                if np.any(window > amplitude_threshold):
                    k_complex_count += 1
                    i += min_separation
                else:
                    i += 1
            else:
                i += 1

        return {"count": k_complex_count}

    def _detect_slow_waves(self, eeg_signal: np.ndarray, fs: float) -> Dict[str, float]:
        """Detect slow waves (0.5-2 Hz, >75μV amplitude)"""
        # Bandpass filter for slow waves
        nyquist = fs / 2
        low = 0.5 / nyquist
        high = 2.0 / nyquist
        b, a = signal.butter(4, [low, high], btype="band")
        slow_filtered = signal.filtfilt(b, a, eeg_signal)

        # Peak detection
        peaks, properties = signal.find_peaks(
            np.abs(slow_filtered),
            height=75,  # 75 μV threshold
            distance=int(0.5 * fs),  # Minimum 0.5s between peaks
        )

        if len(peaks) > 0:
            mean_amplitude = np.mean(properties["peak_heights"])
            count = len(peaks)
        else:
            mean_amplitude = 0
            count = 0

        return {
            "count": count,
            "mean_amplitude": mean_amplitude,
            "density": count / (len(eeg_signal) / fs / 60),  # per minute
        }

    def _detect_vertex_waves(self, eeg_signal: np.ndarray, fs: float) -> Dict[str, int]:
        """Detect vertex waves (sharp waves in N1)"""
        # Bandpass filter for vertex waves
        nyquist = fs / 2
        low = 2 / nyquist
        high = 8 / nyquist
        b, a = signal.butter(4, [low, high], btype="band")
        filtered = signal.filtfilt(b, a, eeg_signal)

        # Detect sharp negative deflections
        diff = np.diff(filtered)
        sharpness_threshold = 3 * np.std(diff)

        vertex_count = 0
        min_separation = int(0.3 * fs)  # 300ms minimum between vertex waves

        i = 0
        while i < len(diff) - 1:
            if diff[i] < -sharpness_threshold and diff[i + 1] > sharpness_threshold:
                vertex_count += 1
                i += min_separation
            else:
                i += 1

        return {"count": vertex_count}

    def _detect_eye_movements(
        self, eog_signal: np.ndarray, fs: float
    ) -> Dict[str, float]:
        """Detect eye movements from EOG"""
        # Bandpass filter for eye movements
        nyquist = fs / 2
        low = 0.3 / nyquist
        high = 10 / nyquist
        b, a = signal.butter(4, [low, high], btype="band")
        filtered = signal.filtfilt(b, a, eog_signal)

        # Detect movements by threshold crossings
        threshold = 2 * np.std(filtered)
        crossings = np.where(np.abs(filtered) > threshold)[0]

        # Group crossings into events
        if len(crossings) > 0:
            events = 1
            for i in range(1, len(crossings)):
                if crossings[i] - crossings[i - 1] > fs * 0.2:  # 200ms gap
                    events += 1

            rate = events / (len(eog_signal) / fs / 60)  # per minute
        else:
            rate = 0

        return {"rate": rate}

    def _detect_rem_events(self, eog_signal: np.ndarray, fs: float) -> Dict[str, float]:
        """Detect rapid eye movements"""
        # Higher frequency components for REM
        nyquist = fs / 2
        low = 0.5 / nyquist
        high = 5 / nyquist
        b, a = signal.butter(4, [low, high], btype="band")
        filtered = signal.filtfilt(b, a, eog_signal)

        # Calculate signal derivative for rapid changes
        derivative = np.diff(filtered)

        # REM events have high derivative
        threshold = 3 * np.std(derivative)
        rem_samples = np.abs(derivative) > threshold

        # Calculate REM density
        rem_density = np.sum(rem_samples) / len(derivative) * 100

        return {"density": rem_density}

    def _calculate_hjorth_parameters(self, signal_data: np.ndarray) -> Dict[str, float]:
        """Calculate Hjorth parameters (activity, mobility, complexity)"""
        # Activity (variance)
        activity = np.var(signal_data)

        # First derivative
        d1 = np.diff(signal_data)
        # Second derivative
        d2 = np.diff(d1)

        # Mobility
        mobility = np.sqrt(np.var(d1) / (activity + 1e-10))

        # Complexity
        complexity = np.sqrt(np.var(d2) / (np.var(d1) + 1e-10)) / (mobility + 1e-10)

        return {"activity": activity, "mobility": mobility, "complexity": complexity}

    def get_feature_names(self) -> List[str]:
        """Get list of all feature names"""
        return self.feature_names

    def get_required_window_size(self) -> float:
        """Get required window size in milliseconds"""
        return self.window_size_ms
