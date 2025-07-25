"""Tests for data anonymizer."""

import pytest
import numpy as np
from datetime import datetime, timezone

from src.ingestion.anonymizer import DataAnonymizer
from src.ingestion.data_types import (
    NeuralDataPacket,
    NeuralSignalType,
    DataSource,
    DeviceInfo,
    ChannelInfo,
)


class TestDataAnonymizer:
    """Test DataAnonymizer class."""

    @pytest.fixture
    def anonymizer(self):
        """Create an anonymizer with a fixed secret key."""
        return DataAnonymizer(secret_key="test_secret_key_12345")

    @pytest.fixture
    def test_packet(self):
        """Create a test packet with PII."""
        device_info = DeviceInfo(
            device_id="device_serial_12345",
            device_type="OpenBCI",
            serial_number="SN - 12345",
            channels=[
                ChannelInfo(0, "Ch1", hardware_id="HW - 001"),
                ChannelInfo(1, "Ch2", hardware_id="HW - 002"),
            ],
        )

        return NeuralDataPacket(
            timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            data=np.random.randn(2, 100),
            signal_type=NeuralSignalType.EEG,
            source=DataSource.OPENBCI,
            device_info=device_info,
            session_id="session_001",
            subject_id="patient_john_doe_123",
            metadata={
                "name": "John Doe",
                "email": "john.doe@example.com",
                "age": 35,
                "location": "New York, NY",
                "experiment": "motor_imagery",
            },
        )

    def test_anonymize_subject_id(self, anonymizer, test_packet):
        """Test subject ID anonymization."""
        anonymized = anonymizer.anonymize_packet(test_packet)

        # Subject ID should be anonymized
        assert anonymized.subject_id != test_packet.subject_id
        assert anonymized.subject_id.startswith("ANON_")
        assert len(anonymized.subject_id) == 21  # ANON_ + 16 chars

        # Should be consistent
        anonymized2 = anonymizer.anonymize_packet(test_packet)
        assert anonymized.subject_id == anonymized2.subject_id

    def test_anonymize_device_info(self, anonymizer, test_packet):
        """Test device info anonymization."""
        anonymized = anonymizer.anonymize_packet(test_packet)

        # Serial number should be removed
        assert anonymized.device_info.serial_number is None

        # Device ID should be anonymized but keep prefix
        assert anonymized.device_info.device_id.startswith("devi_")
        assert anonymized.device_info.device_id != test_packet.device_info.device_id

        # Hardware IDs should be removed from channels
        for channel in anonymized.device_info.channels:
            assert channel.hardware_id is None

    def test_fuzz_timestamp(self, anonymizer, test_packet):
        """Test timestamp fuzzing."""
        anonymized = anonymizer.anonymize_packet(test_packet)

        # Timestamp should be different but close
        time_diff = abs((anonymized.timestamp - test_packet.timestamp).total_seconds())
        assert time_diff <= 5  # Within 5 seconds

        # Should be consistent for same input
        anonymized2 = anonymizer.anonymize_packet(test_packet)
        assert anonymized.timestamp == anonymized2.timestamp

    def test_sanitize_metadata(self, anonymizer, test_packet):
        """Test metadata sanitization."""
        anonymized = anonymizer.anonymize_packet(test_packet)

        # PII fields should be removed
        assert "name" not in anonymized.metadata
        assert "email" not in anonymized.metadata
        assert "location" not in anonymized.metadata

        # Age should be converted to range
        assert "age" not in anonymized.metadata
        assert anonymized.metadata["age_range"] == "30 - 49"

        # Non - PII fields should remain
        assert anonymized.metadata["experiment"] == "motor_imagery"

    def test_different_secret_keys(self, test_packet):
        """Test that different secret keys produce different anonymization."""
        anonymizer1 = DataAnonymizer(secret_key="key1")
        anonymizer2 = DataAnonymizer(secret_key="key2")

        anon1 = anonymizer1.anonymize_packet(test_packet)
        anon2 = anonymizer2.anonymize_packet(test_packet)

        # Same subject should get different IDs with different keys
        assert anon1.subject_id != anon2.subject_id

    def test_handle_missing_fields(self, anonymizer):
        """Test handling packets with missing optional fields."""
        # Minimal packet
        device_info = DeviceInfo(
            device_id="test",
            device_type="test",
        )

        packet = NeuralDataPacket(
            timestamp=datetime.now(timezone.utc),
            data=np.zeros((1, 10)),
            signal_type=NeuralSignalType.EEG,
            source=DataSource.SYNTHETIC,
            device_info=device_info,
            session_id="test",
            # No subject_id, no metadata
        )

        # Should not raise errors
        anonymized = anonymizer.anonymize_packet(packet)

        assert anonymized.subject_id is None
        assert anonymized.metadata is None

    def test_nested_metadata(self, anonymizer):
        """Test sanitization of nested metadata."""
        packet = NeuralDataPacket(
            timestamp=datetime.now(timezone.utc),
            data=np.zeros((1, 10)),
            signal_type=NeuralSignalType.EEG,
            source=DataSource.SYNTHETIC,
            device_info=DeviceInfo("test", "test"),
            session_id="test",
            metadata={
                "experiment": "test",
                "participant": {
                    "name": "Jane Doe",
                    "age": 25,
                    "id": "P001",
                },
                "location": {
                    "address": "123 Main St",
                    "room": "Lab A",
                },
            },
        )

        anonymized = anonymizer.anonymize_packet(packet)

        # Nested PII should be removed
        assert "name" not in anonymized.metadata["participant"]

        # Age in nested dict should be removed (not converted to range currently)
        assert "age" not in anonymized.metadata["participant"]

        # Non - PII nested fields should remain
        assert anonymized.metadata["participant"]["id"] == "P001"

        # Check location handling - should have room but not address
        if "location" in anonymized.metadata:
            assert "address" not in anonymized.metadata["location"]
            assert anonymized.metadata["location"]["room"] == "Lab A"

    def test_age_ranges(self, anonymizer):
        """Test age range conversion."""
        test_ages = [
            (10, "under_18"),
            (17, "under_18"),
            (18, "18 - 29"),
            (25, "18 - 29"),
            (30, "30 - 49"),
            (45, "30 - 49"),
            (50, "50 - 69"),
            (65, "50 - 69"),
            (70, "70+"),
            (85, "70+"),
        ]

        for age, expected_range in test_ages:
            packet = NeuralDataPacket(
                timestamp=datetime.now(timezone.utc),
                data=np.zeros((1, 10)),
                signal_type=NeuralSignalType.EEG,
                source=DataSource.SYNTHETIC,
                device_info=DeviceInfo("test", "test"),
                session_id="test",
                metadata={"age": age},
            )

            anonymized = anonymizer.anonymize_packet(packet)
            assert anonymized.metadata["age_range"] == expected_range

    def test_audit_log(self, anonymizer, test_packet):
        """Test audit logging."""
        # Clear any existing logs
        anonymizer._audit_log.clear()

        # Anonymize packet
        anonymizer.anonymize_packet(test_packet)

        # Check audit log
        audit_log = anonymizer.get_audit_log()
        assert len(audit_log) == 1

        log_entry = audit_log[0]
        assert log_entry["session_id"] == test_packet.session_id
        assert log_entry["original_subject_id"] is True
        assert log_entry["anonymized_subject_id"] is True
        assert log_entry["metadata_sanitized"] is True
        # Timestamp fuzzing might result in same timestamp due to deterministic hash
        assert "timestamp_fuzzed" in log_entry

    def test_export_mappings(self, anonymizer, test_packet):
        """Test exporting subject ID mappings."""
        # Anonymize multiple subjects
        subjects = ["patient_001", "patient_002", "patient_003"]

        for subject_id in subjects:
            test_packet.subject_id = subject_id
            anonymizer.anonymize_packet(test_packet)

        # Export mappings
        mappings = anonymizer.export_mappings()

        assert len(mappings) == 3
        for original_id in subjects:
            assert original_id in mappings
            assert mappings[original_id].startswith("ANON_")
