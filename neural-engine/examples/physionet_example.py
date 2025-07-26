"""Example demonstrating PhysioNet dataset loading and quality validation."""

import logging
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

from src.datasets import PhysioNetLoader, PhysioNetDataset
from src.datasets.physionet_loader import PhysioNetConfig
from src.datasets.data_quality import DataQualityValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_eegmmidb_example():
    """Example loading EEG Motor Movement/Imagery Database."""
    logger.info("=== EEGMMIDB Dataset Example ===")

    # Configure dataset
    config = PhysioNetConfig(
        name="eegmmidb_example",
        dataset_type=PhysioNetDataset.EEGMMIDB,
        subjects=["S001", "S002"],  # Load only 2 subjects for demo
        tasks=["left_fist", "right_fist"],  # Only motor imagery tasks
        channels=["C3", "C4", "Cz"],  # Motor cortex channels
        sampling_rate=160.0,  # Downsample to 160 Hz
        window_size=2.0,  # 2-second windows
        overlap=0.5,  # 50% overlap
        bandpass_freq=(8.0, 30.0),  # Mu and beta bands
        notch_freq=60.0,  # Remove 60 Hz noise
        cache_dir=Path.home() / ".neurascale" / "datasets" / "demo",
    )

    # Create loader
    loader = PhysioNetLoader(config)

    # Load data
    logger.info("Loading EEGMMIDB dataset...")
    data, labels = loader.load()

    # Print dataset info
    logger.info(f"Data shape: {data.shape}")
    logger.info(f"Labels shape: {labels.shape}")
    logger.info(f"Unique labels: {np.unique(labels)}")
    logger.info(f"Metadata: {loader.get_metadata()}")

    # Split data
    train_data, val_data, test_data = loader.split_data(data, labels)
    logger.info(
        f"Train: {train_data[0].shape}, Val: {val_data[0].shape}, Test: {test_data[0].shape}"
    )

    return data, labels, loader


def load_chbmit_example():
    """Example loading CHB-MIT epilepsy dataset."""
    logger.info("\n=== CHB-MIT Dataset Example ===")

    # Configure dataset
    config = PhysioNetConfig(
        name="chbmit_example",
        dataset_type=PhysioNetDataset.CHB_MIT,
        subjects=["chb01"],  # Load only first subject
        sampling_rate=256.0,  # Keep original sampling rate
        window_size=1.0,  # 1-second windows
        overlap=0.5,
        bandpass_freq=(0.5, 50.0),
        notch_freq=60.0,
        cache_dir=Path.home() / ".neurascale" / "datasets" / "demo",
    )

    # Create loader
    loader = PhysioNetLoader(config)

    # Load data
    logger.info("Loading CHB-MIT dataset...")
    data, labels = loader.load()

    # Print dataset info
    logger.info(f"Data shape: {data.shape}")
    logger.info(f"Seizure epochs: {np.sum(labels == 1)}")
    logger.info(f"Normal epochs: {np.sum(labels == 0)}")
    logger.info(f"Channel info: {loader.get_channel_info()}")

    return data, labels, loader


def validate_data_quality(data, labels, loader):
    """Example of data quality validation."""
    logger.info("\n=== Data Quality Validation ===")

    # Create validator
    validator = DataQualityValidator(
        sampling_rate=loader.config.sampling_rate or loader._original_sampling_rate,
        line_freq=60.0,
        amplitude_range=(-200, 200),
        min_snr_db=10.0,
    )

    # Validate a sample of data
    sample_idx = np.random.choice(len(data), size=min(100, len(data)), replace=False)
    sample_data = data[sample_idx]

    # Reshape for validation (concatenate epochs)
    n_epochs, n_channels, n_samples = sample_data.shape
    validation_data = sample_data.transpose(1, 0, 2).reshape(n_channels, -1).T

    # Run validation
    metrics = validator.validate(validation_data, loader._channel_names)

    # Generate report
    report = validator.generate_report(metrics)
    logger.info("\n" + report)

    # Plot quality summary
    output_dir = Path("output") / "quality_reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    plot_path = output_dir / "quality_summary.png"
    validator.plot_quality_summary(metrics, save_path=plot_path)

    return metrics


def demonstrate_batch_loading(loader, data, labels):
    """Example of batch iteration."""
    logger.info("\n=== Batch Loading Example ===")

    # Get first 1000 samples for demo
    demo_data = data[:1000]
    demo_labels = labels[:1000]

    # Create batch iterator
    batch_count = 0
    for batch_data, batch_labels in loader.get_batch_iterator(
        demo_data, demo_labels, shuffle=True
    ):
        logger.info(
            f"Batch {batch_count}: data={batch_data.shape}, labels={batch_labels.shape}"
        )
        batch_count += 1

        if batch_count >= 5:  # Show only first 5 batches
            break


def plot_sample_data(data, labels, loader):
    """Plot sample EEG data."""
    logger.info("\n=== Plotting Sample Data ===")

    # Get a few epochs of each class
    unique_labels = np.unique(labels)
    fig, axes = plt.subplots(
        len(unique_labels), 1, figsize=(12, 4 * len(unique_labels))
    )

    if len(unique_labels) == 1:
        axes = [axes]

    for i, label in enumerate(unique_labels):
        # Get first epoch of this label
        idx = np.where(labels == label)[0][0]
        epoch = data[idx]  # (n_channels, n_samples)

        # Plot channels
        ax = axes[i]
        time = np.arange(epoch.shape[1]) / (
            loader.config.sampling_rate or loader._original_sampling_rate
        )

        # Offset channels for visibility
        offsets = np.arange(epoch.shape[0]) * np.std(epoch) * 5
        for ch in range(epoch.shape[0]):
            ax.plot(time, epoch[ch] + offsets[ch], linewidth=0.5)

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Channels")
        ax.set_title(f"Label: {label}")
        ax.set_yticks(offsets)
        ax.set_yticklabels(loader._channel_names[: epoch.shape[0]])
        ax.grid(True, alpha=0.3)

    plt.tight_layout()

    output_dir = Path("output") / "physionet_examples"
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / "sample_epochs.png", dpi=150, bbox_inches="tight")
    plt.close()

    logger.info(f"Sample plot saved to {output_dir / 'sample_epochs.png'}")


def export_to_lsl_example(loader, data, labels):
    """Example of exporting to LSL for real-time testing."""
    logger.info("\n=== LSL Export Example ===")

    # Note: This would actually stream the data if pylsl is installed
    # For demo, we just show how it would be called

    try:
        # Export first 10 epochs
        # demo_data = data[:10]
        # demo_labels = labels[:10]

        logger.info("Exporting to LSL stream...")
        logger.info("(Install pylsl to actually stream: pip install pylsl)")

        # This would stream the data
        # loader.export_to_lsl(demo_data, demo_labels)

    except ImportError:
        logger.info("pylsl not installed - skipping LSL export")


def main():
    """Run all examples."""
    logger.info("=== PhysioNet Dataset Loading Examples ===\n")

    # Example 1: Load EEGMMIDB (Motor Imagery)
    try:
        data_mi, labels_mi, loader_mi = load_eegmmidb_example()

        # Validate quality
        validate_data_quality(data_mi, labels_mi, loader_mi)

        # Demonstrate batch loading
        demonstrate_batch_loading(loader_mi, data_mi, labels_mi)

        # Plot samples
        plot_sample_data(data_mi, labels_mi, loader_mi)

        # Export to LSL
        export_to_lsl_example(loader_mi, data_mi, labels_mi)

    except Exception as e:
        logger.error(f"Error loading EEGMMIDB: {e}")

    # Example 2: Load CHB-MIT (Epilepsy)
    try:
        data_ep, labels_ep, loader_ep = load_chbmit_example()

        # Show class distribution
        logger.info("\nClass distribution:")
        unique, counts = np.unique(labels_ep, return_counts=True)
        for label, count in zip(unique, counts):
            logger.info(
                f"  Class {label}: {count} samples ({count / len(labels_ep) * 100:.1f}%)"
            )

    except Exception as e:
        logger.error(f"Error loading CHB-MIT: {e}")

    logger.info("\n=== Examples Complete ===")


if __name__ == "__main__":
    main()
