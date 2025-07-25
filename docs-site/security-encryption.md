---
layout: doc
title: Security & Encryption
permalink: /security-encryption/
---

# Security & Encryption Infrastructure

The NeuraScale Security Infrastructure provides HIPAA-compliant encryption and data protection for neural data, ensuring patient privacy and regulatory compliance.

## Overview

Our security infrastructure implements defense-in-depth with multiple layers of protection:

- **Envelope Encryption**: Using Google Cloud KMS for key management
- **Field-Level Encryption**: Granular protection for PII/PHI data
- **Performance Optimization**: <10ms latency for real-time processing
- **Compliance**: HIPAA, GDPR, and healthcare regulations

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  (Neural Processing, API Services, Data Pipeline)           │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 Encryption Layer                             │
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
│  - Automatic key rotation (90-day cycle)                    │
│  - Hardware security module (HSM)                           │
│  - Audit logging                                           │
└──────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Neural Data Encryption

The main encryption service using envelope encryption:

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

# Encrypt neural data array
neural_data = np.random.randn(32, 1000).astype(np.float32)
encrypted_data, encrypted_dek = encryption.encrypt_neural_data(neural_data)

# Decrypt when needed
decrypted_data = encryption.decrypt_neural_data(encrypted_data, encrypted_dek)
```

### 2. Field-Level Encryption

Granular encryption for sensitive fields:

```python
from neural_engine.security import FieldLevelEncryption

# Initialize field encryption
field_encryption = FieldLevelEncryption(encryption)

# Patient data with sensitive fields
session_data = {
    "session_id": "session-2024-001",
    "patient": {
        "id": "PAT-12345",
        "name": "John Doe",
        "ssn": "123-45-6789",
        "medical_record_number": "MRN-98765"
    },
    "device": {
        "serial_number": "SN-ABC123",
        "location": {"lat": 37.7749, "lon": -122.4194}
    }
}

# Encrypt specific fields
encrypted_data = field_encryption.encrypt_fields(
    session_data,
    fields_to_encrypt=[
        "patient.id",
        "patient.name",
        "patient.ssn",
        "patient.medical_record_number",
        "device.serial_number",
        "device.location"
    ]
)
```

## Security Features

### Envelope Encryption

- **KEK (Key Encryption Key)**: Stored in Google Cloud KMS
- **DEK (Data Encryption Key)**: Generated per session/dataset
- **Automatic Rotation**: KEKs rotated every 90 days
- **Hardware Security**: Keys protected by FIPS 140-2 Level 3 HSMs

### Performance Optimization

- **DEK Caching**: Configurable TTL for frequently used keys
- **Batch Processing**: Reuse DEKs for streaming data
- **Lazy Decryption**: Decrypt only when data is accessed
- **Concurrent Operations**: Thread-safe encryption/decryption

### Compliance Features

- **HIPAA Compliance**:

  - Encryption at rest and in transit
  - Access controls and audit logging
  - Key management procedures
  - Data retention policies

- **GDPR Compliance**:
  - Right to erasure (crypto-shredding)
  - Data minimization
  - Purpose limitation
  - Privacy by design

## Usage Patterns

### Real-Time Neural Streaming

```python
# Generate session DEK for streaming
session_dek = encryption.generate_dek()

# Process streaming chunks
for chunk in neural_data_stream:
    # Encrypt each chunk with same DEK
    encrypted_chunk, _ = encryption.encrypt_neural_data(chunk, session_dek)

    # Send to storage/processing
    send_to_pipeline(encrypted_chunk)

# Store DEK with session metadata
session_metadata["encrypted_dek"] = base64.b64encode(session_dek)
```

### Batch Processing

```python
# Process multiple datasets efficiently
datasets = load_datasets()
encrypted_dek = encryption.generate_dek()

encrypted_datasets = []
for dataset in datasets:
    encrypted_data, _ = encryption.encrypt_neural_data(
        dataset.data,
        encrypted_dek
    )
    encrypted_datasets.append(encrypted_data)
```

### Secure Data Deletion

```python
# Crypto-shredding for GDPR compliance
def secure_delete_patient_data(patient_id: str):
    # Delete DEKs associated with patient
    encryption.revoke_patient_keys(patient_id)

    # Data becomes unrecoverable even if files remain
    # No need to overwrite actual data files
```

## Performance Benchmarks

Our encryption infrastructure is optimized for real-time neural processing:

| Operation               | Data Size         | Latency    | Throughput |
| ----------------------- | ----------------- | ---------- | ---------- |
| Neural Array Encryption | 32ch × 1s @ 256Hz | <10ms      | >200 Mbps  |
| Field-Level Encryption  | Typical metadata  | <5ms       | N/A        |
| Batch Encryption        | 100 chunks        | ~1ms/chunk | >500 Mbps  |
| DEK Generation          | N/A               | <50ms      | N/A        |
| DEK Decryption (cached) | N/A               | <1ms       | N/A        |

## Best Practices

### 1. Key Management

- **Never store plaintext DEKs** in databases or files
- **Use separate DEKs** for different data types or sessions
- **Enable automatic rotation** in Cloud KMS
- **Store encrypted DEKs** alongside encrypted data

### 2. Performance

- **Enable DEK caching** for frequently accessed data
- **Reuse DEKs** for related data (e.g., streaming session)
- **Monitor metrics** to identify bottlenecks
- **Use field-level encryption** only for truly sensitive fields

### 3. Compliance

- **Encrypt all PII/PHI** at rest and in transit
- **Implement audit logging** for all data access
- **Use field-level encryption** for granular control
- **Follow key rotation** schedules

### 4. Development

```python
# Always handle encryption errors
try:
    encrypted_data, dek = encryption.encrypt_neural_data(data)
except EncryptionError as e:
    logger.error(f"Encryption failed: {e}")
    # Implement appropriate fallback
```

## Cloud KMS Setup

### 1. Create Key Ring

```bash
gcloud kms keyrings create neural-data-keyring \
    --location=us-central1
```

### 2. Create Crypto Key

```bash
gcloud kms keys create neural-data-key \
    --location=us-central1 \
    --keyring=neural-data-keyring \
    --purpose=encryption \
    --rotation-period=90d \
    --next-rotation-time=2024-04-01T00:00:00.000Z
```

### 3. Grant Permissions

```bash
gcloud kms keys add-iam-policy-binding neural-data-key \
    --location=us-central1 \
    --keyring=neural-data-keyring \
    --member="serviceAccount:neural-engine@project.iam.gserviceaccount.com" \
    --role="roles/cloudkms.cryptoKeyEncrypterDecrypter"
```

## Monitoring & Alerts

### Performance Metrics

```python
# Get encryption performance metrics
metrics = encryption.get_metrics_summary()
for operation, stats in metrics.items():
    print(f"{operation}:")
    print(f"  Success rate: {stats['success_rate']:.1%}")
    print(f"  Avg duration: {stats['average_duration_ms']:.2f}ms")
```

### Recommended Alerts

- DEK generation failures > 1%
- Encryption latency > 50ms (p95)
- Key rotation failures
- Unauthorized access attempts

## Integration Examples

### With Dataset Management

```python
from neural_engine.datasets import DatasetManager
from neural_engine.security import NeuralDataEncryption

# Automatic encryption when saving datasets
manager = DatasetManager(encryption_service=encryption)
dataset = manager.load_dataset("eeg_recording")

# Data automatically encrypted on save
manager.save_dataset(dataset, encrypt=True)
```

### With API Services

```python
from fastapi import FastAPI, Depends
from neural_engine.security import get_encryption_service

app = FastAPI()

@app.post("/api/v1/neural-data")
async def ingest_data(
    data: NeuralData,
    encryption: NeuralDataEncryption = Depends(get_encryption_service)
):
    # Automatically encrypt before storage
    encrypted_data, dek = encryption.encrypt_neural_data(data.signals)
    # Store encrypted data and DEK
```

## Troubleshooting

### Common Issues

1. **"Failed to generate DEK"**

   - Check KMS permissions
   - Verify key ring and key exist
   - Check service account credentials

2. **"Decryption failed"**

   - Ensure correct DEK is used
   - Verify data integrity
   - Check for key rotation issues

3. **Performance degradation**
   - Monitor DEK cache hit rate
   - Check for excessive key generation
   - Verify batch processing is used

## Future Enhancements

- [ ] Hardware Security Module (HSM) integration
- [ ] Homomorphic encryption for processing encrypted data
- [ ] Distributed key management
- [ ] Quantum-resistant algorithms
- [ ] Zero-knowledge proofs for data verification

---

_Last updated: July 26, 2025_
