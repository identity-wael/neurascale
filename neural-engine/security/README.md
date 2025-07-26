# NeuraScale Security Module

This module provides comprehensive encryption and security features for protecting sensitive neural data in compliance with HIPAA and healthcare regulations.

## Features

### 1. **Neural Data Encryption**

- Envelope encryption using Google Cloud KMS
- High-performance encryption optimized for real-time neural data
- Automatic key rotation with KMS
- DEK caching for improved performance

### 2. **Field-Level Encryption**

- Granular encryption for sensitive fields (PII/PHI)
- Support for nested field paths
- Separate DEKs per field for enhanced security

### 3. **Performance Optimization**

- DEK caching with configurable TTL
- Batch encryption support for streaming data
- Minimal latency for real-time processing
- Performance metrics and monitoring

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
│  (Neural Processing, API Services, Data Pipeline)           │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    Encryption Layer                          │
│  ┌─────────────────────────┐  ┌──────────────────────────┐ │
│  │  NeuralDataEncryption   │  │  FieldLevelEncryption    │ │
│  │  - Envelope encryption  │  │  - PII/PHI encryption    │ │
│  │  - DEK management       │  │  - Granular control      │ │
│  │  - Performance metrics  │  │  - Field-specific DEKs   │ │
│  └───────────┬─────────────┘  └────────────┬─────────────┘ │
└──────────────┼──────────────────────────────┼───────────────┘
               │                              │
┌──────────────▼──────────────────────────────▼───────────────┐
│                    Google Cloud KMS                          │
│  - Master key management                                     │
│  - Automatic key rotation                                    │
│  - Hardware security module (HSM)                           │
└──────────────────────────────────────────────────────────────┘
```

## Usage

### Basic Neural Data Encryption

```python
from neural_engine.security import NeuralDataEncryption
import numpy as np

# Initialize encryption service
encryption = NeuralDataEncryption(
    project_id="your-project-id",
    location="us-central1",
    key_ring="neural-data-keyring",
    key_name="neural-data-key"
)

# Encrypt neural data
neural_data = np.random.randn(32, 1000).astype(np.float32)  # 32 channels, 1000 samples
encrypted_data, encrypted_dek = encryption.encrypt_neural_data(neural_data)

# Decrypt neural data
decrypted_data = encryption.decrypt_neural_data(encrypted_data, encrypted_dek)
```

### Field-Level Encryption for Sensitive Data

```python
from neural_engine.security import FieldLevelEncryption

# Initialize field encryption
field_encryption = FieldLevelEncryption(encryption)

# Patient data with sensitive fields
patient_data = {
    "session_id": "session-123",
    "patient": {
        "id": "PAT-001",
        "name": "John Doe",
        "ssn": "123-45-6789"
    }
}

# Encrypt specific fields
encrypted_data = field_encryption.encrypt_fields(
    patient_data,
    fields_to_encrypt=["patient.id", "patient.name", "patient.ssn"]
)

# Decrypt fields when needed
decrypted_data = field_encryption.decrypt_fields(
    encrypted_data,
    fields_to_decrypt=["patient.id", "patient.name", "patient.ssn"]
)
```

### Streaming Data Encryption

```python
# Generate session DEK for streaming
session_dek = encryption.generate_dek()

# Encrypt streaming chunks with shared DEK
for chunk in neural_data_stream:
    encrypted_chunk, _ = encryption.encrypt_neural_data(chunk, session_dek)
    # Send encrypted_chunk to storage/processing
```

## Security Best Practices

1. **Key Management**

   - Never store plaintext DEKs
   - Use separate DEKs for different data types
   - Enable automatic key rotation in KMS
   - Store encrypted DEKs alongside encrypted data

2. **Performance Optimization**

   - Enable DEK caching for frequently accessed data
   - Use batch encryption for streaming data
   - Monitor encryption metrics for bottlenecks
   - Consider field-level encryption only for truly sensitive fields

3. **Compliance**
   - Encrypt all PII/PHI at rest and in transit
   - Implement audit logging for data access
   - Use field-level encryption for granular control
   - Follow HIPAA guidelines for key management

## Performance Benchmarks

Run the benchmark suite to test encryption performance:

```bash
python benchmark_encryption.py
```

Expected performance metrics:

- Neural array encryption: <10ms for typical EEG data (32 channels, 1 second)
- Field-level encryption: <5ms for typical metadata
- Batch encryption: ~1ms per chunk for streaming data

## Testing

Run the comprehensive test suite:

```bash
pytest test_encryption.py -v
```

## Configuration

### Environment Variables

- `GCP_PROJECT_ID`: Your Google Cloud project ID
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account key file

### KMS Setup

1. Create a key ring:

   ```bash
   gcloud kms keyrings create neural-data-keyring \
       --location=us-central1
   ```

2. Create a crypto key with automatic rotation:
   ```bash
   gcloud kms keys create neural-data-key \
       --location=us-central1 \
       --keyring=neural-data-keyring \
       --purpose=encryption \
       --rotation-period=90d \
       --next-rotation-time=2024-04-01T00:00:00.000Z
   ```

## Monitoring

The module provides built-in performance metrics:

```python
# Get encryption performance summary
metrics = encryption.get_metrics_summary()
print(json.dumps(metrics, indent=2))
```

Metrics include:

- Operation count and success rate
- Average duration per operation
- Data throughput statistics
- Error tracking

## Error Handling

The module defines specific exception types:

- `EncryptionError`: Base exception for encryption failures
- `KeyRotationError`: Specific to key rotation operations

Always wrap encryption operations in try-except blocks:

```python
try:
    encrypted_data, dek = encryption.encrypt_neural_data(data)
except EncryptionError as e:
    logger.error(f"Encryption failed: {e}")
    # Handle error appropriately
```

## Future Enhancements

- [ ] Support for additional encryption algorithms
- [ ] Integration with Cloud HSM for enhanced security
- [ ] Distributed DEK caching with Redis
- [ ] Quantum-resistant encryption algorithms
- [ ] Homomorphic encryption for processing encrypted data
