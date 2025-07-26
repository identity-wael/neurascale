"""Dataset conversion utilities for neural data."""

import logging
from pathlib import Path
from typing import Dict, List, Any
import numpy as np
import pandas as pd
import mne
import h5py
import scipy.io
from datetime import datetime

from .custom_dataset import CustomDatasetLoader, CustomDatasetConfig, DataFormat

logger = logging.getLogger(__name__)


class DatasetConverter:
    """Convert between different neural data formats."""

    @staticmethod
    def convert(
        input_path: Path,
        output_path: Path,
        input_format: DataFormat,
        output_format: DataFormat,
        **kwargs,
    ) -> None:
        """
        Convert dataset from one format to another.

        Args:
            input_path: Path to input data file
            output_path: Path to output data file
            input_format: Input data format
            output_format: Output data format
            **kwargs: Additional configuration options
        """
        logger.info(f"Converting {input_format.value} to {output_format.value}")

        # Load data using custom loader
        config = CustomDatasetConfig(
            name="conversion_temp",
            data_format=input_format,
            data_path=input_path,
            **kwargs,
        )

        loader = CustomDatasetLoader(config)
        data, labels = loader.load()
        metadata = loader.get_metadata()

        # Convert to output format
        converter_method = getattr(
            DatasetConverter, f"_save_{output_format.value}", None
        )

        if converter_method is None:
            raise ValueError(f"Unsupported output format: {output_format}")

        converter_method(
            data=data,
            labels=labels,
            metadata=metadata,
            output_path=output_path,
            channel_names=loader._channel_names,
            sampling_rate=loader._original_sampling_rate or config.sampling_rate,
            **kwargs,
        )

        logger.info(f"Conversion complete: {output_path}")

    @staticmethod
    def _save_csv(
        data: np.ndarray,
        labels: np.ndarray,
        output_path: Path,
        channel_names: List[str],
        sampling_rate: float,
        **kwargs,
    ) -> None:
        """Save data to CSV format."""
        # Flatten epoched data if necessary
        if data.ndim == 3:
            # Concatenate epochs
            n_epochs, n_samples, n_channels = data.shape
            data = data.reshape(-1, n_channels)

            # Repeat labels for each sample in epoch
            labels = np.repeat(labels, n_samples)

        # Create DataFrame
        df_data = pd.DataFrame(data, columns=channel_names)

        # Add time column
        time = np.arange(len(data)) / sampling_rate
        df_data.insert(0, "time", time)

        # Add labels
        df_data["label"] = labels

        # Save to CSV
        df_data.to_csv(output_path, index=False)

        # Save metadata
        metadata_path = output_path.with_suffix(".meta.json")
        metadata = {
            "sampling_rate": sampling_rate,
            "n_channels": len(channel_names),
            "channel_names": channel_names,
            "n_samples": len(data),
            "conversion_date": datetime.now().isoformat(),
        }

        import json

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

    @staticmethod
    def _save_hdf5(
        data: np.ndarray,
        labels: np.ndarray,
        metadata: Dict[str, Any],
        output_path: Path,
        channel_names: List[str],
        sampling_rate: float,
        **kwargs,
    ) -> None:
        """Save data to HDF5 format."""
        with h5py.File(output_path, "w") as f:
            # Save data
            f.create_dataset("data", data=data, compression="gzip")

            # Save labels
            f.create_dataset("labels", data=labels, compression="gzip")

            # Save metadata
            metadata_group = f.create_group("metadata")
            metadata_group.attrs["sampling_rate"] = sampling_rate
            metadata_group.attrs["channel_names"] = channel_names
            metadata_group.attrs["n_channels"] = len(channel_names)
            metadata_group.attrs["conversion_date"] = datetime.now().isoformat()

            # Add original metadata
            for key, value in metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    metadata_group.attrs[key] = value
                elif isinstance(value, (list, tuple)) and len(value) > 0:
                    if isinstance(value[0], str):
                        metadata_group.attrs[key] = value

            # Add data shape info
            if data.ndim == 2:
                metadata_group.attrs["data_type"] = "continuous"
                metadata_group.attrs["n_samples"] = data.shape[0]
            else:
                metadata_group.attrs["data_type"] = "epoched"
                metadata_group.attrs["n_epochs"] = data.shape[0]
                metadata_group.attrs["n_samples_per_epoch"] = data.shape[1]

    @staticmethod
    def _save_mat(
        data: np.ndarray,
        labels: np.ndarray,
        metadata: Dict[str, Any],
        output_path: Path,
        channel_names: List[str],
        sampling_rate: float,
        **kwargs,
    ) -> None:
        """Save data to MATLAB format."""
        # Prepare data for MATLAB
        mat_data = {
            "data": data,
            "labels": labels,
            "fs": sampling_rate,
            "channel_names": channel_names,
        }

        # Add metadata
        mat_data["metadata"] = {
            "sampling_rate": sampling_rate,
            "n_channels": len(channel_names),
            "conversion_date": datetime.now().isoformat(),
        }

        # Add channel locations for EEGLAB compatibility
        if channel_names:
            chanlocs = []
            for i, name in enumerate(channel_names):
                chanlocs.append(
                    {
                        "labels": name,
                        "theta": 0,
                        "radius": 0,
                        "X": 0,
                        "Y": 0,
                        "Z": 0,
                    }
                )
            mat_data["chanlocs"] = np.array(chanlocs, dtype=object)

        # Save to MAT file
        scipy.io.savemat(output_path, mat_data)

    @staticmethod
    def _save_npy(
        data: np.ndarray,
        labels: np.ndarray,
        metadata: Dict[str, Any],
        output_path: Path,
        **kwargs,
    ) -> None:
        """Save data to NumPy format."""
        # Save data
        np.save(output_path, data)

        # Save labels
        labels_path = output_path.with_suffix(".labels.npy")
        np.save(labels_path, labels)

        # Save metadata
        metadata_path = output_path.with_suffix(".meta.json")
        import json

        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

    @staticmethod
    def _save_edf(
        data: np.ndarray,
        labels: np.ndarray,
        output_path: Path,
        channel_names: List[str],
        sampling_rate: float,
        **kwargs,
    ) -> None:
        """Save data to EDF format using MNE."""
        # Convert to MNE format first
        if data.ndim == 3:
            # Concatenate epochs for continuous representation
            n_epochs, n_samples, n_channels = data.shape
            data = data.reshape(-1, n_channels).T
        else:
            data = data.T  # MNE expects (channels, samples)

        # Create MNE info
        info = mne.create_info(
            ch_names=channel_names, sfreq=sampling_rate, ch_types="eeg"
        )

        # Create Raw object
        raw = mne.io.RawArray(data, info)

        # Add annotations for labels if they change
        if labels is not None and len(np.unique(labels)) > 1:
            label_changes = np.where(np.diff(labels, prepend=labels[0]))[0]

            onsets = []
            durations = []
            descriptions = []

            for i in range(len(label_changes)):
                onset = label_changes[i] / sampling_rate
                if i < len(label_changes) - 1:
                    duration = (label_changes[i + 1] - label_changes[i]) / sampling_rate
                else:
                    duration = (len(labels) - label_changes[i]) / sampling_rate

                description = str(labels[label_changes[i]])

                onsets.append(onset)
                durations.append(duration)
                descriptions.append(description)

            annotations = mne.Annotations(onsets, durations, descriptions)
            raw.set_annotations(annotations)

        # Export to EDF
        mne.export.export_raw(str(output_path), raw, fmt="edf", overwrite=True)

    @staticmethod
    def _save_fif(
        data: np.ndarray,
        labels: np.ndarray,
        output_path: Path,
        channel_names: List[str],
        sampling_rate: float,
        **kwargs,
    ) -> None:
        """Save data to FIF format using MNE."""
        # Similar to EDF but with FIF format
        if data.ndim == 3:
            n_epochs, n_samples, n_channels = data.shape
            data = data.reshape(-1, n_channels).T
        else:
            data = data.T

        # Create MNE info
        info = mne.create_info(
            ch_names=channel_names, sfreq=sampling_rate, ch_types="eeg"
        )

        # Create Raw object
        raw = mne.io.RawArray(data, info)

        # Add events for labels
        if labels is not None:
            # Create events array
            events = []
            for i, label in enumerate(labels):
                if i == 0 or label != labels[i - 1]:
                    events.append([i, 0, int(label)])

            if events:
                events = np.array(events)
                # Add events as annotations
                annotations = mne.annotations_from_events(
                    events,
                    sfreq=sampling_rate,
                    event_desc={int(label): str(label) for label in np.unique(labels)},
                )
                raw.set_annotations(annotations)

        # Save to FIF
        raw.save(output_path, overwrite=True)

    @staticmethod
    def batch_convert(
        input_dir: Path,
        output_dir: Path,
        input_format: DataFormat,
        output_format: DataFormat,
        pattern: str = "*",
        **kwargs,
    ) -> None:
        """
        Convert multiple files in a directory.

        Args:
            input_dir: Input directory
            output_dir: Output directory
            input_format: Input format
            output_format: Output format
            pattern: File pattern to match
            **kwargs: Additional options
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Find all matching files
        if input_format == DataFormat.BRAINVISION:
            files = list(input_dir.glob(f"{pattern}.vhdr"))
        else:
            files = list(input_dir.glob(f"{pattern}.{input_format.value}"))

        logger.info(f"Found {len(files)} files to convert")

        # Convert each file
        for i, input_file in enumerate(files):
            logger.info(f"Converting {i + 1}/{len(files)}: {input_file.name}")

            # Generate output filename
            output_name = input_file.stem + f".{output_format.value}"
            output_path = output_dir / output_name

            try:
                DatasetConverter.convert(
                    input_file, output_path, input_format, output_format, **kwargs
                )
            except Exception as e:
                logger.error(f"Failed to convert {input_file}: {e}")
                continue

    @staticmethod
    def validate_conversion(
        original_path: Path,
        converted_path: Path,
        original_format: DataFormat,
        converted_format: DataFormat,
        tolerance: float = 1e-5,
    ) -> bool:
        """
        Validate that conversion preserved data integrity.

        Args:
            original_path: Path to original file
            converted_path: Path to converted file
            original_format: Original format
            converted_format: Converted format
            tolerance: Numerical tolerance for comparison

        Returns:
            True if data matches within tolerance
        """
        # Load original
        config1 = CustomDatasetConfig(
            name="validation_original",
            data_format=original_format,
            data_path=original_path,
        )
        loader1 = CustomDatasetLoader(config1)
        data1, labels1 = loader1.load()

        # Load converted
        config2 = CustomDatasetConfig(
            name="validation_converted",
            data_format=converted_format,
            data_path=converted_path,
        )
        loader2 = CustomDatasetLoader(config2)
        data2, labels2 = loader2.load()

        # Compare shapes
        if data1.shape != data2.shape:
            logger.error(f"Shape mismatch: {data1.shape} vs {data2.shape}")
            return False

        # Compare data
        max_diff = np.max(np.abs(data1 - data2))
        if max_diff > tolerance:
            logger.error(f"Data mismatch: max difference = {max_diff}")
            return False

        # Compare labels
        if not np.array_equal(labels1, labels2):
            logger.error("Label mismatch")
            return False

        logger.info("Conversion validation passed")
        return True
