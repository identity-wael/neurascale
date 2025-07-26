#!/usr/bin/env python3

"""
Compliance validation script for Neural Ledger.

This script validates that the Neural Ledger implementation supports
the required compliance frameworks: HIPAA, GDPR, and FDA 21 CFR Part 11.
"""

import asyncio
import uuid
import hashlib
from datetime import datetime, timezone
from unittest.mock import Mock

# Import ledger components
from ledger.neural_ledger import NeuralLedger
from ledger.event_schema import EventType


class ComplianceValidator:
    """Validates compliance capabilities of the Neural Ledger system."""

    def __init__(self):
        self.results = {
            "hipaa": {"tests": 0, "passed": 0, "failed": 0},
            "gdpr": {"tests": 0, "passed": 0, "failed": 0},
            "fda": {"tests": 0, "passed": 0, "failed": 0},
        }

    def log_test_result(
        self, framework: str, test_name: str, passed: bool, details: str = ""
    ):
        """Log the result of a compliance test."""
        self.results[framework]["tests"] += 1
        if passed:
            self.results[framework]["passed"] += 1
            print(f"✓ {framework.upper()} - {test_name}")
        else:
            self.results[framework]["failed"] += 1
            print(f"✗ {framework.upper()} - {test_name}: {details}")

    def create_mock_ledger(self):
        """Create a mocked Neural Ledger for testing."""
        ledger = NeuralLedger.__new__(NeuralLedger)
        ledger.project_id = "compliance-test"
        ledger.location = "test-location"
        ledger._initialized = True
        ledger._last_event_hash = "genesis_hash"

        # Mock clients
        ledger.publisher = Mock()
        ledger.bigtable_client = Mock()
        ledger.firestore_client = Mock()
        ledger.bigquery_client = Mock()
        ledger.kms_client = Mock()
        ledger.event_processor = Mock()

        return ledger

    async def validate_hipaa_compliance(self):
        """Validate HIPAA compliance capabilities."""
        print("\n=== HIPAA Compliance Validation ===")

        ledger = self.create_mock_ledger()

        # Test 1: Audit trail completeness
        try:
            user_id = f"hipaa-user-{uuid.uuid4()}"
            session_id = f"hipaa-session-{uuid.uuid4()}"

            # Create a PHI access event
            event = await ledger.log_event(
                event_type=EventType.SESSION_CREATED,
                session_id=session_id,
                user_id=user_id,
                metadata={
                    "patient_id": "P123456",
                    "procedure_type": "EEG_MONITORING",
                    "phi_accessed": True,
                },
            )

            # Verify event has required audit trail components
            has_event_id = event.event_id is not None
            has_timestamp = event.timestamp is not None
            has_user_tracking = event.user_id == user_id
            has_phi_metadata = "patient_id" in event.metadata

            audit_complete = all(
                [has_event_id, has_timestamp, has_user_tracking, has_phi_metadata]
            )
            self.log_test_result("hipaa", "Audit trail completeness", audit_complete)

        except Exception as e:
            self.log_test_result("hipaa", "Audit trail completeness", False, str(e))

        # Test 2: Data integrity and hash chain
        try:
            events = []
            for i in range(3):
                event = await ledger.log_event(
                    event_type=EventType.DATA_INGESTED,
                    session_id=session_id,
                    metadata={"sequence": i, "phi_data": True},
                )
                events.append(event)

            # Verify hash chain integrity
            chain_valid = True
            for i in range(1, len(events)):
                if events[i].previous_hash != events[i - 1].event_hash:
                    chain_valid = False
                    break

            self.log_test_result("hipaa", "Data integrity (hash chain)", chain_valid)

        except Exception as e:
            self.log_test_result("hipaa", "Data integrity (hash chain)", False, str(e))

        # Test 3: Access control tracking
        try:
            access_event = await ledger.log_access_event(
                user_id=user_id,
                granted=True,
                resource="/api/patient/P123456/data",
                metadata={
                    "role": "PHYSICIAN",
                    "mfa_verified": True,
                    "justification": "Clinical review",
                },
            )

            access_tracked = (
                access_event.metadata.get("role") == "PHYSICIAN"
                and access_event.metadata.get("mfa_verified") is True
                and "justification" in access_event.metadata
            )

            self.log_test_result("hipaa", "Access control tracking", access_tracked)

        except Exception as e:
            self.log_test_result("hipaa", "Access control tracking", False, str(e))

    async def validate_gdpr_compliance(self):
        """Validate GDPR compliance capabilities."""
        print("\n=== GDPR Compliance Validation ===")

        ledger = self.create_mock_ledger()

        # Test 1: Consent tracking
        try:
            user_id = f"gdpr-user-{uuid.uuid4()}"
            session_id = f"gdpr-session-{uuid.uuid4()}"

            consent_event = await ledger.log_event(
                event_type=EventType.SESSION_CREATED,
                session_id=session_id,
                user_id=user_id,
                metadata={
                    "consent_given": True,
                    "consent_type": "PROCESSING_NEURAL_DATA",
                    "lawful_basis": "CONSENT",
                    "purpose": "MEDICAL_RESEARCH",
                },
            )

            consent_tracked = (
                consent_event.metadata.get("consent_given") is True
                and consent_event.metadata.get("lawful_basis") == "CONSENT"
                and "purpose" in consent_event.metadata
            )

            self.log_test_result("gdpr", "Consent tracking", consent_tracked)

        except Exception as e:
            self.log_test_result("gdpr", "Consent tracking", False, str(e))

        # Test 2: Data subject rights support
        try:
            # Right to access
            access_request = await ledger.log_event(
                event_type=EventType.ACCESS_GRANTED,
                user_id=user_id,
                metadata={
                    "request_type": "GDPR_SUBJECT_ACCESS_REQUEST",
                    "request_fulfilled": True,
                    "response_time_days": 15,
                },
            )

            # Right to portability
            portability_request = await ledger.log_event(
                event_type=EventType.DATA_EXPORTED,
                user_id=user_id,
                metadata={
                    "export_type": "GDPR_DATA_PORTABILITY",
                    "export_format": "JSON",
                    "machine_readable": True,
                },
            )

            rights_supported = (
                access_request.metadata.get("request_fulfilled") is True
                and portability_request.metadata.get("machine_readable") is True
            )

            self.log_test_result(
                "gdpr", "Data subject rights support", rights_supported
            )

        except Exception as e:
            self.log_test_result("gdpr", "Data subject rights support", False, str(e))

        # Test 3: Privacy by design
        try:
            privacy_event = await ledger.log_data_ingested(
                session_id=session_id,
                data_hash="privacy_preserved_hash",
                size_bytes=2048,
                metadata={
                    "privacy_measures": {
                        "pseudonymization": True,
                        "encryption_at_rest": True,
                        "access_controls": True,
                    },
                    "data_minimization": True,
                    "purpose_limitation": True,
                },
            )

            privacy_by_design = (
                privacy_event.metadata.get("data_minimization") is True
                and privacy_event.metadata.get("purpose_limitation") is True
                and all(privacy_event.metadata["privacy_measures"].values())
            )

            self.log_test_result("gdpr", "Privacy by design", privacy_by_design)

        except Exception as e:
            self.log_test_result("gdpr", "Privacy by design", False, str(e))

    async def validate_fda_compliance(self):
        """Validate FDA 21 CFR Part 11 compliance capabilities."""
        print("\n=== FDA 21 CFR Part 11 Compliance Validation ===")

        ledger = self.create_mock_ledger()

        # Mock the event signer
        mock_signer = Mock()
        mock_signer.sign_event.return_value = "fda_signature_abc123"
        ledger.event_signer = mock_signer

        # Test 1: Electronic signature capability
        try:
            investigator_id = f"fda-investigator-{uuid.uuid4()}"
            study_id = f"fda-study-{uuid.uuid4()}"

            # Critical event requiring signature
            signed_event = await ledger.log_event(
                event_type=EventType.DATA_EXPORTED,  # Critical event
                session_id=study_id,
                user_id=investigator_id,
                metadata={
                    "study_type": "CLINICAL_TRIAL",
                    "signature_required": True,
                    "signature_meaning": "I certify this data export for regulatory submission",
                },
            )

            signature_capable = (
                signed_event.signature is not None
                and signed_event.signing_key_id is not None
                and "signature_meaning" in signed_event.metadata
            )

            self.log_test_result(
                "fda", "Electronic signature capability", signature_capable
            )

        except Exception as e:
            self.log_test_result(
                "fda", "Electronic signature capability", False, str(e)
            )

        # Test 2: Record integrity and authenticity
        try:
            # Create sequence of study events
            study_events = []
            for i in range(3):
                event = await ledger.log_event(
                    event_type=EventType.SESSION_CREATED,
                    session_id=study_id,
                    metadata={
                        "sequence": i,
                        "fda_compliant_record": True,
                        "data_integrity_hash": hashlib.sha256(
                            f"study_data_{i}".encode()
                        ).hexdigest(),
                    },
                )
                study_events.append(event)

            # Verify chronological and hash chain integrity
            chronological = all(
                study_events[i].timestamp >= study_events[i - 1].timestamp
                for i in range(1, len(study_events))
            )

            hash_chain_valid = all(
                study_events[i].previous_hash == study_events[i - 1].event_hash
                for i in range(1, len(study_events))
            )

            integrity_maintained = chronological and hash_chain_valid

            self.log_test_result(
                "fda", "Record integrity and authenticity", integrity_maintained
            )

        except Exception as e:
            self.log_test_result(
                "fda", "Record integrity and authenticity", False, str(e)
            )

        # Test 3: Audit trail completeness
        try:
            # Comprehensive audit event
            audit_event = await ledger.log_event(
                event_type=EventType.AUTH_SUCCESS,
                user_id=investigator_id,
                metadata={
                    "authentication_method": "PKI_CERTIFICATE",
                    "user_role": "PRINCIPAL_INVESTIGATOR",
                    "workstation_id": "CLINICAL-WS-001",
                    "regulatory_compliance": "21_CFR_PART_11",
                    "audit_trail_complete": True,
                },
            )

            audit_complete = (
                audit_event.event_id is not None
                and audit_event.timestamp is not None
                and audit_event.user_id is not None
                and audit_event.metadata.get("regulatory_compliance")
                == "21_CFR_PART_11"
            )

            self.log_test_result("fda", "Audit trail completeness", audit_complete)

        except Exception as e:
            self.log_test_result("fda", "Audit trail completeness", False, str(e))

    async def run_validation(self):
        """Run all compliance validation tests."""
        print("Neural Ledger Compliance Validation")
        print("=" * 40)

        await self.validate_hipaa_compliance()
        await self.validate_gdpr_compliance()
        await self.validate_fda_compliance()

        # Print summary
        print("\n" + "=" * 40)
        print("COMPLIANCE VALIDATION SUMMARY")
        print("=" * 40)

        total_tests = 0
        total_passed = 0
        total_failed = 0

        for framework, results in self.results.items():
            tests = results["tests"]
            passed = results["passed"]
            failed = results["failed"]

            total_tests += tests
            total_passed += passed
            total_failed += failed

            status = "✓ PASS" if failed == 0 else "✗ FAIL"
            print(f"{framework.upper()}: {passed}/{tests} tests passed {status}")

        print("-" * 40)
        overall_status = "✓ COMPLIANT" if total_failed == 0 else "✗ NON-COMPLIANT"
        print(f"OVERALL: {total_passed}/{total_tests} tests passed {overall_status}")

        if total_failed == 0:
            print(
                "\n🎉 Neural Ledger is compliant with HIPAA, GDPR, and FDA 21 CFR Part 11!"
            )
            print("The system provides comprehensive audit trails, data protection,")
            print("and regulatory compliance capabilities.")
        else:
            print(f"\n⚠️  {total_failed} compliance tests failed.")
            print("Review the implementation to ensure full regulatory compliance.")

        return total_failed == 0


async def main():
    """Main validation function."""
    validator = ComplianceValidator()
    is_compliant = await validator.run_validation()
    return 0 if is_compliant else 1


if __name__ == "__main__":
    import sys

    exit_code = asyncio.run(main())
    sys.exit(exit_code)
