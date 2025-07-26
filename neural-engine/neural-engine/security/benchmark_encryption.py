"""Performance benchmarks for neural data encryption.

This module tests encryption performance with various data sizes
and configurations to ensure real-time processing capability.
"""

import time
import numpy as np
import pandas as pd
from typing import List, Dict, Any
import matplotlib.pyplot as plt
from dataclasses import dataclass
import os

from encryption import NeuralDataEncryption, FieldLevelEncryption


@dataclass
class BenchmarkResult:
    """Result of a single benchmark test."""
    operation: str
    data_size_mb: float
    duration_ms: float
    throughput_mbps: float
    test_type: str


class EncryptionBenchmark:
    """Benchmark suite for neural data encryption."""

    def __init__(self, project_id: str):
        """Initialize benchmark suite.

        Args:
            project_id: GCP project ID
        """
        self.project_id = project_id
        self.encryption = NeuralDataEncryption(
            project_id=project_id,
            enable_caching=True
        )
        self.field_encryption = FieldLevelEncryption(self.encryption)
        self.results: List[BenchmarkResult] = []

    def benchmark_neural_array_encryption(self):
        """Benchmark encryption of neural signal arrays."""
        print("Benchmarking neural array encryption...")

        # Test different array sizes (simulating different sampling rates/channels)
        test_configs = [
            (1, 256, 1000),    # 1 channel, 256Hz, 1 second
            (8, 256, 1000),    # 8 channels, 256Hz, 1 second
            (32, 512, 1000),   # 32 channels, 512Hz, 1 second
            (64, 1024, 1000),  # 64 channels, 1024Hz, 1 second
            (128, 2048, 1000), # 128 channels, 2048Hz, 1 second
        ]

        for channels, sample_rate, duration_ms in test_configs:
            # Generate synthetic neural data
            samples = int(sample_rate * duration_ms / 1000)
            data = np.random.randn(channels, samples).astype(np.float32)
            data_size_mb = data.nbytes / (1024 * 1024)

            # Benchmark encryption
            start_time = time.time()
            encrypted_data, encrypted_dek = self.encryption.encrypt_neural_data(data)
            encrypt_duration = (time.time() - start_time) * 1000

            # Benchmark decryption
            start_time = time.time()
            decrypted_data = self.encryption.decrypt_neural_data(
                encrypted_data, encrypted_dek
            )
            decrypt_duration = (time.time() - start_time) * 1000

            # Record results
            self.results.append(BenchmarkResult(
                operation="encrypt",
                data_size_mb=data_size_mb,
                duration_ms=encrypt_duration,
                throughput_mbps=(data_size_mb * 8) / (encrypt_duration / 1000),
                test_type=f"neural_array_{channels}ch_{sample_rate}Hz"
            ))

            self.results.append(BenchmarkResult(
                operation="decrypt",
                data_size_mb=data_size_mb,
                duration_ms=decrypt_duration,
                throughput_mbps=(data_size_mb * 8) / (decrypt_duration / 1000),
                test_type=f"neural_array_{channels}ch_{sample_rate}Hz"
            ))

            print(f"  {channels}ch @ {sample_rate}Hz: "
                  f"Encrypt {encrypt_duration:.2f}ms, "
                  f"Decrypt {decrypt_duration:.2f}ms")

    def benchmark_field_level_encryption(self):
        """Benchmark field-level encryption for metadata."""
        print("\nBenchmarking field-level encryption...")

        # Test data with sensitive fields
        test_data = {
            "session_id": "test-session-123",
            "patient": {
                "id": "patient-456",
                "name": "John Doe",
                "date_of_birth": "1990-01-01",
                "ssn": "123-45-6789"
            },
            "device": {
                "id": "device-789",
                "serial": "SN123456",
                "location": {
                    "lat": 37.7749,
                    "lon": -122.4194
                }
            },
            "metadata": {
                "timestamp": "2024-01-01T12:00:00Z",
                "notes": "Test session for benchmarking"
            }
        }

        fields_to_encrypt = [
            "patient.id",
            "patient.name",
            "patient.date_of_birth",
            "patient.ssn",
            "device.serial",
            "device.location"
        ]

        # Benchmark encryption
        start_time = time.time()
        encrypted_data = self.field_encryption.encrypt_fields(
            test_data, fields_to_encrypt
        )
        encrypt_duration = (time.time() - start_time) * 1000

        # Benchmark decryption
        start_time = time.time()
        decrypted_data = self.field_encryption.decrypt_fields(
            encrypted_data, fields_to_encrypt
        )
        decrypt_duration = (time.time() - start_time) * 1000

        # Record results
        data_size_mb = len(str(test_data).encode()) / (1024 * 1024)

        self.results.append(BenchmarkResult(
            operation="field_encrypt",
            data_size_mb=data_size_mb,
            duration_ms=encrypt_duration,
            throughput_mbps=(data_size_mb * 8) / (encrypt_duration / 1000),
            test_type="metadata_fields"
        ))

        self.results.append(BenchmarkResult(
            operation="field_decrypt",
            data_size_mb=data_size_mb,
            duration_ms=decrypt_duration,
            throughput_mbps=(data_size_mb * 8) / (decrypt_duration / 1000),
            test_type="metadata_fields"
        ))

        print(f"  Field encryption: {encrypt_duration:.2f}ms")
        print(f"  Field decryption: {decrypt_duration:.2f}ms")

    def benchmark_batch_operations(self):
        """Benchmark batch encryption operations."""
        print("\nBenchmarking batch operations...")

        # Simulate batch of neural data chunks
        batch_sizes = [10, 50, 100, 500]
        chunk_size = (32, 256)  # 32 channels, 256 samples

        for batch_size in batch_sizes:
            # Generate batch data
            batch_data = [
                np.random.randn(*chunk_size).astype(np.float32)
                for _ in range(batch_size)
            ]
            total_size_mb = sum(d.nbytes for d in batch_data) / (1024 * 1024)

            # Benchmark batch encryption
            start_time = time.time()
            encrypted_batch = []
            encrypted_dek = self.encryption.generate_dek()  # Reuse DEK for batch

            for data in batch_data:
                encrypted, _ = self.encryption.encrypt_neural_data(
                    data, encrypted_dek
                )
                encrypted_batch.append(encrypted)

            encrypt_duration = (time.time() - start_time) * 1000

            # Record results
            self.results.append(BenchmarkResult(
                operation="batch_encrypt",
                data_size_mb=total_size_mb,
                duration_ms=encrypt_duration,
                throughput_mbps=(total_size_mb * 8) / (encrypt_duration / 1000),
                test_type=f"batch_{batch_size}_chunks"
            ))

            print(f"  Batch size {batch_size}: {encrypt_duration:.2f}ms "
                  f"({encrypt_duration/batch_size:.2f}ms per chunk)")

    def benchmark_key_operations(self):
        """Benchmark key generation and rotation."""
        print("\nBenchmarking key operations...")

        # Benchmark DEK generation
        iterations = 100
        start_time = time.time()

        for _ in range(iterations):
            encrypted_dek = self.encryption.generate_dek()

        gen_duration = (time.time() - start_time) * 1000 / iterations

        # Benchmark DEK decryption (with caching)
        start_time = time.time()

        for _ in range(iterations):
            self.encryption.decrypt_dek(encrypted_dek)

        decrypt_duration = (time.time() - start_time) * 1000 / iterations

        # Benchmark key rotation
        start_time = time.time()
        new_encrypted_dek = self.encryption.rotate_dek(encrypted_dek)
        rotate_duration = (time.time() - start_time) * 1000

        print(f"  DEK generation: {gen_duration:.2f}ms avg")
        print(f"  DEK decryption (cached): {decrypt_duration:.2f}ms avg")
        print(f"  Key rotation: {rotate_duration:.2f}ms")

    def generate_report(self):
        """Generate performance report with visualizations."""
        print("\nGenerating performance report...")

        # Convert results to DataFrame
        df = pd.DataFrame([
            {
                'operation': r.operation,
                'data_size_mb': r.data_size_mb,
                'duration_ms': r.duration_ms,
                'throughput_mbps': r.throughput_mbps,
                'test_type': r.test_type
            }
            for r in self.results
        ])

        # Create visualizations
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        # 1. Throughput by operation type
        ax = axes[0, 0]
        df.groupby('operation')['throughput_mbps'].mean().plot(
            kind='bar', ax=ax
        )
        ax.set_title('Average Throughput by Operation')
        ax.set_ylabel('Throughput (Mbps)')

        # 2. Duration vs Data Size
        ax = axes[0, 1]
        for op in df['operation'].unique():
            op_data = df[df['operation'] == op]
            ax.scatter(op_data['data_size_mb'], op_data['duration_ms'],
                      label=op, alpha=0.7)
        ax.set_xlabel('Data Size (MB)')
        ax.set_ylabel('Duration (ms)')
        ax.set_title('Operation Duration vs Data Size')
        ax.legend()

        # 3. Performance by test type
        ax = axes[1, 0]
        test_perf = df.groupby('test_type')['duration_ms'].mean().sort_values()
        test_perf.plot(kind='barh', ax=ax)
        ax.set_xlabel('Average Duration (ms)')
        ax.set_title('Performance by Test Type')

        # 4. Metrics summary
        ax = axes[1, 1]
        ax.axis('off')
        metrics = self.encryption.get_metrics_summary()
        summary_text = "Encryption Metrics Summary\n\n"

        for op, stats in metrics.items():
            summary_text += f"{op}:\n"
            summary_text += f"  Success rate: {stats['success_rate']:.1%}\n"
            summary_text += f"  Avg duration: {stats['average_duration_ms']:.2f}ms\n"
            summary_text += f"  Total ops: {stats['total_operations']}\n\n"

        ax.text(0.1, 0.9, summary_text, transform=ax.transAxes,
                verticalalignment='top', fontfamily='monospace')

        plt.tight_layout()
        plt.savefig('encryption_benchmark_report.png', dpi=150)
        print("  Report saved to encryption_benchmark_report.png")

        # Print summary statistics
        print("\nSummary Statistics:")
        print(f"  Total tests run: {len(self.results)}")
        print(f"  Average throughput: {df['throughput_mbps'].mean():.2f} Mbps")
        print(f"  Average latency: {df['duration_ms'].mean():.2f} ms")

        # Check real-time requirements
        real_time_threshold_ms = 10  # 10ms for real-time processing
        fast_ops = df[df['duration_ms'] < real_time_threshold_ms]
        print(f"\n  Operations under {real_time_threshold_ms}ms: "
              f"{len(fast_ops)}/{len(df)} ({len(fast_ops)/len(df)*100:.1f}%)")

    def run_all_benchmarks(self):
        """Run all benchmark tests."""
        print("Starting Neural Data Encryption Benchmarks")
        print("=" * 50)

        self.benchmark_neural_array_encryption()
        self.benchmark_field_level_encryption()
        self.benchmark_batch_operations()
        self.benchmark_key_operations()
        self.generate_report()

        print("\nBenchmarks completed!")


if __name__ == "__main__":
    # Get project ID from environment or use default
    project_id = os.environ.get("GCP_PROJECT_ID", "neurascale-ai")

    # Run benchmarks
    benchmark = EncryptionBenchmark(project_id)
    benchmark.run_all_benchmarks()
