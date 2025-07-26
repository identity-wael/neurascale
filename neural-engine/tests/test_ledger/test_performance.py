"""Performance benchmarking tests for Neural Ledger.

These tests validate that the system meets the <100ms latency requirement
and other performance targets specified in the design.
"""

import pytest
import asyncio
import time
import statistics
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
import uuid
from concurrent.futures import ThreadPoolExecutor
import numpy as np

from ledger.neural_ledger import NeuralLedger
from ledger.event_schema import EventType, NeuralLedgerEvent
from ledger.hash_chain import HashChain
from ledger.event_processor import EventProcessor


class TestNeuralLedgerPerformance:
    """Performance tests for Neural Ledger operations."""

    @pytest.fixture
    def mock_ledger(self, mocker):
        """Create a mocked Neural Ledger for performance testing."""
        # Mock GCP clients to avoid actual API calls
        mocker.patch("google.cloud.bigtable.Client")
        mocker.patch("google.cloud.firestore.Client")
        mocker.patch("google.cloud.bigquery.Client")
        mocker.patch("google.cloud.kms.KeyManagementServiceClient")
        mocker.patch("google.cloud.pubsub_v1.PublisherClient")
        mocker.patch("google.cloud.monitoring_v3.MetricServiceClient")

        # Mock the EventProcessor to avoid monitoring issues
        mock_processor = mocker.Mock()
        mocker.patch("ledger.neural_ledger.EventProcessor", return_value=mock_processor)

        ledger = NeuralLedger(project_id="test-project", location="test-location")
        # Mock the initialization
        ledger._initialized = True
        ledger._last_event_hash = "initial_hash"

        return ledger

    @pytest.fixture
    def hash_chain(self):
        """Create a hash chain instance for testing."""
        return HashChain()

    async def _measure_latency(
        self, operation, iterations: int = 100
    ) -> Dict[str, float]:
        """Measure latency statistics for an operation.

        Args:
            operation: Async function to measure
            iterations: Number of iterations to run

        Returns:
            Dictionary with latency statistics
        """
        latencies = []

        for _ in range(iterations):
            start = time.perf_counter()
            await operation()
            end = time.perf_counter()
            latencies.append((end - start) * 1000)  # Convert to ms

        return {
            "min": min(latencies),
            "max": max(latencies),
            "mean": statistics.mean(latencies),
            "median": statistics.median(latencies),
            "p95": np.percentile(latencies, 95),
            "p99": np.percentile(latencies, 99),
        }

    @pytest.mark.asyncio
    async def test_event_creation_performance(self):
        """Test that event creation meets performance requirements."""

        # Create test event
        async def create_event():
            return NeuralLedgerEvent(
                event_type=EventType.SESSION_STARTED,
                session_id=f"perf-session-{uuid.uuid4()}",
                device_id="test-device",
                metadata={"test": True},
            )

        stats = await self._measure_latency(create_event, iterations=1000)

        # Event creation should be very fast (< 1ms)
        assert (
            stats["p99"] < 1.0
        ), f"Event creation p99 latency {stats['p99']:.2f}ms exceeds 1ms"
        assert (
            stats["mean"] < 0.5
        ), f"Event creation mean latency {stats['mean']:.2f}ms exceeds 0.5ms"

        print(f"\nEvent Creation Performance:")
        print(f"  Mean: {stats['mean']:.3f}ms")
        print(f"  P95: {stats['p95']:.3f}ms")
        print(f"  P99: {stats['p99']:.3f}ms")

    @pytest.mark.asyncio
    async def test_hash_computation_performance(self, hash_chain):
        """Test hash computation performance."""
        # Create test event
        event = NeuralLedgerEvent(
            event_type=EventType.DATA_INGESTED,
            session_id="test-session",
            data_hash="test-data-hash",
            metadata={"size_bytes": 1024},
        )

        async def compute_hash():
            return HashChain.compute_event_hash(event, "previous_hash")

        stats = await self._measure_latency(compute_hash, iterations=1000)

        # Hash computation should be fast (< 5ms)
        assert (
            stats["p99"] < 5.0
        ), f"Hash computation p99 latency {stats['p99']:.2f}ms exceeds 5ms"
        assert (
            stats["mean"] < 2.0
        ), f"Hash computation mean latency {stats['mean']:.2f}ms exceeds 2ms"

        print(f"\nHash Computation Performance:")
        print(f"  Mean: {stats['mean']:.3f}ms")
        print(f"  P95: {stats['p95']:.3f}ms")
        print(f"  P99: {stats['p99']:.3f}ms")

    @pytest.mark.asyncio
    async def test_event_logging_latency(self, mock_ledger, mocker):
        """Test end-to-end event logging latency."""
        # Mock the publish future
        future = mocker.Mock()
        future.result.return_value = "message-id"
        mock_ledger.publisher.publish.return_value = future

        # Set up hash chain state
        mock_ledger._last_event_hash = "current_hash"

        async def log_event():
            return await mock_ledger.log_event(
                event_type=EventType.SESSION_STARTED,
                session_id=f"perf-{uuid.uuid4()}",
                metadata={"test": True},
            )

        stats = await self._measure_latency(log_event, iterations=100)

        # Event logging should meet <100ms requirement
        assert (
            stats["p99"] < 100.0
        ), f"Event logging p99 latency {stats['p99']:.2f}ms exceeds 100ms"
        assert (
            stats["mean"] < 50.0
        ), f"Event logging mean latency {stats['mean']:.2f}ms exceeds 50ms"

        print(f"\nEvent Logging Performance:")
        print(f"  Mean: {stats['mean']:.3f}ms")
        print(f"  P95: {stats['p95']:.3f}ms")
        print(f"  P99: {stats['p99']:.3f}ms")

    @pytest.mark.asyncio
    async def test_concurrent_event_logging(self, mock_ledger, mocker):
        """Test performance under concurrent load."""
        # Mock the publish future
        future = mocker.Mock()
        future.result.return_value = "message-id"
        mock_ledger.publisher.publish.return_value = future

        # Set up hash chain state
        mock_ledger._last_event_hash = "current_hash"

        async def log_events_batch(batch_size: int):
            """Log multiple events concurrently."""
            tasks = []
            for i in range(batch_size):
                task = mock_ledger.log_event(
                    event_type=EventType.DATA_INGESTED,
                    session_id=f"concurrent-{uuid.uuid4()}",
                    data_hash=f"hash-{i}",
                    metadata={"batch": True},
                )
                tasks.append(task)

            return await asyncio.gather(*tasks)

        # Test with different batch sizes
        batch_sizes = [10, 50, 100]

        for batch_size in batch_sizes:
            start = time.perf_counter()
            await log_events_batch(batch_size)
            end = time.perf_counter()

            total_time_ms = (end - start) * 1000
            avg_time_ms = total_time_ms / batch_size

            print(f"\nConcurrent Logging (batch={batch_size}):")
            print(f"  Total time: {total_time_ms:.2f}ms")
            print(f"  Avg per event: {avg_time_ms:.2f}ms")

            # Even under load, average should stay under 100ms
            assert (
                avg_time_ms < 100.0
            ), f"Average latency {avg_time_ms:.2f}ms exceeds 100ms for batch={batch_size}"

    @pytest.mark.asyncio
    async def test_merkle_tree_performance(self, hash_chain):
        """Test Merkle tree computation performance for integrity checks."""
        # Create test events
        events = []
        for i in range(1000):
            event = NeuralLedgerEvent(
                event_type=EventType.MODEL_INFERENCE,
                session_id="merkle-test",
                metadata={"index": i},
            )
            event.event_hash = f"hash_{i}"
            events.append(event)

        # Measure Merkle root computation
        start = time.perf_counter()
        merkle_root = hash_chain.compute_merkle_root(events)
        end = time.perf_counter()

        computation_time_ms = (end - start) * 1000

        print(f"\nMerkle Tree Performance (1000 events):")
        print(f"  Computation time: {computation_time_ms:.2f}ms")

        # Merkle tree computation should be efficient
        assert (
            computation_time_ms < 50.0
        ), f"Merkle computation time {computation_time_ms:.2f}ms exceeds 50ms"

    @pytest.mark.asyncio
    async def test_event_processor_performance(self, mocker):
        """Test event processor performance with mocked storage."""
        # Mock all storage clients
        mock_bigtable = mocker.Mock()
        mock_firestore = mocker.Mock()
        mock_bigquery = mocker.Mock()
        mock_kms = mocker.Mock()

        # Mock monitoring to avoid initialization issues
        mock_monitoring = mocker.Mock()
        mocker.patch(
            "ledger.event_processor.LedgerMonitoring", return_value=mock_monitoring
        )

        # Mock storage operations to be fast
        mocker.patch("asyncio.get_event_loop")

        processor = EventProcessor(
            project_id="test-project",
            location="test-location",
            bigtable_client=mock_bigtable,
            firestore_client=mock_firestore,
            bigquery_client=mock_bigquery,
            kms_client=mock_kms,
        )

        # Mock the storage write methods
        mocker.patch.object(processor, "_write_to_bigtable", return_value=None)
        mocker.patch.object(processor, "_write_to_firestore", return_value=None)
        mocker.patch.object(processor, "_write_to_bigquery", return_value=None)
        mocker.patch.object(processor, "_verify_signature", return_value=True)
        mocker.patch.object(processor, "_update_metrics", return_value=None)
        mocker.patch.object(processor, "_trigger_compliance_check", return_value=None)

        # Create test event
        event = NeuralLedgerEvent(
            event_type=EventType.SESSION_CREATED,
            session_id="processor-test",
            user_id="test-user",
        )

        async def process_event():
            return await processor.process_event(event.to_dict())

        stats = await self._measure_latency(process_event, iterations=100)

        print(f"\nEvent Processor Performance:")
        print(f"  Mean: {stats['mean']:.3f}ms")
        print(f"  P95: {stats['p95']:.3f}ms")
        print(f"  P99: {stats['p99']:.3f}ms")

        # Processing should be fast when storage is mocked
        assert (
            stats["p99"] < 10.0
        ), f"Event processing p99 latency {stats['p99']:.2f}ms exceeds 10ms"

    @pytest.mark.asyncio
    async def test_batch_processing_throughput(self, mocker):
        """Test batch processing throughput."""
        # Mock monitoring to avoid initialization issues
        mock_monitoring = mocker.Mock()
        mocker.patch(
            "ledger.event_processor.LedgerMonitoring", return_value=mock_monitoring
        )

        # Mock storage clients
        processor = EventProcessor(
            project_id="test-project",
            location="test-location",
            bigtable_client=mocker.Mock(),
            firestore_client=mocker.Mock(),
            bigquery_client=mocker.Mock(),
            kms_client=mocker.Mock(),
        )

        # Mock processing methods
        mocker.patch.object(processor, "process_event", return_value=True)

        # Create batch of events
        batch_size = 1000
        events = []
        for i in range(batch_size):
            event = NeuralLedgerEvent(
                event_type=EventType.DATA_INGESTED,
                session_id=f"batch-{i // 100}",
                data_hash=f"hash-{i}",
            )
            events.append(event.to_dict())

        # Measure batch processing time
        start = time.perf_counter()
        results = await processor.process_batch(events)
        end = time.perf_counter()

        processing_time_s = end - start
        throughput = batch_size / processing_time_s

        print(f"\nBatch Processing Performance:")
        print(f"  Batch size: {batch_size}")
        print(f"  Processing time: {processing_time_s:.2f}s")
        print(f"  Throughput: {throughput:.0f} events/second")

        # Should process at least 1000 events per second
        assert (
            throughput > 1000
        ), f"Throughput {throughput:.0f} events/s is below 1000 events/s"

    def test_memory_efficiency(self):
        """Test memory efficiency of event objects."""
        import sys

        # Create a sample event
        event = NeuralLedgerEvent(
            event_type=EventType.SESSION_CREATED,
            session_id="memory-test",
            device_id="test-device",
            user_id="test-user",
            metadata={"test": True, "data": "x" * 100},
        )

        # Get size of event object
        event_size = sys.getsizeof(event)
        dict_size = sys.getsizeof(event.to_dict())

        print(f"\nMemory Efficiency:")
        print(f"  Event object size: {event_size} bytes")
        print(f"  Event dict size: {dict_size} bytes")

        # Events should be memory efficient (< 10KB per event)
        assert event_size < 10240, f"Event object size {event_size} bytes exceeds 10KB"
        assert dict_size < 5120, f"Event dict size {dict_size} bytes exceeds 5KB"


class TestPerformanceUnderLoad:
    """Test performance under various load conditions."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_sustained_load(self, mock_ledger, mocker):
        """Test performance under sustained load for 60 seconds."""
        # Mock the publish future
        future = mocker.Mock()
        future.result.return_value = "message-id"
        mock_ledger.publisher.publish.return_value = future

        # Set up hash chain state
        mock_ledger._last_event_hash = "current_hash"

        # Track metrics
        latencies = []
        errors = 0
        events_logged = 0

        # Run for 60 seconds
        start_time = time.time()
        target_duration = 60  # seconds

        async def log_event_with_tracking():
            nonlocal events_logged, errors
            try:
                event_start = time.perf_counter()
                await mock_ledger.log_event(
                    event_type=EventType.DATA_INGESTED,
                    session_id=f"load-test-{uuid.uuid4()}",
                    metadata={"load_test": True},
                )
                event_end = time.perf_counter()

                latency_ms = (event_end - event_start) * 1000
                latencies.append(latency_ms)
                events_logged += 1
            except Exception:
                errors += 1

        # Generate load
        while (time.time() - start_time) < target_duration:
            # Create 10 concurrent requests
            tasks = [log_event_with_tracking() for _ in range(10)]
            await asyncio.gather(*tasks, return_exceptions=True)

            # Small delay to avoid overwhelming
            await asyncio.sleep(0.1)

        # Calculate statistics
        p99_latency = np.percentile(latencies, 99)
        mean_latency = np.mean(latencies)
        error_rate = (
            errors / (events_logged + errors) if (events_logged + errors) > 0 else 0
        )

        print(f"\nSustained Load Test Results:")
        print(f"  Duration: {target_duration}s")
        print(f"  Events logged: {events_logged}")
        print(f"  Errors: {errors}")
        print(f"  Error rate: {error_rate:.2%}")
        print(f"  Mean latency: {mean_latency:.2f}ms")
        print(f"  P99 latency: {p99_latency:.2f}ms")

        # Validate performance under load
        assert (
            p99_latency < 200.0
        ), f"P99 latency {p99_latency:.2f}ms exceeds 200ms under load"
        assert error_rate < 0.01, f"Error rate {error_rate:.2%} exceeds 1%"
