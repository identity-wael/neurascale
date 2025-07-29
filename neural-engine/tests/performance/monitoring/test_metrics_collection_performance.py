"""
Test monitoring metrics collection performance and overhead
"""

import pytest
import asyncio
import time
import psutil
from datetime import datetime, timedelta
from typing import List

from neural_engine.src.monitoring import (
    PerformanceMonitor,
    MonitoringConfig,
    NeuralMetricsCollector,
    DeviceMetricsCollector,
    SystemMetricsCollector,
)


class TestMetricsCollectionPerformance:
    """Test metrics collection overhead and performance"""

    @pytest.fixture
    async def performance_monitor(self):
        """Create performance monitor instance"""
        config = MonitoringConfig(
            neural_metrics_interval_ms=100,
            device_metrics_interval_ms=1000,
            system_metrics_interval_ms=5000,
            prometheus_port=9091,  # Use different port for tests
        )
        monitor = PerformanceMonitor(config)
        yield monitor
        await monitor.stop_monitoring()

    @pytest.fixture
    def neural_collector(self):
        """Create neural metrics collector"""
        return NeuralMetricsCollector(history_size=1000)

    @pytest.fixture
    def device_collector(self):
        """Create device metrics collector"""
        return DeviceMetricsCollector(stability_window_size=100)

    @pytest.fixture
    def system_collector(self):
        """Create system metrics collector"""
        return SystemMetricsCollector(history_size=1000)

    @pytest.mark.asyncio
    async def test_neural_metrics_collection_overhead(self, neural_collector):
        """Test neural metrics collection CPU and memory overhead"""
        # Baseline measurements
        process = psutil.Process()
        cpu_before = process.cpu_percent(interval=0.1)
        memory_before = process.memory_info().rss / 1024 / 1024  # MB

        # Simulate high-frequency metrics collection
        start_time = time.time()
        iterations = 10000

        for _ in range(iterations):
            # Simulate metric recording
            neural_collector.start_signal_processing()
            await asyncio.sleep(0.001)  # 1ms processing
            neural_collector.end_signal_processing()

            neural_collector.start_feature_extraction()
            await asyncio.sleep(0.002)  # 2ms extraction
            neural_collector.end_feature_extraction()

            neural_collector.start_model_inference()
            await asyncio.sleep(0.005)  # 5ms inference
            neural_collector.end_model_inference()

            neural_collector.record_data_quality_score("test_session", 0.95)
            neural_collector.record_processing_accuracy(0.98)
            neural_collector.record_processing_throughput(1000)

        # Measure overhead
        elapsed_time = time.time() - start_time
        cpu_after = process.cpu_percent(interval=0.1)
        memory_after = process.memory_info().rss / 1024 / 1024

        cpu_overhead = cpu_after - cpu_before
        memory_overhead = memory_after - memory_before
        avg_collection_time = (
            (elapsed_time - iterations * 0.008) / iterations * 1000
        )  # ms

        # Verify overhead is within acceptable limits
        assert cpu_overhead < 5.0, f"CPU overhead too high: {cpu_overhead}%"
        assert memory_overhead < 50, f"Memory overhead too high: {memory_overhead}MB"
        assert (
            avg_collection_time < 0.1
        ), f"Collection time too high: {avg_collection_time}ms"

        # Verify metrics were collected correctly
        metrics = await neural_collector.collect_current_metrics()
        assert metrics.signal_processing_latency > 0
        assert metrics.feature_extraction_time > 0
        assert metrics.model_inference_latency > 0
        assert metrics.data_quality_score == 0.95
        assert metrics.processing_accuracy == 0.98

    @pytest.mark.asyncio
    async def test_device_metrics_collection_scalability(self, device_collector):
        """Test device metrics collection with many devices"""
        num_devices = 100
        device_ids = [f"device_{i}" for i in range(num_devices)]

        # Register all devices
        start_time = time.time()
        for device_id in device_ids:
            device_collector.register_device(device_id)

        registration_time = time.time() - start_time
        assert registration_time < 0.1, f"Registration too slow: {registration_time}s"

        # Simulate metrics collection for all devices
        collection_start = time.time()

        for _ in range(100):  # 100 collection cycles
            for device_id in device_ids:
                # Simulate device metrics
                device_collector.monitor_device_connection(device_id)
                device_collector.record_signal_quality(device_id, 0.9)
                device_collector.track_data_rate(device_id, 250)
                device_collector.record_device_latency(device_id, 10)
                device_collector.record_packet_stats(device_id, 1000, 5)

        collection_time = time.time() - collection_start
        avg_time_per_device = collection_time / (100 * num_devices) * 1000  # ms

        assert (
            avg_time_per_device < 0.1
        ), f"Per-device collection too slow: {avg_time_per_device}ms"

        # Verify metrics retrieval performance
        retrieval_start = time.time()

        for device_id in device_ids:
            metrics = await device_collector.get_device_metrics(device_id)
            assert metrics.connection_stability > 0
            assert metrics.signal_quality == 0.9
            assert metrics.data_rate > 0

        retrieval_time = time.time() - retrieval_start
        avg_retrieval_time = retrieval_time / num_devices * 1000  # ms

        assert (
            avg_retrieval_time < 1.0
        ), f"Metrics retrieval too slow: {avg_retrieval_time}ms"

    @pytest.mark.asyncio
    async def test_system_metrics_collection_efficiency(self, system_collector):
        """Test system metrics collection efficiency"""
        # Measure collection time
        collection_times = []

        for _ in range(100):
            start = time.time()
            metrics = await system_collector.collect_current_metrics()
            collection_times.append((time.time() - start) * 1000)  # ms

            # Verify metrics are collected
            assert metrics.cpu_usage_percent >= 0
            assert metrics.memory_usage_mb > 0
            assert metrics.disk_usage_percent >= 0
            await asyncio.sleep(0.01)  # Small delay between collections

        # Calculate statistics
        avg_collection_time = sum(collection_times) / len(collection_times)
        max_collection_time = max(collection_times)

        assert (
            avg_collection_time < 10
        ), f"Average collection time too high: {avg_collection_time}ms"
        assert (
            max_collection_time < 50
        ), f"Max collection time too high: {max_collection_time}ms"

    @pytest.mark.asyncio
    async def test_monitoring_system_startup_performance(self, performance_monitor):
        """Test monitoring system startup time"""
        start_time = time.time()

        await performance_monitor.start_monitoring()

        startup_time = time.time() - start_time

        # Verify startup completes quickly
        assert startup_time < 2.0, f"Startup too slow: {startup_time}s"

        # Verify all components are running
        status = performance_monitor.get_monitoring_status()
        assert status.is_running
        assert status.system_health in ["healthy", "degraded"]

    @pytest.mark.asyncio
    async def test_concurrent_metrics_collection(self, performance_monitor):
        """Test concurrent metrics collection from multiple sources"""
        await performance_monitor.start_monitoring()

        # Simulate concurrent metric collection
        async def collect_neural_metrics(session_id: str, count: int):
            for i in range(count):
                await performance_monitor.collect_neural_metrics(f"{session_id}_{i}")
                await asyncio.sleep(0.001)

        async def monitor_devices(device_ids: List[str], count: int):
            for i in range(count):
                for device_id in device_ids:
                    await performance_monitor.monitor_device_performance(device_id)
                await asyncio.sleep(0.01)

        # Run concurrent collections
        start_time = time.time()

        tasks = [
            collect_neural_metrics("session1", 100),
            collect_neural_metrics("session2", 100),
            collect_neural_metrics("session3", 100),
            monitor_devices(["dev1", "dev2", "dev3"], 50),
            monitor_devices(["dev4", "dev5", "dev6"], 50),
        ]

        await asyncio.gather(*tasks)

        elapsed_time = time.time() - start_time

        # Verify concurrent execution doesn't cause significant slowdown
        assert elapsed_time < 2.0, f"Concurrent collection too slow: {elapsed_time}s"

        # Check metrics were collected
        status = performance_monitor.get_monitoring_status()
        assert status.metrics_collected > 0

    @pytest.mark.asyncio
    async def test_metric_history_memory_usage(self, neural_collector):
        """Test memory usage of metric history storage"""
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024

        # Fill history to capacity
        for i in range(1000):  # History size is 1000
            neural_collector.signal_latency_history.append(10.0 + i * 0.1)
            neural_collector.feature_time_history.append(20.0 + i * 0.1)
            neural_collector.inference_latency_history.append(50.0 + i * 0.1)
            neural_collector.quality_score_history.append(0.9)
            neural_collector.accuracy_history.append(0.95)
            neural_collector.throughput_history.append(1000 + i)

        memory_after = process.memory_info().rss / 1024 / 1024
        memory_used = memory_after - memory_before

        # Verify memory usage is reasonable
        assert memory_used < 10, f"History memory usage too high: {memory_used}MB"

        # Verify old data is evicted
        neural_collector.signal_latency_history.append(999.9)
        assert len(neural_collector.signal_latency_history) == 1000
        assert neural_collector.signal_latency_history[0] != 10.0  # First item evicted

    @pytest.mark.asyncio
    async def test_metrics_aggregation_performance(self, neural_collector):
        """Test performance of metrics aggregation and summary generation"""
        # Fill with test data
        for i in range(1000):
            neural_collector.signal_latency_history.append(10.0 + (i % 10))
            neural_collector.feature_time_history.append(20.0 + (i % 20))
            neural_collector.inference_latency_history.append(50.0 + (i % 30))

        # Measure aggregation time
        start_time = time.time()

        summary = neural_collector.get_metrics_summary(
            datetime.now() - timedelta(hours=1), datetime.now()
        )

        aggregation_time = (time.time() - start_time) * 1000  # ms

        # Verify aggregation is fast
        assert aggregation_time < 10, f"Aggregation too slow: {aggregation_time}ms"

        # Verify summary contains expected metrics
        assert "avg_processing_latency" in summary
        assert "p95_processing_latency" in summary
        assert "max_processing_latency" in summary

        # Test percentile calculation performance
        start_time = time.time()
        percentiles = neural_collector.get_latency_percentiles()
        percentile_time = (time.time() - start_time) * 1000

        assert (
            percentile_time < 5
        ), f"Percentile calculation too slow: {percentile_time}ms"
        assert "signal_p50" in percentiles
        assert "signal_p95" in percentiles
        assert "signal_p99" in percentiles


@pytest.mark.benchmark
class TestMonitoringBenchmarks:
    """Benchmark tests for monitoring performance"""

    def test_neural_metrics_throughput(self, benchmark, neural_collector):
        """Benchmark neural metrics collection throughput"""

        def collect_metrics():
            neural_collector.record_signal_latency(10.5, "test_device")
            neural_collector.record_processing_throughput(1000)
            neural_collector.record_feature_extraction_time(25.0)
            neural_collector.record_model_inference_latency("model_1", 50.0)
            neural_collector.record_data_quality_score("session_1", 0.95)
            neural_collector.record_processing_accuracy(0.98)

        # Run benchmark
        result = benchmark(collect_metrics)

        # Verify we can handle high throughput
        ops_per_second = 1.0 / result
        assert ops_per_second > 10000, f"Throughput too low: {ops_per_second} ops/sec"

    def test_device_metrics_lookup_performance(self, benchmark, device_collector):
        """Benchmark device metrics lookup performance"""
        # Setup: Register many devices
        for i in range(1000):
            device_collector.register_device(f"device_{i}")
            device_collector.record_signal_quality(f"device_{i}", 0.9)

        def lookup_metrics():
            # Look up random device
            device_id = f"device_{benchmark._num % 1000}"
            return device_collector.get_device_health_score(device_id)

        # Run benchmark
        result = benchmark(lookup_metrics)

        # Verify lookup is fast
        assert result < 0.001, f"Lookup too slow: {result}s"
