"""Cloud Function for processing spike neural data streams."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_processor import process_neural_stream as base_process_neural_stream, NeuralDataProcessor
import numpy as np
from scipy import signal
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class SpikeProcessor(NeuralDataProcessor):
    """Specialized processor for spike data."""

    def __init__(self) -> None:
        super().__init__('spikes')

    def detect_spikes(self, data: np.ndarray, threshold_factor: float = 4.0) -> dict:
        """Detect spikes using threshold crossing method."""
        # High-pass filter the data
        b, a = signal.butter(4, 300, 'high', fs=self.config['sampling_rate'])
        filtered_data = signal.filtfilt(b, a, data)

        # Calculate threshold
        noise_std = np.median(np.abs(filtered_data)) / 0.6745  # Robust std estimation
        threshold = threshold_factor * noise_std

        # Detect threshold crossings
        spike_indices = np.where(filtered_data < -threshold)[0]

        # Remove duplicates (keep only first sample of each spike)
        if len(spike_indices) > 1:
            spike_diff = np.diff(spike_indices)
            spike_indices = spike_indices[np.concatenate(([True], spike_diff > 30))]  # 1ms refractory period at 30kHz

        return {
            'spike_count': len(spike_indices),
            'spike_rate': float(len(spike_indices) / (len(data) / self.config['sampling_rate'])),
            'spike_times': spike_indices.tolist()
        }

    def extract_features(self, data: np.ndarray) -> Dict[str, Any]:
        """Extract spike-specific features."""
        features: Dict[str, Any] = super().extract_features(data)

        # Add spike detection results
        spike_info = self.detect_spikes(data)
        features.update(spike_info)

        return features


# Override to use SpikeProcessor
def process_neural_stream(cloud_event: Any) -> None:
    """Cloud Function entry point for processing spike data streams."""
    import base64
    import json
    from google.cloud import error_reporting

    error_client = error_reporting.Client()

    message = cloud_event.data["message"]
    message_data = base64.b64decode(message["data"]).decode()

    try:
        data = json.loads(message_data)
        processor = SpikeProcessor()
        result = processor.process(data)
        logger.info(f"Spike processing result: {result}")

    except Exception as e:
        logger.error(f"Fatal error in spike cloud function: {str(e)}")
        error_client.report_exception()
        raise
