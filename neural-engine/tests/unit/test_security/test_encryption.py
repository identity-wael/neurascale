"""Unit tests for neural data encryption module."""

import pytest
import numpy as np
import base64
import time
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from neural_engine.security.encryption import (
    NeuralDataEncryption,
    FieldLevelEncryption,
    EncryptionError,
)


class TestNeuralDataEncryption:
    """Test cases for NeuralDataEncryption class."""

    @pytest.fixture
    def mock_kms_client(self):
        """Create a mock KMS client."""
        with patch(
            "neural_engine.security.encryption.kms.KeyManagementServiceClient"
        ) as mock:
            mock_instance = Mock()
            mock.return_value = mock_instance

            # Mock KMS methods
            mock_instance.crypto_key_path.return_value = "projects/test/locations/us-central1/keyRings/test-ring/cryptoKeys/test-key"
            mock_instance.get_key_ring.return_value = Mock()
            mock_instance.get_crypto_key.return_value = Mock()

            # Mock encryption/decryption
            mock_instance.encrypt.return_value = Mock(ciphertext=b"encrypted_dek_data")
            mock_instance.decrypt.return_value = Mock(
                plaintext=b"gAAAAABhdjJf_example_fernet_key_data_here_1234567890"  # Valid Fernet key format
            )

            yield mock_instance

    @pytest.fixture
    def mock_secret_client(self):
        """Create a mock Secret Manager client."""
        with patch(
            "neural_engine.security.encryption.secretmanager.SecretManagerServiceClient"
        ) as mock:
            yield mock.return_value

    @pytest.fixture
    def encryption_service(self, mock_kms_client, mock_secret_client):
        """Create encryption service with mocked dependencies."""
        service = NeuralDataEncryption(
            project_id="test-project",
            location="us-central1",
            key_ring="test-ring",
            key_name="test-key",
            enable_caching=True,
            cache_ttl_seconds=60,
        )
        return service

    def test_initialization(self, encryption_service):
        """Test encryption service initialization."""
        assert encryption_service.project_id == "test-project"
        assert encryption_service.location == "us-central1"
        assert encryption_service.key_ring == "test-ring"
        assert encryption_service.key_name == "test-key"
        assert encryption_service.enable_caching is True
        assert encryption_service.cache_ttl_seconds == 60

    def test_generate_dek(self, encryption_service, mock_kms_client):
        """Test DEK generation."""
        # Generate DEK
        encrypted_dek = encryption_service.generate_dek()

        # Verify
        assert encrypted_dek == b"encrypted_dek_data"
        mock_kms_client.encrypt.assert_called_once()

        # Check metrics were recorded
        metrics = encryption_service.get_metrics_summary()
        assert "generate_dek" in metrics
        assert metrics["generate_dek"]["successful"] == 1

    def test_decrypt_dek_with_caching(self, encryption_service, mock_kms_client):
        """Test DEK decryption with caching."""
        encrypted_dek = b"encrypted_dek_data"

        # First decryption - should hit KMS
        dek1 = encryption_service.decrypt_dek(encrypted_dek)
        assert mock_kms_client.decrypt.call_count == 1

        # Second decryption - should use cache
        dek2 = encryption_service.decrypt_dek(encrypted_dek)
        assert mock_kms_client.decrypt.call_count == 1  # No additional call
        assert dek1 == dek2

    def test_encrypt_neural_array(self, encryption_service, mock_kms_client):
        """Test encryption of numpy array neural data."""
        # Create test neural data
        neural_data = np.random.randn(32, 1000).astype(np.float32)

        # Encrypt
        encrypted_data, encrypted_dek = encryption_service.encrypt_neural_data(
            neural_data
        )

        # Verify
        assert isinstance(encrypted_data, bytes)
        assert isinstance(encrypted_dek, bytes)
        assert len(encrypted_data) > 0

        # Check metrics
        metrics = encryption_service.get_metrics_summary()
        assert "encrypt_neural_data" in metrics

    def test_encrypt_decrypt_roundtrip(self, encryption_service):
        """Test full encryption/decryption roundtrip."""
        # Test with numpy array
        original_array = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])

        # Mock Fernet key for consistent testing
        from cryptography.fernet import Fernet

        test_key = Fernet.generate_key()

        with patch.object(encryption_service, "decrypt_dek", return_value=test_key):
            # Encrypt
            encrypted_data, encrypted_dek = encryption_service.encrypt_neural_data(
                original_array
            )

            # Decrypt
            decrypted_array = encryption_service.decrypt_neural_data(
                encrypted_data, encrypted_dek
            )

            # Verify
            np.testing.assert_array_equal(original_array, decrypted_array)

    def test_encrypt_decrypt_dict_data(self, encryption_service):
        """Test encryption/decryption of dictionary data."""
        # Test data
        original_data = {
            "session_id": "test-123",
            "metadata": {
                "timestamp": "2024-01-01T12:00:00Z",
                "device_id": "device-456",
            },
            "values": [1, 2, 3, 4, 5],
        }

        # Mock Fernet key
        from cryptography.fernet import Fernet

        test_key = Fernet.generate_key()

        with patch.object(encryption_service, "decrypt_dek", return_value=test_key):
            # Encrypt
            encrypted_data, encrypted_dek = encryption_service.encrypt_neural_data(
                original_data
            )

            # Decrypt
            decrypted_data = encryption_service.decrypt_neural_data(
                encrypted_data, encrypted_dek
            )

            # Verify
            assert decrypted_data == original_data

    def test_key_rotation(self, encryption_service, mock_kms_client):
        """Test DEK rotation."""
        old_encrypted_dek = b"old_encrypted_dek"

        # Rotate key
        new_encrypted_dek = encryption_service.rotate_dek(old_encrypted_dek)

        # Verify
        assert new_encrypted_dek == b"encrypted_dek_data"
        assert mock_kms_client.decrypt.called
        assert mock_kms_client.encrypt.called

    def test_cache_expiration(self, encryption_service):
        """Test DEK cache expiration."""
        # Add to cache with expired timestamp
        cache_key = "test_key"
        encryption_service._dek_cache[cache_key] = (
            b"cached_dek",
            datetime.now()
            - timedelta(seconds=encryption_service.cache_ttl_seconds + 1),
        )

        # Clean cache
        encryption_service._clean_dek_cache()

        # Verify expired entry was removed
        assert cache_key not in encryption_service._dek_cache

    def test_encryption_error_handling(self, encryption_service, mock_kms_client):
        """Test error handling in encryption operations."""
        # Mock KMS error
        mock_kms_client.encrypt.side_effect = Exception("KMS error")

        # Test DEK generation error
        with pytest.raises(EncryptionError) as exc_info:
            encryption_service.generate_dek()

        assert "Failed to generate DEK" in str(exc_info.value)

        # Check error was recorded in metrics
        metrics = encryption_service.get_metrics_summary()
        assert metrics["generate_dek"]["failed"] == 1

    def test_metrics_collection(self, encryption_service):
        """Test performance metrics collection."""
        # Record some test metrics
        encryption_service._record_metric(
            "test_operation", duration_ms=10.5, data_size_bytes=1024, success=True
        )

        encryption_service._record_metric(
            "test_operation", duration_ms=15.2, data_size_bytes=2048, success=True
        )

        encryption_service._record_metric(
            "test_operation",
            duration_ms=0,
            data_size_bytes=0,
            success=False,
            error_message="Test error",
        )

        # Get summary
        summary = encryption_service.get_metrics_summary()

        # Verify
        assert "test_operation" in summary
        assert summary["test_operation"]["total_operations"] == 3
        assert summary["test_operation"]["successful"] == 2
        assert summary["test_operation"]["failed"] == 1
        assert summary["test_operation"]["success_rate"] == 2 / 3


class TestFieldLevelEncryption:
    """Test cases for FieldLevelEncryption class."""

    @pytest.fixture
    def mock_encryption_service(self):
        """Create a mock encryption service."""
        service = Mock(spec=NeuralDataEncryption)

        # Mock encryption methods
        service.generate_dek.return_value = b"test_dek"
        service.encrypt_neural_data.return_value = (b"encrypted_value", b"test_dek")
        service.decrypt_neural_data.return_value = "decrypted_value"

        return service

    @pytest.fixture
    def field_encryption(self, mock_encryption_service):
        """Create field-level encryption instance."""
        return FieldLevelEncryption(mock_encryption_service)

    def test_encrypt_simple_fields(self, field_encryption, mock_encryption_service):
        """Test encryption of simple fields."""
        data = {
            "patient_id": "12345",
            "name": "John Doe",
            "age": 30,
            "session_id": "session-123",
        }

        fields_to_encrypt = ["patient_id", "name"]

        # Encrypt fields
        encrypted_data = field_encryption.encrypt_fields(data, fields_to_encrypt)

        # Verify encrypted fields
        assert "encrypted" in encrypted_data["patient_id"]
        assert "dek_field" in encrypted_data["patient_id"]
        assert "algorithm" in encrypted_data["patient_id"]
        assert encrypted_data["patient_id"]["algorithm"] == "AES-256-GCM"

        assert "encrypted" in encrypted_data["name"]

        # Verify unencrypted fields remain unchanged
        assert encrypted_data["age"] == 30
        assert encrypted_data["session_id"] == "session-123"

    def test_encrypt_nested_fields(self, field_encryption, mock_encryption_service):
        """Test encryption of nested fields."""
        data = {
            "patient": {
                "id": "patient-123",
                "personal": {"name": "Jane Doe", "ssn": "123-45-6789"},
            },
            "device": {
                "id": "device-456",
                "location": {"lat": 37.7749, "lon": -122.4194},
            },
        }

        fields_to_encrypt = ["patient.id", "patient.personal.ssn", "device.location"]

        # Encrypt fields
        encrypted_data = field_encryption.encrypt_fields(data, fields_to_encrypt)

        # Verify nested encrypted fields
        assert "encrypted" in encrypted_data["patient"]["id"]
        assert "encrypted" in encrypted_data["patient"]["personal"]["ssn"]
        assert "encrypted" in encrypted_data["device"]["location"]

        # Verify unencrypted nested field
        assert encrypted_data["patient"]["personal"]["name"] == "Jane Doe"

    def test_decrypt_fields(self, field_encryption, mock_encryption_service):
        """Test field decryption."""
        # Prepare encrypted data
        encrypted_data = {
            "patient_id": {
                "encrypted": base64.b64encode(b"encrypted_patient_id").decode(),
                "dek_field": "patient_id",
                "algorithm": "AES-256-GCM",
            },
            "name": {
                "encrypted": base64.b64encode(b"encrypted_name").decode(),
                "dek_field": "name",
                "algorithm": "AES-256-GCM",
            },
            "age": 30,
        }

        # Set up DEKs
        field_encryption._field_deks = {"patient_id": b"dek1", "name": b"dek2"}

        fields_to_decrypt = ["patient_id", "name"]

        # Decrypt fields
        decrypted_data = field_encryption.decrypt_fields(
            encrypted_data, fields_to_decrypt
        )

        # Verify
        assert decrypted_data["patient_id"] == "decrypted_value"
        assert decrypted_data["name"] == "decrypted_value"
        assert decrypted_data["age"] == 30

    def test_encrypt_nonexistent_field(self, field_encryption):
        """Test encryption of non-existent fields."""
        data = {"existing_field": "value"}
        fields_to_encrypt = ["nonexistent_field"]

        # Should not raise error
        encrypted_data = field_encryption.encrypt_fields(data, fields_to_encrypt)

        # Verify original data unchanged
        assert encrypted_data == data

    def test_decrypt_missing_dek(self, field_encryption):
        """Test decryption when DEK is missing."""
        encrypted_data = {
            "field": {
                "encrypted": base64.b64encode(b"encrypted").decode(),
                "dek_field": "field",
                "algorithm": "AES-256-GCM",
            }
        }

        # No DEK in cache
        field_encryption._field_deks = {}

        # Should raise error
        with pytest.raises(EncryptionError) as exc_info:
            field_encryption.decrypt_fields(encrypted_data, ["field"])

        assert "No DEK found for field" in str(exc_info.value)

    def test_nested_value_operations(self, field_encryption):
        """Test nested value getter/setter methods."""
        data = {"level1": {"level2": {"level3": "deep_value"}}}

        # Test getter
        value = field_encryption._get_nested_value(data, "level1.level2.level3")
        assert value == "deep_value"

        # Test getter with non-existent path
        value = field_encryption._get_nested_value(data, "level1.nonexistent")
        assert value is None

        # Test setter
        field_encryption._set_nested_value(data, "level1.level2.new_field", "new_value")
        assert data["level1"]["level2"]["new_field"] == "new_value"

        # Test setter creating new path
        field_encryption._set_nested_value(data, "new.path.field", "value")
        assert data["new"]["path"]["field"] == "value"


class TestEncryptionIntegration:
    """Integration tests for encryption functionality."""

    @pytest.fixture
    def real_encryption_service(self):
        """Create encryption service with real Fernet encryption."""
        with patch("neural_engine.security.encryption.kms.KeyManagementServiceClient"):
            with patch(
                "neural_engine.security.encryption.secretmanager.SecretManagerServiceClient"
            ):
                service = NeuralDataEncryption(
                    project_id="test-project", enable_caching=True
                )

                # Mock KMS operations but use real Fernet
                from cryptography.fernet import Fernet

                real_key = Fernet.generate_key()

                # Override methods to use real encryption
                service.generate_dek = Mock(return_value=b"mock_encrypted_dek")
                service.decrypt_dek = Mock(return_value=real_key)

                return service

    def test_large_array_encryption(self, real_encryption_service):
        """Test encryption of large neural data arrays."""
        # Create large neural data array (simulating 1 minute of 64-channel EEG at 1kHz)
        large_array = np.random.randn(64, 60000).astype(np.float32)

        # Encrypt
        start_time = time.time()
        encrypted_data, encrypted_dek = real_encryption_service.encrypt_neural_data(
            large_array
        )
        encrypt_time = time.time() - start_time

        # Decrypt
        start_time = time.time()
        decrypted_array = real_encryption_service.decrypt_neural_data(
            encrypted_data, encrypted_dek
        )
        decrypt_time = time.time() - start_time

        # Verify
        np.testing.assert_array_almost_equal(large_array, decrypted_array)

        # Performance check (should be reasonably fast)
        assert encrypt_time < 1.0  # Less than 1 second
        assert decrypt_time < 1.0  # Less than 1 second

        print(
            f"Large array encryption: {encrypt_time:.3f}s, decryption: {decrypt_time:.3f}s"
        )

    def test_batch_encryption_performance(self, real_encryption_service):
        """Test batch encryption performance."""
        # Create batch of neural data chunks
        batch_size = 100
        chunk_shape = (32, 256)  # 32 channels, 256 samples

        batch_data = [
            np.random.randn(*chunk_shape).astype(np.float32) for _ in range(batch_size)
        ]

        # Encrypt batch
        start_time = time.time()
        encrypted_dek = real_encryption_service.generate_dek()

        encrypted_batch = []
        for data in batch_data:
            encrypted, _ = real_encryption_service.encrypt_neural_data(
                data, encrypted_dek
            )
            encrypted_batch.append(encrypted)

        batch_time = time.time() - start_time

        # Performance check
        avg_time_per_chunk = batch_time / batch_size
        assert avg_time_per_chunk < 0.01  # Less than 10ms per chunk

        print(
            f"Batch encryption ({batch_size} chunks): {batch_time:.3f}s "
            f"({avg_time_per_chunk * 1000:.2f}ms per chunk)"
        )

    def test_concurrent_encryption(self, real_encryption_service):
        """Test concurrent encryption operations."""
        import concurrent.futures

        # Function to encrypt data
        def encrypt_chunk(data):
            encrypted, dek = real_encryption_service.encrypt_neural_data(data)
            decrypted = real_encryption_service.decrypt_neural_data(encrypted, dek)
            return np.array_equal(data, decrypted)

        # Create test data
        num_workers = 4
        chunks_per_worker = 25
        test_data = [
            np.random.randn(32, 256).astype(np.float32)
            for _ in range(num_workers * chunks_per_worker)
        ]

        # Run concurrent encryption
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            results = list(executor.map(encrypt_chunk, test_data))

        # Verify all succeeded
        assert all(results)
        print(f"Concurrent encryption test passed: {len(results)} chunks processed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
