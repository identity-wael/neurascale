---
layout: doc
title: Dataset Management System
permalink: /dataset-management/
---

# Dataset Management System

The NeuraScale Dataset Management System provides a robust infrastructure for handling neural datasets with support for various data formats, lazy loading, caching, and dataset transformations.

## Overview

The dataset management system is designed to handle large-scale neural data efficiently while providing a consistent interface for different data sources and formats.

### Key Features

- **Abstract Base Classes**: Extensible framework for custom dataset implementations
- **Lazy Loading**: Load data on-demand to optimize memory usage
- **Caching Support**: Built-in caching mechanisms for improved performance
- **Dataset Registry**: Centralized registration and discovery of dataset types
- **Metadata Management**: Comprehensive metadata tracking and persistence
- **Statistics Computation**: Automatic computation of dataset statistics
- **Batch Processing**: Efficient batch iteration with configurable batch sizes

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  (ML Models, Signal Processing, Analysis Tools)             │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 Dataset Manager                              │
│  ┌─────────────────────────┐  ┌──────────────────────────┐ │
│  │   Dataset Registry      │  │   Cache Management       │ │
│  │   - Type registration   │  │   - Memory cache         │ │
│  │   - Factory methods     │  │   - Disk cache           │ │
│  └───────────┬─────────────┘  └────────────┬─────────────┘ │
└──────────────┼──────────────────────────────┼───────────────┘
               │                              │
┌──────────────▼──────────────────────────────▼───────────────┐
│                    BaseDataset                               │
│  - Abstract interface for all datasets                      │
│  - Common functionality (loading, caching, iteration)       │
│  - Metadata and statistics management                       │
└──────────────────────────┬───────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┬─────────────────┐
        │                 │                 │                 │
┌───────▼────────┐ ┌──────▼──────┐ ┌───────▼────────┐ ┌──────▼──────┐
│ EEGDataset     │ │ EMGDataset  │ │ ECOGDataset    │ │ Custom...   │
│ - EDF files    │ │ - BDF files │ │ - HDF5 files   │ │             │
│ - Preprocessing│ │ - Filtering │ │ - Montages     │ │             │
└────────────────┘ └─────────────┘ └────────────────┘ └─────────────┘
```

## Core Components

### 1. BaseDataset

The abstract base class that all neural datasets inherit from:

```python
from neural_engine.datasets import BaseDataset, DatasetInfo, DataSample

class CustomDataset(BaseDataset):
    def __init__(self, name: str, data_dir: str):
        super().__init__(name, data_dir)

    def _load_data(self) -> List[DataSample]:
        # Implement data loading logic
        pass

    def _compute_statistics(self) -> Dict[str, Any]:
        # Compute dataset-specific statistics
        pass
```

### 2. DatasetManager

Central management for all datasets:

```python
from neural_engine.datasets import DatasetManager

# Initialize manager
manager = DatasetManager(cache_dir="/path/to/cache")

# Load a dataset
dataset = manager.load_dataset(
    dataset_type="synthetic",
    name="test_eeg",
    config={"channels": 32, "duration": 300}
)

# Access dataset
for batch in dataset.get_batches(batch_size=32):
    process_batch(batch)
```

### 3. DatasetRegistry

Register custom dataset types:

```python
from neural_engine.datasets import DatasetRegistry

# Register a custom dataset type
@DatasetRegistry.register("custom_type")
class MyCustomDataset(BaseDataset):
    # Implementation
    pass

# List available types
available_types = DatasetRegistry.list_types()
```

## Dataset Types

### SyntheticNeuralDataset

A reference implementation that generates synthetic EEG signals:

```python
from neural_engine.datasets import SyntheticNeuralDataset

# Create synthetic dataset
dataset = SyntheticNeuralDataset(
    name="synthetic_eeg",
    data_dir="./data",
    num_samples=1000,
    channels=32,
    sample_rate=256,
    duration=1.0
)

# Generate and access data
dataset.generate()
info = dataset.get_info()
print(f"Dataset: {info.name}")
print(f"Samples: {info.total_samples}")
print(f"Size: {info.total_size_mb:.2f} MB")
```

## Usage Examples

### Loading and Processing Data

```python
from neural_engine.datasets import DatasetManager

# Initialize manager
manager = DatasetManager()

# Load dataset
dataset = manager.load_dataset("synthetic", "training_data", {
    "num_samples": 5000,
    "channels": 64,
    "sample_rate": 512
})

# Access splits
train_split = dataset.get_split("train", split_ratio=0.8)
val_split = dataset.get_split("validation", split_ratio=0.2)

# Iterate through batches
for batch in train_split.get_batches(batch_size=32):
    # Process batch
    signals = batch.data  # Neural signals
    labels = batch.labels  # Associated labels
    metadata = batch.metadata  # Additional information
```

### Computing Statistics

```python
# Get dataset statistics
stats = dataset.get_statistics()
print(f"Mean amplitude: {stats['mean']}")
print(f"Std deviation: {stats['std']}")
print(f"Signal range: {stats['min']} to {stats['max']}")

# Get split-specific statistics
train_stats = train_split.get_statistics()
```

### Caching and Performance

```python
# Enable caching for faster subsequent loads
dataset = manager.load_dataset(
    "eeg_dataset",
    "subject_001",
    use_cache=True
)

# Clear cache if needed
dataset.clear_cache()

# Get cache information
cache_info = manager.get_cache_info()
print(f"Cache size: {cache_info['size_mb']:.2f} MB")
print(f"Cached datasets: {cache_info['num_datasets']}")
```

## Best Practices

1. **Memory Management**

   - Use lazy loading for large datasets
   - Process data in batches rather than loading everything at once
   - Clear cache periodically for long-running processes

2. **Data Organization**

   - Store raw data separately from processed data
   - Use consistent naming conventions
   - Include comprehensive metadata

3. **Performance Optimization**

   - Enable caching for frequently accessed datasets
   - Use appropriate batch sizes based on available memory
   - Precompute statistics when possible

4. **Custom Implementations**
   - Inherit from BaseDataset for consistency
   - Implement all abstract methods
   - Register custom types with DatasetRegistry
   - Include proper error handling

## Integration with Neural Pipeline

The dataset management system integrates seamlessly with other NeuraScale components:

- **Signal Processing**: Direct access to neural signals for filtering and analysis
- **ML Models**: Standardized data format for training and inference
- **Security**: Automatic encryption of sensitive data using the security module
- **Monitoring**: Performance metrics and usage statistics

## Future Enhancements

- [ ] Support for streaming datasets
- [ ] Distributed dataset loading
- [ ] Advanced data augmentation pipelines
- [ ] Integration with cloud storage (GCS, S3)
- [ ] Real-time data validation
- [ ] Dataset versioning and lineage tracking

---

_Last updated: July 26, 2025_
