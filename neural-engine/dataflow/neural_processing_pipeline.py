"""Neural data processing pipeline using Apache Beam for real-time feature extraction."""

import logging
from typing import Dict, List, Any, Iterator
from datetime import datetime
import json

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.transforms import window
from apache_beam.transforms.trigger import AfterWatermark, AfterProcessingTime
from apache_beam.transforms.trigger import AccumulationMode
from apache_beam.io.gcp.bigquery import WriteToBigQuery
from apache_beam.io.gcp.pubsub import ReadFromPubSub
import numpy as np
from scipy import signal as scipy_signal
from scipy.stats import skew, kurtosis
import scipy.fft

logger = logging.getLogger(__name__)


class NeuralSignalQualityCheck(beam.DoFn):
    """Check neural signal quality and filter artifacts."""

    def __init__(self, artifact_threshold: float = 100.0):
        self.artifact_threshold = artifact_threshold

    def process(self, element: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        try:
            data = np.array(element['data'])

            # Check for flat lines
            if np.std(data) < 0.1:
                element['quality_score'] = 0.0
                element['artifact_detected'] = True
                element['artifact_type'] = 'flat_line'
                return

            # Check for amplitude artifacts
            if np.max(np.abs(data)) > self.artifact_threshold:
                element['quality_score'] = 0.3
                element['artifact_detected'] = True
                element['artifact_type'] = 'amplitude_artifact'
                return

            # Check for clipping
            max_val = np.max(data)
            min_val = np.min(data)
            if np.sum(data == max_val) > len(data) * 0.01 or np.sum(data == min_val) > len(data) * 0.01:
                element['quality_score'] = 0.5
                element['artifact_detected'] = True
                element['artifact_type'] = 'clipping'
                return

            element['quality_score'] = 1.0
            element['artifact_detected'] = False
            element['artifact_type'] = None

            yield element

        except Exception as e:
            logger.error(f"Error in quality check: {str(e)}")
            yield element


class ExtractBandPowers(beam.DoFn):
    """Extract band power features from neural signals."""

    def __init__(self, sampling_rate: float = 250.0):
        self.sampling_rate = sampling_rate
        self.bands = {
            'delta': (0.5, 4),
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 100)
        }

    def process(self, element: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        try:
            data = np.array(element['data'])

            # Compute power spectral density
            freqs, psd = scipy_signal.welch(data, self.sampling_rate, nperseg=min(256, len(data)))

            band_powers = {}
            total_power = np.trapz(psd, freqs)

            for band_name, (low_freq, high_freq) in self.bands.items():
                idx_band = np.logical_and(freqs >= low_freq, freqs < high_freq)
                band_power = np.trapz(psd[idx_band], freqs[idx_band])
                band_powers[f'{band_name}_power'] = float(band_power)
                band_powers[f'{band_name}_relative_power'] = float(band_power / total_power) if total_power > 0 else 0.0

            element['band_powers'] = band_powers
            element['total_power'] = float(total_power)

            yield element

        except Exception as e:
            logger.error(f"Error extracting band powers: {str(e)}")
            yield element


class ExtractStatisticalFeatures(beam.DoFn):
    """Extract statistical features from neural signals."""

    def process(self, element: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        try:
            data = np.array(element['data'])

            stats = {
                'mean': float(np.mean(data)),
                'variance': float(np.var(data)),
                'std': float(np.std(data)),
                'skewness': float(skew(data)),
                'kurtosis': float(kurtosis(data)),
                'rms': float(np.sqrt(np.mean(data**2))),
                'peak_to_peak': float(np.ptp(data)),
                'zero_crossing_rate': float(np.sum(np.diff(np.sign(data)) != 0) / len(data))
            }

            element['statistical_features'] = stats

            yield element

        except Exception as e:
            logger.error(f"Error extracting statistical features: {str(e)}")
            yield element


class ExtractSpectralFeatures(beam.DoFn):
    """Extract spectral features including coherence and phase."""

    def __init__(self, sampling_rate: float = 250.0):
        self.sampling_rate = sampling_rate

    def process(self, element: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        try:
            data = np.array(element['data'])

            # FFT for spectral analysis
            fft_vals = scipy.fft.fft(data)
            fft_freq = scipy.fft.fftfreq(len(data), 1 / self.sampling_rate)

            # Get positive frequencies only
            pos_mask = fft_freq > 0
            fft_vals_pos = fft_vals[pos_mask]
            fft_freq_pos = fft_freq[pos_mask]

            # Spectral features
            power_spectrum = np.abs(fft_vals_pos)**2

            # Spectral centroid
            spectral_centroid = float(np.sum(fft_freq_pos * power_spectrum) / np.sum(power_spectrum))

            # Spectral edge frequency (95% of power)
            cumsum_power = np.cumsum(power_spectrum)
            total_power = cumsum_power[-1]
            edge_idx = np.where(cumsum_power >= 0.95 * total_power)[0][0]
            spectral_edge = float(fft_freq_pos[edge_idx])

            # Peak frequency
            peak_idx = np.argmax(power_spectrum)
            peak_frequency = float(fft_freq_pos[peak_idx])

            spectral_features = {
                'spectral_centroid': spectral_centroid,
                'spectral_edge_95': spectral_edge,
                'peak_frequency': peak_frequency,
                'spectral_entropy': float(-np.sum(power_spectrum * np.log2(power_spectrum + 1e-10)) / np.log2(len(power_spectrum)))
            }

            element['spectral_features'] = spectral_features

            yield element

        except Exception as e:
            logger.error(f"Error extracting spectral features: {str(e)}")
            yield element


class ExtractTemporalFeatures(beam.DoFn):
    """Extract temporal features including autocorrelation and entropy."""

    def process(self, element: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        try:
            data = np.array(element['data'])

            # Autocorrelation at different lags
            autocorr_lags = [1, 5, 10, 20]
            autocorr_features = {}

            for lag in autocorr_lags:
                if lag < len(data):
                    autocorr = np.corrcoef(data[:-lag], data[lag:])[0, 1]
                    autocorr_features[f'autocorr_lag_{lag}'] = float(autocorr) if not np.isnan(autocorr) else 0.0

            # Sample entropy
            def sample_entropy(data: np.ndarray, m: int = 2, r: float = 0.2) -> float:
                N = len(data)
                r = r * np.std(data)

                def _maxdist(xi: np.ndarray, xj: np.ndarray, m: int) -> float:
                    return float(max([abs(ua - va) for ua, va in zip(xi[0:m], xj[0:m])]))

                def _phi(m: int) -> float:
                    patterns = np.array([data[i:i + m] for i in range(N - m + 1)])
                    C = 0
                    for i in range(N - m + 1):
                        matches = sum([1 for j in range(N - m + 1) if i != j and _maxdist(patterns[i], patterns[j], m) <= r])
                        C += matches
                    return C / (N - m + 1) / (N - m)

                return -np.log(_phi(m + 1) / _phi(m)) if _phi(m) > 0 else 0

            temporal_features = {
                **autocorr_features,
                'sample_entropy': float(sample_entropy(data[:min(len(data), 100)]))  # Limit for performance
            }

            element['temporal_features'] = temporal_features

            yield element

        except Exception as e:
            logger.error(f"Error extracting temporal features: {str(e)}")
            yield element


class FormatForBigQuery(beam.DoFn):
    """Format processed data for BigQuery insertion."""

    def process(self, element: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        try:
            # Flatten nested dictionaries
            flattened = {
                'session_id': element.get('session_id', ''),
                'device_id': element.get('device_id', ''),
                'timestamp': element.get('timestamp', datetime.utcnow().isoformat()),
                'channel': element.get('channel', 0),
                'quality_score': element.get('quality_score', 0.0),
                'artifact_detected': element.get('artifact_detected', False),
                'artifact_type': element.get('artifact_type', None),
                'total_power': element.get('total_power', 0.0)
            }

            # Add band powers
            if 'band_powers' in element:
                flattened.update(element['band_powers'])

            # Add statistical features
            if 'statistical_features' in element:
                for key, value in element['statistical_features'].items():
                    flattened[f'stat_{key}'] = value

            # Add spectral features
            if 'spectral_features' in element:
                for key, value in element['spectral_features'].items():
                    flattened[f'spec_{key}'] = value

            # Add temporal features
            if 'temporal_features' in element:
                for key, value in element['temporal_features'].items():
                    flattened[f'temp_{key}'] = value

            yield flattened

        except Exception as e:
            logger.error(f"Error formatting for BigQuery: {str(e)}")
            yield {}


class NeuralProcessingPipeline:
    """Main neural data processing pipeline."""

    def __init__(self, project_id: str, region: str):
        self.project_id = project_id
        self.region = region
        self.dataset_id = 'neural_analytics'
        self.table_id = 'processed_signals'

    def get_pipeline_options(self, streaming: bool = True) -> PipelineOptions:
        """Get pipeline options for Dataflow."""
        options = PipelineOptions(
            project=self.project_id,
            region=self.region,
            job_name='neural-processing-pipeline',
            temp_location=f'gs://{self.project_id}-temp/dataflow',
            staging_location=f'gs://{self.project_id}-staging/dataflow',
            runner='DataflowRunner' if streaming else 'DirectRunner',
            streaming=streaming,
            save_main_session=True,
            setup_file='./setup.py'
        )

        return options

    def get_table_schema(self) -> Dict[str, List[Dict[str, str]]]:
        """Get BigQuery table schema."""
        return {
            'fields': [
                {'name': 'session_id', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'device_id', 'type': 'STRING', 'mode': 'REQUIRED'},
                {'name': 'timestamp', 'type': 'TIMESTAMP', 'mode': 'REQUIRED'},
                {'name': 'channel', 'type': 'INTEGER', 'mode': 'REQUIRED'},
                {'name': 'quality_score', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'artifact_detected', 'type': 'BOOLEAN', 'mode': 'NULLABLE'},
                {'name': 'artifact_type', 'type': 'STRING', 'mode': 'NULLABLE'},
                {'name': 'total_power', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                # Band powers
                {'name': 'delta_power', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'delta_relative_power', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'theta_power', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'theta_relative_power', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'alpha_power', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'alpha_relative_power', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'beta_power', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'beta_relative_power', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'gamma_power', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'gamma_relative_power', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                # Statistical features
                {'name': 'stat_mean', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'stat_variance', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'stat_std', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'stat_skewness', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'stat_kurtosis', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'stat_rms', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'stat_peak_to_peak', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'stat_zero_crossing_rate', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                # Spectral features
                {'name': 'spec_spectral_centroid', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'spec_spectral_edge_95', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'spec_peak_frequency', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'spec_spectral_entropy', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                # Temporal features
                {'name': 'temp_autocorr_lag_1', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'temp_autocorr_lag_5', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'temp_autocorr_lag_10', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'temp_autocorr_lag_20', 'type': 'FLOAT', 'mode': 'NULLABLE'},
                {'name': 'temp_sample_entropy', 'type': 'FLOAT', 'mode': 'NULLABLE'},
            ]
        }

    def run(self, pubsub_topic: str, streaming: bool = True) -> None:
        """Run the neural processing pipeline."""
        options = self.get_pipeline_options(streaming)

        with beam.Pipeline(options=options) as pipeline:
            # Read from Pub/Sub
            neural_data = (
                pipeline
                | 'ReadFromPubSub' >> ReadFromPubSub(topic=pubsub_topic)
                | 'ParseJSON' >> beam.Map(lambda x: json.loads(x.decode('utf-8')))
            )

            # Apply windowing for streaming (50ms windows for real-time processing)
            if streaming:
                neural_data = (
                    neural_data
                    | 'AddTimestamp' >> beam.Map(lambda x: beam.window.TimestampedValue(x, x.get('timestamp', datetime.utcnow().timestamp())))
                    | 'Window' >> beam.WindowInto(
                        window.FixedWindows(0.05),  # 50ms windows
                        trigger=AfterWatermark(early=AfterProcessingTime(0.01)),  # 10ms early firing
                        accumulation_mode=AccumulationMode.DISCARDING
                    )
                )

            # Process neural data
            processed_data = (
                neural_data
                | 'QualityCheck' >> beam.ParDo(NeuralSignalQualityCheck())
                | 'ExtractBandPowers' >> beam.ParDo(ExtractBandPowers())
                | 'ExtractStatisticalFeatures' >> beam.ParDo(ExtractStatisticalFeatures())
                | 'ExtractSpectralFeatures' >> beam.ParDo(ExtractSpectralFeatures())
                | 'ExtractTemporalFeatures' >> beam.ParDo(ExtractTemporalFeatures())
                | 'FormatForBigQuery' >> beam.ParDo(FormatForBigQuery())
            )

            # Write to BigQuery
            processed_data | 'WriteToBigQuery' >> WriteToBigQuery(
                table=f'{self.project_id}:{self.dataset_id}.{self.table_id}',
                schema=self.get_table_schema(),
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
            )

            # Also write quality metrics to a separate topic for monitoring
            quality_metrics = (
                processed_data
                | 'FilterQualityMetrics' >> beam.Map(lambda x: {
                    'timestamp': x['timestamp'],
                    'device_id': x['device_id'],
                    'quality_score': x['quality_score'],
                    'artifact_detected': x['artifact_detected']
                })
                | 'SerializeMetrics' >> beam.Map(lambda x: json.dumps(x).encode('utf-8'))
            )

            # Note: Add WriteToPubSub for quality metrics if needed


def main() -> None:
    """Main entry point for the pipeline."""
    import argparse

    parser = argparse.ArgumentParser(description='Neural Processing Pipeline')
    parser.add_argument('--project-id', required=True, help='GCP Project ID')
    parser.add_argument('--region', default='us-central1', help='GCP Region')
    parser.add_argument('--pubsub-topic', required=True, help='Pub/Sub topic for neural data')
    parser.add_argument('--streaming', action='store_true', help='Run in streaming mode')

    args = parser.parse_args()

    pipeline = NeuralProcessingPipeline(args.project_id, args.region)
    pipeline.run(args.pubsub_topic, args.streaming)


if __name__ == '__main__':
    main()
