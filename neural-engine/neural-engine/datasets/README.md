# NeuraScale Dataset Management System

This module provides a comprehensive infrastructure for managing neural datasets in the NeuraScale system.

## Features

- **Base Infrastructure**: Abstract base classes for consistent dataset interface
- **Dataset Registry**: Central registry for all available datasets
- **Dataset Manager**: High-level interface for loading and managing datasets
- **Lazy Loading**: Efficient memory usage with on-demand data loading
- **Caching**: Multi-level caching for improved performance
- **Metadata Management**: Automatic tracking of dataset information
- **Split Support**: Built-in support for train/validation/test splits
- **Transform Support**: Apply custom transforms to data and labels
- **Batch Iteration**: Efficient batch processing with shuffling options

## Architecture

### Core Components

1. **BaseDataset**: Abstract base class that all datasets must inherit from
2. **DatasetManager**: Central manager for loading and caching datasets
3. **DatasetRegistry**: Registry for available dataset classes
4. **DatasetInfo**: Metadata container for dataset information
5. **DataSample**: Container for individual data samples

### Class Hierarchy

```
BaseDataset (abstract)
├── SyntheticNeuralDataset
├── BCICompetitionDataset (future)
├── PhysioNetDataset (future)
└── CustomDataset (future)
```

## Usage

### Basic Example

```python
from neural_engine.datasets import DatasetManager, DatasetSplit

# Create manager
manager = DatasetManager()

# Register and load dataset
manager.register_dataset("synthetic", SyntheticNeuralDataset)
dataset = manager.load_dataset("synthetic", download=True)

# Get specific split
train_set = manager.load_dataset("synthetic", split=DatasetSplit.TRAIN)

# Access samples
sample = train_set[0]
print(f"Data shape: {sample.data.shape}")
print(f"Label: {sample.label}")

# Iterate in batches
for batch in train_set.iter_batches(batch_size=32, shuffle=True):
    # Process batch
    pass
```

### Custom Dataset Implementation

```python
from neural_engine.datasets import BaseDataset, DatasetInfo, DataSample

class MyCustomDataset(BaseDataset):
    @property
    def name(self) -> str:
        return "my_dataset"

    @property
    def version(self) -> str:
        return "1.0.0"

    def _check_exists(self) -> bool:
        # Check if dataset files exist
        return (self.data_dir / "data.npz").exists()

    def _download(self):
        # Download or generate dataset
        pass

    def _load_info(self) -> DatasetInfo:
        # Return dataset metadata
        return DatasetInfo(
            name=self.name,
            version=self.version,
            description="My custom dataset",
            n_samples=1000,
            n_channels=32,
            sampling_rate=250.0,
        )

    def __len__(self) -> int:
        return 1000

    def __getitem__(self, idx: int) -> DataSample:
        # Load and return sample
        pass
```

### Advanced Features

#### Custom Transforms

```python
def normalize_transform(data):
    return (data - data.mean()) / data.std()

dataset = manager.load_dataset(
    "synthetic",
    transform=normalize_transform,
)
```

#### Caching Control

```python
# Disable caching for memory-constrained environments
manager.disable_lazy_loading()

# Clear cache for specific dataset
manager.clear_cache("synthetic")

# Preload multiple datasets
manager.preload_datasets(["dataset1", "dataset2"])
```

#### Dataset Statistics

```python
# Compute statistics (cached automatically)
stats = dataset.compute_statistics()
print(f"Mean: {stats['mean']}")
print(f"Std: {stats['std']}")
```

## Dataset Format

### DataSample Structure

Each sample contains:

- `data`: Neural signal data (n_channels × n_samples)
- `label`: Class label or target value
- `sample_id`: Unique sample identifier
- `subject_id`: Subject/participant identifier
- `session_id`: Recording session identifier
- `trial_id`: Trial number within session
- `timestamp`: Sample timestamp
- `sampling_rate`: Sampling frequency in Hz
- `metadata`: Additional sample-specific metadata

### Storage Format

Datasets are stored in:

- `~/.neurascale/datasets/`: Raw dataset files
- `~/.neurascale/cache/`: Processed cache files

## Performance Considerations

1. **Memory Usage**: Use lazy loading for large datasets
2. **Disk I/O**: Enable caching for frequently accessed data
3. **Batch Processing**: Use `iter_batches()` for efficient processing
4. **Parallel Loading**: Manager supports concurrent dataset loading

## Future Enhancements

- [ ] BCI Competition dataset loaders
- [ ] PhysioNet dataset integration
- [ ] HDF5 and EDF format support
- [ ] Distributed dataset loading
- [ ] Cloud storage backends
- [ ] Dataset versioning and tracking
- [ ] Automatic data augmentation
- [ ] Cross-validation utilities
