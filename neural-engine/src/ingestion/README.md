# Neural Data Ingestion Module

This module provides a comprehensive system for ingesting, validating, and anonymizing neural signals from various BCI devices in real-time.

## Key Components

### 1. **NeuralDataIngestion** (`neural_data_ingestion.py`)

The main orchestrator class that handles:

- Real-time data ingestion from multiple sources
- Data validation and quality assessment
- HIPAA-compliant anonymization
- Publishing to Google Cloud Pub/Sub
- Storage in Google Cloud Bigtable
- Stream management for continuous data sources

### 2. **Data Types** (`data_types.py`)

Core data structures:

- `NeuralDataPacket`: Standardized format for neural signals
- `NeuralSignalType`: Enum for signal types (EEG, ECoG, Spikes, LFP, EMG, Accelerometer)
- `DataSource`: Enum for data sources (LSL, OpenBCI, BrainFlow, File Upload, Synthetic)
- `DeviceInfo` & `ChannelInfo`: Device and channel metadata
- `ValidationResult`: Validation results with errors, warnings, and quality score

### 3. **Data Validator** (`validators.py`)

Comprehensive validation including:

- Signal-specific range validation
- Sampling rate verification
- Data quality assessment (noise, flat channels, clipping)
- Metadata validation
- Quality score calculation (0-1 scale)

### 4. **Data Anonymizer** (`anonymizer.py`)

HIPAA-compliant anonymization:

- Consistent subject ID anonymization using HMAC
- Timestamp fuzzing (±5 seconds)
- PII removal from metadata
- Age range conversion
- Audit logging for compliance

## Features

- **Multi-Source Support**: Handles data from LSL, OpenBCI, BrainFlow, and custom APIs
- **Real-time Processing**: Async architecture for low-latency ingestion
- **Signal-Specific Validation**: Different validation rules for each signal type
- **HIPAA Compliance**: Built-in anonymization for protected health information
- **Cloud Integration**: Optional integration with Google Cloud services
- **Comprehensive Testing**: Full test coverage for all components

## Usage Example

```python
from src.ingestion import NeuralDataIngestion
from src.ingestion.data_types import NeuralDataPacket, NeuralSignalType, DataSource

# Initialize ingestion system
ingestion = NeuralDataIngestion(
    project_id="your-project",
    enable_pubsub=True,
    enable_bigtable=True
)

# Create a data packet
packet = NeuralDataPacket(
    timestamp=datetime.now(timezone.utc),
    data=eeg_data,  # numpy array (n_channels, n_samples)
    signal_type=NeuralSignalType.EEG,
    source=DataSource.OPENBCI,
    device_info=device_info,
    session_id="session_001",
    subject_id="patient_123",  # Will be anonymized
    sampling_rate=256.0,
    data_quality=0.95
)

# Ingest the packet
success = await ingestion.ingest_packet(packet)
```

## Signal Types and Ranges

| Signal Type   | Expected Range   | Typical Sampling Rates                 |
| ------------- | ---------------- | -------------------------------------- |
| EEG           | -200 to 200 μV   | 125, 250, 256, 500, 512, 1000, 1024 Hz |
| ECoG          | -500 to 500 μV   | 1000, 2000, 5000, 10000 Hz             |
| LFP           | -1000 to 1000 μV | 1000, 2000, 5000 Hz                    |
| EMG           | -5000 to 5000 μV | 500, 1000, 2000 Hz                     |
| Spikes        | -100 to 100 μV   | 10000, 20000, 30000 Hz                 |
| Accelerometer | -20 to 20 g      | 50, 100, 200 Hz                        |

## Testing

Run tests with:

```bash
python -m pytest tests/unit/test_ingestion/ -v
```

## Future Enhancements

- Implement actual device interfaces (LSL, OpenBCI, BrainFlow)
- Add Cloud Functions for stream processing
- Create Bigtable schema and admin tools
- Add real-time anomaly detection
- Implement data compression for storage optimization
