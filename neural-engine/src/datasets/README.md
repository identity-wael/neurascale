# NeuraScale Dataset Management System

This module provides a comprehensive dataset management system for neural data, with special support for PhysioNet datasets, custom dataset formats, and data quality validation.

## Table of Contents
- [Features](#features)
- [Supported Formats](#supported-formats)
- [Quick Start](#quick-start)
- [Custom Dataset Support](#custom-dataset-support)
- [Data Quality Validation](#data-quality-validation)
- [Dataset Conversion](#dataset-conversion)
- [Examples](#examples)
- [API Reference](#api-reference)

## Features

### 1. **Base Dataset Interface**

- Abstract base class for all dataset types
- Automatic caching and lazy loading
- Built-in train/validation/test splitting
- Batch iteration support
- Metadata management

### 2. **PhysioNet Dataset Loader**

- Support for major PhysioNet EEG/ECG datasets:

  - **EEGMMIDB**: EEG Motor Movement/Imagery Database
  - **CHB-MIT**: Scalp EEG Database (epilepsy)
  - **Sleep-EDF**: Sleep staging datasets
  - **MIT-BIH**: Arrhythmia Database
  - **PTB Diagnostic**: ECG Database

- Automatic downloading and caching
- Configurable preprocessing pipeline
- Channel selection and filtering
- Windowing and epoching
- Export to LSL for real-time testing

### 3. **Data Quality Validation**

- Comprehensive quality metrics:

  - Signal-to-noise ratio (SNR)
  - Artifact detection (motion, eye, muscle)
  - Flatline and clipping detection
  - Channel correlation analysis
  - Statistical properties

- Quality assessment levels:

  - Excellent, Good, Fair, Poor, Unusable

- Report generation and visualization

### 4. **Custom Dataset Support**

- Load data from multiple formats:
  - CSV files
  - EDF (European Data Format)
  - FIF (Neuromag/MNE format)
  - HDF5
  - MATLAB (.mat)
  - BrainVision (.vhdr)
  - NumPy arrays
  - Custom formats via user-defined loaders

- Flexible configuration for any data structure
- Built-in preprocessing pipeline
- Automatic epoching for continuous data

### 5. **Dataset Conversion**

- Convert between any supported formats
- Batch conversion for multiple files
- Data integrity validation
- Metadata preservation

## Supported Formats

| Format | Extension | Read | Write | Notes |
|--------|-----------|------|-------|-------|
| CSV | .csv | ✅ | ✅ | Flexible column mapping |
| EDF | .edf | ✅ | ✅ | European Data Format |
| FIF | .fif | ✅ | ✅ | MNE/Neuromag format |
| HDF5 | .h5/.hdf5 | ✅ | ✅ | Hierarchical data |
| MATLAB | .mat | ✅ | ✅ | MATLAB v5-v7.3 |
| BrainVision | .vhdr | ✅ | ❌ | Header/data/marker files |
| NumPy | .npy | ✅ | ✅ | Native Python arrays |

## Installation

```bash
# Install required dependencies
pip install mne wfdb scipy requests

# Optional: For LSL streaming
pip install pylsl
```

## Quick Start

### Loading EEGMMIDB (Motor Imagery)

```python
from src.datasets import PhysioNetLoader, PhysioNetDataset
from src.datasets.physionet_loader import PhysioNetConfig

# Configure dataset
config = PhysioNetConfig(
    name="motor_imagery",
    dataset_type=PhysioNetDataset.EEGMMIDB,
    subjects=["S001", "S002"],  # Select subjects
    tasks=["left_fist", "right_fist"],  # Motor imagery tasks
    channels=["C3", "C4", "Cz"],  # Motor cortex channels
    sampling_rate=160.0,  # Downsample to 160 Hz
    window_size=2.0,  # 2-second windows
    overlap=0.5,  # 50% overlap
    bandpass_freq=(8.0, 30.0),  # Mu and beta bands
)

# Load data
loader = PhysioNetLoader(config)
data, labels = loader.load()

# Split data
train, val, test = loader.split_data(data, labels)
```

### Loading CHB-MIT (Epilepsy)

```python
config = PhysioNetConfig(
    name="epilepsy",
    dataset_type=PhysioNetDataset.CHB_MIT,
    subjects=["chb01", "chb02"],
    sampling_rate=256.0,
    window_size=1.0,
    bandpass_freq=(0.5, 50.0),
)

loader = PhysioNetLoader(config)
data, labels = loader.load()

# labels: 0 = normal, 1 = seizure
print(f"Seizure epochs: {np.sum(labels == 1)}")
print(f"Normal epochs: {np.sum(labels == 0)}")
```

### Data Quality Validation

```python
from src.datasets.data_quality import DataQualityValidator

# Create validator
validator = DataQualityValidator(
    sampling_rate=250.0,
    line_freq=60.0,
    min_snr_db=10.0
)

# Validate data
metrics = validator.validate(data)

# Generate report
report = validator.generate_report(metrics)
print(report)

# Plot quality summary
validator.plot_quality_summary(metrics, save_path="quality_summary.png")
```

### Batch Processing

```python
# Iterate over batches
for batch_data, batch_labels in loader.get_batch_iterator(data, labels, shuffle=True):
    # Process batch
    # batch_data shape: (batch_size, n_channels, n_samples)
    predictions = model.predict(batch_data)
```

### Export to LSL Stream

```python
# Export dataset as LSL stream for real-time testing
loader.export_to_lsl(data, labels)
```

## Custom Dataset Support

### Loading CSV Data

```python
from src.datasets import CustomDatasetLoader, CustomDatasetConfig, DataFormat

# Configure CSV loader
config = CustomDatasetConfig(
    name="my_eeg_data",
    data_format=DataFormat.CSV,
    data_path="path/to/data.csv",
    
    # CSV structure
    csv_time_column="timestamp",
    csv_label_column="event",
    csv_channel_columns=["Fp1", "Fp2", "C3", "C4", "O1", "O2"],
    
    # Signal properties
    sampling_rate=500.0,
    
    # Preprocessing
    filter_low=1.0,
    filter_high=45.0,
    notch_freq=60.0,
    reference="average",
    
    # Epoching
    epoch_length=2.0,      # 2-second epochs
    epoch_overlap=0.5      # 50% overlap
)

loader = CustomDatasetLoader(config)
data, labels = loader.load()
```

### Loading EDF/FIF Files

```python
# Load EDF file
config = CustomDatasetConfig(
    name="clinical_eeg",
    data_format=DataFormat.EDF,
    data_path="path/to/recording.edf",
    sampling_rate=256.0,
    filter_low=0.5,
    filter_high=70.0
)

# Load FIF file (MNE format)
config = CustomDatasetConfig(
    name="meg_data",
    data_format=DataFormat.FIF,
    data_path="path/to/raw.fif"
)
```

### Loading HDF5/MATLAB Files

```python
# HDF5 with custom structure
config = CustomDatasetConfig(
    name="research_data",
    data_format=DataFormat.HDF5,
    data_path="path/to/data.h5",
    data_key="neural_signals",      # Key containing data array
    labels_key="trial_labels",      # Key containing labels
    metadata_key="recording_info"   # Key containing metadata
)

# MATLAB file
config = CustomDatasetConfig(
    name="matlab_export",
    data_format=DataFormat.MAT,
    data_path="path/to/data.mat",
    data_key="EEG"  # MATLAB variable name
)
```

### Custom Loader Function

```python
def my_custom_loader(config: CustomDatasetConfig):
    """Load data from proprietary format."""
    # Your custom loading logic here
    data = load_my_format(config.data_path)
    labels = extract_labels(data)
    
    return {
        'data': data,
        'labels': labels,
        'channel_names': ['Ch1', 'Ch2', 'Ch3'],
        'sampling_rate': 1000.0,
        'metadata': {'experiment': 'my_experiment'}
    }

# Use custom loader
config = CustomDatasetConfig(
    name="proprietary_format",
    data_format=DataFormat.CUSTOM,
    custom_loader=my_custom_loader
)
```

## Dataset Conversion

### Convert Between Formats

```python
from src.datasets.dataset_converter import DatasetConverter

# Convert EDF to HDF5
DatasetConverter.convert(
    input_path="data.edf",
    output_path="data.h5",
    input_format=DataFormat.EDF,
    output_format=DataFormat.HDF5
)

# Batch convert all CSV files to HDF5
DatasetConverter.batch_convert(
    input_dir=Path("raw_data"),
    output_dir=Path("processed_data"),
    input_format=DataFormat.CSV,
    output_format=DataFormat.HDF5,
    pattern="subject_*.csv"
)

# Validate conversion
is_valid = DatasetConverter.validate_conversion(
    original_path="data.edf",
    converted_path="data.h5",
    original_format=DataFormat.EDF,
    converted_format=DataFormat.HDF5
)
```

### Export to MNE Format

```python
# Convert custom data to MNE Raw object
raw = loader.convert_to_mne(data, labels)

# Use MNE functionality
raw.plot()
raw.filter(1.0, 40.0)
raw.save("processed_raw.fif")

## Configuration Options

### PhysioNetConfig Parameters

- `dataset_type`: Which PhysioNet dataset to load
- `subjects`: List of subjects to load (None = all)
- `tasks`: Specific tasks for motor imagery datasets
- `channels`: Channel selection (None = all)
- `sampling_rate`: Target sampling rate for resampling
- `window_size`: Window size in seconds for epoching
- `overlap`: Overlap between windows (0-1)
- `bandpass_freq`: Tuple of (low, high) frequencies for bandpass filter
- `notch_freq`: Notch filter frequency (50 or 60 Hz)
- `reference`: EEG reference type ("average", "linked-ears", etc.)
- `cache_dir`: Directory for caching downloaded data

### Quality Validation Parameters

- `sampling_rate`: Data sampling rate
- `line_freq`: Power line frequency
- `amplitude_range`: Expected amplitude range
- `min_snr_db`: Minimum acceptable SNR
- `max_correlation`: Maximum channel correlation
- `max_flatline_ratio`: Maximum flatline ratio
- `max_clipping_ratio`: Maximum clipping ratio

## Supported Datasets

### EEGMMIDB

- 109 subjects
- 14 runs per subject
- Motor execution and imagery tasks
- 64 EEG channels
- 160 Hz sampling rate

### CHB-MIT

- 24 subjects with epilepsy
- Continuous scalp EEG recordings
- Seizure annotations
- 23-26 channels
- 256 Hz sampling rate

### Sleep-EDF

- Sleep stage annotations
- Polysomnography recordings
- 2 EEG channels + EOG, EMG
- 100 Hz sampling rate

## Data Format

All datasets are returned in the format:

- `data`: numpy array of shape `(n_epochs, n_channels, n_samples)`
- `labels`: numpy array of shape `(n_epochs,)` with task/condition labels

## Caching

Datasets are automatically cached after first download:

- Default cache location: `~/.neurascale/datasets/`
- Cache includes preprocessed data and metadata
- Use `lazy_loading=False` to disable caching

## Performance Tips

1. **Download once**: Datasets are large (GBs). Download happens only on first use.
2. **Use caching**: Preprocessed data is cached for faster subsequent loads.
3. **Select channels**: Load only needed channels to reduce memory usage.
4. **Batch processing**: Use batch iterator for large datasets.
5. **Parallel download**: Multiple subjects download in parallel.

## Troubleshooting

### Download Issues

- Check internet connection
- Verify PhysioNet is accessible
- Some datasets require PhysioNet account

### Memory Issues

- Reduce number of subjects
- Select fewer channels
- Use smaller window sizes
- Enable lazy loading

### Quality Issues

- Check sampling rate matches data
- Verify channel names
- Adjust quality thresholds
- Check for proper grounding in recordings

## Examples

See `examples/physionet_example.py` for complete examples including:

- Loading different dataset types
- Quality validation
- Batch processing
- Visualization
- LSL streaming

## Citation

When using PhysioNet datasets, please cite:

```
Goldberger AL, Amaral LAN, Glass L, Hausdorff JM, Ivanov PCh, Mark RG, Mietus JE, Moody GB, Peng C-K, Stanley HE.
PhysioBank, PhysioToolkit, and PhysioNet: Components of a New Research Resource for Complex Physiologic Signals.
Circulation 101(23):e215-e220 [2000]
```
