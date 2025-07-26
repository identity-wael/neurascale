"""Example usage of the dataset management system."""

import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

from neural_engine.datasets import DatasetManager, DatasetRegistry
from neural_engine.datasets.synthetic_dataset import SyntheticNeuralDataset
from neural_engine.datasets.base_dataset import DatasetSplit


def main():
    """Demonstrate dataset management system usage."""
    print("=== NeuraScale Dataset Management Example ===\n")

    # 1. Create dataset manager
    print("1. Creating dataset manager...")
    manager = DatasetManager(
        data_root=Path("./demo_data"),
        cache_root=Path("./demo_cache"),
    )

    # 2. Register synthetic dataset
    print("\n2. Registering synthetic neural dataset...")
    manager.register_dataset(
        name="synthetic",
        dataset_class=SyntheticNeuralDataset,
        metadata={
            "description": "Synthetic EEG dataset for testing",
            "created_by": "NeuraScale Team",
        }
    )

    # 3. List available datasets
    print("\n3. Available datasets:")
    datasets = manager.list_available_datasets()
    for dataset in datasets:
        print(f"   - {dataset['registered_name']}: {dataset.get('description', 'No description')}")

    # 4. Load the dataset
    print("\n4. Loading synthetic dataset...")
    dataset = manager.load_dataset(
        "synthetic",
        n_samples=500,  # Generate 500 samples
        n_channels=16,  # 16 EEG channels
        n_classes=3,    # 3 different brain states
        download=True,
    )

    print(f"   Dataset loaded: {dataset}")
    print(f"   Total samples: {len(dataset)}")

    # 5. Get dataset information
    print("\n5. Dataset information:")
    info = dataset.info
    print(f"   - Name: {info.name}")
    print(f"   - Version: {info.version}")
    print(f"   - Channels: {info.n_channels}")
    print(f"   - Sampling rate: {info.sampling_rate} Hz")
    print(f"   - Signal types: {info.signal_types}")
    print(f"   - Task: {info.task_type} with {info.n_classes} classes")

    # 6. Load different splits
    print("\n6. Loading dataset splits...")
    train_set = manager.load_dataset("synthetic", split=DatasetSplit.TRAIN)
    val_set = manager.load_dataset("synthetic", split=DatasetSplit.VALIDATION)
    test_set = manager.load_dataset("synthetic", split=DatasetSplit.TEST)

    print(f"   - Train set: {len(train_set)} samples")
    print(f"   - Validation set: {len(val_set)} samples")
    print(f"   - Test set: {len(test_set)} samples")

    # 7. Access individual samples
    print("\n7. Accessing individual samples...")
    sample = train_set[0]
    print(f"   Sample shape: {sample.data.shape}")
    print(f"   Label: {sample.label}")
    print(f"   Subject ID: {sample.subject_id}")
    print(f"   Duration: {sample.duration_seconds} seconds")

    # 8. Iterate through batches
    print("\n8. Iterating through batches...")
    batch_size = 32
    n_batches = 0

    for batch in train_set.iter_batches(batch_size=batch_size, shuffle=True):
        n_batches += 1
        if n_batches == 1:
            print(f"   First batch size: {len(batch)}")
            print(f"   Batch data shape: {batch[0].data.shape}")

    print(f"   Total batches: {n_batches}")

    # 9. Compute dataset statistics
    print("\n9. Computing dataset statistics...")
    stats = dataset.compute_statistics()
    print(f"   - Mean shape: {len(stats['mean'])} channels")
    print(f"   - Mean values (first 5 channels): {stats['mean'][:5]}")
    print(f"   - Std values (first 5 channels): {stats['std'][:5]}")

    # 10. Apply custom transforms
    print("\n10. Applying custom transforms...")

    def normalize_transform(data):
        """Normalize each channel to zero mean and unit variance."""
        return (data - data.mean(axis=1, keepdims=True)) / (data.std(axis=1, keepdims=True) + 1e-8)

    normalized_dataset = manager.load_dataset(
        "synthetic",
        transform=normalize_transform,
        force_reload=True,  # Force reload with new transform
    )

    sample = normalized_dataset[0]
    print(f"   Normalized data mean: {sample.data.mean():.6f}")
    print(f"   Normalized data std: {sample.data.std():.6f}")

    # 11. Visualize sample data
    print("\n11. Visualizing sample data...")
    sample = dataset[0]

    # Create figure
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))

    # Plot raw signal (first 4 channels)
    time = np.arange(sample.n_samples) / sample.sampling_rate
    for ch in range(min(4, sample.n_channels)):
        axes[0].plot(time, sample.data[ch] + ch * 2, label=f"Ch {ch}")

    axes[0].set_xlabel("Time (s)")
    axes[0].set_ylabel("Amplitude")
    axes[0].set_title(f"Raw Neural Signal - Label: {sample.label}")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Plot power spectrum
    from scipy import signal
    for ch in range(min(4, sample.n_channels)):
        freqs, psd = signal.welch(sample.data[ch], fs=sample.sampling_rate, nperseg=256)
        axes[1].semilogy(freqs, psd, label=f"Ch {ch}")

    axes[1].set_xlabel("Frequency (Hz)")
    axes[1].set_ylabel("Power Spectral Density")
    axes[1].set_title("Power Spectrum")
    axes[1].set_xlim(0, 50)  # Focus on 0-50 Hz
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("demo_neural_signal.png", dpi=150)
    print("   Saved visualization to: demo_neural_signal.png")

    # 12. Cache management
    print("\n12. Cache management...")
    print("   - Clearing dataset cache...")
    manager.clear_cache("synthetic")

    # 13. Save manager state
    print("\n13. Saving manager state...")
    state_file = Path("./demo_manager_state.pkl")
    manager.save_state(state_file)
    print(f"   Manager state saved to: {state_file}")

    print("\n=== Example completed successfully! ===")


if __name__ == "__main__":
    main()
