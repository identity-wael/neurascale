"""Advanced Filtering - Signal filtering algorithms for neural data.

This module implements various filtering techniques including adaptive filters,
notch filters, and advanced digital filter designs.
"""

import logging
from typing import Dict, List, Any, Tuple, Union
import numpy as np
from scipy import signal
from scipy.signal import butter, ellip, cheby1, cheby2, bessel, filtfilt

logger = logging.getLogger(__name__)


class AdvancedFilters:
    """Advanced filtering algorithms for neural signal processing."""

    def __init__(self, config: Any):
        """Initialize advanced filters.

        Args:
            config: Processing configuration
        """
        self.config = config

        # Filter cache to avoid recomputing coefficients
        self._filter_cache = {}

        # Adaptive filter parameters
        self.lms_step_size = 0.01
        self.rls_forgetting_factor = 0.99

        logger.info("AdvancedFilters initialized")

    async def adaptive_filter(
        self,
        signal_data: np.ndarray,
        reference: np.ndarray,
        algorithm: str = "lms",
        filter_length: int = 32,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Apply adaptive filtering to remove correlated noise.

        Args:
            signal_data: Primary signal (channels x samples)
            reference: Reference signal for noise (channels x samples)
            algorithm: 'lms' or 'rls'
            filter_length: Length of adaptive filter

        Returns:
            Tuple of (filtered_signal, filter_info)
        """
        filter_info = {
            "algorithm": algorithm,
            "filter_length": filter_length,
            "convergence": [],
        }

        try:
            if signal_data.shape != reference.shape:
                raise ValueError("Signal and reference must have same shape")

            filtered_signal = np.zeros_like(signal_data)

            # Process each channel
            for ch in range(signal_data.shape[0]):
                if algorithm == "lms":
                    filtered_signal[ch, :], convergence = await self._lms_filter(
                        signal_data[ch, :],
                        reference[ch, :],
                        filter_length,
                        self.lms_step_size,
                    )
                elif algorithm == "rls":
                    filtered_signal[ch, :], convergence = await self._rls_filter(
                        signal_data[ch, :],
                        reference[ch, :],
                        filter_length,
                        self.rls_forgetting_factor,
                    )
                else:
                    raise ValueError(f"Unknown algorithm: {algorithm}")

                filter_info["convergence"].append(convergence)

            return filtered_signal, filter_info

        except Exception as e:
            logger.error(f"Error in adaptive filtering: {str(e)}")
            return signal_data, filter_info

    async def notch_filter(
        self,
        signal_data: np.ndarray,
        frequency: float,
        sampling_rate: float,
        quality_factor: float = 30,
    ) -> np.ndarray:
        """Apply notch filter to remove specific frequency.

        Args:
            signal_data: Signal data (channels x samples)
            frequency: Frequency to remove (Hz)
            sampling_rate: Sampling rate (Hz)
            quality_factor: Q factor (bandwidth = frequency / Q)

        Returns:
            Filtered signal
        """
        try:
            # Check cache
            cache_key = f"notch_{frequency}_{sampling_rate}_{quality_factor}"
            if cache_key in self._filter_cache:
                b, a = self._filter_cache[cache_key]
            else:
                # Design notch filter
                w0 = frequency / (sampling_rate / 2)  # Normalized frequency
                b, a = signal.iirnotch(w0, quality_factor)
                self._filter_cache[cache_key] = (b, a)

            # Apply filter to each channel
            filtered = np.zeros_like(signal_data)
            for ch in range(signal_data.shape[0]):
                filtered[ch, :] = filtfilt(b, a, signal_data[ch, :])

            return filtered

        except Exception as e:
            logger.error(f"Error in notch filtering: {str(e)}")
            return signal_data

    async def notch_filter_cascade(
        self,
        signal_data: np.ndarray,
        frequencies: List[float],
        sampling_rate: float,
        quality_factor: float = 30,
    ) -> np.ndarray:
        """Apply cascaded notch filters for multiple frequencies.

        Args:
            signal_data: Signal data (channels x samples)
            frequencies: List of frequencies to remove (Hz)
            sampling_rate: Sampling rate (Hz)
            quality_factor: Q factor for all notch filters

        Returns:
            Filtered signal
        """
        filtered = signal_data.copy()

        for freq in frequencies:
            filtered = await self.notch_filter(
                filtered, freq, sampling_rate, quality_factor
            )

        return filtered

    async def butterworth_bandpass(
        self,
        signal_data: np.ndarray,
        low_freq: float,
        high_freq: float,
        sampling_rate: float,
        order: int = 4,
    ) -> np.ndarray:
        """Apply Butterworth bandpass filter.

        Args:
            signal_data: Signal data (channels x samples)
            low_freq: Low cutoff frequency (Hz)
            high_freq: High cutoff frequency (Hz)
            sampling_rate: Sampling rate (Hz)
            order: Filter order

        Returns:
            Filtered signal
        """
        try:
            # Check cache
            cache_key = f"butter_bp_{low_freq}_{high_freq}_{sampling_rate}_{order}"
            if cache_key in self._filter_cache:
                b, a = self._filter_cache[cache_key]
            else:
                # Design filter
                nyquist = sampling_rate / 2
                low = low_freq / nyquist
                high = high_freq / nyquist

                if low <= 0 or high >= 1:
                    raise ValueError("Cutoff frequencies must be between 0 and Nyquist")

                b, a = butter(order, [low, high], btype="band")
                self._filter_cache[cache_key] = (b, a)

            # Apply filter
            filtered = np.zeros_like(signal_data)
            for ch in range(signal_data.shape[0]):
                filtered[ch, :] = filtfilt(b, a, signal_data[ch, :])

            return filtered

        except Exception as e:
            logger.error(f"Error in Butterworth filtering: {str(e)}")
            return signal_data

    async def elliptic_filter(
        self, signal_data: np.ndarray, filter_params: Dict[str, Any]
    ) -> np.ndarray:
        """Apply elliptic (Cauer) filter with custom parameters.

        Args:
            signal_data: Signal data (channels x samples)
            filter_params: Dictionary with filter parameters:
                - filter_type: 'lowpass', 'highpass', 'bandpass', 'bandstop'
                - cutoff: Cutoff frequency / frequencies
                - order: Filter order
                - ripple_pass: Passband ripple (dB)
                - ripple_stop: Stopband attenuation (dB)
                - sampling_rate: Sampling rate (Hz)

        Returns:
            Filtered signal
        """
        try:
            # Extract parameters
            filter_type = filter_params.get("filter_type", "bandpass")
            cutoff = filter_params.get("cutoff", [1, 50])
            order = filter_params.get("order", 4)
            ripple_pass = filter_params.get("ripple_pass", 0.1)  # dB
            ripple_stop = filter_params.get("ripple_stop", 60)  # dB
            fs = filter_params.get("sampling_rate", self.config.sampling_rate)

            # Normalize frequencies
            nyquist = fs / 2
            if isinstance(cutoff, list):
                wn = [f / nyquist for f in cutoff]
            else:
                wn = cutoff / nyquist

            # Design filter
            b, a = ellip(order, ripple_pass, ripple_stop, wn, btype=filter_type)

            # Apply filter
            filtered = np.zeros_like(signal_data)
            for ch in range(signal_data.shape[0]):
                filtered[ch, :] = filtfilt(b, a, signal_data[ch, :])

            return filtered

        except Exception as e:
            logger.error(f"Error in elliptic filtering: {str(e)}")
            return signal_data

    async def chebyshev_filter(
        self,
        signal_data: np.ndarray,
        filter_type: str,
        cutoff: Union[float, List[float]],
        order: int = 4,
        ripple: float = 0.1,
        cheby_type: int = 1,
    ) -> np.ndarray:
        """Apply Chebyshev Type I or II filter.

        Args:
            signal_data: Signal data (channels x samples)
            filter_type: 'lowpass', 'highpass', 'bandpass', 'bandstop'
            cutoff: Cutoff frequency / frequencies (Hz)
            order: Filter order
            ripple: Ripple in dB (passband for Type I, stopband for Type II)
            cheby_type: 1 or 2 for Chebyshev Type I or II

        Returns:
            Filtered signal
        """
        try:
            # Normalize frequencies
            nyquist = self.config.sampling_rate / 2
            if isinstance(cutoff, list):
                wn = [f / nyquist for f in cutoff]
            else:
                wn = cutoff / nyquist

            # Design filter
            if cheby_type == 1:
                b, a = cheby1(order, ripple, wn, btype=filter_type)
            else:
                b, a = cheby2(order, ripple, wn, btype=filter_type)

            # Apply filter
            filtered = np.zeros_like(signal_data)
            for ch in range(signal_data.shape[0]):
                filtered[ch, :] = filtfilt(b, a, signal_data[ch, :])

            return filtered

        except Exception as e:
            logger.error(f"Error in Chebyshev filtering: {str(e)}")
            return signal_data

    async def bessel_filter(
        self,
        signal_data: np.ndarray,
        filter_type: str,
        cutoff: Union[float, List[float]],
        order: int = 4,
    ) -> np.ndarray:
        """Apply Bessel filter (maximally flat group delay).

        Args:
            signal_data: Signal data (channels x samples)
            filter_type: 'lowpass', 'highpass', 'bandpass', 'bandstop'
            cutoff: Cutoff frequency / frequencies (Hz)
            order: Filter order

        Returns:
            Filtered signal
        """
        try:
            # Normalize frequencies
            nyquist = self.config.sampling_rate / 2
            if isinstance(cutoff, list):
                wn = [f / nyquist for f in cutoff]
            else:
                wn = cutoff / nyquist

            # Design filter
            b, a = bessel(order, wn, btype=filter_type)

            # Apply filter
            filtered = np.zeros_like(signal_data)
            for ch in range(signal_data.shape[0]):
                filtered[ch, :] = filtfilt(b, a, signal_data[ch, :])

            return filtered

        except Exception as e:
            logger.error(f"Error in Bessel filtering: {str(e)}")
            return signal_data

    async def _lms_filter(
        self,
        primary: np.ndarray,
        reference: np.ndarray,
        filter_length: int,
        step_size: float,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Least Mean Squares adaptive filter implementation.

        Args:
            primary: Primary signal with noise
            reference: Reference noise signal
            filter_length: Length of adaptive filter
            step_size: LMS step size (learning rate)

        Returns:
            Tuple of (filtered_signal, convergence_curve)
        """
        n_samples = len(primary)

        # Initialize filter weights
        weights = np.zeros(filter_length)

        # Output and error signals
        output = np.zeros(n_samples)
        error = np.zeros(n_samples)
        convergence = []

        # Pad reference signal
        padded_ref = np.pad(reference, (filter_length - 1, 0), mode="constant")

        # LMS algorithm
        for i in range(n_samples):
            # Get reference vector
            ref_vector = padded_ref[i : i + filter_length][::-1]

            # Filter output
            y = np.dot(weights, ref_vector)

            # Error signal (cleaned signal)
            e = primary[i] - y
            error[i] = e
            output[i] = e

            # Update weights
            weights += step_size * e * ref_vector

            # Track convergence
            if i % 100 == 0:
                convergence.append(np.mean(np.abs(weights)))

        return output, np.array(convergence)

    async def _rls_filter(
        self,
        primary: np.ndarray,
        reference: np.ndarray,
        filter_length: int,
        forgetting_factor: float,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Recursive Least Squares adaptive filter implementation.

        Args:
            primary: Primary signal with noise
            reference: Reference noise signal
            filter_length: Length of adaptive filter
            forgetting_factor: RLS forgetting factor (0 < λ ≤ 1)

        Returns:
            Tuple of (filtered_signal, convergence_curve)
        """
        n_samples = len(primary)

        # Initialize
        weights = np.zeros(filter_length)
        P = np.eye(filter_length) / 0.01  # Inverse correlation matrix

        # Output and error signals
        output = np.zeros(n_samples)
        convergence = []

        # Pad reference signal
        padded_ref = np.pad(reference, (filter_length - 1, 0), mode="constant")

        # RLS algorithm
        for i in range(n_samples):
            # Get reference vector
            ref_vector = padded_ref[i : i + filter_length][::-1].reshape(-1, 1)

            # Prior estimation error
            y = np.dot(weights, ref_vector)[0]
            e = primary[i] - y

            # Gain vector
            k = P @ ref_vector / (forgetting_factor + ref_vector.T @ P @ ref_vector)

            # Update weights
            weights += (k * e).flatten()

            # Update inverse correlation matrix
            P = (P - k @ ref_vector.T @ P) / forgetting_factor

            # Store output
            output[i] = e

            # Track convergence
            if i % 100 == 0:
                convergence.append(np.mean(np.abs(weights)))

        return output, np.array(convergence)

    def update_config(self, params: Dict[str, Any]) -> None:
        """Update filter configuration.

        Args:
            params: Parameters to update
        """
        if "lms_step_size" in params:
            self.lms_step_size = params["lms_step_size"]
        if "rls_forgetting_factor" in params:
            self.rls_forgetting_factor = params["rls_forgetting_factor"]

        # Clear filter cache if filter parameters changed
        filter_params = [
            "notch_frequencies",
            "bandpass_low",
            "bandpass_high",
            "filter_order",
        ]
        if any(param in params for param in filter_params):
            self._filter_cache.clear()
            logger.debug("Filter cache cleared due to parameter update")

    def clear_cache(self) -> None:
        """Clear filter coefficient cache."""
        self._filter_cache.clear()
        logger.debug("Filter cache cleared")
