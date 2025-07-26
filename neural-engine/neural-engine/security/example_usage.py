"""Example usage of the neural data encryption module.

This script demonstrates how to:
1. Encrypt neural signal data
2. Use field-level encryption for sensitive metadata
3. Handle key rotation
4. Monitor encryption performance
"""

import os
import numpy as np
import json
from datetime import datetime

from encryption import NeuralDataEncryption, FieldLevelEncryption


def main():
    """Demonstrate encryption usage."""
    # Get project ID from environment
    project_id = os.environ.get("GCP_PROJECT_ID", "neurascale-ai")

    print("Neural Data Encryption Example")
    print("=" * 50)

    # Initialize encryption service
    print("\n1. Initializing encryption service...")
    encryption = NeuralDataEncryption(
        project_id=project_id,
        location="us-central1",
        key_ring="neural-data-keyring",
        key_name="neural-data-key",
        enable_caching=True,
        cache_ttl_seconds=3600,
    )
    print("   ✓ Encryption service initialized")

    # Example 1: Encrypt neural signal data
    print("\n2. Encrypting neural signal data...")

    # Simulate 32-channel EEG data at 256Hz for 1 second
    neural_data = np.random.randn(32, 256).astype(np.float32)
    print(f"   Original data shape: {neural_data.shape}")
    print(f"   Original data size: {neural_data.nbytes / 1024:.2f} KB")

    # Encrypt the data
    encrypted_data, encrypted_dek = encryption.encrypt_neural_data(neural_data)
    print(f"   ✓ Data encrypted")
    print(f"   Encrypted size: {len(encrypted_data) / 1024:.2f} KB")

    # Decrypt to verify
    decrypted_data = encryption.decrypt_neural_data(encrypted_data, encrypted_dek)
    print(f"   ✓ Data decrypted")
    print(f"   Decryption verified: {np.array_equal(neural_data, decrypted_data)}")

    # Example 2: Field-level encryption for patient data
    print("\n3. Field-level encryption for sensitive metadata...")

    field_encryption = FieldLevelEncryption(encryption)

    # Patient session data with sensitive fields
    session_data = {
        "session_id": "session-2024-001",
        "timestamp": datetime.now().isoformat(),
        "patient": {
            "id": "PAT-12345",
            "name": "John Doe",
            "date_of_birth": "1990-01-15",
            "ssn": "123-45-6789",
            "medical_record_number": "MRN-98765",
        },
        "device": {
            "id": "DEV-001",
            "serial_number": "SN-ABC123",
            "type": "OpenBCI-32",
            "location": {"room": "Lab-101", "lat": 37.7749, "lon": -122.4194},
        },
        "recording": {
            "duration_seconds": 300,
            "sampling_rate": 256,
            "channels": 32,
            "reference": "Cz",
        },
    }

    # Define sensitive fields to encrypt
    sensitive_fields = [
        "patient.id",
        "patient.name",
        "patient.date_of_birth",
        "patient.ssn",
        "patient.medical_record_number",
        "device.serial_number",
        "device.location.lat",
        "device.location.lon",
    ]

    print("   Original patient name:", session_data["patient"]["name"])

    # Encrypt sensitive fields
    encrypted_session = field_encryption.encrypt_fields(session_data, sensitive_fields)
    print("   ✓ Sensitive fields encrypted")
    print(
        "   Encrypted patient name:",
        encrypted_session["patient"]["name"].get("encrypted", "")[:20] + "...",
    )

    # Decrypt fields
    decrypted_session = field_encryption.decrypt_fields(
        encrypted_session, sensitive_fields
    )
    print("   ✓ Fields decrypted")
    print("   Decrypted patient name:", decrypted_session["patient"]["name"])

    # Example 3: Batch encryption for streaming data
    print("\n4. Batch encryption for streaming neural data...")

    # Simulate streaming chunks (100ms chunks at 256Hz)
    chunk_size = 26  # ~100ms at 256Hz
    num_chunks = 10

    # Generate a single DEK for the stream
    stream_dek = encryption.generate_dek()
    print(f"   ✓ Generated stream DEK")

    encrypted_chunks = []
    for i in range(num_chunks):
        # Simulate neural data chunk
        chunk = np.random.randn(32, chunk_size).astype(np.float32)

        # Encrypt with shared DEK
        encrypted_chunk, _ = encryption.encrypt_neural_data(chunk, stream_dek)
        encrypted_chunks.append(encrypted_chunk)

    print(f"   ✓ Encrypted {num_chunks} chunks with shared DEK")

    # Example 4: Key rotation
    print("\n5. Demonstrating key rotation...")

    # Rotate the stream DEK
    try:
        new_stream_dek = encryption.rotate_dek(stream_dek)
        print("   ✓ DEK rotated successfully")
    except Exception as e:
        print(f"   ! Key rotation skipped (requires KMS): {e}")

    # Example 5: Performance metrics
    print("\n6. Encryption performance metrics...")

    metrics = encryption.get_metrics_summary()
    if metrics:
        for operation, stats in metrics.items():
            print(f"\n   {operation}:")
            print(f"     - Total operations: {stats['total_operations']}")
            print(f"     - Success rate: {stats['success_rate']:.1%}")
            print(f"     - Avg duration: {stats['average_duration_ms']:.2f}ms")
            print(f"     - Avg data size: {stats['average_size_bytes']/1024:.2f}KB")

    # Example 6: Best practices summary
    print("\n7. Best Practices:")
    print("   • Use field-level encryption for PII/PHI")
    print("   • Generate session-specific DEKs for neural data")
    print("   • Enable caching for better performance")
    print("   • Monitor encryption metrics for performance")
    print("   • Rotate keys regularly (automated by KMS)")
    print("   • Store encrypted DEKs with the data")

    print("\n" + "=" * 50)
    print("Example completed successfully!")


if __name__ == "__main__":
    main()
