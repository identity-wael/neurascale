"""Synthetic dataset for testing and demonstration.

This module provides a synthetic neural dataset that can be used for testing
and development without requiring real data downloads.
"""

import numpy as np
import json

from .base_dataset import BaseDataset, DatasetInfo, DatasetSplit, DataSample


class SyntheticNeuralDataset(BaseDataset):
    """Synthetic neural dataset for testing and development."""

    def __init__(
        self,
        n_samples: int = 1000,
        n_channels: int = 32,
        sample_length: int = 1000,
        sampling_rate: float = 250.0,
        n_classes: int = 4,
        noise_level: float = 0.1,
        **kwargs,
    ):
        """
        Initialize synthetic dataset.

        Args:
            n_samples: Number of samples to generate
            n_channels: Number of channels
            sample_length: Length of each sample in time points
            sampling_rate: Sampling rate in Hz
            n_classes: Number of classes for classification
            noise_level: Noise level to add to signals
            **kwargs: Additional arguments for BaseDataset
        """
        self.n_samples = n_samples
        self.n_channels = n_channels
        self.sample_length = sample_length
        self.sampling_rate = sampling_rate
        self.n_classes = n_classes
        self.noise_level = noise_level

        # Initialize base class
        super().__init__(**kwargs)

    @property
    def name(self) -> str:
        return "synthetic_neural"

    @property
    def version(self) -> str:
        return "1.0.0"

    def _check_exists(self) -> bool:
        """Check if dataset exists."""
        config_file = self.data_dir / "config.json"
        data_file = self.data_dir / "synthetic_data.npz"
        return config_file.exists() and data_file.exists()

    def _download(self):
        """Generate synthetic dataset."""
        print(f"Generating synthetic neural dataset with {self.n_samples} samples...")

        # Set random seed for reproducibility
        np.random.seed(42)

        # Generate data
        data = []
        labels = []
        metadata = []

        for i in range(self.n_samples):
            # Generate class label
            label = i % self.n_classes

            # Generate base signal based on class
            t = np.linspace(
                0, self.sample_length / self.sampling_rate, self.sample_length
            )

            # Create different patterns for different classes
            signal = np.zeros((self.n_channels, self.sample_length))

            if label == 0:
                # Alpha rhythm (8-12 Hz)
                for ch in range(self.n_channels):
                    freq = 8 + 4 * np.random.rand()
                    phase = np.random.rand() * 2 * np.pi
                    signal[ch] = np.sin(2 * np.pi * freq * t + phase)

            elif label == 1:
                # Beta rhythm (12-30 Hz)
                for ch in range(self.n_channels):
                    freq = 12 + 18 * np.random.rand()
                    phase = np.random.rand() * 2 * np.pi
                    signal[ch] = 0.5 * np.sin(2 * np.pi * freq * t + phase)

            elif label == 2:
                # Theta rhythm (4-8 Hz)
                for ch in range(self.n_channels):
                    freq = 4 + 4 * np.random.rand()
                    phase = np.random.rand() * 2 * np.pi
                    signal[ch] = 1.5 * np.sin(2 * np.pi * freq * t + phase)

            else:
                # Mixed rhythms
                for ch in range(self.n_channels):
                    freq1 = 5 + 5 * np.random.rand()
                    freq2 = 15 + 10 * np.random.rand()
                    phase1 = np.random.rand() * 2 * np.pi
                    phase2 = np.random.rand() * 2 * np.pi
                    signal[ch] = 0.7 * np.sin(
                        2 * np.pi * freq1 * t + phase1
                    ) + 0.3 * np.sin(2 * np.pi * freq2 * t + phase2)

            # Add noise
            noise = (
                np.random.randn(self.n_channels, self.sample_length) * self.noise_level
            )
            signal += noise

            # Add artifacts to some channels randomly
            if np.random.rand() < 0.1:  # 10% chance of artifacts
                artifact_ch = np.random.randint(0, self.n_channels)
                artifact_time = np.random.randint(0, self.sample_length - 100)
                signal[artifact_ch, artifact_time : artifact_time + 100] += (
                    np.random.randn() * 5
                )

            data.append(signal)
            labels.append(label)

            # Generate metadata
            metadata.append(
                {
                    "subject_id": f"S{i // 100:03d}",
                    "session_id": f"sess_{i // 10:04d}",
                    "trial_id": i,
                    "has_artifact": np.any(np.abs(signal) > 3),
                }
            )

        # Convert to arrays
        data = np.array(data, dtype=np.float32)
        labels = np.array(labels, dtype=np.int64)

        # Save configuration
        config = {
            "n_samples": self.n_samples,
            "n_channels": self.n_channels,
            "sample_length": self.sample_length,
            "sampling_rate": self.sampling_rate,
            "n_classes": self.n_classes,
            "noise_level": self.noise_level,
        }

        config_file = self.data_dir / "config.json"
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        # Save data
        data_file = self.data_dir / "synthetic_data.npz"
        np.savez_compressed(
            data_file,
            data=data,
            labels=labels,
            metadata=metadata,
        )

        print(f"Synthetic dataset generated successfully at {self.data_dir}")

    def _load_info(self) -> DatasetInfo:
        """Load dataset information."""
        # Load configuration
        config_file = self.data_dir / "config.json"
        if config_file.exists():
            with open(config_file, "r") as f:
                config = json.load(f)
        else:
            config = {
                "n_samples": self.n_samples,
                "n_channels": self.n_channels,
                "sample_length": self.sample_length,
                "sampling_rate": self.sampling_rate,
                "n_classes": self.n_classes,
            }

        return DatasetInfo(
            name=self.name,
            version=self.version,
            description="Synthetic neural dataset for testing and development",
            n_samples=config["n_samples"],
            n_channels=config["n_channels"],
            sampling_rate=config["sampling_rate"],
            duration_seconds=config["sample_length"] / config["sampling_rate"],
            signal_types=["EEG"],
            n_subjects=config["n_samples"] // 100 + 1,
            subject_ids=[f"S{i:03d}" for i in range(config["n_samples"] // 100 + 1)],
            task_type="multiclass_classification",
            n_classes=config["n_classes"],
            class_names=[f"class_{i}" for i in range(config["n_classes"])],
            total_size_mb=config["n_samples"]
            * config["n_channels"]
            * config["sample_length"]
            * 4
            / 1024
            / 1024,
            format="npz",
            metadata=config,
        )

    def __len__(self) -> int:
        """Number of samples in the dataset."""
        if hasattr(self, "_data"):
            return len(self._data)

        # Load data to get length
        self._load_data()
        return len(self._data)

    def _load_data(self):
        """Load data from disk."""
        if hasattr(self, "_data"):
            return

        data_file = self.data_dir / "synthetic_data.npz"
        loaded = np.load(data_file, allow_pickle=True)

        self._data = loaded["data"]
        self._labels = loaded["labels"]
        self._metadata = loaded["metadata"]

    def __getitem__(self, idx: int) -> DataSample:
        """Get a single sample."""
        # Load data if needed
        if not hasattr(self, "_data"):
            self._load_data()

        if idx < 0 or idx >= len(self._data):
            raise IndexError(f"Index {idx} out of range [0, {len(self._data)})")

        # Get data and label
        data = self._data[idx]
        label = self._labels[idx]
        metadata = self._metadata[idx]

        # Apply transforms
        if self.transform:
            data = self.transform(data)

        if self.target_transform:
            label = self.target_transform(label)

        return DataSample(
            data=data,
            label=label,
            sample_id=f"synthetic_{idx:06d}",
            subject_id=metadata["subject_id"],
            session_id=metadata["session_id"],
            trial_id=metadata["trial_id"],
            sampling_rate=self.sampling_rate,
            duration_seconds=self.sample_length / self.sampling_rate,
            metadata=metadata,
        )

    def get_split(self, split: DatasetSplit) -> "SyntheticNeuralDataset":
        """Get a specific split of the dataset."""
        # Load data to get total size
        if not hasattr(self, "_data"):
            self._load_data()

        total_samples = len(self._data)

        # Define split ratios
        if split == DatasetSplit.TRAIN:
            start_idx = 0
            end_idx = int(0.7 * total_samples)
        elif split == DatasetSplit.VALIDATION:
            start_idx = int(0.7 * total_samples)
            end_idx = int(0.85 * total_samples)
        elif split == DatasetSplit.TEST:
            start_idx = int(0.85 * total_samples)
            end_idx = total_samples
        else:  # ALL
            start_idx = 0
            end_idx = total_samples

        # Create subset
        subset = SyntheticNeuralDatasetSubset(
            self,
            indices=list(range(start_idx, end_idx)),
            split=split,
        )

        return subset


class SyntheticNeuralDatasetSubset(SyntheticNeuralDataset):
    """Subset of synthetic neural dataset."""

    def __init__(
        self, parent: SyntheticNeuralDataset, indices: list, split: DatasetSplit
    ):
        """Initialize subset."""
        self.parent = parent
        self.indices = indices
        self.split = split

        # Copy parent attributes
        self.data_dir = parent.data_dir
        self.cache_dir = parent.cache_dir
        self.transform = parent.transform
        self.target_transform = parent.target_transform
        self.sampling_rate = parent.sampling_rate
        self.sample_length = parent.sample_length
        self.n_channels = parent.n_channels
        self.n_classes = parent.n_classes

        # Load parent data
        if not hasattr(parent, "_data"):
            parent._load_data()

        self._data = parent._data
        self._labels = parent._labels
        self._metadata = parent._metadata
        self._info = parent._info

    def __len__(self) -> int:
        return len(self.indices)

    def __getitem__(self, idx: int) -> DataSample:
        if idx < 0 or idx >= len(self.indices):
            raise IndexError(f"Index {idx} out of range [0, {len(self.indices)})")

        parent_idx = self.indices[idx]
        return self.parent[parent_idx]

    def get_split(self, split: DatasetSplit) -> "SyntheticNeuralDataset":
        """Cannot split a subset further."""
        if split == self.split or split == DatasetSplit.ALL:
            return self
        else:
            raise ValueError(
                f"Cannot get split '{split.value}' from subset '{self.split.value}'"
            )
