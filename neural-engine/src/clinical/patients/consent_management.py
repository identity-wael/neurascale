"""Dynamic consent management for HIPAA compliance."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from uuid import uuid4

from ..types import ConsentRecord, ConsentStatus, ClinicalConfig

logger = logging.getLogger(__name__)


class ConsentManager:
    """Manages dynamic patient consent with HIPAA compliance.

    Handles consent workflows, updates, withdrawals, and audit trails
    for comprehensive privacy management.
    """

    def __init__(self, config: ClinicalConfig):
        """Initialize consent manager."""
        self.config = config

        # Consent storage (would be database in production)
        self._consent_records: Dict[str, List[ConsentRecord]] = {}

        # Consent templates and requirements
        self.consent_templates = self._load_consent_templates()

        logger.info("Consent manager initialized")

    async def create_consent_workflow(
        self, patient_id: str, consent_types: List[str]
    ) -> str:
        """Create comprehensive consent workflow for patient.

        Args:
            patient_id: Patient identifier
            consent_types: List of consent types required

        Returns:
            Workflow ID for tracking
        """
        workflow_id = str(uuid4())

        # Initialize consent records for each type
        consent_records = []

        for consent_type in consent_types:
            if consent_type in self.consent_templates:
                template = self.consent_templates[consent_type]

                consent_record = ConsentRecord(
                    patient_id=patient_id,
                    consent_type=consent_type,
                    status=ConsentStatus.PENDING,
                    consent_text=template["text"],
                    expiry_date=self._calculate_expiry_date(consent_type),
                )

                consent_records.append(consent_record)
            else:
                logger.warning(f"Unknown consent type: {consent_type}")

        # Store consent records
        if patient_id not in self._consent_records:
            self._consent_records[patient_id] = []

        self._consent_records[patient_id].extend(consent_records)

        logger.info(
            f"Consent workflow created for patient {patient_id}: {len(consent_records)} consents"
        )

        return workflow_id

    async def process_consent_update(
        self, patient_id: str, consent_changes: dict
    ) -> Dict[str, Any]:
        """Process patient consent updates.

        Args:
            patient_id: Patient identifier
            consent_changes: Dictionary of consent updates

        Returns:
            Update processing result
        """
        if patient_id not in self._consent_records:
            raise ValueError(f"No consent records found for patient: {patient_id}")

        results = {
            "patient_id": patient_id,
            "updated_consents": [],
            "failed_updates": [],
            "warnings": [],
            "audit_entries": [],
        }

        for consent_type, consent_data in consent_changes.items():
            try:
                # Find existing consent record
                existing_consent = self._find_consent_record(patient_id, consent_type)

                if existing_consent:
                    # Update existing consent
                    old_status = existing_consent.status

                    if consent_data.get("granted", False):
                        existing_consent.status = ConsentStatus.APPROVED
                        existing_consent.granted_date = datetime.now(timezone.utc)
                        existing_consent.signed_by = consent_data.get("signed_by", "")
                        existing_consent.witness = consent_data.get("witness")
                    else:
                        existing_consent.status = ConsentStatus.WITHDRAWN
                        existing_consent.withdrawn_date = datetime.now(timezone.utc)

                    # Create audit entry
                    audit_entry = {
                        "timestamp": datetime.now(timezone.utc),
                        "patient_id": patient_id,
                        "consent_id": existing_consent.consent_id,
                        "consent_type": consent_type,
                        "action": "status_change",
                        "old_status": old_status.value,
                        "new_status": existing_consent.status.value,
                        "user_id": consent_data.get("updated_by", "system"),
                    }

                    results["updated_consents"].append(
                        {
                            "consent_type": consent_type,
                            "old_status": old_status.value,
                            "new_status": existing_consent.status.value,
                        }
                    )

                    results["audit_entries"].append(audit_entry)

                else:
                    # Create new consent record
                    new_consent = ConsentRecord(
                        patient_id=patient_id,
                        consent_type=consent_type,
                        status=(
                            ConsentStatus.APPROVED
                            if consent_data.get("granted", False)
                            else ConsentStatus.PENDING
                        ),
                        granted_date=(
                            datetime.now(timezone.utc)
                            if consent_data.get("granted", False)
                            else None
                        ),
                        consent_text=consent_data.get("text", ""),
                        signed_by=consent_data.get("signed_by", ""),
                        witness=consent_data.get("witness"),
                        expiry_date=self._calculate_expiry_date(consent_type),
                    )

                    self._consent_records[patient_id].append(new_consent)

                    results["updated_consents"].append(
                        {
                            "consent_type": consent_type,
                            "old_status": "none",
                            "new_status": new_consent.status.value,
                        }
                    )

            except Exception as e:
                results["failed_updates"].append(
                    {"consent_type": consent_type, "error": str(e)}
                )
                logger.error(
                    f"Failed to update consent {consent_type} for patient {patient_id}: {e}"
                )

        # Check for compliance issues
        compliance_warnings = await self._check_consent_compliance(patient_id)
        results["warnings"].extend(compliance_warnings)

        logger.info(
            f"Processed consent updates for patient {patient_id}: {len(results['updated_consents'])} updated"
        )

        return results

    async def validate_data_usage_consent(
        self, patient_id: str, usage_type: str
    ) -> bool:
        """Validate patient consent for specific data usage.

        Args:
            patient_id: Patient identifier
            usage_type: Type of data usage requested

        Returns:
            Whether usage is consented to
        """
        if patient_id not in self._consent_records:
            return False

        # Map usage types to consent types
        usage_consent_mapping = {
            "treatment": ["treatment_consent"],
            "research": ["research_participation", "data_sharing"],
            "analytics": ["data_collection_consent"],
            "marketing": ["marketing_communications"],
            "quality_improvement": ["data_collection_consent"],
            "billing": ["treatment_consent"],
            "care_coordination": ["treatment_consent", "data_sharing"],
        }

        required_consents = usage_consent_mapping.get(usage_type, [])

        if not required_consents:
            logger.warning(f"Unknown usage type: {usage_type}")
            return False

        # Check that all required consents are granted and valid
        for consent_type in required_consents:
            consent_record = self._find_consent_record(patient_id, consent_type)

            if not consent_record:
                return False

            if consent_record.status != ConsentStatus.APPROVED:
                return False

            # Check if consent has expired
            if (
                consent_record.expiry_date
                and consent_record.expiry_date < datetime.now(timezone.utc)
            ):
                return False

        # Log consent validation for audit
        await self._log_consent_validation(patient_id, usage_type, True)

        return True

    async def handle_consent_withdrawal(
        self, patient_id: str, consent_id: str, reason: str = ""
    ) -> bool:
        """Handle patient consent withdrawal.

        Args:
            patient_id: Patient identifier
            consent_id: Specific consent to withdraw
            reason: Reason for withdrawal

        Returns:
            Success status
        """
        if patient_id not in self._consent_records:
            return False

        # Find consent record
        consent_record = None
        for record in self._consent_records[patient_id]:
            if record.consent_id == consent_id:
                consent_record = record
                break

        if not consent_record:
            return False

        # Update consent status
        old_status = consent_record.status
        consent_record.status = ConsentStatus.WITHDRAWN
        consent_record.withdrawn_date = datetime.now(timezone.utc)

        # Log audit entry
        logger.info(
            f"Consent withdrawal audit: patient={patient_id}, "
            f"consent_id={consent_id}, type={consent_record.consent_type}, "
            f"old_status={old_status.value}, reason={reason}"
        )

        # Check if withdrawal affects ongoing treatments
        impact_assessment = await self._assess_withdrawal_impact(
            patient_id, consent_record.consent_type
        )

        if impact_assessment["affects_treatment"]:
            logger.warning(
                f"Consent withdrawal affects active treatment for patient {patient_id}"
            )
            # In production, would trigger care team notifications

        logger.info(
            f"Consent withdrawn for patient {patient_id}: {consent_record.consent_type}"
        )

        return True

    async def get_consent_status(self, patient_id: str) -> Dict[str, Any]:
        """Get comprehensive consent status for patient.

        Args:
            patient_id: Patient identifier

        Returns:
            Consent status summary
        """
        if patient_id not in self._consent_records:
            return {"patient_id": patient_id, "consents": [], "status": "no_consents"}

        consent_records = self._consent_records[patient_id]

        consent_summary = {
            "patient_id": patient_id,
            "last_updated": max(
                record.granted_date
                or record.withdrawn_date
                or datetime.min.replace(tzinfo=timezone.utc)
                for record in consent_records
            ),
            "consents": [],
            "overall_status": "active",
            "expired_consents": [],
            "pending_consents": [],
            "compliance_issues": [],
        }

        now = datetime.now(timezone.utc)

        for record in consent_records:
            consent_info = {
                "consent_id": record.consent_id,
                "consent_type": record.consent_type,
                "status": record.status.value,
                "granted_date": (
                    record.granted_date.isoformat() if record.granted_date else None
                ),
                "expiry_date": (
                    record.expiry_date.isoformat() if record.expiry_date else None
                ),
                "is_expired": record.expiry_date and record.expiry_date < now,
                "days_until_expiry": (
                    (record.expiry_date - now).days if record.expiry_date else None
                ),
            }

            consent_summary["consents"].append(consent_info)

            # Track expired and pending consents
            if consent_info["is_expired"]:
                consent_summary["expired_consents"].append(record.consent_type)

            if record.status == ConsentStatus.PENDING:
                consent_summary["pending_consents"].append(record.consent_type)

        # Check compliance
        compliance_issues = await self._check_consent_compliance(patient_id)
        consent_summary["compliance_issues"] = compliance_issues

        if compliance_issues:
            consent_summary["overall_status"] = "compliance_issues"
        elif consent_summary["expired_consents"]:
            consent_summary["overall_status"] = "expired_consents"
        elif consent_summary["pending_consents"]:
            consent_summary["overall_status"] = "pending_consents"

        return consent_summary

    def _find_consent_record(
        self, patient_id: str, consent_type: str
    ) -> Optional[ConsentRecord]:
        """Find specific consent record for patient."""
        if patient_id not in self._consent_records:
            return None

        for record in self._consent_records[patient_id]:
            if record.consent_type == consent_type:
                return record

        return None

    def _calculate_expiry_date(self, consent_type: str) -> datetime:
        """Calculate consent expiry date based on type and regulations."""
        base_date = datetime.now(timezone.utc)

        # Consent expiry periods based on type and regulations
        expiry_periods = {
            "treatment_consent": timedelta(days=365),  # 1 year
            "data_collection_consent": timedelta(days=365),
            "research_participation": timedelta(days=730),  # 2 years for research
            "data_sharing": timedelta(days=365),
            "marketing_communications": timedelta(days=730),
            "hipaa_authorization": timedelta(days=365),
            "privacy_notice": timedelta(days=1095),  # 3 years
        }

        period = expiry_periods.get(
            consent_type, timedelta(days=self.config.consent_expiry_days)
        )
        return base_date + period

    async def _check_consent_compliance(self, patient_id: str) -> List[str]:
        """Check consent compliance for patient."""
        warnings = []

        if patient_id not in self._consent_records:
            return ["No consent records found"]

        # Required consents for BCI treatment
        required_consents = [
            "treatment_consent",
            "data_collection_consent",
            "hipaa_authorization",
            "privacy_notice",
        ]

        current_consents = {
            record.consent_type: record for record in self._consent_records[patient_id]
        }
        now = datetime.now(timezone.utc)

        for required_consent in required_consents:
            if required_consent not in current_consents:
                warnings.append(f"Missing required consent: {required_consent}")
            else:
                record = current_consents[required_consent]

                if record.status != ConsentStatus.APPROVED:
                    warnings.append(
                        f"Required consent not approved: {required_consent}"
                    )

                if record.expiry_date and record.expiry_date < now:
                    warnings.append(f"Required consent expired: {required_consent}")

                # Warn about upcoming expirations (30 days)
                if record.expiry_date and (record.expiry_date - now).days < 30:
                    warnings.append(f"Consent expiring soon: {required_consent}")

        return warnings

    async def _assess_withdrawal_impact(
        self, patient_id: str, consent_type: str
    ) -> Dict[str, Any]:
        """Assess impact of consent withdrawal on patient care."""
        impact = {
            "affects_treatment": False,
            "affected_services": [],
            "required_actions": [],
        }

        # Map consent types to affected services
        service_dependencies = {
            "treatment_consent": [
                "bci_sessions",
                "clinical_assessments",
                "care_coordination",
            ],
            "data_collection_consent": [
                "progress_tracking",
                "outcome_measurement",
                "analytics",
            ],
            "research_participation": ["research_studies", "data_export"],
            "data_sharing": ["care_coordination", "provider_communication"],
        }

        affected_services = service_dependencies.get(consent_type, [])

        if affected_services:
            impact["affects_treatment"] = True
            impact["affected_services"] = affected_services

            # Generate required actions
            if "bci_sessions" in affected_services:
                impact["required_actions"].append("Suspend active BCI sessions")
                impact["required_actions"].append(
                    "Notify care team of treatment interruption"
                )

            if "data_collection_consent" in consent_type:
                impact["required_actions"].append("Stop non-essential data collection")
                impact["required_actions"].append("Review data retention policies")

        return impact

    async def _log_consent_validation(
        self, patient_id: str, usage_type: str, validated: bool
    ):
        """Log consent validation for audit trail."""
        audit_entry = {
            "timestamp": datetime.now(timezone.utc),
            "patient_id": patient_id,
            "action": "consent_validation",
            "usage_type": usage_type,
            "validation_result": validated,
            "user_id": "system",
        }

        logger.info(f"Consent validation: {audit_entry}")

    def _load_consent_templates(self) -> Dict[str, Any]:
        """Load consent form templates."""
        # In production, these would be loaded from database or files
        return {
            "treatment_consent": {
                "text": "I consent to BCI treatment and understand the risks and benefits.",
                "required": True,
                "category": "treatment",
            },
            "data_collection_consent": {
                "text": "I consent to the collection and processing of my neural data for treatment purposes.",
                "required": True,
                "category": "data",
            },
            "research_participation": {
                "text": "I consent to participate in research studies using my anonymized data.",
                "required": False,
                "category": "research",
            },
            "data_sharing": {
                "text": "I consent to sharing my data with my care team and approved providers.",
                "required": False,
                "category": "sharing",
            },
            "marketing_communications": {
                "text": "I consent to receive marketing communications about related services.",
                "required": False,
                "category": "marketing",
            },
            "hipaa_authorization": {
                "text": "I acknowledge receipt of the HIPAA Privacy Notice and authorize use of my health information.",
                "required": True,
                "category": "privacy",
            },
            "privacy_notice": {
                "text": "I acknowledge that I have received and understand the Privacy Notice.",
                "required": True,
                "category": "privacy",
            },
        }
