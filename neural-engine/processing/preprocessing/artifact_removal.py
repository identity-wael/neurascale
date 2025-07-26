"""Artifact Removal - EOG, EMG, and motion artifact detection and removal.

This module implements various artifact removal techniques including
Independent Component Analysis (ICA) and regression-based methods.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from scipy import signal, stats
from sklearn.decomposition import FastICA
from sklearn.linear_model import LinearRegression
import warnings

logger = logging.getLogger(__name__)


class ArtifactRemover:
    """Artifact detection and removal for neural signals."""

    def __init__(self, config: Any):
        """Initialize artifact remover.

        Args:
            config: Processing configuration
        """
        self.config = config

        # ICA parameters
        self.ica_model = None
        self.mixing_matrix = None
        self.unmixing_matrix = None

        # Artifact detection thresholds
        self.eog_threshold = 100.0  # microvolts
        self.emg_threshold = 50.0  # microvolts RMS in high frequencies
        self.motion_threshold = 200.0  # microvolts

        # Frequency bands for artifact detection
        self.emg_band = (20, 100)  # Hz
        self.eog_band = (0.1, 10)  # Hz

        logger.info("ArtifactRemover initialized")

    async def initialize(self) -> None:
        """Initialize artifact removal components."""
        # Pre-create ICA model if needed
        if "ica" in self.config.artifact_methods:
            self.ica_model = FastICA(
                n_components=self.config.ica_components,
                algorithm="parallel",
                whiten=True,
                max_iter=500,
                random_state=42,
            )
        logger.info("Artifact remover initialization complete")

    async def detect_eog_artifacts(
        self, eeg_data: np.ndarray, eog_channels: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """Detect EOG (eye movement) artifacts in EEG data.

        Args:
            eeg_data: EEG signal data (channels x samples)
            eog_channels: Indices of EOG channels if available

        Returns:
            Dictionary with EOG artifact information
        """
        artifact_info = {
            "detected": False,
            "affected_channels": [],
            "artifact_periods": [],
            "confidence": 0.0,
        }

        try:
            # If EOG channels are provided, use them directly
            if eog_channels:
                eog_data = eeg_data[eog_channels, :]

                # Detect large amplitude deflections in EOG
                for i, ch in enumerate(eog_channels):
                    ch_data = eog_data[i, :]

                    # Calculate moving standard deviation
                    window_size = int(0.5 * self.config.sampling_rate)  # 500ms window
                    rolling_std = self._moving_std(ch_data, window_size)

                    # Find periods where amplitude exceeds threshold
                    artifact_mask = np.abs(ch_data) > self.eog_threshold

                    if np.any(artifact_mask):
                        artifact_info["detected"] = True
                        artifact_info["affected_channels"].append(ch)

                        # Find artifact periods
                        artifact_periods = self._find_artifact_periods(artifact_mask)
                        artifact_info["artifact_periods"].extend(artifact_periods)

            else:
                # Detect EOG artifacts without dedicated EOG channels
                # Look for correlated activity in frontal channels
                frontal_channels = self._get_frontal_channels(eeg_data.shape[0])

                if frontal_channels:
                    frontal_data = eeg_data[frontal_channels, :]

                    # Check for high amplitude, low frequency activity
                    for i, ch in enumerate(frontal_channels):
                        # Bandpass filter to EOG frequency range
                        filtered = await self._bandpass_filter(
                            frontal_data[i, :], self.eog_band[0], self.eog_band[1]
                        )

                        # Check amplitude
                        if np.max(np.abs(filtered)) > self.eog_threshold:
                            artifact_info["detected"] = True
                            artifact_info["affected_channels"].append(ch)

            # Calculate confidence score
            if artifact_info["detected"]:
                artifact_info["confidence"] = (
                    min(
                        len(artifact_info["affected_channels"]) / len(frontal_channels),
                        1.0,
                    )
                    if frontal_channels
                    else 0.5
                )

            return artifact_info

        except Exception as e:
            logger.error(f"Error detecting EOG artifacts: {str(e)}")
            return artifact_info

    async def detect_emg_artifacts(
        self,
        eeg_data: np.ndarray,
        frequency_bands: Optional[Tuple[float, float]] = None,
    ) -> Dict[str, Any]:
        """Detect EMG (muscle) artifacts in EEG data.

        Args:
            eeg_data: EEG signal data (channels x samples)
            frequency_bands: Frequency range to check for EMG activity

        Returns:
            Dictionary with EMG artifact information
        """
        artifact_info = {
            "detected": False,
            "affected_channels": [],
            "artifact_periods": [],
            "mean_emg_power": 0.0,
        }

        try:
            freq_band = frequency_bands or self.emg_band

            # Check each channel for high frequency activity
            for ch in range(eeg_data.shape[0]):
                # Bandpass filter to EMG frequency range
                filtered = await self._bandpass_filter(
                    eeg_data[ch, :], freq_band[0], freq_band[1]
                )

                # Calculate RMS in sliding windows
                window_size = int(0.1 * self.config.sampling_rate)  # 100ms window
                rms_values = self._moving_rms(filtered, window_size)

                # Check if RMS exceeds threshold
                if np.mean(rms_values) > self.emg_threshold:
                    artifact_info["detected"] = True
                    artifact_info["affected_channels"].append(ch)

                    # Find high EMG periods
                    emg_mask = rms_values > self.emg_threshold
                    artifact_periods = self._find_artifact_periods(emg_mask)
                    artifact_info["artifact_periods"].extend(artifact_periods)

            # Calculate mean EMG power across channels
            if artifact_info["detected"]:
                artifact_info["mean_emg_power"] = np.mean(
                    [
                        np.mean(
                            self._moving_rms(
                                await self._bandpass_filter(
                                    eeg_data[ch, :], freq_band[0], freq_band[1]
                                ),
                                window_size,
                            )
                        )
                        for ch in artifact_info["affected_channels"]
                    ]
                )

            return artifact_info

        except Exception as e:
            logger.error(f"Error detecting EMG artifacts: {str(e)}")
            return artifact_info

    async def remove_artifacts_ica(
        self,
        data: np.ndarray,
        n_components: Optional[int] = None,
        artifact_components: Optional[List[int]] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Remove artifacts using Independent Component Analysis.

        Args:
            data: Signal data (channels x samples)
            n_components: Number of ICA components
            artifact_components: Indices of components to remove (if known)

        Returns:
            Tuple of (cleaned_data, ica_info)
        """
        ica_info = {
            "n_components": n_components or data.shape[0],
            "removed_components": [],
            "variance_explained": 0.0,
        }

        try:
            # Initialize ICA if not already done
            if self.ica_model is None:
                self.ica_model = FastICA(
                    n_components=n_components or min(data.shape[0], 20),
                    algorithm="parallel",
                    whiten=True,
                    max_iter=500,
                    random_state=42,
                )

            # Fit ICA
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                sources = self.ica_model.fit_transform(data.T).T

            # Store mixing matrices
            self.mixing_matrix = self.ica_model.mixing_.T
            self.unmixing_matrix = self.ica_model.components_

            # Identify artifact components if not provided
            if artifact_components is None:
                artifact_components = await self._identify_artifact_components(
                    sources, data
                )

            # Zero out artifact components
            cleaned_sources = sources.copy()
            for comp_idx in artifact_components:
                cleaned_sources[comp_idx, :] = 0

            # Reconstruct signal
            cleaned_data = self.mixing_matrix @ cleaned_sources

            # Calculate variance explained by removed components
            if artifact_components:
                removed_variance = np.sum(
                    [np.var(sources[i, :]) for i in artifact_components]
                )
                total_variance = np.sum(np.var(sources, axis=1))
                ica_info["variance_explained"] = removed_variance / total_variance

            ica_info["removed_components"] = artifact_components

            logger.info(
                f"ICA artifact removal: removed {len(artifact_components)} components, "
                f"variance explained: {ica_info['variance_explained']:.2%}"
            )

            return cleaned_data, ica_info

        except Exception as e:
            logger.error(f"Error in ICA artifact removal: {str(e)}")
            # Return original data on error
            return data, ica_info

    async def remove_eog_regression(
        self, eeg_data: np.ndarray, eog_channels: List[int]
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Remove EOG artifacts using regression.

        Args:
            eeg_data: EEG data including EOG channels (channels x samples)
            eog_channels: Indices of EOG channels

        Returns:
            Tuple of (cleaned_data, regression_info)
        """
        regression_info = {
            "eog_channels_used": eog_channels,
            "channels_corrected": [],
            "mean_r_squared": 0.0,
        }

        try:
            # Separate EOG and EEG channels
            eog_data = eeg_data[eog_channels, :]
            eeg_channel_indices = [
                i for i in range(eeg_data.shape[0]) if i not in eog_channels
            ]

            cleaned_data = eeg_data.copy()
            r_squared_values = []

            # For each EEG channel, regress out EOG influence
            for eeg_ch in eeg_channel_indices:
                # Prepare regression data
                X = eog_data.T  # EOG signals as predictors
                y = eeg_data[eeg_ch, :]  # EEG channel as target

                # Fit linear regression
                reg = LinearRegression()
                reg.fit(X, y)

                # Calculate R-squared
                r_squared = reg.score(X, y)
                r_squared_values.append(r_squared)

                # Remove EOG contribution if significant
                if r_squared > 0.1:  # 10% variance explained threshold
                    eog_contribution = reg.predict(X)
                    cleaned_data[eeg_ch, :] = y - eog_contribution
                    regression_info["channels_corrected"].append(eeg_ch)

            regression_info["mean_r_squared"] = np.mean(r_squared_values)

            logger.info(
                f"EOG regression: corrected {len(regression_info['channels_corrected'])} channels, "
                f"mean R²: {regression_info['mean_r_squared']:.3f}"
            )

            return cleaned_data, regression_info

        except Exception as e:
            logger.error(f"Error in EOG regression: {str(e)}")
            return eeg_data, regression_info

    async def _identify_artifact_components(
        self, sources: np.ndarray, original_data: np.ndarray
    ) -> List[int]:
        """Automatically identify artifact components in ICA.

        Args:
            sources: ICA source signals (components x samples)
            original_data: Original signal data

        Returns:
            List of artifact component indices
        """
        artifact_components = []

        try:
            for comp_idx in range(sources.shape[0]):
                component = sources[comp_idx, :]

                # Check for EOG-like characteristics
                # 1. High amplitude in low frequencies
                low_freq_power = await self._calculate_band_power(component, 0.1, 4.0)
                total_power = np.var(component)

                if low_freq_power / total_power > 0.8:  # >80% power in low frequencies
                    artifact_components.append(comp_idx)
                    continue

                # 2. Check for EMG-like characteristics
                # High frequency noise
                high_freq_power = await self._calculate_band_power(component, 20, 100)

                if (
                    high_freq_power / total_power > 0.7
                ):  # >70% power in high frequencies
                    artifact_components.append(comp_idx)
                    continue

                # 3. Check for abnormal kurtosis (spiky artifacts)
                kurt = stats.kurtosis(component)
                if abs(kurt) > 10:  # Very high kurtosis
                    artifact_components.append(comp_idx)

            return artifact_components

        except Exception as e:
            logger.error(f"Error identifying artifact components: {str(e)}")
            return []

    async def _bandpass_filter(
        self, signal_data: np.ndarray, low_freq: float, high_freq: float
    ) -> np.ndarray:
        """Apply bandpass filter to signal.

        Args:
            signal_data: 1D signal data
            low_freq: Low cutoff frequency (Hz)
            high_freq: High cutoff frequency (Hz)

        Returns:
            Filtered signal
        """
        nyquist = self.config.sampling_rate / 2
        low = low_freq / nyquist
        high = high_freq / nyquist

        # Design Butterworth filter
        b, a = signal.butter(4, [low, high], btype="band")

        # Apply filter (forward-backward to preserve phase)
        filtered = signal.filtfilt(b, a, signal_data)

        return filtered

    async def _calculate_band_power(
        self, signal_data: np.ndarray, low_freq: float, high_freq: float
    ) -> float:
        """Calculate power in specific frequency band.

        Args:
            signal_data: 1D signal data
            low_freq: Low frequency bound (Hz)
            high_freq: High frequency bound (Hz)

        Returns:
            Power in frequency band
        """
        # Filter to frequency band
        filtered = await self._bandpass_filter(signal_data, low_freq, high_freq)

        # Calculate power (variance)
        return np.var(filtered)

    def _moving_std(self, signal_data: np.ndarray, window_size: int) -> np.ndarray:
        """Calculate moving standard deviation.

        Args:
            signal_data: 1D signal data
            window_size: Window size in samples

        Returns:
            Moving standard deviation
        """
        return (
            np.convolve(
                (signal_data - np.mean(signal_data)) ** 2,
                np.ones(window_size) / window_size,
                mode="same",
            )
            ** 0.5
        )

    def _moving_rms(self, signal_data: np.ndarray, window_size: int) -> np.ndarray:
        """Calculate moving RMS (Root Mean Square).

        Args:
            signal_data: 1D signal data
            window_size: Window size in samples

        Returns:
            Moving RMS values
        """
        return np.sqrt(
            np.convolve(signal_data**2, np.ones(window_size) / window_size, mode="same")
        )

    def _find_artifact_periods(
        self, artifact_mask: np.ndarray
    ) -> List[Tuple[int, int]]:
        """Find continuous artifact periods from boolean mask.

        Args:
            artifact_mask: Boolean array indicating artifact presence

        Returns:
            List of (start, end) sample indices for artifact periods
        """
        # Find transitions
        diff = np.diff(np.concatenate(([False], artifact_mask, [False])).astype(int))
        starts = np.where(diff == 1)[0]
        ends = np.where(diff == -1)[0]

        return list(zip(starts, ends))

    def _get_frontal_channels(self, n_channels: int) -> List[int]:
        """Get indices of frontal channels (simplified).

        Args:
            n_channels: Total number of channels

        Returns:
            List of frontal channel indices
        """
        # Simple heuristic: assume first 20% are frontal
        n_frontal = max(2, int(n_channels * 0.2))
        return list(range(n_frontal))

    def update_config(self, params: Dict[str, Any]) -> None:
        """Update artifact removal configuration.

        Args:
            params: Parameters to update
        """
        if "artifact_methods" in params:
            self.config.artifact_methods = params["artifact_methods"]
        if "ica_components" in params:
            self.config.ica_components = params["ica_components"]
        if "eog_channels" in params:
            self.config.eog_channels = params["eog_channels"]

    async def cleanup(self) -> None:
        """Cleanup artifact removal resources."""
        self.ica_model = None
        self.mixing_matrix = None
        self.unmixing_matrix = None
        logger.info("Artifact remover cleanup complete")
