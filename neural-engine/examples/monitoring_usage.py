"""
Example usage of the Neural Engine performance monitoring system
"""

import asyncio
from datetime import datetime, timedelta

from neural_engine.src.monitoring import (
    PerformanceMonitor,
    MonitoringConfig,
    AlertRule,
    AlertSeverity,
)


async def main():  # noqa: C901
    """Demonstrate monitoring system usage"""

    # Configure monitoring
    config = MonitoringConfig(
        neural_metrics_interval_ms=100,  # Collect neural metrics every 100ms
        device_metrics_interval_ms=1000,  # Collect device metrics every 1s
        system_metrics_interval_ms=5000,  # Collect system metrics every 5s
        health_check_interval_ms=30000,  # Health check every 30s
        prometheus_port=9090,
        grafana_url="http://localhost:3000",
        slack_webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
        max_processing_latency_ms=100.0,
        min_data_quality_score=0.7,
        max_device_error_rate=0.01,
    )

    # Create performance monitor
    monitor = PerformanceMonitor(config)

    # Register custom alert rules
    monitor.alert_manager.register_alert_rule(
        AlertRule(
            name="HighSignalProcessingLatency",
            expression="signal_processing_latency > 100",
            duration=timedelta(minutes=2),
            severity=AlertSeverity.CRITICAL,
            labels={"component": "signal-processing"},
            annotations={
                "summary": "Neural signal processing latency is critically high",
                "description": "Processing latency has exceeded 100ms for 2 minutes",
            },
        )
    )

    monitor.alert_manager.register_alert_rule(
        AlertRule(
            name="LowDataQuality",
            expression="data_quality_score < 0.7",
            duration=timedelta(minutes=5),
            severity=AlertSeverity.WARNING,
            labels={"component": "data-quality"},
            annotations={
                "summary": "Neural data quality below threshold",
                "description": "Data quality has been below 0.7 for 5 minutes",
            },
        )
    )

    # Start monitoring
    print("Starting performance monitoring...")
    await monitor.start_monitoring()

    # Simulate neural processing session
    session_id = "example_session_001"
    device_id = "openbb_device_001"

    # Register device
    monitor.device_metrics.register_device(device_id)

    # Simulate processing loop
    for i in range(100):
        # Start signal processing
        monitor.neural_metrics.start_signal_processing()
        await asyncio.sleep(0.02)  # Simulate 20ms processing
        signal_latency = monitor.neural_metrics.end_signal_processing()

        # Feature extraction
        monitor.neural_metrics.start_feature_extraction()
        await asyncio.sleep(0.03)  # Simulate 30ms extraction
        feature_time = monitor.neural_metrics.end_feature_extraction()

        # Model inference
        monitor.neural_metrics.start_model_inference()
        await asyncio.sleep(0.05)  # Simulate 50ms inference
        inference_latency = monitor.neural_metrics.end_model_inference()

        # Record other metrics
        monitor.neural_metrics.record_data_quality_score(
            session_id, 0.85 + (i % 10) * 0.01
        )
        monitor.neural_metrics.record_processing_accuracy(0.92 + (i % 5) * 0.01)
        monitor.neural_metrics.record_processing_throughput(250 + i)

        # Record device metrics
        monitor.device_metrics.record_signal_quality(device_id, 0.9 + (i % 20) * 0.005)
        monitor.device_metrics.track_data_rate(device_id, 250)
        monitor.device_metrics.record_device_latency(device_id, 10 + (i % 10))
        monitor.device_metrics.record_packet_stats(device_id, 1000, i % 10)

        # Collect and record current metrics
        neural_metrics = await monitor.collect_neural_metrics(session_id)
        device_metrics = await monitor.monitor_device_performance(device_id)

        # Print some metrics
        if i % 10 == 0:
            print(f"\nIteration {i}:")
            print(f"  Signal latency: {signal_latency:.2f}ms")
            print(f"  Feature extraction: {feature_time:.2f}ms")
            print(f"  Inference latency: {inference_latency:.2f}ms")
            print(f"  Data quality: {neural_metrics.data_quality_score:.3f}")
            print(f"  Device stability: {device_metrics.connection_stability:.3f}")

        await asyncio.sleep(0.1)  # 100ms between iterations

    # Get monitoring status
    status = monitor.get_monitoring_status()
    print("\nMonitoring Status:")
    print(f"  Running: {status.is_running}")
    print(f"  Metrics collected: {status.metrics_collected}")
    print(f"  Alerts triggered: {status.alerts_triggered}")
    print(f"  Active devices: {status.active_devices}")
    print(f"  System health: {status.system_health}")

    # Generate performance report
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=5)

    report = monitor.generate_performance_report(start_time, end_time)

    print(f"\nPerformance Report ({start_time} to {end_time}):")
    print("  Neural Metrics:")
    for metric, value in report.neural_metrics.items():
        print(f"    {metric}: {value:.3f}")

    print("  Device Metrics:")
    for device, metrics in report.device_metrics.items():
        print(f"    {device}:")
        for metric, value in metrics.items():
            print(f"      {metric}: {value:.3f}")

    print("  System Metrics:")
    for metric, value in report.system_metrics.items():
        print(f"    {metric}: {value:.3f}")

    print(f"  Alerts: {len(report.alerts)}")
    for alert in report.alerts[:5]:  # Show first 5 alerts
        print(f"    - {alert['name']} ({alert['severity']}): {alert['message']}")

    print("  Recommendations:")
    for rec in report.recommendations:
        print(f"    - {rec}")

    # Health check
    health_report = await monitor.health_checker.generate_health_report()
    print("\nHealth Report:")
    print(f"  Overall status: {health_report.overall_status.value}")
    print("  Services:")
    for service, health in health_report.services.items():
        print(
            f"    {service}: {health['status']} (latency: {health['latency_ms']:.1f}ms)"
        )

    # Get active alerts
    active_alerts = monitor.alert_manager.get_active_alerts()
    print(f"\nActive Alerts: {len(active_alerts)}")
    for alert in active_alerts:
        print(f"  - {alert.name} ({alert.severity.value}): {alert.message}")

    # Cleanup
    await asyncio.sleep(2)  # Let background tasks finish
    print("\nStopping monitoring...")
    await monitor.stop_monitoring()
    print("Monitoring stopped.")


if __name__ == "__main__":
    asyncio.run(main())
