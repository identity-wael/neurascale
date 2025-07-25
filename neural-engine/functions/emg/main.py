"""Cloud Function for processing EMG (Electromyography) data streams."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_processor import process_neural_stream, NeuralDataProcessor
import numpy as np
from scipy import signal
import logging

logger = logging.getLogger(__name__)


class EMGProcessor(NeuralDataProcessor):
    """Specialized processor for EMG data."""

    def __init__(self):
        super().__init__('emg')

    def calculate_muscle_activation(self, data: np.ndarray) -> dict:
        """Calculate muscle activation metrics from EMG signal."""
        # Rectify the signal
        rectified = np.abs(data)

        # Apply moving average (100ms window)
        window_size = int(0.1 * self.config['sampling_rate'])
        if window_size > len(rectified):
            window_size = len(rectified)

        smoothed = np.convolve(rectified, np.ones(window_size)/window_size, mode='valid')

        # Calculate activation metrics
        return {
            'mean_activation': float(np.mean(smoothed)),
            'peak_activation': float(np.max(smoothed)),
            'activation_duration': float(np.sum(smoothed > 0.1 * np.max(smoothed)) / self.config['sampling_rate']),
            'fatigue_index': float(np.polyfit(range(len(smoothed)), smoothed, 1)[0])  # Slope as fatigue indicator
        }

    def extract_features(self, data: np.ndarray) -> dict:
        """Extract EMG-specific features."""
        features = super().extract_features(data)

        # Add EMG-specific features
        activation_metrics = self.calculate_muscle_activation(data)
        features.update(activation_metrics)

        # Frequency domain features for EMG
        freqs, psd = signal.welch(data, self.config['sampling_rate'])

        # Median frequency
        cumsum_psd = np.cumsum(psd)
        median_freq_idx = np.where(cumsum_psd >= cumsum_psd[-1] / 2)[0][0]
        features['median_frequency'] = float(freqs[median_freq_idx])

        return features


# Override to use EMGProcessor
def process_neural_stream(cloud_event):
    """Cloud Function entry point for processing EMG data streams."""
    import base64
    import json
    from google.cloud import error_reporting

    error_client = error_reporting.Client()

    message = cloud_event.data["message"]
    message_data = base64.b64decode(message["data"]).decode()

    try:
        data = json.loads(message_data)
        processor = EMGProcessor()
        result = processor.process(data)
        logger.info(f"EMG processing result: {result}")

    except Exception as e:
        logger.error(f"Fatal error in EMG cloud function: {str(e)}")
        error_client.report_exception()
        raise
