# Phase 20: Performance Testing Specification

**Version**: 1.0.0
**Created**: 2025-07-29
**GitHub Issue**: #160 (to be created)
**Priority**: HIGH
**Duration**: 5-6 days
**Lead**: Senior Performance Engineer

## Executive Summary

Phase 20 implements comprehensive performance testing for the NeuraScale Neural Engine, including load testing, stress testing, capacity planning, and performance regression testing to ensure system scalability and reliability under real-world conditions.

## Functional Requirements

### 1. Performance Test Types

- **Load Testing**: Normal and peak load scenarios
- **Stress Testing**: System breaking point identification
- **Volume Testing**: Large dataset processing
- **Endurance Testing**: Long-running stability
- **Spike Testing**: Sudden load increases

### 2. Performance Metrics

- **Throughput**: Requests per second, data processing rate
- **Latency**: Response times, processing delays
- **Resource Usage**: CPU, memory, disk, network utilization
- **Scalability**: Horizontal and vertical scaling limits
- **Reliability**: Error rates, system stability

### 3. Test Automation

- **Continuous Performance Testing**: Automated test execution
- **Performance Regression Detection**: Baseline comparison
- **Real-time Monitoring**: Live performance tracking
- **Alerting**: Performance threshold violations
- **Reporting**: Comprehensive performance reports

## Technical Architecture

### Performance Testing Structure

```
tests/performance/
├── load/                    # Load testing scenarios
│   ├── api_load_test.py
│   ├── streaming_load_test.py
│   ├── ml_inference_load_test.py
│   └── database_load_test.py
├── stress/                  # Stress testing scenarios
│   ├── memory_stress_test.py
│   ├── cpu_stress_test.py
│   ├── network_stress_test.py
│   └── storage_stress_test.py
├── volume/                  # Volume testing scenarios
│   ├── large_dataset_test.py
│   ├── concurrent_sessions_test.py
│   └── bulk_operations_test.py
├── endurance/               # Endurance testing scenarios
│   ├── long_running_test.py
│   ├── memory_leak_test.py
│   └── stability_test.py
├── spike/                   # Spike testing scenarios
│   ├── sudden_load_test.py
│   ├── traffic_burst_test.py
│   └── connection_spike_test.py
├── benchmarks/              # Performance benchmarks
│   ├── signal_processing_bench.py
│   ├── ml_model_bench.py
│   ├── database_bench.py
│   └── api_bench.py
├── scenarios/               # Real-world scenarios
│   ├── clinical_workflow_test.py
│   ├── research_session_test.py
│   └── multi_device_test.py
├── utils/                   # Testing utilities
│   ├── data_generators.py
│   ├── load_generators.py
│   ├── metrics_collectors.py
│   └── report_generators.py
├── config/                  # Test configurations
│   ├── load_profiles.yaml
│   ├── test_environments.yaml
│   └── performance_thresholds.yaml
└── reports/                 # Test reports
    ├── templates/
    └── generated/
```

### Core Performance Testing Framework

```python
# tests/performance/framework/base.py
import asyncio
import time
import psutil
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import numpy as np

@dataclass
class PerformanceMetrics:
    """Performance test metrics"""
    timestamp: float
    response_time: float
    throughput: float
    cpu_usage: float
    memory_usage: float
    disk_io: float
    network_io: float
    error_count: int
    success_count: int

@dataclass
class TestConfiguration:
    """Performance test configuration"""
    name: str
    description: str
    duration: int  # seconds
    users: int
    ramp_up_time: int  # seconds
    think_time: float  # seconds between requests
    success_criteria: Dict[str, float]

class PerformanceTestBase(ABC):
    """Base class for performance tests"""

    def __init__(self, config: TestConfiguration):
        self.config = config
        self.metrics: List[PerformanceMetrics] = []
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def setup(self):
        """Setup test environment"""
        pass

    @abstractmethod
    async def execute_user_scenario(self, user_id: int) -> Dict[str, Any]:
        """Execute single user scenario"""
        pass

    @abstractmethod
    async def teardown(self):
        """Cleanup test environment"""
        pass

    async def collect_system_metrics(self) -> Dict[str, float]:
        """Collect system performance metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        network_io = psutil.net_io_counters()

        return {
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'memory_available': memory.available / (1024**3),  # GB
            'disk_read_mb_s': disk_io.read_bytes / (1024**2) if disk_io else 0,
            'disk_write_mb_s': disk_io.write_bytes / (1024**2) if disk_io else 0,
            'network_sent_mb_s': network_io.bytes_sent / (1024**2) if network_io else 0,
            'network_recv_mb_s': network_io.bytes_recv / (1024**2) if network_io else 0
        }

    async def run_test(self) -> Dict[str, Any]:
        """Execute performance test"""
        self.logger.info(f"Starting performance test: {self.config.name}")

        await self.setup()

        self.start_time = time.time()

        # Start metrics collection
        metrics_task = asyncio.create_task(self._collect_metrics_continuously())

        # Execute user scenarios
        tasks = []
        for user_id in range(self.config.users):
            # Stagger user ramp-up
            delay = (user_id * self.config.ramp_up_time) / self.config.users
            task = asyncio.create_task(self._delayed_user_execution(user_id, delay))
            tasks.append(task)

        # Wait for all users to complete or timeout
        try:
            await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.config.duration + self.config.ramp_up_time
            )
        except asyncio.TimeoutError:
            self.logger.warning("Test timed out, collecting partial results")

        self.end_time = time.time()

        # Stop metrics collection
        metrics_task.cancel()

        await self.teardown()

        return self._generate_test_report()

    async def _delayed_user_execution(self, user_id: int, delay: float):
        """Execute user scenario with initial delay"""
        await asyncio.sleep(delay)

        end_time = self.start_time + self.config.duration

        while time.time() < end_time:
            try:
                start = time.time()
                result = await self.execute_user_scenario(user_id)
                duration = time.time() - start

                # Record metrics
                self.metrics.append(PerformanceMetrics(
                    timestamp=time.time(),
                    response_time=duration,
                    throughput=1.0 / duration if duration > 0 else 0,
                    cpu_usage=0,  # Will be filled by system metrics
                    memory_usage=0,
                    disk_io=0,
                    network_io=0,
                    error_count=1 if result.get('error') else 0,
                    success_count=1 if not result.get('error') else 0
                ))

            except Exception as e:
                self.logger.error(f"User {user_id} error: {e}")
                self.metrics.append(PerformanceMetrics(
                    timestamp=time.time(),
                    response_time=0,
                    throughput=0,
                    cpu_usage=0,
                    memory_usage=0,
                    disk_io=0,
                    network_io=0,
                    error_count=1,
                    success_count=0
                ))

            # Think time between requests
            if self.config.think_time > 0:
                await asyncio.sleep(self.config.think_time)

    async def _collect_metrics_continuously(self):
        """Continuously collect system metrics"""
        while True:
            try:
                system_metrics = await self.collect_system_metrics()

                # Update recent metrics with system data
                current_time = time.time()
                for metric in reversed(self.metrics):
                    if current_time - metric.timestamp < 5:  # Within 5 seconds
                        metric.cpu_usage = system_metrics['cpu_usage']
                        metric.memory_usage = system_metrics['memory_usage']
                        metric.disk_io = system_metrics['disk_read_mb_s'] + system_metrics['disk_write_mb_s']
                        metric.network_io = system_metrics['network_sent_mb_s'] + system_metrics['network_recv_mb_s']

                await asyncio.sleep(1)  # Collect every second

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Metrics collection error: {e}")

    def _generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        if not self.metrics:
            return {"error": "No metrics collected"}

        response_times = [m.response_time for m in self.metrics if m.response_time > 0]
        throughputs = [m.throughput for m in self.metrics if m.throughput > 0]
        cpu_usages = [m.cpu_usage for m in self.metrics if m.cpu_usage > 0]
        memory_usages = [m.memory_usage for m in self.metrics if m.memory_usage > 0]

        total_requests = len(self.metrics)
        successful_requests = sum(m.success_count for m in self.metrics)
        failed_requests = sum(m.error_count for m in self.metrics)

        test_duration = self.end_time - self.start_time if self.end_time and self.start_time else 0

        report = {
            "test_name": self.config.name,
            "duration": test_duration,
            "users": self.config.users,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
            "average_throughput": sum(throughputs) / len(throughputs) if throughputs else 0,
            "response_times": {
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "mean": np.mean(response_times) if response_times else 0,
                "p50": np.percentile(response_times, 50) if response_times else 0,
                "p90": np.percentile(response_times, 90) if response_times else 0,
                "p95": np.percentile(response_times, 95) if response_times else 0,
                "p99": np.percentile(response_times, 99) if response_times else 0
            },
            "system_usage": {
                "avg_cpu": np.mean(cpu_usages) if cpu_usages else 0,
                "max_cpu": max(cpu_usages) if cpu_usages else 0,
                "avg_memory": np.mean(memory_usages) if memory_usages else 0,
                "max_memory": max(memory_usages) if memory_usages else 0
            },
            "success_criteria_met": self._check_success_criteria()
        }

        return report

    def _check_success_criteria(self) -> Dict[str, bool]:
        """Check if test meets success criteria"""
        if not self.metrics:
            return {}

        response_times = [m.response_time for m in self.metrics if m.response_time > 0]
        successful_requests = sum(m.success_count for m in self.metrics)
        total_requests = len(self.metrics)

        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        avg_response_time = np.mean(response_times) if response_times else float('inf')
        p95_response_time = np.percentile(response_times, 95) if response_times else float('inf')

        criteria_met = {}
        for criterion, threshold in self.config.success_criteria.items():
            if criterion == "success_rate":
                criteria_met[criterion] = success_rate >= threshold
            elif criterion == "avg_response_time":
                criteria_met[criterion] = avg_response_time <= threshold
            elif criterion == "p95_response_time":
                criteria_met[criterion] = p95_response_time <= threshold

        return criteria_met
```

## Implementation Plan

### Phase 20.1: API Load Testing (1.5 days)

**Senior Performance Engineer Tasks:**

1. **REST API Load Tests** (6 hours)

   ```python
   # tests/performance/load/api_load_test.py
   import asyncio
   import aiohttp
   import json
   from tests.performance.framework.base import PerformanceTestBase, TestConfiguration

   class APILoadTest(PerformanceTestBase):
       """Load test for REST API endpoints"""

       def __init__(self):
           config = TestConfiguration(
               name="API Load Test",
               description="Test API performance under normal load",
               duration=300,  # 5 minutes
               users=50,
               ramp_up_time=30,
               think_time=1.0,
               success_criteria={
                   "success_rate": 99.0,
                   "avg_response_time": 0.5,
                   "p95_response_time": 1.0
               }
           )
           super().__init__(config)
           self.session = None
           self.base_url = "http://localhost:8000"
           self.auth_token = None

       async def setup(self):
           """Setup HTTP session and authentication"""
           self.session = aiohttp.ClientSession()

           # Authenticate
           async with self.session.post(
               f"{self.base_url}/auth/token",
               json={"username": "test_user", "password": "test_pass"}
           ) as response:
               if response.status == 200:
                   data = await response.json()
                   self.auth_token = data["access_token"]
               else:
                   raise Exception("Authentication failed")

       async def execute_user_scenario(self, user_id: int) -> Dict[str, Any]:
           """Execute typical user API operations"""
           headers = {"Authorization": f"Bearer {self.auth_token}"}

           try:
               # Scenario: List sessions -> Get session details -> Query data

               # 1. List sessions
               async with self.session.get(
                   f"{self.base_url}/api/v2/sessions",
                   headers=headers
               ) as response:
                   if response.status != 200:
                       return {"error": f"List sessions failed: {response.status}"}
                   sessions = await response.json()

               if not sessions.get("sessions"):
                   return {"error": "No sessions available"}

               # 2. Get session details
               session_id = sessions["sessions"][0]["id"]
               async with self.session.get(
                   f"{self.base_url}/api/v2/sessions/{session_id}",
                   headers=headers
               ) as response:
                   if response.status != 200:
                       return {"error": f"Get session failed: {response.status}"}
                   session_details = await response.json()

               # 3. Query session data
               async with self.session.get(
                   f"{self.base_url}/api/v2/sessions/{session_id}/data",
                   headers=headers,
                   params={"limit": 100}
               ) as response:
                   if response.status != 200:
                       return {"error": f"Query data failed: {response.status}"}
                   data = await response.json()

               return {
                   "success": True,
                   "operations": 3,
                   "data_points": len(data.get("chunks", []))
               }

           except Exception as e:
               return {"error": str(e)}

       async def teardown(self):
           """Cleanup HTTP session"""
           if self.session:
               await self.session.close()

   class APIStressTest(PerformanceTestBase):
       """Stress test to find API breaking point"""

       def __init__(self):
           config = TestConfiguration(
               name="API Stress Test",
               description="Find API breaking point",
               duration=600,  # 10 minutes
               users=200,  # High load
               ramp_up_time=60,
               think_time=0.1,  # Minimal think time
               success_criteria={
                   "success_rate": 95.0,  # Lower expectation for stress test
                   "avg_response_time": 2.0,
                   "p95_response_time": 5.0
               }
           )
           super().__init__(config)
           self.session = None
           self.base_url = "http://localhost:8000"
           self.auth_token = None

       async def setup(self):
           """Setup with connection pooling for high load"""
           connector = aiohttp.TCPConnector(
               limit=300,  # Total connection pool size
               limit_per_host=100,  # Connections per host
               ttl_dns_cache=300,
               use_dns_cache=True
           )
           self.session = aiohttp.ClientSession(connector=connector)

           # Authenticate
           async with self.session.post(
               f"{self.base_url}/auth/token",
               json={"username": "stress_test", "password": "test_pass"}
           ) as response:
               data = await response.json()
               self.auth_token = data["access_token"]

       async def execute_user_scenario(self, user_id: int) -> Dict[str, Any]:
           """Aggressive API usage scenario"""
           headers = {"Authorization": f"Bearer {self.auth_token}"}

           try:
               # Rapid-fire requests
               tasks = []

               # Concurrent API calls
               for _ in range(5):
                   task = self.session.get(
                       f"{self.base_url}/api/v2/devices",
                       headers=headers
                   )
                   tasks.append(task)

               responses = await asyncio.gather(*tasks, return_exceptions=True)

               success_count = 0
               for response in responses:
                   if isinstance(response, aiohttp.ClientResponse):
                       if response.status == 200:
                           success_count += 1
                       response.close()

               return {
                   "success": success_count > 0,
                   "successful_requests": success_count,
                   "total_requests": len(tasks)
               }

           except Exception as e:
               return {"error": str(e)}

       async def teardown(self):
           if self.session:
               await self.session.close()
   ```

2. **WebSocket Performance Tests** (6 hours)

   ```python
   # tests/performance/load/streaming_load_test.py
   import asyncio
   import websockets
   import json
   import time
   import numpy as np
   from tests.performance.framework.base import PerformanceTestBase, TestConfiguration

   class WebSocketStreamingTest(PerformanceTestBase):
       """Test WebSocket streaming performance"""

       def __init__(self):
           config = TestConfiguration(
               name="WebSocket Streaming Test",
               description="Test real-time data streaming performance",
               duration=180,  # 3 minutes
               users=20,  # Concurrent streaming connections
               ramp_up_time=10,
               think_time=0,  # Continuous streaming
               success_criteria={
                   "success_rate": 98.0,
                   "avg_response_time": 0.1,  # Real-time requirement
                   "p95_response_time": 0.2
               }
           )
           super().__init__(config)
           self.ws_url = "ws://localhost:8000/ws/stream"

       async def setup(self):
           """Setup test environment"""
           # Verify WebSocket endpoint is available
           try:
               async with websockets.connect(self.ws_url) as websocket:
                   await websocket.ping()
           except Exception as e:
               raise Exception(f"WebSocket endpoint not available: {e}")

       async def execute_user_scenario(self, user_id: int) -> Dict[str, Any]:
           """Stream neural data and measure latency"""

           try:
               async with websockets.connect(self.ws_url) as websocket:
                   # Subscribe to data stream
                   await websocket.send(json.dumps({
                       "type": "subscribe",
                       "channels": ["neural_data", "signal_quality"]
                   }))

                   messages_received = 0
                   total_latency = 0
                   errors = 0

                   # Stream for test duration
                   start_time = time.time()
                   while time.time() - start_time < 30:  # 30 seconds per user
                       try:
                           # Set timeout for message reception
                           message = await asyncio.wait_for(
                               websocket.recv(),
                               timeout=1.0
                           )

                           # Parse message and calculate latency
                           data = json.loads(message)
                           if "timestamp" in data:
                               server_time = data["timestamp"]
                               latency = time.time() - server_time
                               total_latency += latency

                           messages_received += 1

                       except asyncio.TimeoutError:
                           errors += 1
                       except json.JSONDecodeError:
                           errors += 1

                   avg_latency = total_latency / messages_received if messages_received > 0 else 0

                   return {
                       "success": messages_received > 0,
                       "messages_received": messages_received,
                       "average_latency": avg_latency,
                       "errors": errors,
                       "throughput": messages_received / 30  # messages per second
                   }

           except Exception as e:
               return {"error": str(e)}

       async def teardown(self):
           """Cleanup resources"""
           pass

   class HighThroughputDataTest(PerformanceTestBase):
       """Test system under high data throughput"""

       def __init__(self):
           config = TestConfiguration(
               name="High Throughput Data Test",
               description="Test processing of high-volume neural data",
               duration=300,  # 5 minutes
               users=10,  # Fewer users, more data per user
               ramp_up_time=20,
               think_time=0,
               success_criteria={
                   "success_rate": 95.0,
                   "avg_response_time": 1.0,
                   "p95_response_time": 3.0
               }
           )
           super().__init__(config)
           self.base_url = "http://localhost:8000"

       async def setup(self):
           """Generate test data"""
           # Generate large neural datasets
           self.test_datasets = []
           for i in range(10):
               # Large EEG dataset: 64 channels, 10 minutes at 1kHz
               data = np.random.randn(64, 600000).astype(np.float32)
               self.test_datasets.append({
                   "session_id": f"perf_test_{i}",
                   "data": data.tobytes(),
                   "metadata": {
                       "channels": 64,
                       "sample_rate": 1000,
                       "duration": 600
                   }
               })

       async def execute_user_scenario(self, user_id: int) -> Dict[str, Any]:
           """Upload and process large datasets"""

           try:
               async with aiohttp.ClientSession() as session:
                   dataset = self.test_datasets[user_id % len(self.test_datasets)]

                   # Upload large dataset
                   start_time = time.time()

                   form_data = aiohttp.FormData()
                   form_data.add_field('session_id', dataset['session_id'])
                   form_data.add_field('data', dataset['data'],
                                     content_type='application/octet-stream')
                   form_data.add_field('metadata', json.dumps(dataset['metadata']))

                   async with session.post(
                       f"{self.base_url}/api/v2/data/upload",
                       data=form_data
                   ) as response:
                       upload_time = time.time() - start_time

                       if response.status != 200:
                           return {"error": f"Upload failed: {response.status}"}

                       result = await response.json()
                       processing_job_id = result["job_id"]

                   # Monitor processing
                   processed = False
                   processing_start = time.time()

                   while time.time() - processing_start < 60:  # 1 minute timeout
                       async with session.get(
                           f"{self.base_url}/api/v2/jobs/{processing_job_id}"
                       ) as response:
                           if response.status == 200:
                               job_status = await response.json()
                               if job_status["status"] == "completed":
                                   processed = True
                                   break
                               elif job_status["status"] == "failed":
                                   return {"error": "Processing failed"}

                       await asyncio.sleep(1)

                   processing_time = time.time() - processing_start

                   return {
                       "success": processed,
                       "upload_time": upload_time,
                       "processing_time": processing_time,
                       "data_size_mb": len(dataset['data']) / (1024**2),
                       "throughput_mb_s": (len(dataset['data']) / (1024**2)) / upload_time
                   }

           except Exception as e:
               return {"error": str(e)}

       async def teardown(self):
           """Cleanup test data"""
           pass
   ```

### Phase 20.2: ML Pipeline Performance Testing (1 day)

**ML Performance Engineer Tasks:**

1. **Model Inference Benchmarks** (4 hours)

   ```python
   # tests/performance/benchmarks/ml_model_bench.py
   import asyncio
   import time
   import torch
   import numpy as np
   from tests.performance.framework.base import PerformanceTestBase, TestConfiguration

   class MLInferenceBenchmark(PerformanceTestBase):
       """Benchmark ML model inference performance"""

       def __init__(self):
           config = TestConfiguration(
               name="ML Inference Benchmark",
               description="Benchmark neural network inference speed",
               duration=120,  # 2 minutes
               users=10,  # Concurrent inference requests
               ramp_up_time=5,
               think_time=0.1,
               success_criteria={
                   "success_rate": 99.0,
                   "avg_response_time": 0.05,  # 50ms for real-time
                   "p95_response_time": 0.1    # 100ms max
               }
           )
           super().__init__(config)
           self.models = {}
           self.test_data = []

       async def setup(self):
           """Load ML models and test data"""
           from src.ml_models.movement_decoder import MovementDecoder
           from src.ml_models.emotion_classifier import EmotionClassifier

           # Load models
           self.models = {
               "movement": MovementDecoder.load_pretrained("models/movement_v1.pth"),
               "emotion": EmotionClassifier.load_pretrained("models/emotion_v1.pth")
           }

           # Generate test data
           for _ in range(100):
               # EEG data: 8 channels, 250 samples (1 second at 250Hz)
               eeg_data = torch.randn(1, 8, 250)
               self.test_data.append(eeg_data)

           # Warm up models
           for model in self.models.values():
               model.eval()
               with torch.no_grad():
                   _ = model(self.test_data[0])

       async def execute_user_scenario(self, user_id: int) -> Dict[str, Any]:
           """Run inference on random test data"""

           try:
               test_sample = self.test_data[np.random.randint(len(self.test_data))]
               model_name = np.random.choice(list(self.models.keys()))
               model = self.models[model_name]

               # Measure inference time
               start_time = time.time()

               with torch.no_grad():
                   if torch.cuda.is_available():
                       test_sample = test_sample.cuda()
                       model = model.cuda()

                   prediction = model(test_sample)

                   # Ensure computation is complete
                   if torch.cuda.is_available():
                       torch.cuda.synchronize()

               inference_time = time.time() - start_time

               return {
                   "success": True,
                   "model": model_name,
                   "inference_time": inference_time,
                   "input_shape": list(test_sample.shape),
                   "output_shape": list(prediction.shape)
               }

           except Exception as e:
               return {"error": str(e)}

       async def teardown(self):
           """Cleanup GPU memory"""
           if torch.cuda.is_available():
               torch.cuda.empty_cache()

   class BatchInferenceBenchmark(PerformanceTestBase):
       """Benchmark batch inference performance"""

       def __init__(self):
           config = TestConfiguration(
               name="Batch Inference Benchmark",
               description="Test batch processing efficiency",
               duration=180,  # 3 minutes
               users=5,   # Fewer concurrent users for batch processing
               ramp_up_time=10,
               think_time=2.0,  # Time between batches
               success_criteria={
                   "success_rate": 99.0,
                   "avg_response_time": 0.5,   # 500ms for batch
                   "p95_response_time": 1.0    # 1s max
               }
           )
           super().__init__(config)
           self.model = None
           self.batch_sizes = [1, 8, 16, 32, 64]

       async def setup(self):
           """Load model for batch testing"""
           from src.ml_models.emotion_classifier import EmotionClassifier
           self.model = EmotionClassifier.load_pretrained("models/emotion_v1.pth")
           self.model.eval()

           # Warm up
           test_batch = torch.randn(32, 8, 250)
           with torch.no_grad():
               _ = self.model(test_batch)

       async def execute_user_scenario(self, user_id: int) -> Dict[str, Any]:
           """Test different batch sizes"""

           try:
               batch_size = np.random.choice(self.batch_sizes)
               test_batch = torch.randn(batch_size, 8, 250)

               start_time = time.time()

               with torch.no_grad():
                   if torch.cuda.is_available():
                       test_batch = test_batch.cuda()
                       self.model = self.model.cuda()

                   predictions = self.model(test_batch)

                   if torch.cuda.is_available():
                       torch.cuda.synchronize()

               batch_time = time.time() - start_time
               throughput = batch_size / batch_time  # samples per second

               return {
                   "success": True,
                   "batch_size": batch_size,
                   "batch_time": batch_time,
                   "throughput": throughput,
                   "time_per_sample": batch_time / batch_size
               }

           except Exception as e:
               return {"error": str(e)}

       async def teardown(self):
           if torch.cuda.is_available():
               torch.cuda.empty_cache()
   ```

2. **Data Pipeline Performance** (4 hours)

   ```python
   # tests/performance/load/ml_pipeline_load_test.py
   import asyncio
   import time
   import numpy as np
   from concurrent.futures import ThreadPoolExecutor
   from tests.performance.framework.base import PerformanceTestBase, TestConfiguration

   class DataPipelinePerformanceTest(PerformanceTestBase):
       """Test data preprocessing pipeline performance"""

       def __init__(self):
           config = TestConfiguration(
               name="Data Pipeline Performance Test",
               description="Test signal processing pipeline throughput",
               duration=240,  # 4 minutes
               users=8,   # CPU-bound processing
               ramp_up_time=15,
               think_time=0.5,
               success_criteria={
                   "success_rate": 98.0,
                   "avg_response_time": 2.0,
                   "p95_response_time": 5.0
               }
           )
           super().__init__(config)
           self.processor = None
           self.executor = None

       async def setup(self):
           """Setup signal processing pipeline"""
           from src.neural_processor.signal_processing import SignalProcessor
           from src.neural_processor.feature_extraction import FeatureExtractor

           self.processor = SignalProcessor()
           self.feature_extractor = FeatureExtractor()
           self.executor = ThreadPoolExecutor(max_workers=4)

       async def execute_user_scenario(self, user_id: int) -> Dict[str, Any]:
           """Process neural data through full pipeline"""

           try:
               # Generate test data
               channels = 32
               duration = 30  # seconds
               sample_rate = 1000
               samples = duration * sample_rate

               raw_data = np.random.randn(channels, samples).astype(np.float32)

               start_time = time.time()

               # Run CPU-intensive processing in thread pool
               loop = asyncio.get_event_loop()

               # Step 1: Filtering
               filtered_data = await loop.run_in_executor(
                   self.executor,
                   self.processor.apply_bandpass_filter,
                   raw_data,
                   0.5, 50, sample_rate
               )

               filter_time = time.time() - start_time

               # Step 2: Artifact removal
               clean_data = await loop.run_in_executor(
                   self.executor,
                   self.processor.remove_artifacts,
                   filtered_data
               )

               artifact_time = time.time() - start_time - filter_time

               # Step 3: Feature extraction
               features = await loop.run_in_executor(
                   self.executor,
                   self.feature_extractor.extract_features,
                   clean_data
               )

               feature_time = time.time() - start_time - filter_time - artifact_time
               total_time = time.time() - start_time

               # Calculate throughput
               data_size_mb = raw_data.nbytes / (1024**2)
               throughput = data_size_mb / total_time

               return {
                   "success": True,
                   "total_time": total_time,
                   "filter_time": filter_time,
                   "artifact_time": artifact_time,
                   "feature_time": feature_time,
                   "data_size_mb": data_size_mb,
                   "throughput_mb_s": throughput,
                   "samples_processed": samples * channels
               }

           except Exception as e:
               return {"error": str(e)}

       async def teardown(self):
           """Cleanup thread pool"""
           if self.executor:
               self.executor.shutdown(wait=True)
   ```

### Phase 20.3: Database Performance Testing (1 day)

**Database Performance Engineer Tasks:**

1. **TimescaleDB Performance** (4 hours)

   ```python
   # tests/performance/load/database_load_test.py
   import asyncio
   import asyncpg
   import numpy as np
   import time
   from tests.performance.framework.base import PerformanceTestBase, TestConfiguration

   class DatabaseWritePerformanceTest(PerformanceTestBase):
       """Test database write performance"""

       def __init__(self):
           config = TestConfiguration(
               name="Database Write Performance Test",
               description="Test TimescaleDB write throughput",
               duration=300,  # 5 minutes
               users=20,  # Concurrent writers
               ramp_up_time=30,
               think_time=1.0,
               success_criteria={
                   "success_rate": 99.0,
                   "avg_response_time": 0.5,
                   "p95_response_time": 1.0
               }
           )
           super().__init__(config)
           self.db_pool = None

       async def setup(self):
           """Setup database connection pool"""
           self.db_pool = await asyncpg.create_pool(
               host="localhost",
               port=5432,
               user="neural_test",
               password="test_pass",
               database="neural_test",
               min_size=10,
               max_size=50
           )

           # Create test table if not exists
           async with self.db_pool.acquire() as conn:
               await conn.execute("""
                   CREATE TABLE IF NOT EXISTS performance_test_data (
                       time TIMESTAMPTZ NOT NULL,
                       session_id TEXT,
                       channel INT,
                       value REAL,
                       metadata JSONB
                   );

                   SELECT create_hypertable('performance_test_data', 'time',
                                          if_not_exists => TRUE);
               """)

       async def execute_user_scenario(self, user_id: int) -> Dict[str, Any]:
           """Write batch of neural data to database"""

           try:
               # Generate batch data
               batch_size = 1000
               session_id = f"perf_session_{user_id}"

               # Time series data
               current_time = time.time()
               timestamps = [current_time - i * 0.004 for i in range(batch_size)]  # 250Hz

               data_rows = []
               for i, ts in enumerate(timestamps):
                   for channel in range(8):
                       data_rows.append((
                           ts,
                           session_id,
                           channel,
                           np.random.randn(),
                           {"batch": i // 100}
                       ))

               start_time = time.time()

               async with self.db_pool.acquire() as conn:
                   # Bulk insert
                   await conn.executemany("""
                       INSERT INTO performance_test_data
                       (time, session_id, channel, value, metadata)
                       VALUES ($1, $2, $3, $4, $5)
                   """, data_rows)

               write_time = time.time() - start_time
               rows_written = len(data_rows)

               return {
                   "success": True,
                   "write_time": write_time,
                   "rows_written": rows_written,
                   "rows_per_second": rows_written / write_time,
                   "session_id": session_id
               }

           except Exception as e:
               return {"error": str(e)}

       async def teardown(self):
           """Cleanup database connections"""
           if self.db_pool:
               await self.db_pool.close()

   class DatabaseQueryPerformanceTest(PerformanceTestBase):
       """Test database query performance"""

       def __init__(self):
           config = TestConfiguration(
               name="Database Query Performance Test",
               description="Test TimescaleDB query performance",
               duration=240,  # 4 minutes
               users=15,
               ramp_up_time=20,
               think_time=0.5,
               success_criteria={
                   "success_rate": 99.0,
                   "avg_response_time": 0.3,
                   "p95_response_time": 1.0
               }
           )
           super().__init__(config)
           self.db_pool = None
           self.test_sessions = []

       async def setup(self):
           """Setup test data and connections"""
           self.db_pool = await asyncpg.create_pool(
               host="localhost",
               port=5432,
               user="neural_test",
               password="test_pass",
               database="neural_test",
               min_size=10,
               max_size=30
           )

           # Create test sessions for querying
           self.test_sessions = [f"query_session_{i}" for i in range(50)]

       async def execute_user_scenario(self, user_id: int) -> Dict[str, Any]:
           """Execute various database queries"""

           try:
               session_id = np.random.choice(self.test_sessions)
               query_type = np.random.choice(["range", "aggregate", "latest"])

               start_time = time.time()

               async with self.db_pool.acquire() as conn:
                   if query_type == "range":
                       # Time range query
                       result = await conn.fetch("""
                           SELECT time, channel, value
                           FROM performance_test_data
                           WHERE session_id = $1
                             AND time >= NOW() - INTERVAL '1 hour'
                           ORDER BY time DESC
                           LIMIT 1000
                       """, session_id)

                   elif query_type == "aggregate":
                       # Aggregation query
                       result = await conn.fetch("""
                           SELECT
                               channel,
                               AVG(value) as avg_value,
                               STDDEV(value) as std_value,
                               COUNT(*) as count
                           FROM performance_test_data
                           WHERE session_id = $1
                             AND time >= NOW() - INTERVAL '10 minutes'
                           GROUP BY channel
                       """, session_id)

                   else:  # latest
                       # Latest data query
                       result = await conn.fetch("""
                           SELECT DISTINCT ON (channel)
                               channel, time, value
                           FROM performance_test_data
                           WHERE session_id = $1
                           ORDER BY channel, time DESC
                       """, session_id)

               query_time = time.time() - start_time

               return {
                   "success": True,
                   "query_type": query_type,
                   "query_time": query_time,
                   "rows_returned": len(result),
                   "session_id": session_id
               }

           except Exception as e:
               return {"error": str(e)}

       async def teardown(self):
           if self.db_pool:
               await self.db_pool.close()
   ```

2. **Cache Performance Testing** (4 hours)

   ```python
   # tests/performance/load/cache_performance_test.py
   import asyncio
   import aioredis
   import json
   import time
   import numpy as np
   from tests.performance.framework.base import PerformanceTestBase, TestConfiguration

   class CachePerformanceTest(PerformanceTestBase):
       """Test Redis cache performance"""

       def __init__(self):
           config = TestConfiguration(
               name="Cache Performance Test",
               description="Test Redis cache read/write performance",
               duration=180,  # 3 minutes
               users=30,  # High concurrency for cache
               ramp_up_time=15,
               think_time=0.1,
               success_criteria={
                   "success_rate": 99.5,
                   "avg_response_time": 0.01,  # 10ms
                   "p95_response_time": 0.05   # 50ms
               }
           )
           super().__init__(config)
           self.redis_pool = None
           self.test_keys = []

       async def setup(self):
           """Setup Redis connection pool"""
           self.redis_pool = aioredis.ConnectionPool.from_url(
               "redis://localhost:6379",
               max_connections=50
           )

           # Pre-populate cache with test data
           redis = aioredis.Redis(connection_pool=self.redis_pool)

           for i in range(1000):
               key = f"perf_test_key_{i}"
               self.test_keys.append(key)

               # Store various data types
               if i % 3 == 0:
                   # String data
                   await redis.set(key, f"test_value_{i}", ex=3600)
               elif i % 3 == 1:
                   # JSON data
                   data = {
                       "session_id": f"session_{i}",
                       "channels": 8,
                       "sample_rate": 250,
                       "features": np.random.randn(10).tolist()
                   }
                   await redis.set(key, json.dumps(data), ex=3600)
               else:
                   # Binary data (simulated neural data)
                   neural_data = np.random.randn(8, 1000).astype(np.float32)
                   await redis.set(key, neural_data.tobytes(), ex=3600)

           await redis.close()

       async def execute_user_scenario(self, user_id: int) -> Dict[str, Any]:
           """Execute cache operations"""

           try:
               redis = aioredis.Redis(connection_pool=self.redis_pool)

               operation = np.random.choice(["read", "write", "delete", "pipeline"])

               if operation == "read":
                   # Cache read
                   key = np.random.choice(self.test_keys)
                   start_time = time.time()
                   value = await redis.get(key)
                   operation_time = time.time() - start_time

                   return {
                       "success": value is not None,
                       "operation": "read",
                       "operation_time": operation_time,
                       "data_size": len(value) if value else 0
                   }

               elif operation == "write":
                   # Cache write
                   key = f"write_test_{user_id}_{int(time.time() * 1000)}"
                   data = json.dumps({
                       "timestamp": time.time(),
                       "user_id": user_id,
                       "data": np.random.randn(100).tolist()
                   })

                   start_time = time.time()
                   await redis.set(key, data, ex=300)  # 5 minute expiry
                   operation_time = time.time() - start_time

                   return {
                       "success": True,
                       "operation": "write",
                       "operation_time": operation_time,
                       "data_size": len(data)
                   }

               elif operation == "delete":
                   # Cache delete
                   key = np.random.choice(self.test_keys[:100])  # Don't delete all test data
                   start_time = time.time()
                   result = await redis.delete(key)
                   operation_time = time.time() - start_time

                   return {
                       "success": True,
                       "operation": "delete",
                       "operation_time": operation_time,
                       "keys_deleted": result
                   }

               else:  # pipeline
                   # Pipeline operations
                   pipe = redis.pipeline()
                   keys_to_read = np.random.choice(self.test_keys, 10, replace=False)

                   start_time = time.time()
                   for key in keys_to_read:
                       pipe.get(key)
                   results = await pipe.execute()
                   operation_time = time.time() - start_time

                   successful_reads = sum(1 for r in results if r is not None)

                   return {
                       "success": successful_reads > 0,
                       "operation": "pipeline",
                       "operation_time": operation_time,
                       "operations_count": len(keys_to_read),
                       "successful_reads": successful_reads
                   }

               await redis.close()

           except Exception as e:
               return {"error": str(e)}

       async def teardown(self):
           """Cleanup Redis connections"""
           if self.redis_pool:
               await self.redis_pool.disconnect()
   ```

### Phase 20.4: System Integration Performance (1 day)

**Integration Performance Engineer Tasks:**

1. **End-to-End Scenarios** (4 hours)

   ```python
   # tests/performance/scenarios/clinical_workflow_test.py
   import asyncio
   import aiohttp
   import time
   import numpy as np
   from tests.performance.framework.base import PerformanceTestBase, TestConfiguration

   class ClinicalWorkflowPerformanceTest(PerformanceTestBase):
       """Test complete clinical workflow performance"""

       def __init__(self):
           config = TestConfiguration(
               name="Clinical Workflow Performance Test",
               description="Test complete patient session workflow",
               duration=600,  # 10 minutes
               users=5,   # Realistic clinical load
               ramp_up_time=60,
               think_time=30.0,  # Realistic time between operations
               success_criteria={
                   "success_rate": 98.0,
                   "avg_response_time": 120.0,  # 2 minutes per workflow
                   "p95_response_time": 300.0   # 5 minutes max
               }
           )
           super().__init__(config)
           self.base_url = "http://localhost:8000"
           self.auth_tokens = {}

       async def setup(self):
           """Setup clinical user accounts"""
           # Create multiple clinical user sessions
           for i in range(10):
               async with aiohttp.ClientSession() as session:
                   async with session.post(
                       f"{self.base_url}/auth/token",
                       json={
                           "username": f"clinician_{i}",
                           "password": os.environ.get("TEST_PASSWORD", "test_pass")
                       }
                   ) as response:
                       if response.status == 200:
                           data = await response.json()
                           self.auth_tokens[i] = data["access_token"]

       async def execute_user_scenario(self, user_id: int) -> Dict[str, Any]:
           """Execute complete clinical workflow"""

           try:
               token = self.auth_tokens[user_id % len(self.auth_tokens)]
               headers = {"Authorization": f"Bearer {token}"}

               workflow_start = time.time()
               operations = []

               async with aiohttp.ClientSession() as session:
                   # Step 1: Create patient
                   patient_data = {
                       "name": f"Patient {user_id}_{int(time.time())}",
                       "dob": "1980-01-01",
                       "mrn": f"MRN{user_id}{int(time.time()) % 10000}"
                   }

                   start_time = time.time()
                   async with session.post(
                       f"{self.base_url}/api/v2/patients",
                       json=patient_data,
                       headers=headers
                   ) as response:
                       if response.status != 201:
                           return {"error": f"Patient creation failed: {response.status}"}
                       patient = await response.json()

                   operations.append({
                       "step": "create_patient",
                       "duration": time.time() - start_time
                   })

                   # Step 2: Setup recording session
                   session_data = {
                       "patient_id": patient["id"],
                       "device_id": "clinical_device_001",
                       "protocol": "standard_eeg",
                       "duration": 1800  # 30 minutes
                   }

                   start_time = time.time()
                   async with session.post(
                       f"{self.base_url}/api/v2/sessions",
                       json=session_data,
                       headers=headers
                   ) as response:
                       if response.status != 201:
                           return {"error": f"Session creation failed: {response.status}"}
                       recording_session = await response.json()

                   operations.append({
                       "step": "create_session",
                       "duration": time.time() - start_time
                   })

                   # Step 3: Simulate recording (fast simulation)
                   session_id = recording_session["id"]

                   # Upload neural data in chunks
                   for chunk_idx in range(5):  # 5 chunks
                       # Generate 6-minute chunk of data
                       neural_data = np.random.randn(32, 90000).astype(np.float32)  # 32ch, 6min@250Hz

                       start_time = time.time()

                       form_data = aiohttp.FormData()
                       form_data.add_field('session_id', session_id)
                       form_data.add_field('chunk_index', str(chunk_idx))
                       form_data.add_field('data', neural_data.tobytes(),
                                         content_type='application/octet-stream')

                       async with session.post(
                           f"{self.base_url}/api/v2/sessions/{session_id}/data",
                           data=form_data,
                           headers=headers
                       ) as response:
                           if response.status != 200:
                               return {"error": f"Data upload failed: {response.status}"}

                       operations.append({
                           "step": f"upload_chunk_{chunk_idx}",
                           "duration": time.time() - start_time,
                           "data_size_mb": neural_data.nbytes / (1024**2)
                       })

                   # Step 4: Run analysis
                   analysis_request = {
                       "session_id": session_id,
                       "analyses": [
                           {"type": "spectral_analysis"},
                           {"type": "connectivity_analysis"},
                           {"type": "artifact_detection"}
                       ]
                   }

                   start_time = time.time()
                   async with session.post(
                       f"{self.base_url}/api/v2/analysis",
                       json=analysis_request,
                       headers=headers
                   ) as response:
                       if response.status != 202:
                           return {"error": f"Analysis request failed: {response.status}"}
                       analysis = await response.json()

                   # Wait for analysis completion
                   analysis_id = analysis["job_id"]
                   analysis_completed = False

                   for _ in range(60):  # Wait up to 60 seconds
                       async with session.get(
                           f"{self.base_url}/api/v2/analysis/{analysis_id}",
                           headers=headers
                       ) as response:
                           if response.status == 200:
                               status = await response.json()
                               if status["status"] == "completed":
                                   analysis_completed = True
                                   break
                               elif status["status"] == "failed":
                                   return {"error": "Analysis failed"}

                       await asyncio.sleep(1)

                   operations.append({
                       "step": "analysis",
                       "duration": time.time() - start_time,
                       "completed": analysis_completed
                   })

                   # Step 5: Generate report
                   if analysis_completed:
                       start_time = time.time()
                       async with session.post(
                           f"{self.base_url}/api/v2/reports",
                           json={
                               "session_id": session_id,
                               "analysis_id": analysis_id,
                               "template": "clinical_standard"
                           },
                           headers=headers
                       ) as response:
                           if response.status == 201:
                               report = await response.json()

                       operations.append({
                           "step": "generate_report",
                           "duration": time.time() - start_time
                       })

               total_workflow_time = time.time() - workflow_start

               return {
                   "success": analysis_completed,
                   "total_workflow_time": total_workflow_time,
                   "operations": operations,
                   "patient_id": patient["id"],
                   "session_id": session_id
               }

           except Exception as e:
               return {"error": str(e)}

       async def teardown(self):
           """Cleanup test data"""
           pass
   ```

2. **Multi-Device Scenarios** (4 hours)

   ```python
   # tests/performance/scenarios/multi_device_test.py
   import asyncio
   import websockets
   import json
   import time
   import numpy as np
   from tests.performance.framework.base import PerformanceTestBase, TestConfiguration

   class MultiDevicePerformanceTest(PerformanceTestBase):
       """Test multi-device concurrent streaming"""

       def __init__(self):
           config = TestConfiguration(
               name="Multi-Device Performance Test",
               description="Test concurrent multi-device data streaming",
               duration=300,  # 5 minutes
               users=20,  # Each user simulates multiple devices
               ramp_up_time=30,
               think_time=0,  # Continuous streaming
               success_criteria={
                   "success_rate": 95.0,
                   "avg_response_time": 0.05,
                   "p95_response_time": 0.2
               }
           )
           super().__init__(config)
           self.ws_url = "ws://localhost:8000/ws/devices"
           self.device_configs = [
               {"name": "OpenBCI_Cyton", "channels": 8, "sample_rate": 250},
               {"name": "Emotiv_EPOC", "channels": 14, "sample_rate": 128},
               {"name": "g.USBamp", "channels": 16, "sample_rate": 512},
               {"name": "ANT_Neuro", "channels": 32, "sample_rate": 1000}
           ]

       async def setup(self):
           """Verify WebSocket endpoint"""
           try:
               async with websockets.connect(self.ws_url) as websocket:
                   await websocket.ping()
           except Exception as e:
               raise Exception(f"WebSocket not available: {e}")

       async def execute_user_scenario(self, user_id: int) -> Dict[str, Any]:
           """Simulate multiple devices streaming simultaneously"""

           try:
               # Each user simulates 2-4 devices
               num_devices = np.random.randint(2, 5)
               device_tasks = []

               for device_idx in range(num_devices):
                   config = np.random.choice(self.device_configs)
                   device_id = f"device_{user_id}_{device_idx}"

                   task = asyncio.create_task(
                       self._simulate_device_stream(device_id, config)
                   )
                   device_tasks.append(task)

               # Run all device simulations concurrently
               results = await asyncio.gather(*device_tasks, return_exceptions=True)

               # Aggregate results
               total_packets = 0
               total_errors = 0
               successful_devices = 0

               for result in results:
                   if isinstance(result, dict) and not result.get("error"):
                       total_packets += result.get("packets_sent", 0)
                       successful_devices += 1
                   else:
                       total_errors += 1

               return {
                   "success": successful_devices > 0,
                   "devices_simulated": num_devices,
                   "successful_devices": successful_devices,
                   "total_packets": total_packets,
                   "total_errors": total_errors,
                   "avg_packets_per_device": total_packets / num_devices if num_devices > 0 else 0
               }

           except Exception as e:
               return {"error": str(e)}

       async def _simulate_device_stream(self, device_id: str, config: Dict) -> Dict[str, Any]:
           """Simulate single device streaming"""

           try:
               async with websockets.connect(self.ws_url) as websocket:
                   # Register device
                   await websocket.send(json.dumps({
                       "type": "register",
                       "device_id": device_id,
                       "device_type": config["name"],
                       "channels": config["channels"],
                       "sample_rate": config["sample_rate"]
                   }))

                   # Stream data for 30 seconds per device
                   packets_sent = 0
                   errors = 0
                   start_time = time.time()

                   while time.time() - start_time < 30:
                       try:
                           # Generate data packet
                           samples_per_packet = config["sample_rate"] // 10  # 100ms packets
                           data = np.random.randn(
                               config["channels"],
                               samples_per_packet
                           ).astype(np.float32)

                           packet = {
                               "type": "data",
                               "device_id": device_id,
                               "timestamp": time.time(),
                               "data": data.tolist(),
                               "packet_id": packets_sent
                           }

                           # Send data packet
                           await websocket.send(json.dumps(packet))
                           packets_sent += 1

                           # Wait for next packet (maintain sample rate)
                           await asyncio.sleep(0.1)  # 100ms packets

                       except Exception as e:
                           errors += 1

                   # Unregister device
                   await websocket.send(json.dumps({
                       "type": "unregister",
                       "device_id": device_id
                   }))

                   return {
                       "success": True,
                       "device_id": device_id,
                       "packets_sent": packets_sent,
                       "errors": errors,
                       "stream_duration": time.time() - start_time
                   }

           except Exception as e:
               return {"error": str(e)}

       async def teardown(self):
           """Cleanup resources"""
           pass
   ```

### Phase 20.5: Performance Reporting & Analysis (0.5 days)

**Performance Engineer Tasks:**

1. **Report Generation** (2 hours)

   ```python
   # tests/performance/utils/report_generators.py
   import json
   import matplotlib.pyplot as plt
   import pandas as pd
   from datetime import datetime
   from pathlib import Path
   from typing import List, Dict, Any

   class PerformanceReportGenerator:
       """Generate comprehensive performance reports"""

       def __init__(self, output_dir: str = "tests/performance/reports/generated"):
           self.output_dir = Path(output_dir)
           self.output_dir.mkdir(parents=True, exist_ok=True)

       def generate_comprehensive_report(self, test_results: List[Dict[str, Any]]) -> str:
           """Generate HTML performance report"""

           timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
           report_file = self.output_dir / f"performance_report_{timestamp}.html"

           # Process results
           summary_stats = self._calculate_summary_stats(test_results)
           charts_data = self._prepare_charts_data(test_results)

           # Generate HTML report
           html_content = self._generate_html_report(summary_stats, charts_data)

           with open(report_file, 'w') as f:
               f.write(html_content)

           # Generate JSON data for CI/CD
           json_file = self.output_dir / f"performance_data_{timestamp}.json"
           with open(json_file, 'w') as f:
               json.dump({
                   "timestamp": timestamp,
                   "summary": summary_stats,
                   "test_results": test_results
               }, f, indent=2)

           return str(report_file)

       def _calculate_summary_stats(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
           """Calculate summary statistics across all tests"""

           all_response_times = []
           all_throughputs = []
           total_tests = len(test_results)
           passed_tests = 0

           test_summaries = {}

           for result in test_results:
               test_name = result.get("test_name", "Unknown")

               if result.get("success_criteria_met", {}):
                   criteria_met = all(result["success_criteria_met"].values())
                   if criteria_met:
                       passed_tests += 1

               # Collect metrics
               if "response_times" in result:
                   rt = result["response_times"]
                   all_response_times.extend([
                       rt.get("mean", 0),
                       rt.get("p95", 0),
                       rt.get("p99", 0)
                   ])

               if "average_throughput" in result:
                   all_throughputs.append(result["average_throughput"])

               # Test-specific summary
               test_summaries[test_name] = {
                   "duration": result.get("duration", 0),
                   "success_rate": result.get("success_rate", 0),
                   "total_requests": result.get("total_requests", 0),
                   "avg_response_time": result.get("response_times", {}).get("mean", 0),
                   "throughput": result.get("average_throughput", 0)
               }

           return {
               "overall": {
                   "test_success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                   "total_tests": total_tests,
                   "passed_tests": passed_tests,
                   "avg_response_time": sum(all_response_times) / len(all_response_times) if all_response_times else 0,
                   "avg_throughput": sum(all_throughputs) / len(all_throughputs) if all_throughputs else 0
               },
               "test_summaries": test_summaries
           }

       def _prepare_charts_data(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
           """Prepare data for charts"""

           charts_data = {
               "response_time_distribution": [],
               "throughput_comparison": [],
               "success_rates": [],
               "system_utilization": []
           }

           for result in test_results:
               test_name = result.get("test_name", "Unknown")

               # Response time data
               if "response_times" in result:
                   rt = result["response_times"]
                   charts_data["response_time_distribution"].append({
                       "test": test_name,
                       "min": rt.get("min", 0),
                       "p50": rt.get("p50", 0),
                       "p90": rt.get("p90", 0),
                       "p95": rt.get("p95", 0),
                       "p99": rt.get("p99", 0),
                       "max": rt.get("max", 0)
                   })

               # Throughput data
               if "average_throughput" in result:
                   charts_data["throughput_comparison"].append({
                       "test": test_name,
                       "throughput": result["average_throughput"]
                   })

               # Success rate data
               charts_data["success_rates"].append({
                   "test": test_name,
                   "success_rate": result.get("success_rate", 0)
               })

               # System utilization
               if "system_usage" in result:
                   usage = result["system_usage"]
                   charts_data["system_utilization"].append({
                       "test": test_name,
                       "avg_cpu": usage.get("avg_cpu", 0),
                       "max_cpu": usage.get("max_cpu", 0),
                       "avg_memory": usage.get("avg_memory", 0),
                       "max_memory": usage.get("max_memory", 0)
                   })

           return charts_data

       def _generate_html_report(self, summary_stats: Dict, charts_data: Dict) -> str:
           """Generate HTML report content"""

           return f"""
           <!DOCTYPE html>
           <html>
           <head>
               <title>NeuraScale Performance Test Report</title>
               <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
               <style>
                   body {{ font-family: Arial, sans-serif; margin: 20px; }}
                   .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
                   .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
                   .card {{ background: #f8f9fa; padding: 15px; border-radius: 5px; flex: 1; }}
                   .metric {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
                   .label {{ font-size: 14px; color: #666; }}
                   .chart {{ margin: 20px 0; }}
                   .success {{ color: #27ae60; }}
                   .warning {{ color: #f39c12; }}
                   .error {{ color: #e74c3c; }}
               </style>
           </head>
           <body>
               <div class="header">
                   <h1>NeuraScale Performance Test Report</h1>
                   <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
               </div>

               <div class="summary">
                   <div class="card">
                       <div class="metric">{summary_stats['overall']['test_success_rate']:.1f}%</div>
                       <div class="label">Test Success Rate</div>
                   </div>
                   <div class="card">
                       <div class="metric">{summary_stats['overall']['avg_response_time']:.3f}s</div>
                       <div class="label">Avg Response Time</div>
                   </div>
                   <div class="card">
                       <div class="metric">{summary_stats['overall']['avg_throughput']:.1f}</div>
                       <div class="label">Avg Throughput</div>
                   </div>
                   <div class="card">
                       <div class="metric">{summary_stats['overall']['total_tests']}</div>
                       <div class="label">Total Tests</div>
                   </div>
               </div>

               <div class="chart" id="response-time-chart"></div>
               <div class="chart" id="throughput-chart"></div>
               <div class="chart" id="success-rate-chart"></div>
               <div class="chart" id="system-utilization-chart"></div>

               <script>
                   // Response time distribution chart
                   var responseTimeData = {json.dumps(charts_data['response_time_distribution'])};
                   var rtTrace = {{
                       x: responseTimeData.map(d => d.test),
                       y: responseTimeData.map(d => d.p95),
                       type: 'bar',
                       name: 'P95 Response Time',
                       marker: {{ color: '#3498db' }}
                   }};
                   Plotly.newPlot('response-time-chart', [rtTrace], {{
                       title: 'Response Time (P95) by Test',
                       xaxis: {{ title: 'Test Name' }},
                       yaxis: {{ title: 'Response Time (seconds)' }}
                   }});

                   // Throughput comparison chart
                   var throughputData = {json.dumps(charts_data['throughput_comparison'])};
                   var tpTrace = {{
                       x: throughputData.map(d => d.test),
                       y: throughputData.map(d => d.throughput),
                       type: 'bar',
                       name: 'Throughput',
                       marker: {{ color: '#2ecc71' }}
                   }};
                   Plotly.newPlot('throughput-chart', [tpTrace], {{
                       title: 'Throughput by Test',
                       xaxis: {{ title: 'Test Name' }},
                       yaxis: {{ title: 'Requests/Transactions per Second' }}
                   }});

                   // Success rate chart
                   var successData = {json.dumps(charts_data['success_rates'])};
                   var srTrace = {{
                       x: successData.map(d => d.test),
                       y: successData.map(d => d.success_rate),
                       type: 'bar',
                       name: 'Success Rate',
                       marker: {{ color: '#e67e22' }}
                   }};
                   Plotly.newPlot('success-rate-chart', [srTrace], {{
                       title: 'Success Rate by Test',
                       xaxis: {{ title: 'Test Name' }},
                       yaxis: {{ title: 'Success Rate (%)' }}
                   }});

                   // System utilization chart
                   var utilizationData = {json.dumps(charts_data['system_utilization'])};
                   var cpuTrace = {{
                       x: utilizationData.map(d => d.test),
                       y: utilizationData.map(d => d.avg_cpu),
                       type: 'bar',
                       name: 'Avg CPU %',
                       marker: {{ color: '#9b59b6' }}
                   }};
                   var memTrace = {{
                       x: utilizationData.map(d => d.test),
                       y: utilizationData.map(d => d.avg_memory),
                       type: 'bar',
                       name: 'Avg Memory %',
                       marker: {{ color: '#e74c3c' }}
                   }};
                   Plotly.newPlot('system-utilization-chart', [cpuTrace, memTrace], {{
                       title: 'System Utilization by Test',
                       xaxis: {{ title: 'Test Name' }},
                       yaxis: {{ title: 'Utilization (%)' }},
                       barmode: 'group'
                   }});
               </script>

               <h2>Test Details</h2>
               <table border="1" style="width:100%; border-collapse: collapse;">
                   <thead>
                       <tr>
                           <th>Test Name</th>
                           <th>Duration (s)</th>
                           <th>Success Rate (%)</th>
                           <th>Total Requests</th>
                           <th>Avg Response Time (s)</th>
                           <th>Throughput</th>
                       </tr>
                   </thead>
                   <tbody>
           """

           for test_name, data in summary_stats['test_summaries'].items():
               html_content += f"""
                       <tr>
                           <td>{test_name}</td>
                           <td>{data['duration']:.1f}</td>
                           <td>{data['success_rate']:.1f}</td>
                           <td>{data['total_requests']}</td>
                           <td>{data['avg_response_time']:.3f}</td>
                           <td>{data['throughput']:.1f}</td>
                       </tr>
               """

           html_content += """
                   </tbody>
               </table>
           </body>
           </html>
           """

           return html_content
   ```

2. **CI/CD Integration** (2 hours)

   ```bash
   # ci/scripts/run-performance-tests.sh
   #!/bin/bash

   set -e

   # Performance test runner script
   echo "🚀 Starting NeuraScale Performance Tests"

   # Configuration
   TEST_ENV=${TEST_ENV:-staging}
   REPORT_DIR="tests/performance/reports/generated"
   BASELINE_FILE="tests/performance/baselines/baseline.json"

   # Create reports directory
   mkdir -p "$REPORT_DIR"

   # Start test environment
   echo "📦 Starting test environment..."
   docker-compose -f docker/compose/docker-compose.performance.yml up -d

   # Wait for services to be ready
   echo "⏳ Waiting for services..."
   timeout 300 bash -c 'until curl -f http://localhost:8000/health; do sleep 5; done'

   # Run performance tests
   echo "🧪 Running performance tests..."

   # API Load Tests
   python -m pytest tests/performance/load/api_load_test.py \
       --tb=short \
       --json-report \
       --json-report-file="$REPORT_DIR/api_load_results.json"

   # Database Performance Tests
   python -m pytest tests/performance/load/database_load_test.py \
       --tb=short \
       --json-report \
       --json-report-file="$REPORT_DIR/db_results.json"

   # ML Pipeline Tests
   python -m pytest tests/performance/benchmarks/ml_model_bench.py \
       --tb=short \
       --json-report \
       --json-report-file="$REPORT_DIR/ml_results.json"

   # End-to-End Scenarios
   python -m pytest tests/performance/scenarios/ \
       --tb=short \
       --json-report \
       --json-report-file="$REPORT_DIR/e2e_results.json"

   # Generate comprehensive report
   echo "📊 Generating performance report..."
   python tests/performance/utils/generate_report.py \
       --results-dir "$REPORT_DIR" \
       --baseline "$BASELINE_FILE" \
       --output "$REPORT_DIR/performance_report.html"

   # Check for performance regressions
   echo "🔍 Checking for performance regressions..."
   if python tests/performance/utils/regression_check.py \
       --current "$REPORT_DIR" \
       --baseline "$BASELINE_FILE" \
       --threshold 10; then
       echo "✅ No significant performance regressions detected"
   else
       echo "❌ Performance regression detected!"
       exit 1
   fi

   # Cleanup
   echo "🧹 Cleaning up test environment..."
   docker-compose -f docker/compose/docker-compose.performance.yml down

   echo "✅ Performance tests completed successfully"
   ```

## Success Criteria

### Performance Success

- [ ] All load tests meet performance targets
- [ ] Stress tests identify system limits
- [ ] No performance regressions detected
- [ ] Resource utilization within acceptable ranges
- [ ] Scalability requirements validated

### Test Coverage Success

- [ ] API endpoints performance tested
- [ ] Database performance characterized
- [ ] ML pipeline benchmarked
- [ ] Real-world scenarios validated
- [ ] Multi-user concurrency tested

### Reporting Success

- [ ] Comprehensive reports generated
- [ ] Performance baselines established
- [ ] Regression detection working
- [ ] CI/CD integration complete
- [ ] Monitoring dashboards updated

## Cost Estimation

### Infrastructure Costs (Monthly)

- **Performance Test Environment**: $400/month
- **Load Generation Tools**: $200/month
- **Monitoring & Reporting**: $150/month
- **Total**: ~$750/month

### Development Resources

- **Senior Performance Engineer**: 5-6 days
- **ML Performance Engineer**: 2 days
- **Database Performance Engineer**: 2 days
- **Integration Engineer**: 1 day
- **Documentation**: 0.5 days

## Dependencies

### External Dependencies

- **pytest**: 7.4+
- **Locust**: 2.17+
- **asyncio**: Python 3.12+
- **aiohttp**: 3.8+
- **WebSockets**: Latest

### Internal Dependencies

- **Application Services**: Running
- **Test Environment**: Deployed
- **Monitoring Stack**: Configured
- **CI/CD Pipeline**: Functional

## Risk Mitigation

### Technical Risks

1. **Environment Instability**: Containerized test environment
2. **Resource Contention**: Isolated test infrastructure
3. **Test Data Management**: Automated data generation
4. **Network Variability**: Multiple test runs and averaging

### Process Risks

1. **Long Test Execution**: Parallel test execution
2. **Result Interpretation**: Automated regression detection
3. **Environment Differences**: Consistent test configurations
4. **Performance Drift**: Regular baseline updates

---

**Next Phase**: Phase 21 - Documentation & Training
**Dependencies**: All system components, testing infrastructure
**Review Date**: Implementation completion + 1 week
