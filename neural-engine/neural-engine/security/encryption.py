"""Neural data encryption module using Google Cloud KMS.

This module provides encryption services for neural data, including:
- Field-level encryption for sensitive data
- Key management with Google Cloud KMS
- Key rotation mechanisms
- Performance-optimized encryption for real-time data
"""

import os
import json
import base64
import hashlib
import time
from typing import Dict, Any, Optional, Union, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from functools import lru_cache
import logging

import numpy as np
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from google.cloud import kms
from google.cloud import secretmanager
from google.api_core import retry
import msgpack

# Configure logging
logger = logging.getLogger(__name__)


class EncryptionError(Exception):
    """Base exception for encryption-related errors."""
    pass


class KeyRotationError(EncryptionError):
    """Exception raised during key rotation operations."""
    pass


@dataclass
class EncryptionMetrics:
    """Performance metrics for encryption operations."""
    operation: str
    duration_ms: float
    data_size_bytes: int
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None


class NeuralDataEncryption:
    """Main encryption service for neural data using Google Cloud KMS.

    This class provides:
    - Envelope encryption using Cloud KMS
    - Local data encryption with DEKs (Data Encryption Keys)
    - Automatic key rotation
    - Performance optimization for real-time neural data
    """

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        key_ring: str = "neural-data-keyring",
        key_name: str = "neural-data-key",
        enable_caching: bool = True,
        cache_ttl_seconds: int = 3600
    ):
        """Initialize the encryption service.

        Args:
            project_id: GCP project ID
            location: GCP location for KMS
            key_ring: Name of the KMS key ring
            key_name: Name of the KMS crypto key
            enable_caching: Whether to cache DEKs for performance
            cache_ttl_seconds: TTL for cached DEKs
        """
        self.project_id = project_id
        self.location = location
        self.key_ring = key_ring
        self.key_name = key_name
        self.enable_caching = enable_caching
        self.cache_ttl_seconds = cache_ttl_seconds

        # Initialize KMS client
        self.kms_client = kms.KeyManagementServiceClient()
        self.key_path = self.kms_client.crypto_key_path(
            project_id, location, key_ring, key_name
        )

        # Initialize Secret Manager client for DEK storage
        self.secret_client = secretmanager.SecretManagerServiceClient()

        # DEK cache for performance
        self._dek_cache: Dict[str, Tuple[bytes, datetime]] = {}

        # Performance metrics
        self._metrics: List[EncryptionMetrics] = []

        # Initialize or verify KMS resources
        self._ensure_kms_resources()

    def _ensure_kms_resources(self):
        """Ensure KMS key ring and crypto key exist."""
        try:
            # Check if key ring exists
            key_ring_path = self.kms_client.key_ring_path(
                self.project_id, self.location, self.key_ring
            )
            try:
                self.kms_client.get_key_ring(name=key_ring_path)
            except Exception:
                # Create key ring if it doesn't exist
                parent = f"projects/{self.project_id}/locations/{self.location}"
                self.kms_client.create_key_ring(
                    request={
                        "parent": parent,
                        "key_ring_id": self.key_ring,
                        "key_ring": {}
                    }
                )
                logger.info(f"Created KMS key ring: {self.key_ring}")

            # Check if crypto key exists
            try:
                self.kms_client.get_crypto_key(name=self.key_path)
            except Exception:
                # Create crypto key if it doesn't exist
                self.kms_client.create_crypto_key(
                    request={
                        "parent": key_ring_path,
                        "crypto_key_id": self.key_name,
                        "crypto_key": {
                            "purpose": kms.CryptoKey.CryptoKeyPurpose.ENCRYPT_DECRYPT,
                            "version_template": {
                                "algorithm": kms.CryptoKeyVersion.CryptoKeyVersionAlgorithm.GOOGLE_SYMMETRIC_ENCRYPTION
                            },
                            "rotation_period": {"seconds": 7776000},  # 90 days
                        }
                    }
                )
                logger.info(f"Created KMS crypto key: {self.key_name}")

        except Exception as e:
            logger.error(f"Error ensuring KMS resources: {e}")
            raise EncryptionError(f"Failed to initialize KMS resources: {e}")

    @retry.Retry(predicate=retry.if_exception_type(Exception))
    def generate_dek(self, context: Optional[str] = None) -> bytes:
        """Generate a new Data Encryption Key (DEK) encrypted by KMS.

        Args:
            context: Optional context string for key derivation

        Returns:
            Encrypted DEK bytes
        """
        start_time = time.time()

        try:
            # Generate a new DEK
            dek = Fernet.generate_key()

            # Encrypt the DEK with KMS
            encrypt_response = self.kms_client.encrypt(
                request={
                    "name": self.key_path,
                    "plaintext": dek,
                }
            )

            encrypted_dek = encrypt_response.ciphertext

            # Record metrics
            duration_ms = (time.time() - start_time) * 1000
            self._record_metric(
                "generate_dek",
                duration_ms,
                len(encrypted_dek),
                success=True
            )

            return encrypted_dek

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._record_metric(
                "generate_dek",
                duration_ms,
                0,
                success=False,
                error_message=str(e)
            )
            raise EncryptionError(f"Failed to generate DEK: {e}")

    @retry.Retry(predicate=retry.if_exception_type(Exception))
    def decrypt_dek(self, encrypted_dek: bytes) -> bytes:
        """Decrypt a DEK using KMS.

        Args:
            encrypted_dek: The encrypted DEK bytes

        Returns:
            Decrypted DEK bytes
        """
        start_time = time.time()

        try:
            # Check cache first
            if self.enable_caching:
                cache_key = hashlib.sha256(encrypted_dek).hexdigest()
                if cache_key in self._dek_cache:
                    dek, cached_time = self._dek_cache[cache_key]
                    if (datetime.now() - cached_time).seconds < self.cache_ttl_seconds:
                        return dek

            # Decrypt with KMS
            decrypt_response = self.kms_client.decrypt(
                request={
                    "name": self.key_path,
                    "ciphertext": encrypted_dek,
                }
            )

            dek = decrypt_response.plaintext

            # Cache the DEK
            if self.enable_caching:
                cache_key = hashlib.sha256(encrypted_dek).hexdigest()
                self._dek_cache[cache_key] = (dek, datetime.now())
                # Clean old cache entries
                self._clean_dek_cache()

            # Record metrics
            duration_ms = (time.time() - start_time) * 1000
            self._record_metric(
                "decrypt_dek",
                duration_ms,
                len(dek),
                success=True
            )

            return dek

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._record_metric(
                "decrypt_dek",
                duration_ms,
                0,
                success=False,
                error_message=str(e)
            )
            raise EncryptionError(f"Failed to decrypt DEK: {e}")

    def encrypt_neural_data(
        self,
        data: Union[np.ndarray, Dict[str, Any]],
        encrypted_dek: Optional[bytes] = None
    ) -> Tuple[bytes, bytes]:
        """Encrypt neural data using envelope encryption.

        Args:
            data: Neural data (numpy array or dict)
            encrypted_dek: Optional pre-generated encrypted DEK

        Returns:
            Tuple of (encrypted_data, encrypted_dek)
        """
        start_time = time.time()

        try:
            # Generate or use provided DEK
            if encrypted_dek is None:
                encrypted_dek = self.generate_dek()

            # Decrypt the DEK
            dek = self.decrypt_dek(encrypted_dek)

            # Serialize the data
            if isinstance(data, np.ndarray):
                serialized_data = msgpack.packb({
                    "type": "ndarray",
                    "data": data.tobytes(),
                    "shape": data.shape,
                    "dtype": str(data.dtype)
                }, use_bin_type=True)
            else:
                serialized_data = msgpack.packb(data, use_bin_type=True)

            # Encrypt with Fernet
            f = Fernet(dek)
            encrypted_data = f.encrypt(serialized_data)

            # Record metrics
            duration_ms = (time.time() - start_time) * 1000
            self._record_metric(
                "encrypt_neural_data",
                duration_ms,
                len(encrypted_data),
                success=True
            )

            return encrypted_data, encrypted_dek

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._record_metric(
                "encrypt_neural_data",
                duration_ms,
                0,
                success=False,
                error_message=str(e)
            )
            raise EncryptionError(f"Failed to encrypt neural data: {e}")

    def decrypt_neural_data(
        self,
        encrypted_data: bytes,
        encrypted_dek: bytes
    ) -> Union[np.ndarray, Dict[str, Any]]:
        """Decrypt neural data.

        Args:
            encrypted_data: The encrypted data bytes
            encrypted_dek: The encrypted DEK

        Returns:
            Decrypted neural data
        """
        start_time = time.time()

        try:
            # Decrypt the DEK
            dek = self.decrypt_dek(encrypted_dek)

            # Decrypt the data
            f = Fernet(dek)
            decrypted_data = f.decrypt(encrypted_data)

            # Deserialize
            data = msgpack.unpackb(decrypted_data, raw=False)

            # Handle numpy arrays
            if isinstance(data, dict) and data.get("type") == "ndarray":
                array_data = np.frombuffer(data["data"], dtype=data["dtype"])
                data = array_data.reshape(data["shape"])

            # Record metrics
            duration_ms = (time.time() - start_time) * 1000
            self._record_metric(
                "decrypt_neural_data",
                duration_ms,
                len(decrypted_data),
                success=True
            )

            return data

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._record_metric(
                "decrypt_neural_data",
                duration_ms,
                0,
                success=False,
                error_message=str(e)
            )
            raise EncryptionError(f"Failed to decrypt neural data: {e}")

    def rotate_dek(self, old_encrypted_dek: bytes) -> bytes:
        """Rotate a DEK by re-encrypting with the latest KMS key version.

        Args:
            old_encrypted_dek: The old encrypted DEK

        Returns:
            New encrypted DEK
        """
        try:
            # Decrypt old DEK
            dek = self.decrypt_dek(old_encrypted_dek)

            # Re-encrypt with current key version
            encrypt_response = self.kms_client.encrypt(
                request={
                    "name": self.key_path,
                    "plaintext": dek,
                }
            )

            return encrypt_response.ciphertext

        except Exception as e:
            raise KeyRotationError(f"Failed to rotate DEK: {e}")

    def _clean_dek_cache(self):
        """Remove expired entries from DEK cache."""
        if not self.enable_caching:
            return

        now = datetime.now()
        expired_keys = [
            key for key, (_, cached_time) in self._dek_cache.items()
            if (now - cached_time).seconds >= self.cache_ttl_seconds
        ]

        for key in expired_keys:
            del self._dek_cache[key]

    def _record_metric(
        self,
        operation: str,
        duration_ms: float,
        data_size_bytes: int,
        success: bool,
        error_message: Optional[str] = None
    ):
        """Record performance metrics."""
        metric = EncryptionMetrics(
            operation=operation,
            duration_ms=duration_ms,
            data_size_bytes=data_size_bytes,
            timestamp=datetime.now(),
            success=success,
            error_message=error_message
        )
        self._metrics.append(metric)

        # Keep only recent metrics (last hour)
        cutoff_time = datetime.now() - timedelta(hours=1)
        self._metrics = [m for m in self._metrics if m.timestamp > cutoff_time]

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of encryption performance metrics."""
        if not self._metrics:
            return {}

        summary = {}
        operations = set(m.operation for m in self._metrics)

        for op in operations:
            op_metrics = [m for m in self._metrics if m.operation == op]
            successful = [m for m in op_metrics if m.success]

            if successful:
                avg_duration = sum(m.duration_ms for m in successful) / len(successful)
                avg_size = sum(m.data_size_bytes for m in successful) / len(successful)
            else:
                avg_duration = 0
                avg_size = 0

            summary[op] = {
                "total_operations": len(op_metrics),
                "successful": len(successful),
                "failed": len(op_metrics) - len(successful),
                "average_duration_ms": avg_duration,
                "average_size_bytes": avg_size,
                "success_rate": len(successful) / len(op_metrics) if op_metrics else 0
            }

        return summary


class FieldLevelEncryption:
    """Field-level encryption for specific sensitive fields in neural data.

    This class provides granular encryption for specific fields like:
    - Patient identifiers
    - Session metadata
    - Device identifiers
    - Location data
    """

    def __init__(self, encryption_service: NeuralDataEncryption):
        """Initialize field-level encryption.

        Args:
            encryption_service: The main encryption service instance
        """
        self.encryption_service = encryption_service
        self._field_deks: Dict[str, bytes] = {}  # Field-specific DEKs

    def encrypt_fields(
        self,
        data: Dict[str, Any],
        fields_to_encrypt: List[str]
    ) -> Dict[str, Any]:
        """Encrypt specific fields in a data dictionary.

        Args:
            data: The data dictionary
            fields_to_encrypt: List of field paths to encrypt (supports nested)

        Returns:
            Dictionary with encrypted fields
        """
        encrypted_data = data.copy()

        for field_path in fields_to_encrypt:
            # Get field value
            value = self._get_nested_value(data, field_path)
            if value is None:
                continue

            # Get or generate field-specific DEK
            if field_path not in self._field_deks:
                self._field_deks[field_path] = self.encryption_service.generate_dek(
                    context=field_path
                )

            # Encrypt the field value
            encrypted_value, _ = self.encryption_service.encrypt_neural_data(
                value,
                self._field_deks[field_path]
            )

            # Store encrypted value and DEK reference
            self._set_nested_value(
                encrypted_data,
                field_path,
                {
                    "encrypted": base64.b64encode(encrypted_value).decode('utf-8'),
                    "dek_field": field_path,
                    "algorithm": "AES-256-GCM"
                }
            )

        return encrypted_data

    def decrypt_fields(
        self,
        encrypted_data: Dict[str, Any],
        fields_to_decrypt: List[str]
    ) -> Dict[str, Any]:
        """Decrypt specific fields in a data dictionary.

        Args:
            encrypted_data: The encrypted data dictionary
            fields_to_decrypt: List of field paths to decrypt

        Returns:
            Dictionary with decrypted fields
        """
        decrypted_data = encrypted_data.copy()

        for field_path in fields_to_decrypt:
            # Get encrypted field data
            field_data = self._get_nested_value(encrypted_data, field_path)
            if not isinstance(field_data, dict) or "encrypted" not in field_data:
                continue

            # Get the DEK for this field
            dek_field = field_data.get("dek_field", field_path)
            if dek_field not in self._field_deks:
                raise EncryptionError(f"No DEK found for field: {dek_field}")

            # Decrypt the value
            encrypted_value = base64.b64decode(field_data["encrypted"])
            decrypted_value = self.encryption_service.decrypt_neural_data(
                encrypted_value,
                self._field_deks[dek_field]
            )

            # Set decrypted value
            self._set_nested_value(decrypted_data, field_path, decrypted_value)

        return decrypted_data

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get value from nested dictionary using dot notation."""
        keys = path.split('.')
        value = data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None

        return value

    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any):
        """Set value in nested dictionary using dot notation."""
        keys = path.split('.')
        current = data

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value
