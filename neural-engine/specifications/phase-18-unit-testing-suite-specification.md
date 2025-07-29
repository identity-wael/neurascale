# Phase 18: Unit Testing Suite Specification

**Version**: 1.0.0
**Created**: 2025-07-29
**GitHub Issue**: #158 (to be created)
**Priority**: HIGH
**Duration**: 4-5 days
**Lead**: Senior Test Engineer

## Executive Summary

Phase 18 implements a comprehensive unit testing suite for the NeuraScale Neural Engine, ensuring code quality, reliability, and maintainability through extensive test coverage, mocking strategies, and automated testing frameworks.

## Functional Requirements

### 1. Test Coverage

- **Code Coverage Target**: >85% overall, >95% for critical paths
- **Test Categories**: Unit, component, contract tests
- **Test Isolation**: Complete mocking of external dependencies
- **Performance Tests**: Benchmark critical operations
- **Edge Cases**: Comprehensive error scenario coverage

### 2. Testing Framework

- **Python Tests**: pytest with plugins
- **JavaScript Tests**: Jest/Vitest
- **Go Tests**: Native testing + testify
- **Test Data**: Fixtures and factories
- **Mocking**: Comprehensive mock strategies

### 3. Test Automation

- **Continuous Testing**: Tests run on every commit
- **Parallel Execution**: Optimize test runtime
- **Test Reports**: Coverage and failure reports
- **Flaky Test Detection**: Automatic retry and reporting
- **Mutation Testing**: Code quality validation

## Technical Architecture

### Testing Structure

```
tests/
├── unit/                    # Unit tests
│   ├── neural_processor/
│   │   ├── test_signal_processing.py
│   │   ├── test_feature_extraction.py
│   │   ├── test_data_pipeline.py
│   │   └── test_buffer_management.py
│   ├── device_manager/
│   │   ├── test_device_discovery.py
│   │   ├── test_device_connection.py
│   │   ├── test_impedance_check.py
│   │   └── test_signal_quality.py
│   ├── ml_models/
│   │   ├── test_movement_decoder.py
│   │   ├── test_emotion_classifier.py
│   │   ├── test_preprocessing.py
│   │   └── test_model_loader.py
│   ├── api/
│   │   ├── test_endpoints.py
│   │   ├── test_middleware.py
│   │   ├── test_validators.py
│   │   └── test_serializers.py
│   └── storage/
│       ├── test_timescale_adapter.py
│       ├── test_redis_cache.py
│       ├── test_s3_storage.py
│       └── test_query_builder.py
├── fixtures/                # Test data
│   ├── neural_data/
│   │   ├── eeg_samples.npy
│   │   ├── emg_samples.npy
│   │   └── ecg_samples.npy
│   ├── device_configs/
│   │   └── test_devices.json
│   └── ml_models/
│       └── test_weights.h5
├── mocks/                   # Mock implementations
│   ├── __init__.py
│   ├── device_mocks.py
│   ├── storage_mocks.py
│   ├── ml_mocks.py
│   └── external_service_mocks.py
├── factories/               # Test data factories
│   ├── __init__.py
│   ├── neural_data_factory.py
│   ├── session_factory.py
│   ├── device_factory.py
│   └── user_factory.py
├── utils/                   # Testing utilities
│   ├── __init__.py
│   ├── assertions.py
│   ├── helpers.py
│   ├── benchmarks.py
│   └── coverage.py
└── conftest.py              # pytest configuration
```

### Core Testing Implementation

```python
# tests/conftest.py - pytest configuration
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
import numpy as np
from pathlib import Path

# Configure pytest plugins
pytest_plugins = [
    "pytest_asyncio",
    "pytest_benchmark",
    "pytest_cov",
    "pytest_mock",
    "pytest_timeout",
]

# Test configuration
@pytest.fixture(scope="session")
def test_config():
    """Global test configuration"""
    return {
        "neural_data_path": Path(__file__).parent / "fixtures" / "neural_data",
        "sample_rate": 250,
        "num_channels": 8,
        "test_duration": 10,  # seconds
        "timeout": 30,  # seconds per test
    }

# Event loop for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Neural data fixtures
@pytest.fixture
def sample_eeg_data(test_config):
    """Generate sample EEG data"""
    samples = test_config["sample_rate"] * test_config["test_duration"]
    channels = test_config["num_channels"]

    # Generate realistic EEG data with different frequency components
    time = np.linspace(0, test_config["test_duration"], samples)
    data = np.zeros((channels, samples))

    for ch in range(channels):
        # Alpha (8-12 Hz)
        data[ch] += 10 * np.sin(2 * np.pi * 10 * time + np.random.rand())
        # Beta (12-30 Hz)
        data[ch] += 5 * np.sin(2 * np.pi * 20 * time + np.random.rand())
        # Noise
        data[ch] += np.random.normal(0, 2, samples)

    return data

# Mock fixtures
@pytest.fixture
def mock_device():
    """Mock BCI device"""
    device = MagicMock()
    device.name = "Test Device"
    device.sample_rate = 250
    device.channels = 8
    device.is_connected = True
    device.get_data = MagicMock(return_value=np.random.randn(8, 250))
    device.check_impedance = AsyncMock(return_value={i: 5000 for i in range(8)})
    return device

@pytest.fixture
def mock_storage():
    """Mock storage backend"""
    storage = AsyncMock()
    storage.save_data = AsyncMock(return_value="session-123")
    storage.get_data = AsyncMock(return_value=np.random.randn(8, 2500))
    storage.query = AsyncMock(return_value=[])
    return storage

# Benchmark fixtures
@pytest.fixture
def benchmark_data():
    """Large dataset for performance testing"""
    return np.random.randn(64, 250000)  # 64 channels, 1000 seconds

# Cleanup
@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup after each test"""
    yield
    # Clear any test files
    import shutil
    test_output = Path("test_output")
    if test_output.exists():
        shutil.rmtree(test_output)
```

## Implementation Plan

### Phase 18.1: Core Unit Tests (1.5 days)

**Senior Test Engineer Tasks:**

1. **Signal Processing Tests** (6 hours)

   ```python
   # tests/unit/neural_processor/test_signal_processing.py
   import pytest
   import numpy as np
   from numpy.testing import assert_array_almost_equal
   from src.neural_processor.signal_processing import (
       BandpassFilter, NotchFilter, SignalProcessor,
       ArtifactRemover, Resampler
   )

   class TestBandpassFilter:
       """Test bandpass filter implementation"""

       @pytest.fixture
       def filter(self):
           return BandpassFilter(low_freq=8, high_freq=30, sample_rate=250)

       def test_filter_initialization(self, filter):
           """Test filter creates correct coefficients"""
           assert filter.order == 4
           assert len(filter.b) == filter.order + 1
           assert len(filter.a) == filter.order + 1

       def test_filter_frequency_response(self, filter, sample_eeg_data):
           """Test filter removes correct frequencies"""
           # Apply filter
           filtered = filter.apply(sample_eeg_data)

           # Check power spectral density
           from scipy.signal import welch
           freqs, psd_original = welch(sample_eeg_data[0], fs=250)
           freqs, psd_filtered = welch(filtered[0], fs=250)

           # Check attenuation outside passband
           low_freq_idx = np.where(freqs < 8)[0]
           high_freq_idx = np.where(freqs > 30)[0]

           assert np.mean(psd_filtered[low_freq_idx]) < 0.1 * np.mean(psd_original[low_freq_idx])
           assert np.mean(psd_filtered[high_freq_idx]) < 0.1 * np.mean(psd_original[high_freq_idx])

       @pytest.mark.parametrize("low,high", [
           (0.5, 50),
           (1, 100),
           (4, 40),
       ])
       def test_filter_parameters(self, low, high, sample_eeg_data):
           """Test filter with different parameters"""
           filter = BandpassFilter(low, high, 250)
           filtered = filter.apply(sample_eeg_data)

           assert filtered.shape == sample_eeg_data.shape
           assert not np.any(np.isnan(filtered))

       def test_filter_edge_cases(self, filter):
           """Test filter handles edge cases"""
           # Empty data
           with pytest.raises(ValueError):
               filter.apply(np.array([]))

           # Single sample
           single = np.array([[1.0]])
           result = filter.apply(single)
           assert result.shape == single.shape

           # Wrong dimensions
           with pytest.raises(ValueError):
               filter.apply(np.array([1, 2, 3]))  # 1D array

   class TestArtifactRemover:
       """Test artifact removal algorithms"""

       @pytest.fixture
       def remover(self):
           return ArtifactRemover(method="ica")

       def test_eye_blink_removal(self, remover, sample_eeg_data):
           """Test eye blink artifact removal"""
           # Add synthetic eye blink
           blink_times = [2.0, 5.0, 8.0]  # seconds
           for t in blink_times:
               idx = int(t * 250)
               # Eye blinks affect frontal channels more
               sample_eeg_data[0:2, idx-25:idx+25] += 50 * np.sin(np.linspace(0, np.pi, 50))

           # Remove artifacts
           cleaned = remover.remove_artifacts(sample_eeg_data, artifact_type="eye_blink")

           # Check amplitude reduction at blink times
           for t in blink_times:
               idx = int(t * 250)
               original_power = np.mean(sample_eeg_data[0, idx-25:idx+25]**2)
               cleaned_power = np.mean(cleaned[0, idx-25:idx+25]**2)
               assert cleaned_power < 0.5 * original_power

       @pytest.mark.benchmark
       def test_artifact_removal_performance(self, remover, benchmark_data, benchmark):
           """Benchmark artifact removal performance"""
           result = benchmark(remover.remove_artifacts, benchmark_data)
           assert result.shape == benchmark_data.shape
   ```

2. **Device Manager Tests** (6 hours)

   ```python
   # tests/unit/device_manager/test_device_connection.py
   import pytest
   from unittest.mock import MagicMock, patch, AsyncMock
   from src.device_manager import DeviceManager, DeviceConnection
   from src.device_manager.exceptions import (
       DeviceNotFoundError, ConnectionError, DeviceTimeoutError
   )

   @pytest.mark.asyncio
   class TestDeviceConnection:
       """Test device connection handling"""

       @pytest.fixture
       async def device_manager(self):
           manager = DeviceManager()
           await manager.initialize()
           return manager

       async def test_connect_success(self, device_manager, mock_device):
           """Test successful device connection"""
           with patch('src.device_manager.device_factory.create_device', return_value=mock_device):
               device = await device_manager.connect_device(
                   device_type="openbci",
                   port="/dev/ttyUSB0"
               )

               assert device.is_connected
               assert device in device_manager.active_devices
               mock_device.connect.assert_called_once()

       async def test_connect_timeout(self, device_manager):
           """Test connection timeout handling"""
           mock_device = AsyncMock()
           mock_device.connect.side_effect = asyncio.TimeoutError()

           with patch('src.device_manager.device_factory.create_device', return_value=mock_device):
               with pytest.raises(DeviceTimeoutError):
                   await device_manager.connect_device(
                       device_type="openbci",
                       port="/dev/ttyUSB0",
                       timeout=1.0
                   )

       async def test_reconnect_on_disconnect(self, device_manager, mock_device):
           """Test automatic reconnection"""
           mock_device.is_connected = True

           with patch('src.device_manager.device_factory.create_device', return_value=mock_device):
               device = await device_manager.connect_device(
                   device_type="openbci",
                   port="/dev/ttyUSB0",
                   auto_reconnect=True
               )

               # Simulate disconnect
               mock_device.is_connected = False
               await device_manager._handle_disconnect(device)

               # Should attempt reconnection
               assert mock_device.connect.call_count >= 2

       @pytest.mark.parametrize("error_type,expected_exception", [
           (SerialException, ConnectionError),
           (BTLEException, ConnectionError),
           (USBError, DeviceNotFoundError),
       ])
       async def test_connection_errors(self, device_manager, error_type, expected_exception):
           """Test various connection error scenarios"""
           mock_device = AsyncMock()
           mock_device.connect.side_effect = error_type("Connection failed")

           with patch('src.device_manager.device_factory.create_device', return_value=mock_device):
               with pytest.raises(expected_exception):
                   await device_manager.connect_device(
                       device_type="openbci",
                       port="/dev/ttyUSB0"
                   )
   ```

3. **ML Model Tests** (4 hours)

   ```python
   # tests/unit/ml_models/test_movement_decoder.py
   import pytest
   import numpy as np
   import torch
   from src.ml_models.movement_decoder import MovementDecoder, preprocess_input

   class TestMovementDecoder:
       """Test movement decoder model"""

       @pytest.fixture
       def model(self):
           return MovementDecoder(
               input_channels=8,
               num_classes=3,  # x, y, z
               sequence_length=250
           )

       @pytest.fixture
       def sample_input(self):
           # Batch of 10, 8 channels, 250 time points
           return torch.randn(10, 8, 250)

       def test_model_output_shape(self, model, sample_input):
           """Test model produces correct output shape"""
           output = model(sample_input)
           assert output.shape == (10, 3)  # Batch size, num_classes

       def test_model_training_step(self, model, sample_input):
           """Test single training step"""
           model.train()
           optimizer = torch.optim.Adam(model.parameters())

           # Forward pass
           output = model(sample_input)
           target = torch.randn(10, 3)
           loss = torch.nn.functional.mse_loss(output, target)

           # Backward pass
           optimizer.zero_grad()
           loss.backward()
           optimizer.step()

           # Check gradients were computed
           for param in model.parameters():
               assert param.grad is not None
               assert not torch.isnan(param.grad).any()

       @pytest.mark.parametrize("batch_size", [1, 16, 32, 64])
       def test_batch_sizes(self, model, batch_size):
           """Test model handles different batch sizes"""
           input_data = torch.randn(batch_size, 8, 250)
           output = model(input_data)
           assert output.shape[0] == batch_size

       def test_preprocessing(self):
           """Test input preprocessing"""
           raw_data = np.random.randn(8, 1000)
           processed = preprocess_input(raw_data, target_length=250)

           assert processed.shape == (8, 250)
           assert np.abs(processed.mean()) < 0.1  # Centered
           assert 0.9 < processed.std() < 1.1  # Normalized
   ```

### Phase 18.2: Storage & API Tests (1 day)

**Test Engineer Tasks:**

1. **Storage Layer Tests** (4 hours)

   ```python
   # tests/unit/storage/test_timescale_adapter.py
   import pytest
   from datetime import datetime, timedelta
   from src.storage.timescale_adapter import TimescaleAdapter
   from src.storage.exceptions import StorageError, QueryError

   @pytest.mark.asyncio
   class TestTimescaleAdapter:
       """Test TimescaleDB adapter"""

       @pytest.fixture
       async def adapter(self, mock_db_pool):
           adapter = TimescaleAdapter(pool=mock_db_pool)
           await adapter.initialize()
           return adapter

       async def test_save_neural_data(self, adapter, sample_eeg_data):
           """Test saving neural data"""
           session_id = await adapter.save_neural_data(
               data=sample_eeg_data,
               metadata={
                   "patient_id": "P001",
                   "device_type": "openbci",
                   "sample_rate": 250
               }
           )

           assert session_id is not None
           assert adapter.pool.execute.called

       async def test_query_time_range(self, adapter):
           """Test querying data by time range"""
           start_time = datetime.now() - timedelta(hours=1)
           end_time = datetime.now()

           result = await adapter.query_time_range(
               session_id="test-session",
               start_time=start_time,
               end_time=end_time,
               channels=[0, 1, 2]
           )

           assert result is not None
           query = adapter.pool.fetch.call_args[0][0]
           assert "WHERE time >= $1 AND time <= $2" in query

       async def test_compression_ratio(self, adapter, benchmark_data):
           """Test data compression effectiveness"""
           original_size = benchmark_data.nbytes

           compressed = await adapter._compress_data(benchmark_data)
           compressed_size = len(compressed)

           compression_ratio = original_size / compressed_size
           assert compression_ratio > 2.0  # At least 2x compression

       @pytest.mark.benchmark
       async def test_bulk_insert_performance(self, adapter, benchmark_data, benchmark):
           """Benchmark bulk insert performance"""
           async def bulk_insert():
               await adapter.save_neural_data(
                   data=benchmark_data,
                   metadata={"test": True}
               )

           await benchmark(bulk_insert)
   ```

2. **API Endpoint Tests** (4 hours)

   ```python
   # tests/unit/api/test_endpoints.py
   import pytest
   from fastapi.testclient import TestClient
   from unittest.mock import patch, MagicMock
   from src.api.main import app
   from src.api.models import SessionCreate, DeviceStatus

   @pytest.fixture
   def client():
       return TestClient(app)

   @pytest.fixture
   def auth_headers():
       return {"Authorization": "Bearer test-token"}

   class TestNeuralAPI:
       """Test REST API endpoints"""

       def test_health_check(self, client):
           """Test health endpoint"""
           response = client.get("/health")
           assert response.status_code == 200
           assert response.json()["status"] == "healthy"

       def test_create_session(self, client, auth_headers):
           """Test session creation"""
           with patch('src.api.services.session_service.create') as mock_create:
               mock_create.return_value = {
                   "id": "session-123",
                   "status": "active"
               }

               response = client.post(
                   "/api/v2/sessions",
                   json={
                       "patient_id": "P001",
                       "device_id": "device-123",
                       "duration": 300
                   },
                   headers=auth_headers
               )

               assert response.status_code == 201
               assert response.json()["id"] == "session-123"

       @pytest.mark.parametrize("invalid_data,expected_error", [
           ({"patient_id": ""}, "patient_id must not be empty"),
           ({"duration": -1}, "duration must be positive"),
           ({"device_id": None}, "device_id is required"),
       ])
       def test_validation_errors(self, client, auth_headers, invalid_data, expected_error):
           """Test input validation"""
           base_data = {
               "patient_id": "P001",
               "device_id": "device-123",
               "duration": 300
           }
           base_data.update(invalid_data)

           response = client.post(
               "/api/v2/sessions",
               json=base_data,
               headers=auth_headers
           )

           assert response.status_code == 422
           assert expected_error in response.text

       def test_rate_limiting(self, client, auth_headers):
           """Test rate limiting"""
           # Make multiple requests
           for i in range(101):
               response = client.get("/api/v2/devices", headers=auth_headers)

               if i < 100:
                   assert response.status_code == 200
               else:
                   assert response.status_code == 429  # Too many requests
   ```

### Phase 18.3: Test Infrastructure (1 day)

**Test Engineer Tasks:**

1. **Test Factories** (4 hours)

   ```python
   # tests/factories/neural_data_factory.py
   import factory
   import numpy as np
   from datetime import datetime, timedelta
   from src.models import NeuralSession, NeuralData

   class NeuralDataFactory(factory.Factory):
       """Factory for generating test neural data"""

       class Meta:
           model = NeuralData

       @factory.lazy_attribute
       def data(self):
           """Generate realistic neural data"""
           duration = 10  # seconds
           sample_rate = 250
           channels = 8

           samples = duration * sample_rate
           data = np.zeros((channels, samples))

           # Add different frequency components
           time = np.linspace(0, duration, samples)

           for ch in range(channels):
               # Delta (0.5-4 Hz)
               data[ch] += 20 * np.sin(2 * np.pi * 2 * time)
               # Theta (4-8 Hz)
               data[ch] += 15 * np.sin(2 * np.pi * 6 * time)
               # Alpha (8-12 Hz)
               data[ch] += 10 * np.sin(2 * np.pi * 10 * time)
               # Beta (12-30 Hz)
               data[ch] += 5 * np.sin(2 * np.pi * 20 * time)
               # Gamma (30-100 Hz)
               data[ch] += 2 * np.sin(2 * np.pi * 50 * time)
               # Noise
               data[ch] += np.random.normal(0, 1, samples)

           return data

       @factory.lazy_attribute
       def timestamps(self):
           start = datetime.now()
           duration = self.data.shape[1] / 250  # Assuming 250 Hz
           return np.linspace(0, duration, self.data.shape[1])

       sample_rate = 250
       channels = factory.LazyAttribute(lambda o: o.data.shape[0])
       duration = factory.LazyAttribute(lambda o: o.data.shape[1] / o.sample_rate)

   class NeuralSessionFactory(factory.Factory):
       """Factory for generating test sessions"""

       class Meta:
           model = NeuralSession

       id = factory.Sequence(lambda n: f"session-{n}")
       patient_id = factory.Faker('uuid4')
       device_id = factory.Faker('uuid4')
       start_time = factory.Faker('date_time_this_month')

       @factory.lazy_attribute
       def end_time(self):
           return self.start_time + timedelta(minutes=30)

       status = "completed"
       metadata = factory.Dict({
           "technician": factory.Faker('name'),
           "location": factory.Faker('city'),
           "notes": factory.Faker('text', max_nb_chars=200)
       })

       neural_data = factory.SubFactory(NeuralDataFactory)

   # Specialized factories
   class ArtifactDataFactory(NeuralDataFactory):
       """Generate data with artifacts"""

       @factory.post_generation
       def add_artifacts(self, create, extracted, **kwargs):
           if not create:
               return

           # Add eye blink artifacts
           blink_times = np.random.choice(range(100, 2400), 5)
           for t in blink_times:
               self.data[0:2, t-25:t+25] += 50 * np.sin(np.linspace(0, np.pi, 50))

           # Add movement artifacts
           movement_start = np.random.randint(500, 1500)
           self.data[:, movement_start:movement_start+100] += \
               20 * np.random.randn(self.channels, 100)
   ```

2. **Mock Implementations** (4 hours)

   ```python
   # tests/mocks/external_service_mocks.py
   from unittest.mock import MagicMock, AsyncMock
   import numpy as np
   from datetime import datetime

   class MockVertexAIClient:
       """Mock Google Vertex AI client"""

       def __init__(self):
           self.predictions = []
           self.models = {}

       async def predict(self, model_name: str, instances: list):
           """Mock prediction endpoint"""
           # Simulate processing time
           await asyncio.sleep(0.1)

           # Return mock predictions
           if "movement" in model_name:
               # Movement prediction (x, y, z)
               return [{"predictions": [0.1, -0.2, 0.3]} for _ in instances]
           elif "emotion" in model_name:
               # Emotion classification
               return [{
                   "predictions": {
                       "happy": 0.7,
                       "sad": 0.1,
                       "neutral": 0.2
                   }
               } for _ in instances]

       def deploy_model(self, model_path: str, endpoint_name: str):
           """Mock model deployment"""
           self.models[endpoint_name] = {
               "path": model_path,
               "deployed_at": datetime.now(),
               "status": "ready"
           }
           return endpoint_name

   class MockKafkaProducer:
       """Mock Kafka producer for testing"""

       def __init__(self):
           self.messages = []
           self.is_connected = True

       async def send(self, topic: str, value: bytes, key: bytes = None):
           """Mock message sending"""
           if not self.is_connected:
               raise Exception("Producer not connected")

           self.messages.append({
               "topic": topic,
               "key": key,
               "value": value,
               "timestamp": datetime.now()
           })

           # Return mock future
           future = AsyncMock()
           future.get.return_value = MagicMock(
               offset=len(self.messages) - 1,
               partition=0
           )
           return future

       def flush(self):
           """Mock flush operation"""
           pass

   def create_mock_redis():
       """Create mock Redis client"""
       redis = AsyncMock()
       redis.data = {}  # In-memory storage

       async def mock_get(key):
           return redis.data.get(key)

       async def mock_set(key, value, ex=None):
           redis.data[key] = value
           return True

       async def mock_delete(*keys):
           for key in keys:
               redis.data.pop(key, None)
           return len(keys)

       redis.get = mock_get
       redis.set = mock_set
       redis.delete = mock_delete
       redis.exists = AsyncMock(side_effect=lambda k: k in redis.data)

       return redis
   ```

### Phase 18.4: Test Automation (0.5 days)

**DevOps Engineer Tasks:**

1. **Test Runner Configuration** (2 hours)

   ```python
   # pytest.ini - pytest configuration
   [pytest]
   minversion = 7.0
   testpaths = tests
   python_files = test_*.py
   python_classes = Test*
   python_functions = test_*

   # Test markers
   markers =
       unit: Unit tests
       integration: Integration tests
       benchmark: Performance benchmarks
       slow: Slow running tests
       flaky: Flaky tests that may need retry

   # Coverage settings
   addopts =
       --strict-markers
       --cov=src
       --cov-branch
       --cov-report=term-missing:skip-covered
       --cov-report=html
       --cov-report=xml
       --cov-fail-under=85
       -vv

   # Async settings
   asyncio_mode = auto

   # Timeout
   timeout = 300
   timeout_method = thread

   # Parallel execution
   workers = auto
   ```

2. **Mutation Testing** (2 hours)

   ```yaml
   # .mutmut.yml - Mutation testing configuration
   paths_to_mutate: src/

   backup: False
   runner: pytest -x -q

   tests_dir: tests/unit/

   dict_synonyms:
     - Struct
     - NamedStruct
   ```

### Phase 18.5: Test Reporting (0.5 days)

**Test Engineer Tasks:**

1. **Coverage Reports** (2 hours)

   ```python
   # tests/utils/coverage.py
   import coverage
   import json
   from pathlib import Path

   class CoverageReporter:
       """Generate detailed coverage reports"""

       def __init__(self, source_dir="src", min_coverage=85):
           self.source_dir = source_dir
           self.min_coverage = min_coverage
           self.cov = coverage.Coverage(
               source=[source_dir],
               branch=True
           )

       def generate_report(self):
           """Generate coverage report"""
           self.cov.load()

           # Generate reports
           print("\n" + "=" * 70)
           print("COVERAGE REPORT")
           print("=" * 70)

           # Console report
           self.cov.report()

           # HTML report
           self.cov.html_report(directory="htmlcov")

           # JSON report for CI
           self.cov.json_report(outfile="coverage.json")

           # Check minimum coverage
           total_coverage = self.cov.report(show_missing=False)

           if total_coverage < self.min_coverage:
               print(f"\nWARNING: Coverage {total_coverage:.1f}% is below minimum {self.min_coverage}%")
               return False

           return True

       def find_untested_code(self):
           """Find code without tests"""
           analysis = self.cov.analysis2(self.source_dir)

           untested_files = []
           for filename, executable, excluded, missing, _ in analysis:
               if missing:
                   untested_files.append({
                       "file": filename,
                       "missing_lines": missing,
                       "coverage": (len(executable) - len(missing)) / len(executable) * 100
                   })

           return sorted(untested_files, key=lambda x: x["coverage"])
   ```

2. **Test Report Generator** (2 hours)

   ```python
   # Generate test execution report
   import pytest
   import json
   from datetime import datetime

   class TestReportPlugin:
       """Custom pytest plugin for test reporting"""

       def __init__(self):
           self.results = []
           self.start_time = None

       def pytest_sessionstart(self, session):
           self.start_time = datetime.now()

       def pytest_runtest_logreport(self, report):
           if report.when == "call":
               self.results.append({
                   "test": report.nodeid,
                   "outcome": report.outcome,
                   "duration": report.duration,
                   "error": str(report.longrepr) if report.failed else None
               })

       def pytest_sessionfinish(self, session):
           duration = (datetime.now() - self.start_time).total_seconds()

           report = {
               "summary": {
                   "total": len(self.results),
                   "passed": sum(1 for r in self.results if r["outcome"] == "passed"),
                   "failed": sum(1 for r in self.results if r["outcome"] == "failed"),
                   "skipped": sum(1 for r in self.results if r["outcome"] == "skipped"),
                   "duration": duration
               },
               "results": self.results,
               "timestamp": datetime.now().isoformat()
           }

           with open("test-report.json", "w") as f:
               json.dump(report, f, indent=2)
   ```

## Testing Best Practices

### Test Organization

```python
# Good test structure
class TestComponentName:
    """Group related tests in classes"""

    def test_normal_operation(self):
        """Test happy path first"""
        pass

    def test_edge_cases(self):
        """Test boundary conditions"""
        pass

    def test_error_handling(self):
        """Test error scenarios"""
        pass

    @pytest.mark.slow
    def test_performance(self):
        """Mark slow tests"""
        pass
```

### Assertion Patterns

```python
# Custom assertions
def assert_neural_data_valid(data):
    """Custom assertion for neural data validation"""
    assert isinstance(data, np.ndarray)
    assert data.ndim == 2
    assert not np.any(np.isnan(data))
    assert not np.any(np.isinf(data))
    assert np.all(np.abs(data) < 1000)  # Reasonable amplitude
```

## Success Criteria

### Coverage Success

- [ ] Overall coverage >85%
- [ ] Critical path coverage >95%
- [ ] All edge cases tested
- [ ] No untested exceptions
- [ ] Branch coverage >80%

### Quality Success

- [ ] All tests passing
- [ ] No flaky tests
- [ ] Test execution <5 minutes
- [ ] Mutation score >75%
- [ ] Clear test documentation

### Automation Success

- [ ] Tests run on every commit
- [ ] Parallel execution working
- [ ] Coverage reports generated
- [ ] Failed test notifications
- [ ] Performance benchmarks tracked

## Cost Estimation

### Infrastructure Costs (Monthly)

- **CI/CD compute**: Included in Phase 17
- **Test data storage**: $50/month
- **Performance monitoring**: $100/month
- **Total**: ~$150/month

### Development Resources

- **Senior Test Engineer**: 4-5 days
- **Backend Engineers**: 2 days (writing tests)
- **DevOps Engineer**: 1 day
- **Documentation**: 0.5 days

## Dependencies

### External Dependencies

- **pytest**: 7.4+
- **pytest plugins**: asyncio, cov, mock, benchmark
- **Factory Boy**: Test data generation
- **Faker**: Realistic test data
- **Hypothesis**: Property-based testing

### Internal Dependencies

- **Application code**: Testable architecture
- **Test database**: Isolated test environment
- **Mock services**: External service mocks
- **CI/CD pipeline**: Test execution

## Risk Mitigation

### Technical Risks

1. **Flaky Tests**: Retry mechanisms, better isolation
2. **Slow Tests**: Parallel execution, test optimization
3. **Coverage Gaps**: Mutation testing, code analysis
4. **Mock Accuracy**: Contract testing, integration tests

### Process Risks

1. **Test Maintenance**: Clear ownership, regular reviews
2. **False Positives**: Better assertions, stable test data
3. **Performance Regression**: Continuous benchmarking
4. **Knowledge Gaps**: Test documentation, examples

---

**Next Phase**: Phase 19 - Integration Testing
**Dependencies**: Unit tests, test infrastructure
**Review Date**: Implementation completion + 1 week
