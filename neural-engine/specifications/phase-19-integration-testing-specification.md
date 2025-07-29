# Phase 19: Integration Testing Specification

**Version**: 1.0.0
**Created**: 2025-07-29
**GitHub Issue**: #159 (to be created)
**Priority**: HIGH
**Duration**: 3-4 days
**Lead**: Senior QA Engineer

## Executive Summary

Phase 19 implements comprehensive integration testing for the NeuraScale Neural Engine, validating interactions between components, external services, and end-to-end workflows through automated test suites and continuous validation.

## Functional Requirements

### 1. Integration Test Coverage

- **Service Integration**: Microservice communication testing
- **Database Integration**: Data persistence and retrieval
- **External Services**: Third-party API integration
- **Message Queue**: Event-driven architecture testing
- **End-to-End Workflows**: Complete user scenarios

### 2. Test Environment

- **Test Containers**: Dockerized test environment
- **Service Virtualization**: Mock external dependencies
- **Test Data Management**: Realistic test datasets
- **Environment Isolation**: Parallel test execution
- **Configuration Management**: Environment-specific configs

### 3. Test Automation

- **Contract Testing**: API contract validation
- **Performance Testing**: Load and stress testing
- **Chaos Engineering**: Failure scenario testing
- **Security Testing**: Integration security validation
- **Monitoring**: Test execution monitoring

## Technical Architecture

### Integration Test Structure

```
tests/integration/
├── services/               # Service integration tests
│   ├── test_neural_processor_integration.py
│   ├── test_device_manager_integration.py
│   ├── test_api_gateway_integration.py
│   ├── test_ml_pipeline_integration.py
│   └── test_storage_service_integration.py
├── workflows/              # End-to-end workflow tests
│   ├── test_recording_workflow.py
│   ├── test_analysis_workflow.py
│   ├── test_clinical_workflow.py
│   ├── test_ml_training_workflow.py
│   └── test_export_workflow.py
├── external/               # External service tests
│   ├── test_vertex_ai_integration.py
│   ├── test_gcs_integration.py
│   ├── test_kafka_integration.py
│   └── test_auth_provider_integration.py
├── contracts/              # Contract tests
│   ├── api/
│   │   ├── test_rest_api_contracts.py
│   │   └── test_graphql_contracts.py
│   └── events/
│       ├── test_kafka_contracts.py
│       └── test_websocket_contracts.py
├── performance/            # Performance tests
│   ├── load/
│   │   ├── test_api_load.py
│   │   └── test_streaming_load.py
│   ├── stress/
│   │   └── test_system_limits.py
│   └── scenarios/
│       └── test_concurrent_users.py
├── chaos/                  # Chaos engineering tests
│   ├── test_service_failures.py
│   ├── test_network_issues.py
│   ├── test_resource_exhaustion.py
│   └── test_data_corruption.py
├── fixtures/               # Integration test fixtures
│   ├── docker/
│   │   └── docker-compose.test.yml
│   ├── data/
│   │   └── test_datasets.sql
│   └── configs/
│       └── test_configs.yaml
└── utils/                  # Test utilities
    ├── containers.py
    ├── data_generators.py
    ├── assertions.py
    └── monitoring.py
```

### Core Integration Test Framework

```python
# tests/integration/conftest.py
import pytest
import asyncio
import docker
import time
from pathlib import Path
from testcontainers.compose import DockerCompose
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from testcontainers.kafka import KafkaContainer

# Integration test configuration
@pytest.fixture(scope="session")
def docker_compose():
    """Start all services using docker-compose"""
    compose_file = Path(__file__).parent / "fixtures" / "docker" / "docker-compose.test.yml"

    with DockerCompose(
        filepath=str(compose_file.parent),
        compose_file_name=compose_file.name,
        pull=True,
        build=True
    ) as compose:
        # Wait for services to be healthy
        compose.wait_for("http://localhost:8080/health")
        yield compose

@pytest.fixture(scope="session")
def postgres_container():
    """PostgreSQL test container"""
    with PostgresContainer(
        image="timescale/timescaledb:2.13.0-pg16",
        user="test",
        password="test",
        dbname="neural_test"
    ) as postgres:
        # Initialize schema
        conn = postgres.get_connection_url()
        run_migrations(conn)
        yield postgres

@pytest.fixture(scope="session")
def kafka_container():
    """Kafka test container"""
    with KafkaContainer(
        image="confluentinc/cp-kafka:7.5.0"
    ) as kafka:
        # Create test topics
        create_test_topics(kafka.get_bootstrap_server())
        yield kafka

@pytest.fixture
async def test_client(docker_compose):
    """HTTP client for API testing"""
    from httpx import AsyncClient

    async with AsyncClient(
        base_url="http://localhost:8080",
        timeout=30.0
    ) as client:
        # Wait for API to be ready
        for _ in range(30):
            try:
                response = await client.get("/health")
                if response.status_code == 200:
                    break
            except:
                pass
            await asyncio.sleep(1)

        yield client

@pytest.fixture
async def authenticated_client(test_client):
    """Authenticated API client"""
    # Get test token
    response = await test_client.post(
        "/auth/token",
        json={"username": "test_user", "password": "test_pass"}
    )
    token = response.json()["access_token"]

    test_client.headers["Authorization"] = f"Bearer {token}"
    yield test_client

# Test data fixtures
@pytest.fixture
def sample_recording_data():
    """Generate sample recording data"""
    import numpy as np

    return {
        "device_id": "test-device-001",
        "patient_id": "test-patient-001",
        "duration": 300,  # 5 minutes
        "sample_rate": 250,
        "channels": 8,
        "data": np.random.randn(8, 75000).tolist()  # 5 min of data
    }

@pytest.fixture
async def test_database(postgres_container):
    """Test database connection"""
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine(
        postgres_container.get_connection_url().replace("postgresql://", "postgresql+asyncpg://")
    )

    async with engine.begin() as conn:
        # Clean database before test
        await conn.execute("TRUNCATE TABLE sessions, neural_data CASCADE")

    yield engine

    await engine.dispose()
```

## Implementation Plan

### Phase 19.1: Service Integration Tests (1 day)

**Senior QA Engineer Tasks:**

1. **Microservice Communication Tests** (4 hours)

   ```python
   # tests/integration/services/test_neural_processor_integration.py
   import pytest
   import asyncio
   import numpy as np
   from datetime import datetime

   @pytest.mark.integration
   class TestNeuralProcessorIntegration:
       """Test neural processor service integration"""

       async def test_data_ingestion_pipeline(self, authenticated_client, kafka_container):
           """Test complete data ingestion pipeline"""
           # Start recording session
           response = await authenticated_client.post(
               "/api/v2/sessions",
               json={
                   "patient_id": "P001",
                   "device_id": "D001",
                   "duration": 60
               }
           )
           assert response.status_code == 201
           session_id = response.json()["id"]

           # Send data through Kafka
           producer = create_kafka_producer(kafka_container.get_bootstrap_server())

           for i in range(10):
               data_packet = {
                   "session_id": session_id,
                   "timestamp": datetime.now().isoformat(),
                   "data": np.random.randn(8, 250).tolist()
               }

               await producer.send(
                   "neural-data",
                   value=json.dumps(data_packet).encode()
               )
               await asyncio.sleep(0.1)

           # Verify data was processed
           await asyncio.sleep(2)  # Processing time

           response = await authenticated_client.get(
               f"/api/v2/sessions/{session_id}/data"
           )
           assert response.status_code == 200

           data = response.json()
           assert len(data["chunks"]) == 10
           assert data["total_samples"] == 2500

       async def test_real_time_processing(self, authenticated_client, websocket_client):
           """Test real-time data processing"""
           # Connect WebSocket
           async with websocket_client.connect(
               f"/ws/sessions/{session_id}/stream"
           ) as websocket:
               # Send data
               for i in range(5):
                   await websocket.send_json({
                       "type": "data",
                       "payload": {
                           "timestamp": time.time(),
                           "data": np.random.randn(8, 250).tolist()
                       }
                   })

                   # Receive processed data
                   message = await websocket.receive_json()
                   assert message["type"] == "processed"
                   assert "features" in message["payload"]
                   assert "quality_score" in message["payload"]

       async def test_service_communication(self, authenticated_client):
           """Test inter-service communication"""
           # Create session that requires multiple services
           response = await authenticated_client.post(
               "/api/v2/sessions/analyze",
               json={
                   "session_id": "test-session",
                   "analyses": [
                       {"type": "spectral", "params": {}},
                       {"type": "connectivity", "params": {}},
                       {"type": "ml_prediction", "params": {"model": "emotion"}}
                   ]
               }
           )

           assert response.status_code == 202
           job_id = response.json()["job_id"]

           # Poll for completion
           for _ in range(30):
               response = await authenticated_client.get(
                   f"/api/v2/jobs/{job_id}"
               )
               if response.json()["status"] == "completed":
                   break
               await asyncio.sleep(1)

           assert response.json()["status"] == "completed"
           results = response.json()["results"]

           # Verify all analyses completed
           assert len(results) == 3
           assert all(r["status"] == "success" for r in results)
   ```

2. **Database Integration Tests** (4 hours)

   ```python
   # tests/integration/services/test_storage_integration.py
   import pytest
   from datetime import datetime, timedelta

   @pytest.mark.integration
   class TestStorageIntegration:
       """Test storage service integration"""

       async def test_timescale_integration(self, test_database, sample_recording_data):
           """Test TimescaleDB integration"""
           from src.storage.timescale_adapter import TimescaleAdapter

           adapter = TimescaleAdapter(test_database)

           # Save neural data
           session_id = await adapter.save_session(
               patient_id=sample_recording_data["patient_id"],
               device_id=sample_recording_data["device_id"],
               metadata={"test": True}
           )

           # Save time-series data
           await adapter.save_neural_data(
               session_id=session_id,
               data=np.array(sample_recording_data["data"]),
               timestamps=np.arange(0, 300, 0.004)  # 250Hz
           )

           # Query data
           data = await adapter.query_time_range(
               session_id=session_id,
               start_time=0,
               end_time=10,
               channels=[0, 1, 2]
           )

           assert data.shape == (3, 2500)  # 3 channels, 10 seconds

       async def test_redis_caching(self, redis_container, test_database):
           """Test Redis caching integration"""
           from src.storage.cache_manager import CacheManager

           cache = CacheManager(redis_url=redis_container.get_connection_url())

           # Test cache-aside pattern
           async def expensive_query():
               # Simulate expensive database query
               await asyncio.sleep(0.5)
               return {"result": "expensive_data"}

           # First call - cache miss
           start = time.time()
           result1 = await cache.get_or_set(
               "test_key",
               expensive_query,
               ttl=60
           )
           duration1 = time.time() - start

           # Second call - cache hit
           start = time.time()
           result2 = await cache.get_or_set(
               "test_key",
               expensive_query,
               ttl=60
           )
           duration2 = time.time() - start

           assert result1 == result2
           assert duration2 < duration1 * 0.1  # Much faster

       async def test_s3_integration(self, s3_container):
           """Test S3 storage integration"""
           from src.storage.s3_adapter import S3Adapter

           adapter = S3Adapter(
               endpoint_url=s3_container.get_connection_url(),
               bucket="neural-data-test"
           )

           # Upload large file
           large_data = np.random.randn(1000, 10000)  # ~80MB

           key = await adapter.upload_array(
               array=large_data,
               key="test-session/large-data.npy"
           )

           # Download and verify
           downloaded = await adapter.download_array(key)
           np.testing.assert_array_equal(large_data, downloaded)
   ```

### Phase 19.2: End-to-End Workflow Tests (1 day)

**QA Engineer Tasks:**

1. **Complete Recording Workflow** (4 hours)

   ```python
   # tests/integration/workflows/test_recording_workflow.py
   import pytest
   import asyncio

   @pytest.mark.integration
   @pytest.mark.e2e
   class TestRecordingWorkflow:
       """Test complete recording workflow"""

       async def test_full_recording_session(self, authenticated_client, mock_device):
           """Test complete recording session from start to finish"""

           # Step 1: Device discovery
           response = await authenticated_client.get("/api/v2/devices/discover")
           assert response.status_code == 200
           devices = response.json()["devices"]
           assert len(devices) > 0

           device_id = devices[0]["id"]

           # Step 2: Connect device
           response = await authenticated_client.post(
               f"/api/v2/devices/{device_id}/connect"
           )
           assert response.status_code == 200

           # Step 3: Check impedance
           response = await authenticated_client.post(
               f"/api/v2/devices/{device_id}/impedance-check"
           )
           assert response.status_code == 200
           impedances = response.json()["impedances"]
           assert all(z < 10000 for z in impedances.values())

           # Step 4: Create patient
           response = await authenticated_client.post(
               "/api/v2/patients",
               json={
                   "name": "Test Patient",
                   "dob": "1990-01-01",
                   "mrn": "TEST001"
               }
           )
           patient_id = response.json()["id"]

           # Step 5: Start session
           response = await authenticated_client.post(
               "/api/v2/sessions",
               json={
                   "patient_id": patient_id,
                   "device_id": device_id,
                   "protocol_id": "standard-eeg",
                   "duration": 300
               }
           )
           session_id = response.json()["id"]

           # Step 6: Monitor session
           async with authenticated_client.stream(
               "GET",
               f"/api/v2/sessions/{session_id}/status"
           ) as response:
               async for line in response.aiter_lines():
                   status = json.loads(line)
                   if status["state"] == "completed":
                       break
                   assert status["quality_score"] > 0.8

           # Step 7: Get results
           response = await authenticated_client.get(
               f"/api/v2/sessions/{session_id}"
           )
           session = response.json()

           assert session["status"] == "completed"
           assert session["duration"] >= 295  # Allow small variance
           assert session["sample_count"] > 0

           # Step 8: Run analysis
           response = await authenticated_client.post(
               f"/api/v2/sessions/{session_id}/analyze",
               json={"analysis_type": "standard"}
           )
           analysis_id = response.json()["id"]

           # Wait for analysis
           await self.wait_for_analysis(authenticated_client, analysis_id)

           # Step 9: Export data
           response = await authenticated_client.post(
               f"/api/v2/sessions/{session_id}/export",
               json={"format": "edf"}
           )
           export_url = response.json()["download_url"]

           # Verify export
           response = await authenticated_client.get(export_url)
           assert response.status_code == 200
           assert response.headers["content-type"] == "application/edf"

       async def test_error_recovery_workflow(self, authenticated_client):
           """Test workflow with errors and recovery"""

           # Start session
           response = await authenticated_client.post(
               "/api/v2/sessions",
               json={
                   "patient_id": "P001",
                   "device_id": "unreliable-device",
                   "duration": 60
               }
           )
           session_id = response.json()["id"]

           # Simulate device disconnection
           await asyncio.sleep(5)
           response = await authenticated_client.post(
               f"/api/v2/devices/unreliable-device/disconnect"
           )

           # Check session status
           response = await authenticated_client.get(
               f"/api/v2/sessions/{session_id}"
           )
           assert response.json()["status"] == "interrupted"

           # Attempt to resume
           response = await authenticated_client.post(
               f"/api/v2/sessions/{session_id}/resume"
           )
           assert response.status_code == 200

           # Verify resumed
           response = await authenticated_client.get(
               f"/api/v2/sessions/{session_id}"
           )
           assert response.json()["status"] == "active"
   ```

2. **Clinical Workflow Tests** (4 hours)

   ```python
   # tests/integration/workflows/test_clinical_workflow.py
   @pytest.mark.integration
   class TestClinicalWorkflow:
       """Test clinical workflow integration"""

       async def test_patient_session_lifecycle(self, authenticated_client):
           """Test complete patient session lifecycle"""

           # Create patient with consent
           response = await authenticated_client.post(
               "/api/v2/patients",
               json={
                   "name": "John Doe",
                   "dob": "1985-05-15",
                   "consents": [
                       {
                           "type": "data_collection",
                           "granted": True,
                           "expiry": "2026-01-01"
                       }
                   ]
               }
           )
           patient = response.json()

           # Schedule session
           response = await authenticated_client.post(
               "/api/v2/appointments",
               json={
                   "patient_id": patient["id"],
                   "datetime": "2025-02-01T10:00:00Z",
                   "duration": 60,
                   "type": "eeg_recording"
               }
           )
           appointment = response.json()

           # Check-in patient
           response = await authenticated_client.post(
               f"/api/v2/appointments/{appointment['id']}/checkin"
           )

           # Run clinical protocol
           response = await authenticated_client.post(
               "/api/v2/protocols/execute",
               json={
                   "protocol_id": "standard-clinical-eeg",
                   "patient_id": patient["id"],
                   "appointment_id": appointment["id"]
               }
           )
           execution_id = response.json()["id"]

           # Monitor protocol execution
           completed = False
           for _ in range(60):
               response = await authenticated_client.get(
                   f"/api/v2/protocols/executions/{execution_id}"
               )
               status = response.json()

               if status["state"] == "completed":
                   completed = True
                   break

               await asyncio.sleep(1)

           assert completed

           # Generate report
           response = await authenticated_client.post(
               f"/api/v2/protocols/executions/{execution_id}/report"
           )
           report_id = response.json()["id"]

           # Get report
           response = await authenticated_client.get(
               f"/api/v2/reports/{report_id}"
           )
           report = response.json()

           assert report["status"] == "final"
           assert "findings" in report
           assert "recommendations" in report
   ```

### Phase 19.3: External Service Tests (0.5 days)

**Integration Engineer Tasks:**

1. **Cloud Service Integration** (4 hours)

   ```python
   # tests/integration/external/test_vertex_ai_integration.py
   import pytest
   from unittest.mock import patch

   @pytest.mark.integration
   @pytest.mark.external
   class TestVertexAIIntegration:
       """Test Google Vertex AI integration"""

       @pytest.fixture
       def mock_vertex_ai(self):
           """Mock Vertex AI for testing"""
           with patch('google.cloud.aiplatform.Model') as mock:
               mock.predict.return_value = [
                   {"predictions": [0.1, 0.2, 0.7]}
               ]
               yield mock

       async def test_model_deployment(self, authenticated_client, mock_vertex_ai):
           """Test model deployment to Vertex AI"""

           # Upload model
           with open("test_model.h5", "rb") as f:
               response = await authenticated_client.post(
                   "/api/v2/models",
                   files={"model": f},
                   data={
                       "name": "test-classifier",
                       "type": "emotion_classifier",
                       "framework": "tensorflow"
                   }
               )

           model_id = response.json()["id"]

           # Deploy model
           response = await authenticated_client.post(
               f"/api/v2/models/{model_id}/deploy",
               json={
                   "endpoint_name": "test-endpoint",
                   "machine_type": "n1-standard-4",
                   "accelerator": "NVIDIA_TESLA_T4"
               }
           )

           deployment_id = response.json()["deployment_id"]

           # Wait for deployment
           deployed = await self.wait_for_deployment(
               authenticated_client,
               deployment_id
           )
           assert deployed

           # Test prediction
           response = await authenticated_client.post(
               f"/api/v2/models/{model_id}/predict",
               json={
                   "instances": [
                       {"data": np.random.randn(8, 250).tolist()}
                   ]
               }
           )

           predictions = response.json()["predictions"]
           assert len(predictions) == 1
           assert len(predictions[0]) == 3  # 3 emotion classes

       async def test_batch_prediction(self, authenticated_client):
           """Test batch prediction job"""

           # Submit batch job
           response = await authenticated_client.post(
               "/api/v2/ml/batch-predict",
               json={
                   "model_id": "emotion-classifier-v1",
                   "input_path": "gs://neural-data/batch-input/",
                   "output_path": "gs://neural-data/batch-output/",
                   "machine_type": "n1-highmem-8"
               }
           )

           job_id = response.json()["job_id"]

           # Monitor job
           completed = False
           for _ in range(300):  # 5 minutes max
               response = await authenticated_client.get(
                   f"/api/v2/ml/jobs/{job_id}"
               )

               status = response.json()["status"]
               if status == "completed":
                   completed = True
                   break
               elif status == "failed":
                   pytest.fail(f"Batch job failed: {response.json()}")

               await asyncio.sleep(1)

           assert completed
   ```

### Phase 19.4: Contract & Performance Tests (0.5 days)

**Performance Engineer Tasks:**

1. **API Contract Tests** (2 hours)

   ```python
   # tests/integration/contracts/test_api_contracts.py
   import pytest
   from pact import Consumer, Provider

   @pytest.mark.contract
   class TestAPIContracts:
       """Test API contracts between services"""

       def test_neural_processor_contract(self):
           """Test contract between API and neural processor"""

           pact = Consumer('API Gateway').has_pact_with(
               Provider('Neural Processor'),
               version='1.0.0'
           )

           with pact:
               # Define expected interaction
               pact.given(
                   'a session exists'
               ).upon_receiving(
                   'a request for session data'
               ).with_request(
                   'GET',
                   '/sessions/123/data'
               ).will_respond_with(
                   200,
                   headers={'Content-Type': 'application/json'},
                   body={
                       'session_id': '123',
                       'chunks': [],
                       'total_samples': 0
                   }
               )

               # Test the interaction
               response = requests.get(
                   pact.uri + '/sessions/123/data'
               )

               assert response.status_code == 200
               assert response.json()['session_id'] == '123'
   ```

2. **Load Testing** (2 hours)

   ```python
   # tests/integration/performance/test_api_load.py
   import pytest
   from locust import HttpUser, task, between

   class NeuralAPIUser(HttpUser):
       wait_time = between(1, 3)

       def on_start(self):
           # Login
           response = self.client.post(
               "/auth/token",
               json={"username": "load_test", "password": "test"}
           )
           self.token = response.json()["access_token"]
           self.client.headers["Authorization"] = f"Bearer {self.token}"

       @task(3)
       def list_sessions(self):
           self.client.get("/api/v2/sessions")

       @task(2)
       def get_session_data(self):
           session_id = "test-session-001"
           self.client.get(f"/api/v2/sessions/{session_id}/data")

       @task(1)
       def create_session(self):
           self.client.post(
               "/api/v2/sessions",
               json={
                   "patient_id": "P001",
                   "device_id": "D001",
                   "duration": 300
               }
           )

   @pytest.mark.load
   def test_api_load():
       """Run load test"""
       from locust.env import Environment
       from locust.stats import stats_printer

       env = Environment(user_classes=[NeuralAPIUser])
       env.create_local_runner()

       # Start test
       env.runner.start(100, spawn_rate=10)  # 100 users

       # Run for 60 seconds
       env.runner.greenlet.join(timeout=60)

       # Check results
       stats = env.stats

       # Performance assertions
       assert stats.total.fail_ratio < 0.01  # <1% failure rate
       assert stats.total.avg_response_time < 200  # <200ms average
       assert stats.total.get_response_time_percentile(0.95) < 500  # 95th percentile <500ms
   ```

## Testing Infrastructure

### Test Environment Setup

```yaml
# tests/integration/fixtures/docker/docker-compose.test.yml
version: "3.9"

services:
  # Test database
  postgres-test:
    image: timescale/timescaledb:2.13.0-pg16
    environment:
      POSTGRES_DB: neural_test
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U test"]
      interval: 5s
      timeout: 5s
      retries: 10

  # Test message queue
  kafka-test:
    image: confluentinc/cp-kafka:7.5.0
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper-test:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
    depends_on:
      - zookeeper-test

  # Test cache
  redis-test:
    image: redis:7.2-alpine
    command: redis-server --requirepass test

  # Neural services
  neural-processor-test:
    build:
      context: ../..
      dockerfile: docker/dockerfiles/services/neural-processor/Dockerfile
      target: test
    environment:
      DATABASE_URL: postgresql://test:test@postgres-test:5432/neural_test
      REDIS_URL: redis://:test@redis-test:6379
      KAFKA_BOOTSTRAP_SERVERS: kafka-test:9092
      ENVIRONMENT: test
    depends_on:
      - postgres-test
      - redis-test
      - kafka-test

  # Mock external services
  mock-vertex-ai:
    image: mockserver/mockserver:latest
    environment:
      MOCKSERVER_PROPERTY_FILE: /config/mockserver.properties
    volumes:
      - ./mocks/vertex-ai:/config
```

### Test Data Management

```python
# tests/integration/utils/data_generators.py
import numpy as np
from datetime import datetime, timedelta
import random

class TestDataGenerator:
    """Generate realistic test data for integration tests"""

    @staticmethod
    def generate_eeg_session(duration_minutes=30, sample_rate=250, channels=8):
        """Generate complete EEG session data"""
        samples = duration_minutes * 60 * sample_rate

        # Base EEG rhythms
        time = np.linspace(0, duration_minutes * 60, samples)
        data = np.zeros((channels, samples))

        for ch in range(channels):
            # Add different frequency components
            data[ch] += 10 * np.sin(2 * np.pi * 10 * time)  # Alpha
            data[ch] += 5 * np.sin(2 * np.pi * 20 * time)   # Beta
            data[ch] += 20 * np.sin(2 * np.pi * 2 * time)   # Delta

            # Add noise
            data[ch] += np.random.normal(0, 2, samples)

            # Add artifacts
            if ch < 2:  # Frontal channels
                # Eye blinks
                for _ in range(random.randint(10, 30)):
                    blink_pos = random.randint(1000, samples - 1000)
                    data[ch, blink_pos-50:blink_pos+50] += \
                        30 * np.sin(np.linspace(0, np.pi, 100))

        return {
            "data": data,
            "sample_rate": sample_rate,
            "duration": duration_minutes * 60,
            "timestamps": time,
            "metadata": {
                "recorded_at": datetime.now().isoformat(),
                "quality_score": random.uniform(0.85, 0.95)
            }
        }

    @staticmethod
    def generate_patient_data(count=10):
        """Generate test patient records"""
        patients = []

        for i in range(count):
            patients.append({
                "id": f"P{i:04d}",
                "name": f"Test Patient {i}",
                "dob": (datetime.now() - timedelta(days=random.randint(7300, 25550))).date().isoformat(),
                "gender": random.choice(["M", "F", "O"]),
                "mrn": f"MRN{random.randint(100000, 999999)}",
                "conditions": random.sample([
                    "epilepsy", "sleep_disorder", "adhd", "anxiety", "depression"
                ], k=random.randint(0, 2))
            })

        return patients
```

## Success Criteria

### Test Coverage Success

- [ ] All service integrations tested
- [ ] All workflows end-to-end tested
- [ ] External services mocked/tested
- [ ] Contract tests passing
- [ ] Performance benchmarks met

### Quality Success

- [ ] Zero integration test failures
- [ ] Test execution time <30 minutes
- [ ] Flaky test rate <2%
- [ ] Test environment stability >99%
- [ ] Documentation complete

### Operational Success

- [ ] CI/CD integration complete
- [ ] Parallel test execution working
- [ ] Test reports generated
- [ ] Monitoring configured
- [ ] Team trained

## Cost Estimation

### Infrastructure Costs (Monthly)

- **Test Environment**: $200/month (containers)
- **CI/CD Resources**: Included in Phase 17
- **Monitoring**: $100/month
- **Total**: ~$300/month

### Development Resources

- **Senior QA Engineer**: 3-4 days
- **Integration Engineers**: 2 days
- **Performance Engineer**: 1 day
- **Documentation**: 0.5 days

## Dependencies

### External Dependencies

- **Testcontainers**: Latest
- **pytest-asyncio**: 0.21+
- **Locust**: 2.17+
- **Pact**: Contract testing
- **MockServer**: External service mocking

### Internal Dependencies

- **Unit tests**: Phase 18 completed
- **Docker containers**: Phase 16 completed
- **CI/CD pipeline**: Phase 17 completed
- **Test data**: Fixtures prepared

## Risk Mitigation

### Technical Risks

1. **Test Environment Instability**: Container orchestration
2. **External Service Dependencies**: Comprehensive mocking
3. **Test Data Management**: Automated data generation
4. **Performance Bottlenecks**: Resource monitoring

### Process Risks

1. **Long Test Execution**: Parallel test runs
2. **Environment Conflicts**: Isolated test namespaces
3. **Data Cleanup**: Automatic teardown
4. **Debugging Failures**: Comprehensive logging

---

**Next Phase**: Phase 20 - Performance Testing
**Dependencies**: Integration tests, monitoring
**Review Date**: Implementation completion + 1 week
