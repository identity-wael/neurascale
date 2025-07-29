"""
Feature extraction for seizure prediction
"""

import logging
from typing import Dict, List, Optional
import numpy as np
from scipy import signal
from scipy.signal import hilbert
import pywt

from ..interfaces import BaseFeatureExtractor
from ..types import NeuralData, FeatureVector

logger = logging.getLogger(__name__)


class SeizureFeatureExtractor(BaseFeatureExtractor):
    """
    Extract features relevant for seizure prediction.

    Features include:
    - Spectral edge frequency
    - Line length
    - Wavelet energy distribution
    - Phase synchronization
    - Hjorth parameters
    - Entropy measures
    - Spike detection
    """

    def __init__(self, window_size_ms: float = 1000.0):
        """
        Initialize seizure feature extractor

        Args:
            window_size_ms: Window size in milliseconds
        """
        self.window_size_ms = window_size_ms

        # Frequency bands for analysis
        self.freq_bands = {
            "delta": (0.5, 4),
            "theta": (4, 8),
            "alpha": (8, 12),
            "beta": (12, 30),
            "low_gamma": (30, 50),
            "high_gamma": (50, 100),
        }

        # Wavelet parameters
        self.wavelet = "db4"
        self.wavelet_levels = 6

        # Spike detection parameters
        self.spike_threshold = 3.5  # Standard deviations
        self.spike_min_distance_ms = 20

        # Initialize previous features for velocity calculation
        self._previous_features: Optional[Dict[str, np.ndarray]] = None

    async def extract_features(self, data: NeuralData) -> FeatureVector:
        """
        Extract seizure-relevant features from neural data

        Args:
            data: Raw neural data

        Returns:
            Extracted feature vector
        """
        try:
            features = {}

            # Convert to numpy array
            signal_data = data.data
            sampling_rate = data.sampling_rate

            # Extract spectral features
            spectral_features = await self._extract_spectral_features(
                signal_data, sampling_rate
            )
            features.update(spectral_features)

            # Extract temporal features
            temporal_features = await self._extract_temporal_features(
                signal_data, sampling_rate
            )
            features.update(temporal_features)

            # Extract wavelet features
            wavelet_features = await self._extract_wavelet_features(
                signal_data, sampling_rate
            )
            features.update(wavelet_features)

            # Extract synchronization features
            sync_features = await self._extract_synchronization_features(
                signal_data, sampling_rate
            )
            features.update(sync_features)

            # Extract entropy features
            entropy_features = await self._extract_entropy_features(signal_data)
            features.update(entropy_features)

            # Extract spike features
            spike_features = await self._extract_spike_features(
                signal_data, sampling_rate
            )
            features.update(spike_features)

            # Add patient metadata if available
            if data.metadata and "patient_id" in data.metadata:
                features["patient_id"] = np.array([data.metadata["patient_id"]])

            return FeatureVector(
                features=features,
                timestamp=data.timestamp,
                window_size_ms=self.window_size_ms,
                metadata={
                    "extractor": "SeizureFeatureExtractor",
                    "n_channels": signal_data.shape[0],
                    "n_samples": signal_data.shape[1],
                },
            )

        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            raise

    async def _extract_spectral_features(
        self, data: np.ndarray, sampling_rate: float
    ) -> Dict[str, np.ndarray]:
        """Extract spectral features"""
        features = {}

        # Spectral edge frequency (95th percentile)
        sef_values = []
        for channel in data:
            freqs, psd = signal.welch(channel, fs=sampling_rate, nperseg=256)
            cumsum_psd = np.cumsum(psd)
            total_power = cumsum_psd[-1]
            sef_idx = np.where(cumsum_psd >= 0.95 * total_power)[0][0]
            sef_values.append(freqs[sef_idx])

        features["spectral_edge_frequency"] = np.array(sef_values)

        # Band power ratios
        for band_name, (low_freq, high_freq) in self.freq_bands.items():
            band_powers = []
            for channel in data:
                freqs, psd = signal.welch(channel, fs=sampling_rate, nperseg=256)
                band_mask = (freqs >= low_freq) & (freqs <= high_freq)
                band_power = np.trapz(psd[band_mask], freqs[band_mask])
                band_powers.append(band_power)

            features[f"{band_name}_power"] = np.array(band_powers)

        # Spectral entropy
        spectral_entropy = []
        for channel in data:
            freqs, psd = signal.welch(channel, fs=sampling_rate, nperseg=256)
            psd_norm = psd / psd.sum()
            entropy_val = -np.sum(psd_norm * np.log2(psd_norm + 1e-15))
            spectral_entropy.append(entropy_val)

        features["spectral_entropy"] = np.array(spectral_entropy)

        return features

    async def _extract_temporal_features(
        self, data: np.ndarray, sampling_rate: float
    ) -> Dict[str, np.ndarray]:
        """Extract temporal features"""
        features = {}

        # Line length
        line_lengths = []
        for channel in data:
            ll = np.sum(np.abs(np.diff(channel)))
            line_lengths.append(ll)

        features["line_length"] = np.array(line_lengths)

        # Hjorth parameters
        activity = []
        mobility = []
        complexity = []

        for channel in data:
            # Activity (variance)
            act = np.var(channel)
            activity.append(act)

            # First derivative
            first_deriv = np.diff(channel)

            # Mobility
            mob = np.sqrt(np.var(first_deriv) / act) if act > 0 else 0
            mobility.append(mob)

            # Second derivative
            second_deriv = np.diff(first_deriv)

            # Complexity
            if np.var(first_deriv) > 0:
                comp = (
                    np.sqrt(np.var(second_deriv) / np.var(first_deriv)) / mob
                    if mob > 0
                    else 0
                )
            else:
                comp = 0
            complexity.append(comp)

        features["hjorth_activity"] = np.array(activity)
        features["hjorth_mobility"] = np.array(mobility)
        features["hjorth_complexity"] = np.array(complexity)

        # Non-linear energy
        nle = []
        for channel in data:
            if len(channel) > 2:
                energy = np.mean(channel[1:-1] ** 2 - channel[:-2] * channel[2:])
            else:
                energy = 0
            nle.append(energy)

        features["nonlinear_energy"] = np.array(nle)

        return features

    async def _extract_wavelet_features(
        self, data: np.ndarray, sampling_rate: float
    ) -> Dict[str, np.ndarray]:
        """Extract wavelet-based features"""
        features = {}

        # Wavelet decomposition
        wavelet_energies = []
        wavelet_entropy = []

        for channel in data:
            # Perform wavelet decomposition
            coeffs = pywt.wavedec(channel, self.wavelet, level=self.wavelet_levels)

            # Calculate energy for each level
            energies = []
            for coeff in coeffs:
                energy = np.sum(coeff**2)
                energies.append(energy)

            wavelet_energies.append(energies)

            # Wavelet entropy
            total_energy = sum(energies)
            if total_energy > 0:
                probabilities = np.array(energies) / total_energy
                entropy_val = -np.sum(probabilities * np.log2(probabilities + 1e-15))
            else:
                entropy_val = 0

            wavelet_entropy.append(entropy_val)

        features["wavelet_energy"] = np.array(wavelet_energies)
        features["wavelet_entropy"] = np.array(wavelet_entropy)

        return features

    async def _extract_synchronization_features(
        self, data: np.ndarray, sampling_rate: float
    ) -> Dict[str, np.ndarray]:
        """Extract phase synchronization features"""
        features = {}

        n_channels = data.shape[0]

        # Phase synchronization between channel pairs
        sync_values = []
        coherence_values = []

        for i in range(n_channels):
            for j in range(i + 1, n_channels):
                # Hilbert transform for instantaneous phase
                analytic1 = hilbert(data[i])
                analytic2 = hilbert(data[j])

                phase1 = np.angle(analytic1)
                phase2 = np.angle(analytic2)

                # Phase locking value (PLV)
                phase_diff = phase1 - phase2
                plv = np.abs(np.mean(np.exp(1j * phase_diff)))
                sync_values.append(plv)

                # Coherence in specific bands
                freqs, coherence = signal.coherence(
                    data[i], data[j], fs=sampling_rate, nperseg=128
                )

                # Average coherence in beta band (important for seizures)
                beta_mask = (freqs >= 12) & (freqs <= 30)
                beta_coherence = np.mean(coherence[beta_mask])
                coherence_values.append(beta_coherence)

        features["phase_synchronization"] = np.array(sync_values)
        features["channel_coherence"] = np.array(coherence_values)

        return features

    async def _extract_entropy_features(  # noqa: C901
        self, data: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Extract entropy-based features"""
        features = {}

        # Sample entropy
        sample_entropies = []

        for channel in data:
            # Simplified sample entropy calculation
            m = 2  # Pattern length
            r = 0.2 * np.std(channel)  # Tolerance

            N = len(channel)
            patterns = np.array([channel[i : i + m] for i in range(N - m + 1)])

            # Count pattern matches
            matches = 0
            for i in range(len(patterns)):
                for j in range(i + 1, len(patterns)):
                    if np.max(np.abs(patterns[i] - patterns[j])) <= r:
                        matches += 1

            if len(patterns) > 1:
                phi_m = matches / (len(patterns) * (len(patterns) - 1) / 2)
                sample_entropy = -np.log(phi_m + 1e-15)
            else:
                sample_entropy = 0

            sample_entropies.append(sample_entropy)

        features["sample_entropy"] = np.array(sample_entropies)

        # Approximate entropy
        approx_entropies = []

        for channel in data:
            # Simplified approximate entropy
            N = len(channel)
            m = 2
            r = 0.2 * np.std(channel)

            def _maxdist(xi: np.ndarray, xj: np.ndarray, m: int) -> float:
                return max([abs(float(xi[k]) - float(xj[k])) for k in range(m)])

            def _phi(m: int) -> float:
                patterns = np.array([channel[i : i + m] for i in range(N - m + 1)])
                C = np.zeros(N - m + 1)

                for i in range(N - m + 1):
                    matching_patterns = 0
                    for j in range(N - m + 1):
                        if _maxdist(patterns[i], patterns[j], m) <= r:
                            matching_patterns += 1

                    C[i] = matching_patterns / (N - m + 1)

                phi = (N - m + 1) ** (-1) * sum(np.log(C))
                return phi

            try:
                approx_entropy = _phi(m) - _phi(m + 1)
            except Exception:
                approx_entropy = 0

            approx_entropies.append(approx_entropy)

        features["approximate_entropy"] = np.array(approx_entropies)

        return features

    async def _extract_spike_features(
        self, data: np.ndarray, sampling_rate: float
    ) -> Dict[str, np.ndarray]:
        """Extract spike-related features"""
        features = {}

        spike_rates = []
        spike_amplitudes = []

        min_distance_samples = int(self.spike_min_distance_ms * sampling_rate / 1000)

        for channel in data:
            # Simple spike detection using threshold
            channel_mean = np.mean(channel)
            channel_std = np.std(channel)

            # Find peaks above threshold
            spike_threshold = channel_mean + self.spike_threshold * channel_std

            peaks, properties = signal.find_peaks(
                channel,
                height=spike_threshold,
                distance=min_distance_samples,
            )

            # Spike rate (spikes per second)
            duration_seconds = len(channel) / sampling_rate
            spike_rate = len(peaks) / duration_seconds if duration_seconds > 0 else 0
            spike_rates.append(spike_rate)

            # Average spike amplitude
            if len(peaks) > 0:
                avg_amplitude = np.mean(properties["peak_heights"])
            else:
                avg_amplitude = 0
            spike_amplitudes.append(avg_amplitude)

        features["spike_rate"] = np.array(spike_rates)
        features["spike_amplitude"] = np.array(spike_amplitudes)
        features["channel_spike_rate"] = np.array(spike_rates)  # For spatial focus

        # Feature velocity (rate of change)
        if hasattr(self, "_previous_features"):
            # Calculate how fast features are changing
            velocity = []
            for key in ["spectral_edge_frequency", "line_length", "spike_rate"]:
                if key in features and key in self._previous_features:
                    change = np.abs(features[key] - self._previous_features[key])
                    velocity.extend(change)

            features["feature_velocity"] = (
                np.array([np.mean(velocity)]) if velocity else np.array([0.0])
            )

        # Store current features for next iteration
        self._previous_features = features.copy()

        return features

    def get_feature_names(self) -> List[str]:
        """Get list of all feature names"""
        return [
            "spectral_edge_frequency",
            "delta_power",
            "theta_power",
            "alpha_power",
            "beta_power",
            "low_gamma_power",
            "high_gamma_power",
            "spectral_entropy",
            "line_length",
            "hjorth_activity",
            "hjorth_mobility",
            "hjorth_complexity",
            "nonlinear_energy",
            "wavelet_energy",
            "wavelet_entropy",
            "phase_synchronization",
            "channel_coherence",
            "sample_entropy",
            "approximate_entropy",
            "spike_rate",
            "spike_amplitude",
            "channel_spike_rate",
            "feature_velocity",
        ]
