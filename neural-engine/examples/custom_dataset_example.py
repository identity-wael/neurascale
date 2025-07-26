#!/usr/bin/env python3
"""
Example usage of custom dataset loader and converter.

This script demonstrates:
1. Loading datasets from various formats
2. Applying preprocessing
3. Converting between formats
4. Custom loader implementation
"""

import logging
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from typing import Dict, Any

from src.datasets import CustomDatasetLoader, CustomDatasetConfig, DataFormat
from src.datasets.dataset_converter import DatasetConverter

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_csv_example():
    """Example of loading CSV data."""
    logger.info("\n=== CSV Dataset Example ===")

    # Create sample CSV data
    sample_dir = Path("output") / "sample_data"
    sample_dir.mkdir(parents=True, exist_ok=True)

    # Generate synthetic EEG data
    n_samples = 10000
    n_channels = 8
    sampling_rate = 250.0

    # Create time array
    time = np.arange(n_samples) / sampling_rate

    # Generate channels with different frequencies
    data = []
    for i in range(n_channels):
        # Base frequency for this channel
        freq = 10 + i * 2  # 10Hz, 12Hz, 14Hz, etc.
        channel = 0.5 * np.sin(2 * np.pi * freq * time)

        # Add some noise
        channel += 0.1 * np.random.randn(n_samples)

        data.append(channel)

    data = np.array(data).T  # (samples, channels)

    # Create labels (alternating between 0 and 1 every 2 seconds)
    labels = (time // 2).astype(int) % 2

    # Save to CSV
    import pandas as pd

    df = pd.DataFrame(data, columns=[f"ch_{i}" for i in range(n_channels)])
    df.insert(0, "time", time)
    df["label"] = labels

    csv_path = sample_dir / "sample_eeg.csv"
    df.to_csv(csv_path, index=False)
    logger.info(f"Created sample CSV: {csv_path}")

    # Load using custom loader
    config = CustomDatasetConfig(
        name="csv_example",
        data_format=DataFormat.CSV,
        data_path=csv_path,
        csv_time_column="time",
        csv_label_column="label",
        csv_channel_columns=[f"ch_{i}" for i in range(n_channels)],
        sampling_rate=sampling_rate,
        # Preprocessing
        filter_low=1.0,
        filter_high=40.0,
        notch_freq=50.0,  # Remove 50Hz noise
        # Epoching
        epoch_length=1.0,  # 1-second epochs
        epoch_overlap=0.5,  # 50% overlap
    )

    loader = CustomDatasetLoader(config)
    data, labels = loader.load()

    logger.info(f"Loaded data shape: {data.shape}")
    logger.info(f"Labels shape: {labels.shape}")
    logger.info(f"Unique labels: {np.unique(labels)}")

    return data, labels, loader


def load_custom_format_example():
    """Example of using a custom loader function."""
    logger.info("\n=== Custom Format Example ===")

    def my_custom_loader(config: CustomDatasetConfig) -> Dict[str, Any]:
        """Custom loader for proprietary format."""
        # In real use, this would load your specific format
        # For demo, we'll generate some data

        n_epochs = 100
        n_channels = 16
        n_samples = 500  # 2 seconds at 250Hz

        # Generate random data
        data = np.random.randn(n_epochs, n_samples, n_channels)

        # Apply some structure (different power in different bands)
        for epoch in range(n_epochs):
            for ch in range(n_channels):
                if ch < 8:
                    # Alpha band emphasis (8-12 Hz)
                    data[epoch, :, ch] *= 2.0
                else:
                    # Beta band emphasis (12-30 Hz)
                    data[epoch, :, ch] *= 0.5

        # Generate labels (binary classification)
        labels = np.random.randint(0, 2, n_epochs)

        # Return dictionary with all information
        return {
            "data": data,
            "labels": labels,
            "channel_names": [f"EEG_{i + 1}" for i in range(n_channels)],
            "sampling_rate": 250.0,
            "metadata": {
                "experiment": "motor_imagery",
                "subject": "S01",
                "session": 1,
                "paradigm": "left_right_hand",
            },
        }

    # Create config with custom loader
    config = CustomDatasetConfig(
        name="custom_format_example",
        data_format=DataFormat.CUSTOM,
        custom_loader=my_custom_loader,
        # Still can apply preprocessing
        filter_low=8.0,
        filter_high=30.0,
    )

    loader = CustomDatasetLoader(config)
    data, labels = loader.load()

    metadata = loader.get_metadata()
    logger.info(f"Loaded custom format: {data.shape}")
    logger.info(f"Metadata: {metadata}")

    return data, labels, loader


def convert_formats_example():
    """Example of converting between formats."""
    logger.info("\n=== Format Conversion Example ===")

    # Create sample data
    sample_dir = Path("output") / "sample_data"
    sample_dir.mkdir(parents=True, exist_ok=True)

    # Generate and save NPY data
    data = np.random.randn(50, 1000, 8)  # 50 epochs, 1000 samples, 8 channels
    labels = np.random.randint(0, 3, 50)  # 3-class problem

    npy_path = sample_dir / "sample_data.npy"
    np.save(npy_path, data)
    np.save(sample_dir / "sample_data.labels.npy", labels)

    # Convert to HDF5
    hdf5_path = sample_dir / "sample_data.h5"
    DatasetConverter.convert(
        input_path=npy_path,
        output_path=hdf5_path,
        input_format=DataFormat.NPY,
        output_format=DataFormat.HDF5,
        labels_path=sample_dir / "sample_data.labels.npy",
        channel_names=[f"CH{i + 1}" for i in range(8)],
        sampling_rate=500.0,
    )
    logger.info(f"Converted NPY to HDF5: {hdf5_path}")

    # Convert to CSV (will flatten epochs)
    csv_path = sample_dir / "sample_data.csv"
    DatasetConverter.convert(
        input_path=hdf5_path,
        output_path=csv_path,
        input_format=DataFormat.HDF5,
        output_format=DataFormat.CSV,
    )
    logger.info(f"Converted HDF5 to CSV: {csv_path}")

    # Validate conversion
    is_valid = DatasetConverter.validate_conversion(
        original_path=npy_path,
        converted_path=hdf5_path,
        original_format=DataFormat.NPY,
        converted_format=DataFormat.HDF5,
    )
    logger.info(f"Conversion validation: {'PASSED' if is_valid else 'FAILED'}")


def visualize_data(data: np.ndarray, labels: np.ndarray, loader: CustomDatasetLoader):
    """Visualize loaded data."""
    logger.info("\n=== Data Visualization ===")

    output_dir = Path("output") / "custom_dataset_plots"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get channel info
    channel_info = loader.get_channel_info()

    # Plot 1: Sample epochs for each class
    unique_labels = np.unique(labels)
    n_classes = len(unique_labels)

    fig, axes = plt.subplots(n_classes, 1, figsize=(12, 4 * n_classes))
    if n_classes == 1:
        axes = [axes]

    for i, label in enumerate(unique_labels):
        # Get first epoch of this class
        idx = np.where(labels == label)[0][0]

        if data.ndim == 3:
            # Epoched data
            epoch_data = data[idx]  # (samples, channels)
        else:
            # Continuous data - extract a segment
            start = idx * 250  # Assuming 250Hz
            epoch_data = data[start : start + 500]  # 2 seconds

        # Plot channels
        time = np.arange(epoch_data.shape[0]) / channel_info["sampling_rate"]

        # Offset channels for visibility
        offsets = np.arange(epoch_data.shape[1]) * np.std(epoch_data) * 5

        for ch in range(min(epoch_data.shape[1], 8)):  # Plot up to 8 channels
            axes[i].plot(
                time,
                epoch_data[:, ch] + offsets[ch],
                linewidth=0.5,
                label=channel_info["channel_names"][ch] if ch == 0 else "",
            )

        axes[i].set_xlabel("Time (s)")
        axes[i].set_ylabel("Amplitude")
        axes[i].set_title(f"Class {label} - Sample Epoch")
        axes[i].grid(True, alpha=0.3)
        if i == 0:
            axes[i].legend(loc="upper right")

    plt.tight_layout()
    plt.savefig(output_dir / "sample_epochs.png", dpi=150, bbox_inches="tight")
    plt.close()

    # Plot 2: Class distribution
    plt.figure(figsize=(8, 6))
    unique, counts = np.unique(labels, return_counts=True)
    plt.bar(unique.astype(str), counts)
    plt.xlabel("Class")
    plt.ylabel("Count")
    plt.title("Class Distribution")
    plt.grid(True, alpha=0.3)

    # Add percentage labels
    total = len(labels)
    for i, (label, count) in enumerate(zip(unique, counts)):
        plt.text(i, count, f"{count / total * 100:.1f}%", ha="center", va="bottom")

    plt.tight_layout()
    plt.savefig(output_dir / "class_distribution.png", dpi=150, bbox_inches="tight")
    plt.close()

    logger.info(f"Saved visualizations to {output_dir}")


def main():
    """Run all examples."""
    logger.info("=== Custom Dataset Loader Examples ===\n")

    # Example 1: Load CSV data
    try:
        data_csv, labels_csv, loader_csv = load_csv_example()
        visualize_data(data_csv, labels_csv, loader_csv)
    except Exception as e:
        logger.error(f"CSV example failed: {e}")

    # Example 2: Custom format with custom loader
    try:
        data_custom, labels_custom, loader_custom = load_custom_format_example()
        visualize_data(data_custom, labels_custom, loader_custom)
    except Exception as e:
        logger.error(f"Custom format example failed: {e}")

    # Example 3: Format conversion
    try:
        convert_formats_example()
    except Exception as e:
        logger.error(f"Format conversion example failed: {e}")

    logger.info("\n=== Examples Complete ===")


if __name__ == "__main__":
    main()
