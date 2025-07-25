"""Cloud Function for processing EEG neural data streams."""

import sys
import os

# Add parent directory to path to import base processor
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_processor import process_neural_stream as base_process_neural_stream, NeuralDataProcessor
import numpy as np
from scipy import signal
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class EEGProcessor(NeuralDataProcessor):
    """Specialized processor for EEG data."""

    def __init__(self) -> None:
        super().__init__('eeg')

    def extract_features(self, data: np.ndarray) -> Dict[str, Any]:
        """Extract EEG-specific features including band powers."""
        features: Dict[str, Any] = super().extract_features(data)

        # Calculate band powers
        sampling_rate = self.config['sampling_rate']

        # Define EEG frequency bands
        bands = {
            'delta': (0.5, 4),
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 100)
        }

        # Compute power spectral density
        freqs, psd = signal.welch(data, sampling_rate, nperseg=min(256, len(data)))

        # Calculate band powers
        total_power = np.trapz(psd, freqs)

        for band_name, (low_freq, high_freq) in bands.items():
            idx_band = np.logical_and(freqs >= low_freq, freqs < high_freq)
            band_power = np.trapz(psd[idx_band], freqs[idx_band])
            features[f'{band_name}_power'] = float(band_power)
            features[f'{band_name}_relative_power'] = float(band_power / total_power) if total_power > 0 else 0.0

        # Add alpha peak frequency
        alpha_idx = np.logical_and(freqs >= 8, freqs < 13)
        if np.any(alpha_idx):
            alpha_psd = psd[alpha_idx]
            alpha_freqs = freqs[alpha_idx]
            peak_idx = np.argmax(alpha_psd)
            features['alpha_peak_frequency'] = float(alpha_freqs[peak_idx])

        return features

    def detect_eye_blinks(self, data: np.ndarray) -> int:
        """Detect potential eye blink artifacts in frontal channels."""
        # Simple threshold-based detection for demonstration
        # In production, use more sophisticated methods
        diff_signal = np.diff(data)
        threshold = 3 * np.std(diff_signal)
        peaks = np.where(np.abs(diff_signal) > threshold)[0]

        # Count peaks that are sufficiently separated (>100ms apart)
        min_separation = int(0.1 * self.config['sampling_rate'])

        blink_count = 0
        last_peak = -min_separation

        for peak in peaks:
            if peak - last_peak > min_separation:
                blink_count += 1
                last_peak = peak

        return blink_count


# Override the base process_neural_stream to use EEGProcessor
def process_neural_stream(cloud_event: Any) -> None:
    """Cloud Function entry point for processing EEG data streams."""
    import base64
    import json
    from google.cloud import error_reporting

    error_client = error_reporting.Client()

    # Extract message data
    message = cloud_event.data["message"]
    message_data = base64.b64decode(message["data"]).decode()

    try:
        # Parse JSON data
        data = json.loads(message_data)

        # Initialize EEG processor
        processor = EEGProcessor()

        # Process data
        result = processor.process(data)

        logger.info(f"EEG processing result: {result}")

    except Exception as e:
        logger.error(f"Fatal error in EEG cloud function: {str(e)}")
        error_client.report_exception()
        raise
