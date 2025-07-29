"""
Test alert processing latency and performance
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta

from neural_engine.src.monitoring.alerting import (
    AlertManager,
    Alert,
    AlertRule,
    AlertSeverity,
)


class TestAlertProcessingLatency:
    """Test alert processing performance and latency"""

    @pytest.fixture
    async def alert_manager(self):
        """Create alert manager instance"""
        manager = AlertManager(
            webhook_url="http://localhost:8888/webhook", alert_history_size=10000
        )
        yield manager

    @pytest.mark.asyncio
    async def test_single_alert_processing_latency(self, alert_manager):
        """Test latency of processing a single alert"""
        # Trigger alert
        start_time = time.time()

        await alert_manager.trigger_alert(
            name="TestAlert",
            severity="critical",
            message="Test critical alert",
            labels={"component": "test", "service": "monitoring"},
        )

        # Process alert
        processed = await alert_manager.process_pending_alerts()

        processing_time = (time.time() - start_time) * 1000  # ms

        assert processed == 1
        assert processing_time < 10, f"Alert processing too slow: {processing_time}ms"

    @pytest.mark.asyncio
    async def test_bulk_alert_processing_performance(self, alert_manager):
        """Test performance of processing many alerts"""
        num_alerts = 1000

        # Queue many alerts
        queue_start = time.time()

        for i in range(num_alerts):
            await alert_manager.trigger_alert(
                name=f"BulkAlert_{i}",
                severity="warning" if i % 3 == 0 else "info",
                message=f"Bulk test alert {i}",
                labels={"index": str(i), "batch": "test"},
            )

        queue_time = time.time() - queue_start
        avg_queue_time = queue_time / num_alerts * 1000  # ms per alert

        assert (
            avg_queue_time < 0.1
        ), f"Alert queuing too slow: {avg_queue_time}ms per alert"

        # Process all alerts
        process_start = time.time()
        total_processed = 0

        while total_processed < num_alerts:
            processed = await alert_manager.process_pending_alerts()
            total_processed += processed
            if processed == 0:
                await asyncio.sleep(0.01)

        process_time = time.time() - process_start
        avg_process_time = process_time / num_alerts * 1000  # ms per alert

        assert (
            avg_process_time < 1.0
        ), f"Alert processing too slow: {avg_process_time}ms per alert"
        assert total_processed == num_alerts

    @pytest.mark.asyncio
    async def test_alert_rule_evaluation_performance(self, alert_manager):
        """Test performance of alert rule evaluation"""
        # Register multiple alert rules
        rules = [
            AlertRule(
                name="HighCPU",
                expression="cpu_usage > 90",
                duration=timedelta(seconds=0),
                severity=AlertSeverity.CRITICAL,
            ),
            AlertRule(
                name="HighMemory",
                expression="memory_usage_percent > 80",
                duration=timedelta(seconds=0),
                severity=AlertSeverity.WARNING,
            ),
            AlertRule(
                name="HighLatency",
                expression="processing_latency > 100",
                duration=timedelta(seconds=0),
                severity=AlertSeverity.WARNING,
            ),
            AlertRule(
                name="LowQuality",
                expression="data_quality < 0.7",
                duration=timedelta(seconds=0),
                severity=AlertSeverity.INFO,
            ),
        ]

        for rule in rules:
            alert_manager.register_alert_rule(rule)

        # Simulate metrics for evaluation
        metrics = {
            "cpu_usage": 95,
            "memory_usage_percent": 85,
            "processing_latency": 120,
            "data_quality": 0.6,
            "other_metric_1": 100,
            "other_metric_2": 200,
            "other_metric_3": 300,
        }

        # Measure evaluation time
        eval_times = []

        for _ in range(100):
            start = time.time()
            await alert_manager.evaluate_alerts(metrics)
            eval_times.append((time.time() - start) * 1000)  # ms

        avg_eval_time = sum(eval_times) / len(eval_times)
        max_eval_time = max(eval_times)

        assert avg_eval_time < 5, f"Average evaluation too slow: {avg_eval_time}ms"
        assert max_eval_time < 20, f"Max evaluation too slow: {max_eval_time}ms"

        # Verify alerts were triggered
        active_alerts = alert_manager.get_active_alerts()
        assert len(active_alerts) == 4  # All rules should have triggered

    @pytest.mark.asyncio
    async def test_alert_deduplication_performance(self, alert_manager):
        """Test performance of alert deduplication"""
        # Trigger same alert multiple times
        num_duplicates = 100

        start_time = time.time()

        for i in range(num_duplicates):
            await alert_manager.trigger_alert(
                name="DuplicateAlert",
                severity="warning",
                message="This is a duplicate alert",
                labels={"component": "test", "type": "duplicate"},
            )

        # Process alerts
        total_processed = 0
        while True:
            processed = await alert_manager.process_pending_alerts()
            total_processed += processed
            if processed == 0:
                break

        dedup_time = time.time() - start_time

        # Should process quickly due to deduplication
        assert dedup_time < 1.0, f"Deduplication too slow: {dedup_time}s"

        # Should only have one active alert
        active_alerts = alert_manager.get_active_alerts()
        duplicate_alerts = [a for a in active_alerts if a.name == "DuplicateAlert"]
        assert len(duplicate_alerts) == 1

    @pytest.mark.asyncio
    async def test_alert_history_query_performance(self, alert_manager):
        """Test performance of querying alert history"""
        # Generate alert history
        num_historical = 5000

        for i in range(num_historical):
            alert = Alert(
                name=f"HistoricalAlert_{i}",
                severity=AlertSeverity.INFO,
                message=f"Historical alert {i}",
                timestamp=datetime.now() - timedelta(hours=i % 24),
            )
            alert_manager._alert_history.append(alert)

        # Query different time ranges
        query_times = []

        ranges = [
            (timedelta(hours=1), 200),  # Last hour
            (timedelta(hours=6), 1200),  # Last 6 hours
            (timedelta(hours=24), 5000),  # Last 24 hours
        ]

        for time_delta, expected_count in ranges:
            start = time.time()

            alerts = alert_manager.get_alerts_in_range(
                datetime.now() - time_delta, datetime.now()
            )

            query_time = (time.time() - start) * 1000  # ms
            query_times.append(query_time)

            # Verify query is fast
            assert query_time < 50, f"Query too slow for {time_delta}: {query_time}ms"

            # Verify approximate count (allowing for some variance)
            assert len(alerts) > expected_count * 0.8

    @pytest.mark.asyncio
    async def test_concurrent_alert_processing(self, alert_manager):
        """Test concurrent alert triggering and processing"""

        async def trigger_alerts(prefix: str, count: int):
            for i in range(count):
                await alert_manager.trigger_alert(
                    name=f"{prefix}_Alert_{i}",
                    severity="warning",
                    message=f"Concurrent alert from {prefix}",
                    labels={"source": prefix},
                )
                await asyncio.sleep(0.001)

        async def process_alerts():
            total = 0
            while total < 300:  # Expected total alerts
                processed = await alert_manager.process_pending_alerts()
                total += processed
                await asyncio.sleep(0.01)
            return total

        # Run concurrent operations
        start_time = time.time()

        results = await asyncio.gather(
            trigger_alerts("Source1", 100),
            trigger_alerts("Source2", 100),
            trigger_alerts("Source3", 100),
            process_alerts(),
        )

        concurrent_time = time.time() - start_time

        # Verify concurrent execution is efficient
        assert (
            concurrent_time < 5.0
        ), f"Concurrent processing too slow: {concurrent_time}s"
        assert results[3] == 300  # All alerts processed

    @pytest.mark.asyncio
    async def test_alert_notification_latency(self, alert_manager):
        """Test latency of alert notifications"""
        # Mock notification sending
        notification_times = []

        async def mock_send_notification(alert):
            start = time.time()
            # Simulate network call
            await asyncio.sleep(0.01)
            notification_times.append((time.time() - start) * 1000)

        # Replace notification methods with mocks
        alert_manager._send_webhook_notification = mock_send_notification
        alert_manager._send_slack_notification = mock_send_notification

        # Trigger alerts that require notifications
        for i in range(10):
            await alert_manager.trigger_alert(
                name=f"NotificationTest_{i}",
                severity="critical",
                message=f"Test notification {i}",
            )

        # Process and send notifications
        await alert_manager.process_pending_alerts()

        # Verify notification latency
        if notification_times:
            avg_notification_time = sum(notification_times) / len(notification_times)
            max_notification_time = max(notification_times)

            assert (
                avg_notification_time < 20
            ), f"Avg notification too slow: {avg_notification_time}ms"
            assert (
                max_notification_time < 50
            ), f"Max notification too slow: {max_notification_time}ms"

    @pytest.mark.asyncio
    async def test_alert_silence_performance(self, alert_manager):
        """Test performance of alert silencing"""
        # Create many alerts
        num_alerts = 1000

        for i in range(num_alerts):
            alert = Alert(
                name=f"SilenceTest_{i}",
                severity=AlertSeverity.WARNING,
                message=f"Alert to be silenced {i}",
            )
            alert_manager._active_alerts[alert.fingerprint] = alert

        # Silence half of them
        silence_start = time.time()

        for i in range(0, num_alerts, 2):
            alert = Alert(
                name=f"SilenceTest_{i}",
                severity=AlertSeverity.WARNING,
                message=f"Alert to be silenced {i}",
            )
            alert_manager.silence_alert(alert.fingerprint, timedelta(hours=1))

        silence_time = time.time() - silence_start
        avg_silence_time = silence_time / (num_alerts // 2) * 1000  # ms

        assert (
            avg_silence_time < 0.1
        ), f"Silencing too slow: {avg_silence_time}ms per alert"

        # Test checking if alerts are silenced
        check_start = time.time()
        silenced_count = 0

        for fingerprint in list(alert_manager._active_alerts.keys())[:100]:
            if alert_manager._is_silenced(fingerprint):
                silenced_count += 1

        check_time = (time.time() - check_start) * 1000  # ms

        assert (
            check_time < 10
        ), f"Silence checking too slow: {check_time}ms for 100 checks"


@pytest.mark.benchmark
class TestAlertingBenchmarks:
    """Benchmark tests for alerting system"""

    def test_alert_creation_throughput(self, benchmark):
        """Benchmark alert creation throughput"""

        def create_alert():
            return Alert(
                name="BenchmarkAlert",
                severity=AlertSeverity.WARNING,
                message="Benchmark test alert",
                labels={"test": "true", "benchmark": "yes"},
                annotations={"description": "This is a benchmark test"},
            )

        result = benchmark(create_alert)

        # Verify we can create alerts quickly
        alerts_per_second = 1.0 / result
        assert (
            alerts_per_second > 100000
        ), f"Alert creation too slow: {alerts_per_second} alerts/sec"

    def test_alert_matching_performance(self, benchmark, alert_manager):
        """Benchmark alert matching and deduplication"""
        # Pre-populate active alerts
        for i in range(1000):
            alert = Alert(
                name=f"ExistingAlert_{i}",
                severity=AlertSeverity.INFO,
                message=f"Existing alert {i}",
                labels={"index": str(i)},
            )
            alert_manager._active_alerts[alert.fingerprint] = alert

        def match_alert():
            # Create alert that might match existing
            alert = Alert(
                name=f"ExistingAlert_{benchmark._num % 1000}",
                severity=AlertSeverity.INFO,
                message=f"Existing alert {benchmark._num % 1000}",
                labels={"index": str(benchmark._num % 1000)},
            )
            return alert.fingerprint in alert_manager._active_alerts

        result = benchmark(match_alert)

        # Verify matching is fast
        assert result < 0.00001, f"Alert matching too slow: {result}s"
