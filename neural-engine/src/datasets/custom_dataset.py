"""Custom dataset loader supporting multiple formats for neural data."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
import numpy as np
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import mne
import h5py
import scipy.io

from .base_dataset import BaseDataset, DatasetConfig

logger = logging.getLogger(__name__)


class DataFormat(Enum):
    """Supported data formats."""

    CSV = "csv"
    EDF = "edf"
    FIF = "fif"
    HDF5 = "hdf5"
    MAT = "mat"
    BRAINVISION = "vhdr"
    NPY = "npy"
    CUSTOM = "custom"


@dataclass
class CustomDatasetConfig(DatasetConfig):
    """Configuration for custom dataset loading."""

    data_format: DataFormat = DataFormat.CSV
    data_path: Optional[Path] = None
    labels_path: Optional[Path] = None

    # Data structure configuration
    channel_names: Optional[List[str]] = None
    sampling_rate: float = 250.0

    # CSV-specific options
    csv_delimiter: str = ","
    csv_header: bool = True
    csv_time_column: Optional[str] = None
    csv_label_column: Optional[str] = None
    csv_channel_columns: Optional[List[str]] = None

    # HDF5/MAT-specific options
    data_key: str = "data"
    labels_key: str = "labels"
    metadata_key: str = "metadata"

    # Preprocessing options
    filter_low: Optional[float] = None
    filter_high: Optional[float] = None
    notch_freq: Optional[float] = None
    reference: Optional[str] = None  # 'average', 'cz', None

    # Epoching options
    epoch_length: Optional[float] = None  # seconds
    epoch_overlap: float = 0.0  # fraction

    # Custom loader function
    custom_loader: Optional[Callable] = None


class CustomDatasetLoader(BaseDataset):
    """Flexible dataset loader supporting multiple formats."""

    def __init__(self, config: CustomDatasetConfig):
        """Initialize custom dataset loader."""
        super().__init__(config)
        self.config: CustomDatasetConfig = config

        # Validate configuration
        self._validate_config()

        # Format-specific loaders
        self._loaders = {
            DataFormat.CSV: self._load_csv,
            DataFormat.EDF: self._load_edf,
            DataFormat.FIF: self._load_fif,
            DataFormat.HDF5: self._load_hdf5,
            DataFormat.MAT: self._load_mat,
            DataFormat.BRAINVISION: self._load_brainvision,
            DataFormat.NPY: self._load_npy,
            DataFormat.CUSTOM: self._load_custom,
        }

        self._channel_names: List[str] = []
        self._original_sampling_rate: float = 0.0

    def _validate_config(self) -> None:
        """Validate dataset configuration."""
        if (
            self.config.data_path is None
            and self.config.data_format != DataFormat.CUSTOM
        ):
            raise ValueError("data_path must be specified for non-custom formats")

        if (
            self.config.data_format == DataFormat.CUSTOM
            and self.config.custom_loader is None
        ):
            raise ValueError("custom_loader must be provided for CUSTOM format")

        if self.config.data_path and not Path(self.config.data_path).exists():
            raise FileNotFoundError(f"Data path not found: {self.config.data_path}")

    def download(self) -> None:
        """Custom datasets don't support automatic downloading."""
        logger.info("Custom datasets must be provided locally")

    def load(self) -> Tuple[np.ndarray, np.ndarray]:
        """Load dataset using appropriate loader."""
        # Check cache first
        if self.cache_exists():
            logger.info("Loading from cache...")
            return self.load_cache()[:2]

        logger.info(
            f"Loading {self.config.data_format.value} dataset from {self.config.data_path}"
        )

        # Load data using format-specific loader
        loader = self._loaders.get(self.config.data_format)
        if loader is None:
            raise ValueError(f"Unsupported format: {self.config.data_format}")

        data, labels = loader()

        # Apply preprocessing if configured
        data = self.preprocess(data)

        # Validate data
        if not self.validate(data):
            logger.warning("Data validation failed, but continuing...")

        # Save to cache
        self.save_cache(data, labels, self._metadata)

        return data, labels

    def _load_csv(self) -> Tuple[np.ndarray, np.ndarray]:
        """Load data from CSV file(s)."""
        # Load data file
        df = pd.read_csv(
            self.config.data_path,
            delimiter=self.config.csv_delimiter,
            header=0 if self.config.csv_header else None,
        )

        # Extract channel data
        if self.config.csv_channel_columns:
            channel_data = df[self.config.csv_channel_columns].values
            self._channel_names = self.config.csv_channel_columns
        else:
            # Assume all numeric columns except time and label are channels
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if self.config.csv_time_column in numeric_cols:
                numeric_cols.remove(self.config.csv_time_column)
            if self.config.csv_label_column in numeric_cols:
                numeric_cols.remove(self.config.csv_label_column)

            channel_data = df[numeric_cols].values
            self._channel_names = numeric_cols

        # Extract labels
        if self.config.csv_label_column and self.config.csv_label_column in df.columns:
            labels = df[self.config.csv_label_column].values
        elif self.config.labels_path:
            # Load labels from separate file
            labels_df = pd.read_csv(self.config.labels_path)
            labels = labels_df.iloc[:, 0].values
        else:
            # No labels provided
            labels = np.zeros(len(channel_data))

        # Convert to standard format (samples, channels)
        data = channel_data.astype(np.float32)

        # If epoching is configured, apply it
        if self.config.epoch_length:
            data, labels = self._epoch_continuous_data(data, labels)

        # Store metadata
        self._metadata = {
            "format": "csv",
            "n_samples": data.shape[0],
            "n_channels": data.shape[1] if len(data.shape) == 2 else data.shape[2],
            "sampling_rate": self.config.sampling_rate,
            "channel_names": self._channel_names,
        }

        return data, labels

    def _load_edf(self) -> Tuple[np.ndarray, np.ndarray]:
        """Load data from EDF file."""
        # Load EDF file using MNE
        raw = mne.io.read_raw_edf(
            str(self.config.data_path), preload=True, verbose=False
        )

        # Store channel info
        self._channel_names = raw.ch_names
        self._original_sampling_rate = raw.info["sfreq"]

        # Get data
        data = raw.get_data().T  # (samples, channels)

        # Load or create labels
        if self.config.labels_path:
            labels = np.load(self.config.labels_path)
        else:
            # Check for annotations in EDF
            if raw.annotations:
                # Convert annotations to labels
                labels = self._annotations_to_labels(raw, data.shape[0])
            else:
                labels = np.zeros(data.shape[0])

        # Apply epoching if configured
        if self.config.epoch_length:
            data, labels = self._epoch_continuous_data(data, labels)

        # Store metadata
        self._metadata = {
            "format": "edf",
            "n_samples": data.shape[0],
            "n_channels": data.shape[1] if len(data.shape) == 2 else data.shape[2],
            "sampling_rate": self._original_sampling_rate,
            "channel_names": self._channel_names,
            "info": {k: v for k, v in raw.info.items() if k != "chs"},
        }

        return data.astype(np.float32), labels

    def _load_fif(self) -> Tuple[np.ndarray, np.ndarray]:
        """Load data from FIF file."""
        # Load FIF file using MNE
        raw = mne.io.read_raw_fif(
            str(self.config.data_path), preload=True, verbose=False
        )

        # Store channel info
        self._channel_names = raw.ch_names
        self._original_sampling_rate = raw.info["sfreq"]

        # Get data
        data = raw.get_data().T  # (samples, channels)

        # Load or create labels
        if self.config.labels_path:
            labels = np.load(self.config.labels_path)
        else:
            # Check for events in FIF
            events = mne.find_events(raw, stim_channel=None, verbose=False)
            if len(events) > 0:
                labels = self._events_to_labels(events, data.shape[0])
            else:
                labels = np.zeros(data.shape[0])

        # Apply epoching if configured
        if self.config.epoch_length:
            data, labels = self._epoch_continuous_data(data, labels)

        # Store metadata
        self._metadata = {
            "format": "fif",
            "n_samples": data.shape[0],
            "n_channels": data.shape[1] if len(data.shape) == 2 else data.shape[2],
            "sampling_rate": self._original_sampling_rate,
            "channel_names": self._channel_names,
            "info": {k: v for k, v in raw.info.items() if k != "chs"},
        }

        return data.astype(np.float32), labels

    def _load_hdf5(self) -> Tuple[np.ndarray, np.ndarray]:
        """Load data from HDF5 file."""
        with h5py.File(self.config.data_path, "r") as f:
            # Load data
            if self.config.data_key not in f:
                raise KeyError(
                    f"Data key '{self.config.data_key}' not found in HDF5 file"
                )

            data = f[self.config.data_key][:]

            # Load labels
            if self.config.labels_key in f:
                labels = f[self.config.labels_key][:]
            elif self.config.labels_path:
                labels = np.load(self.config.labels_path)
            else:
                labels = np.zeros(data.shape[0])

            # Load metadata if available
            if self.config.metadata_key in f:
                metadata = dict(f[self.config.metadata_key].attrs)
                self._channel_names = metadata.get("channel_names", [])
                self._original_sampling_rate = metadata.get(
                    "sampling_rate", self.config.sampling_rate
                )
            else:
                self._channel_names = [f"ch_{i}" for i in range(data.shape[-1])]
                self._original_sampling_rate = self.config.sampling_rate

        # Ensure correct shape (samples, channels) or (epochs, samples, channels)
        if data.ndim == 2 and data.shape[0] < data.shape[1]:
            # Likely (channels, samples), transpose
            data = data.T

        # Apply epoching if configured and data is continuous
        if self.config.epoch_length and data.ndim == 2:
            data, labels = self._epoch_continuous_data(data, labels)

        # Store metadata
        self._metadata = {
            "format": "hdf5",
            "n_samples": data.shape[0],
            "n_channels": data.shape[-1],
            "sampling_rate": self._original_sampling_rate,
            "channel_names": self._channel_names,
        }

        return data.astype(np.float32), labels

    def _load_mat(self) -> Tuple[np.ndarray, np.ndarray]:  # noqa: C901
        """Load data from MATLAB file."""
        mat_data = scipy.io.loadmat(str(self.config.data_path))

        # Find data array
        data = None
        for key in [self.config.data_key, "data", "EEG", "signal"]:
            if key in mat_data:
                data = mat_data[key]
                break

        if data is None:
            # Try to find the largest array
            arrays = [
                (k, v)
                for k, v in mat_data.items()
                if isinstance(v, np.ndarray) and v.ndim >= 2 and not k.startswith("__")
            ]
            if arrays:
                key, data = max(arrays, key=lambda x: x[1].size)
                logger.info(f"Using array '{key}' as data")
            else:
                raise ValueError("No suitable data array found in MAT file")

        # Find labels
        labels = None
        for key in [self.config.labels_key, "labels", "y", "targets"]:
            if key in mat_data:
                labels = mat_data[key].squeeze()
                break

        if labels is None:
            if self.config.labels_path:
                labels = np.load(self.config.labels_path)
            else:
                labels = np.zeros(data.shape[0])

        # Extract metadata
        if "fs" in mat_data:
            self._original_sampling_rate = float(mat_data["fs"].squeeze())
        elif "srate" in mat_data:
            self._original_sampling_rate = float(mat_data["srate"].squeeze())
        else:
            self._original_sampling_rate = self.config.sampling_rate

        if "chanlocs" in mat_data:
            # Extract channel names from EEGLAB structure
            chanlocs = mat_data["chanlocs"]
            self._channel_names = [ch[0] for ch in chanlocs["labels"][0]]
        else:
            self._channel_names = [f"ch_{i}" for i in range(data.shape[-1])]

        # Ensure correct shape
        if data.ndim == 2 and data.shape[0] < data.shape[1]:
            data = data.T

        # Apply epoching if configured
        if self.config.epoch_length and data.ndim == 2:
            data, labels = self._epoch_continuous_data(data, labels)

        # Store metadata
        self._metadata = {
            "format": "mat",
            "n_samples": data.shape[0],
            "n_channels": data.shape[-1],
            "sampling_rate": self._original_sampling_rate,
            "channel_names": self._channel_names,
        }

        return data.astype(np.float32), labels

    def _load_brainvision(self) -> Tuple[np.ndarray, np.ndarray]:
        """Load data from BrainVision format."""
        # Load BrainVision file using MNE
        raw = mne.io.read_raw_brainvision(
            str(self.config.data_path), preload=True, verbose=False
        )

        # Store channel info
        self._channel_names = raw.ch_names
        self._original_sampling_rate = raw.info["sfreq"]

        # Get data
        data = raw.get_data().T  # (samples, channels)

        # Load or create labels
        if self.config.labels_path:
            labels = np.load(self.config.labels_path)
        else:
            # Check for markers
            events = mne.events_from_annotations(raw, verbose=False)[0]
            if len(events) > 0:
                labels = self._events_to_labels(events, data.shape[0])
            else:
                labels = np.zeros(data.shape[0])

        # Apply epoching if configured
        if self.config.epoch_length:
            data, labels = self._epoch_continuous_data(data, labels)

        # Store metadata
        self._metadata = {
            "format": "brainvision",
            "n_samples": data.shape[0],
            "n_channels": data.shape[1] if len(data.shape) == 2 else data.shape[2],
            "sampling_rate": self._original_sampling_rate,
            "channel_names": self._channel_names,
        }

        return data.astype(np.float32), labels

    def _load_npy(self) -> Tuple[np.ndarray, np.ndarray]:
        """Load data from NumPy file."""
        if self.config.data_path is None:
            raise ValueError("data_path must be specified for NPY format")
        data = np.load(self.config.data_path)

        # Load labels
        if self.config.labels_path:
            labels = np.load(self.config.labels_path)
        else:
            labels = np.zeros(data.shape[0])

        # Set channel names
        if self.config.channel_names:
            self._channel_names = self.config.channel_names
        else:
            self._channel_names = [f"ch_{i}" for i in range(data.shape[-1])]

        self._original_sampling_rate = self.config.sampling_rate

        # Apply epoching if configured
        if self.config.epoch_length and data.ndim == 2:
            data, labels = self._epoch_continuous_data(data, labels)

        # Store metadata
        self._metadata = {
            "format": "npy",
            "n_samples": data.shape[0],
            "n_channels": data.shape[-1],
            "sampling_rate": self._original_sampling_rate,
            "channel_names": self._channel_names,
        }

        return data.astype(np.float32), labels

    def _load_custom(self) -> Tuple[np.ndarray, np.ndarray]:
        """Load data using custom loader function."""
        if self.config.custom_loader is None:
            raise ValueError("Custom loader function not provided")

        # Call custom loader
        result = self.config.custom_loader(self.config)

        if isinstance(result, tuple) and len(result) == 2:
            data, labels = result
        elif isinstance(result, dict):
            data = result["data"]
            labels = result.get("labels", np.zeros(data.shape[0]))

            # Extract metadata if provided
            self._channel_names = result.get("channel_names", [])
            self._original_sampling_rate = result.get(
                "sampling_rate", self.config.sampling_rate
            )

            # Store additional metadata
            self._metadata = result.get("metadata", {})
        else:
            raise ValueError("Custom loader must return (data, labels) tuple or dict")

        # Set defaults if not provided
        if not self._channel_names:
            self._channel_names = [f"ch_{i}" for i in range(data.shape[-1])]

        # Update metadata
        self._metadata.update(
            {
                "format": "custom",
                "n_samples": data.shape[0],
                "n_channels": data.shape[-1],
                "sampling_rate": self._original_sampling_rate
                or self.config.sampling_rate,
                "channel_names": self._channel_names,
            }
        )

        return data.astype(np.float32), labels

    def _epoch_continuous_data(
        self, data: np.ndarray, labels: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Convert continuous data to epochs."""
        sampling_rate = self._original_sampling_rate or self.config.sampling_rate
        if self.config.epoch_length is None:
            raise ValueError("epoch_length must be specified for continuous data")
        epoch_samples = int(self.config.epoch_length * sampling_rate)
        overlap_samples = int(epoch_samples * self.config.epoch_overlap)
        step_samples = epoch_samples - overlap_samples

        n_samples = data.shape[0]
        n_epochs = (n_samples - epoch_samples) // step_samples + 1

        # Create epochs
        epochs = []
        epoch_labels = []

        for i in range(n_epochs):
            start = i * step_samples
            end = start + epoch_samples

            if end > n_samples:
                break

            epoch = data[start:end]
            epochs.append(epoch)

            # Determine epoch label (majority vote)
            epoch_label_segment = labels[start:end]
            if len(np.unique(epoch_label_segment)) == 1:
                epoch_labels.append(epoch_label_segment[0])
            else:
                # Majority vote
                unique, counts = np.unique(epoch_label_segment, return_counts=True)
                epoch_labels.append(unique[np.argmax(counts)])

        # Stack epochs: (n_epochs, n_samples, n_channels)
        epoched_data = np.stack(epochs)
        epoched_labels = np.array(epoch_labels)

        return epoched_data, epoched_labels

    def _annotations_to_labels(self, raw: mne.io.Raw, n_samples: int) -> np.ndarray:
        """Convert MNE annotations to sample-wise labels."""
        labels = np.zeros(n_samples)

        for ann in raw.annotations:
            start_sample = int(ann["onset"] * raw.info["sfreq"])
            duration_samples = int(ann["duration"] * raw.info["sfreq"])
            end_sample = min(start_sample + duration_samples, n_samples)

            # Convert description to numeric label
            try:
                label = int(ann["description"])
            except ValueError:
                # Use hash of description for consistent labeling
                label = hash(ann["description"]) % 100

            labels[start_sample:end_sample] = label

        return labels

    def _events_to_labels(self, events: np.ndarray, n_samples: int) -> np.ndarray:
        """Convert MNE events to sample-wise labels."""
        labels = np.zeros(n_samples)

        for event in events:
            sample_idx = event[0]
            event_id = event[2]

            if sample_idx < n_samples:
                labels[sample_idx] = event_id

        return labels

    def preprocess(self, data: np.ndarray) -> np.ndarray:
        """Apply preprocessing to the data."""
        # Skip if no preprocessing configured
        if not any(
            [
                self.config.filter_low,
                self.config.filter_high,
                self.config.notch_freq,
                self.config.reference,
            ]
        ):
            return data

        logger.info("Applying preprocessing...")

        # Work with a copy
        processed_data = data.copy()

        # Handle different data shapes
        if processed_data.ndim == 2:
            # Continuous data (samples, channels)
            processed_data = self._preprocess_continuous(processed_data)
        elif processed_data.ndim == 3:
            # Epoched data (epochs, samples, channels)
            for i in range(processed_data.shape[0]):
                processed_data[i] = self._preprocess_continuous(processed_data[i])

        return processed_data

    def _preprocess_continuous(self, data: np.ndarray) -> np.ndarray:  # noqa: C901
        """Apply preprocessing to continuous data."""
        from scipy import signal

        sampling_rate = self._original_sampling_rate or self.config.sampling_rate

        # Apply filtering
        if self.config.filter_low or self.config.filter_high:
            nyquist = sampling_rate / 2

            if self.config.filter_low and self.config.filter_high:
                # Bandpass filter
                low = self.config.filter_low / nyquist
                high = self.config.filter_high / nyquist
                b, a = signal.butter(4, [low, high], btype="band")
            elif self.config.filter_low:
                # Highpass filter
                low = self.config.filter_low / nyquist
                b, a = signal.butter(4, low, btype="high")
            else:
                # Lowpass filter
                if self.config.filter_high is None:
                    raise ValueError("filter_high must be specified for lowpass filter")
                high = self.config.filter_high / nyquist
                b, a = signal.butter(4, high, btype="low")

            # Apply filter to each channel
            for ch in range(data.shape[1]):
                data[:, ch] = signal.filtfilt(b, a, data[:, ch])

        # Apply notch filter
        if self.config.notch_freq:
            nyquist = sampling_rate / 2
            notch_freq = self.config.notch_freq / nyquist
            b, a = signal.iirnotch(notch_freq, Q=30)

            for ch in range(data.shape[1]):
                data[:, ch] = signal.filtfilt(b, a, data[:, ch])

        # Apply referencing
        if self.config.reference:
            if self.config.reference.lower() == "average":
                # Common average reference
                avg_ref = np.mean(data, axis=1, keepdims=True)
                data = data - avg_ref
            elif self.config.reference.upper() in self._channel_names:
                # Reference to specific channel
                ref_idx = self._channel_names.index(self.config.reference.upper())
                ref_signal = data[:, ref_idx : ref_idx + 1]
                data = data - ref_signal

        return data

    def validate(self, data: np.ndarray) -> bool:
        """Validate the loaded data."""
        # Basic validation
        if data.size == 0:
            logger.error("Empty dataset")
            return False

        # Check for NaN or Inf values
        if np.any(np.isnan(data)) or np.any(np.isinf(data)):
            logger.warning("Data contains NaN or Inf values")
            return False

        # Check data range
        data_range = np.ptp(data)
        if data_range == 0:
            logger.warning("Data has zero variance")
            return False

        # Check sampling rate if epoched
        if data.ndim == 3 and self.config.epoch_length:
            expected_samples = int(
                self.config.epoch_length
                * (self._original_sampling_rate or self.config.sampling_rate)
            )
            if data.shape[1] != expected_samples:
                logger.warning(
                    f"Epoch length mismatch: expected {expected_samples}, got {data.shape[1]}"
                )

        return True

    def get_channel_info(self) -> Dict[str, Any]:
        """Get channel information."""
        return {
            "channel_names": self._channel_names,
            "n_channels": len(self._channel_names),
            "sampling_rate": self._original_sampling_rate or self.config.sampling_rate,
        }

    def convert_to_mne(
        self, data: np.ndarray, labels: Optional[np.ndarray] = None
    ) -> mne.io.RawArray:
        """Convert data to MNE RawArray format."""
        # Ensure data is in (channels, samples) format
        if data.ndim == 2:
            if data.shape[0] > data.shape[1]:
                data = data.T
        else:
            raise ValueError("Can only convert continuous data to MNE format")

        # Create info
        info = mne.create_info(
            ch_names=self._channel_names or [f"ch_{i}" for i in range(data.shape[0])],
            sfreq=self._original_sampling_rate or self.config.sampling_rate,
            ch_types="eeg",
        )

        # Create RawArray
        raw = mne.io.RawArray(data, info)

        # Add annotations if labels provided
        if labels is not None:
            # Find label changes
            label_changes = np.where(np.diff(labels, prepend=labels[0]))[0]

            onsets = []
            durations = []
            descriptions = []

            for i in range(len(label_changes)):
                onset = label_changes[i] / info["sfreq"]
                if i < len(label_changes) - 1:
                    duration = (label_changes[i + 1] - label_changes[i]) / info["sfreq"]
                else:
                    duration = (len(labels) - label_changes[i]) / info["sfreq"]

                description = str(labels[label_changes[i]])

                onsets.append(onset)
                durations.append(duration)
                descriptions.append(description)

            annotations = mne.Annotations(onsets, durations, descriptions)
            raw.set_annotations(annotations)

        return raw
