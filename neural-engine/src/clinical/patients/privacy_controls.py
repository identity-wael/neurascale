"""Patient privacy controls and data minimization."""

import logging
from datetime import datetime, timezone
from typing import Dict, Any
from enum import Enum

from ..types import PrivacySettings, ClinicalConfig

logger = logging.getLogger(__name__)


class DataSharingScope(Enum):
    """Data sharing scope levels."""

    NONE = "none"
    CARE_TEAM_ONLY = "care_team_only"
    INSTITUTION = "institution"
    RESEARCH_NETWORK = "research_network"
    PUBLIC_HEALTH = "public_health"


class DataRetentionLevel(Enum):
    """Data retention levels."""

    MINIMUM = "minimum"  # Legal minimum only
    STANDARD = "standard"  # Standard clinical retention
    EXTENDED = "extended"  # Extended for research/quality


class PrivacyControls:
    """Manages patient privacy preferences and data minimization.

    Implements granular privacy controls, data sharing preferences,
    and automated data minimization policies.
    """

    def __init__(self, config: ClinicalConfig):
        """Initialize privacy controls."""
        self.config = config

        # Privacy settings storage (would be database in production)
        self._privacy_settings: Dict[str, PrivacySettings] = {}

        # Data policies and rules
        self.data_policies = self._load_data_policies()

        logger.info("Privacy controls initialized")

    async def set_data_sharing_preferences(
        self, patient_id: str, preferences: dict
    ) -> PrivacySettings:
        """Set patient data sharing preferences.

        Args:
            patient_id: Patient identifier
            preferences: Data sharing preferences

        Returns:
            Updated PrivacySettings
        """
        # Get existing settings or create new
        current_settings = self._privacy_settings.get(patient_id, PrivacySettings())

        # Update data sharing preferences
        current_settings.data_sharing_consent = preferences.get(
            "data_sharing_consent", False
        )
        current_settings.research_participation = preferences.get(
            "research_participation", False
        )
        current_settings.marketing_communications = preferences.get(
            "marketing_communications", False
        )

        # Set data sharing scope
        sharing_scope = preferences.get("sharing_scope", "care_team_only")
        if sharing_scope not in [scope.value for scope in DataSharingScope]:
            sharing_scope = "care_team_only"

        # Set retention preference
        retention_preference = preferences.get("retention_preference", "standard")
        if retention_preference not in [level.value for level in DataRetentionLevel]:
            retention_preference = "standard"

        current_settings.data_retention_preference = retention_preference

        # Set anonymization level
        anonymization_level = preferences.get("anonymization_level", "full")
        if anonymization_level not in ["none", "partial", "full"]:
            anonymization_level = "full"

        current_settings.anonymization_level = anonymization_level

        # Store updated settings
        self._privacy_settings[patient_id] = current_settings

        # Apply data policies based on preferences
        await self._apply_data_policies(patient_id, current_settings)

        logger.info(f"Data sharing preferences updated for patient {patient_id}")

        return current_settings

    async def manage_family_access_permissions(
        self, patient_id: str, family_access: dict
    ) -> Dict[str, Any]:
        """Manage family member access permissions.

        Args:
            patient_id: Patient identifier
            family_access: Family access configuration

        Returns:
            Access configuration result
        """
        privacy_settings = self._privacy_settings.get(patient_id, PrivacySettings())

        # Update family access setting
        privacy_settings.family_access_allowed = family_access.get("allowed", False)

        # Configure specific family member permissions
        family_permissions = {
            "patient_id": patient_id,
            "family_access_enabled": privacy_settings.family_access_allowed,
            "authorized_contacts": [],
            "permission_levels": {},
            "access_restrictions": {},
        }

        if privacy_settings.family_access_allowed:
            # Process authorized family members
            authorized_contacts = family_access.get("authorized_contacts", [])

            for contact in authorized_contacts:
                contact_info = {
                    "contact_id": contact.get("id", ""),
                    "name": contact.get("name", ""),
                    "relationship": contact.get("relationship", ""),
                    "contact_phone": contact.get("phone", ""),
                    "contact_email": contact.get("email", ""),
                    "verified": contact.get("verified", False),
                    "permissions": contact.get("permissions", []),
                }

                family_permissions["authorized_contacts"].append(contact_info)

                # Set permission level for this contact
                permission_level = contact.get("permission_level", "basic")
                family_permissions["permission_levels"][
                    contact_info["contact_id"]
                ] = permission_level

                # Set access restrictions
                restrictions = contact.get("restrictions", {})
                family_permissions["access_restrictions"][
                    contact_info["contact_id"]
                ] = {
                    "access_hours": restrictions.get("access_hours", "24/7"),
                    "data_types": restrictions.get("allowed_data_types", ["general"]),
                    "emergency_only": restrictions.get("emergency_only", False),
                }

        # Store updated privacy settings
        self._privacy_settings[patient_id] = privacy_settings

        logger.info(f"Family access permissions updated for patient {patient_id}")

        return family_permissions

    async def configure_research_participation(
        self, patient_id: str, research_consent: dict
    ) -> Dict[str, Any]:
        """Configure research participation preferences.

        Args:
            patient_id: Patient identifier
            research_consent: Research participation configuration

        Returns:
            Research participation configuration
        """
        privacy_settings = self._privacy_settings.get(patient_id, PrivacySettings())

        # Update research participation
        privacy_settings.research_participation = research_consent.get(
            "participate", False
        )

        research_config = {
            "patient_id": patient_id,
            "participation_enabled": privacy_settings.research_participation,
            "research_types": [],
            "data_sharing_level": "none",
            "contact_preferences": {},
            "restrictions": {},
        }

        if privacy_settings.research_participation:
            # Configure research participation details
            research_config.update(
                {
                    "research_types": research_consent.get(
                        "research_types", ["clinical_studies"]
                    ),
                    "data_sharing_level": research_consent.get(
                        "data_sharing_level", "anonymized"
                    ),
                    "contact_preferences": {
                        "contact_for_studies": research_consent.get(
                            "contact_for_studies", True
                        ),
                        "preferred_contact_method": research_consent.get(
                            "contact_method", "email"
                        ),
                        "contact_frequency": research_consent.get(
                            "contact_frequency", "as_needed"
                        ),
                    },
                    "restrictions": {
                        "exclude_sensitive_data": research_consent.get(
                            "exclude_sensitive", True
                        ),
                        "geographic_restrictions": research_consent.get(
                            "geographic_restrictions", []
                        ),
                        "institutional_restrictions": research_consent.get(
                            "institutional_restrictions", []
                        ),
                    },
                }
            )

            # Set data anonymization level based on research participation
            if research_consent.get("data_sharing_level") == "identifiable":
                privacy_settings.anonymization_level = "partial"
            elif research_consent.get("data_sharing_level") == "anonymized":
                privacy_settings.anonymization_level = "full"

        # Store updated settings
        self._privacy_settings[patient_id] = privacy_settings

        logger.info(f"Research participation configured for patient {patient_id}")

        return research_config

    async def apply_data_minimization_rules(self, patient_id: str) -> Dict[str, Any]:
        """Apply data minimization rules based on patient preferences.

        Args:
            patient_id: Patient identifier

        Returns:
            Data policy configuration
        """
        privacy_settings = self._privacy_settings.get(patient_id, PrivacySettings())

        if not privacy_settings:
            # Apply default minimization rules
            privacy_settings = PrivacySettings()

        # Determine data collection scope
        collection_scope = self._determine_collection_scope(privacy_settings)

        # Determine retention period
        retention_period = self._determine_retention_period(privacy_settings)

        # Determine anonymization requirements
        anonymization_rules = self._determine_anonymization_rules(privacy_settings)

        # Create data policy
        data_policy = {
            "patient_id": patient_id,
            "policy_version": "1.0",
            "effective_date": datetime.now(timezone.utc),
            "collection_scope": collection_scope,
            "retention_period": retention_period,
            "anonymization_rules": anonymization_rules,
            "sharing_restrictions": self._determine_sharing_restrictions(
                privacy_settings
            ),
            "deletion_schedule": self._calculate_deletion_schedule(privacy_settings),
            "access_controls": self._determine_access_controls(privacy_settings),
        }

        # Apply policy rules
        await self._enforce_data_policy(patient_id, data_policy)

        logger.info(f"Data minimization rules applied for patient {patient_id}")

        return data_policy

    async def get_privacy_settings(self, patient_id: str) -> Dict[str, Any]:
        """Get comprehensive privacy settings for patient.

        Args:
            patient_id: Patient identifier

        Returns:
            Privacy settings summary
        """
        privacy_settings = self._privacy_settings.get(patient_id, PrivacySettings())

        # Convert to dictionary format
        settings_dict = {
            "patient_id": patient_id,
            "data_sharing_consent": privacy_settings.data_sharing_consent,
            "research_participation": privacy_settings.research_participation,
            "family_access_allowed": privacy_settings.family_access_allowed,
            "marketing_communications": privacy_settings.marketing_communications,
            "data_retention_preference": privacy_settings.data_retention_preference,
            "anonymization_level": privacy_settings.anonymization_level,
            "last_updated": datetime.now(timezone.utc),
            "privacy_score": self._calculate_privacy_score(privacy_settings),
            "compliance_status": await self._check_privacy_compliance(patient_id),
        }

        return settings_dict

    async def update_marketing_preferences(
        self, patient_id: str, marketing_prefs: dict
    ) -> bool:
        """Update marketing communication preferences.

        Args:
            patient_id: Patient identifier
            marketing_prefs: Marketing preferences

        Returns:
            Success status
        """
        privacy_settings = self._privacy_settings.get(patient_id, PrivacySettings())

        # Update marketing preferences
        privacy_settings.marketing_communications = marketing_prefs.get(
            "enabled", False
        )

        # Store marketing-specific preferences
        marketing_config = {
            "enabled": privacy_settings.marketing_communications,
            "channels": marketing_prefs.get("channels", []),
            "frequency": marketing_prefs.get("frequency", "monthly"),
            "categories": marketing_prefs.get("categories", []),
            "opt_out_all": marketing_prefs.get("opt_out_all", False),
        }

        # Log marketing preferences configuration
        logger.info(
            f"Marketing preferences updated for patient {patient_id}: {marketing_config}"
        )

        self._privacy_settings[patient_id] = privacy_settings

        logger.info(f"Marketing preferences updated for patient {patient_id}")

        return True

    def _determine_collection_scope(self, settings: PrivacySettings) -> Dict[str, bool]:
        """Determine data collection scope based on preferences."""
        base_scope = {
            "clinical_data": True,  # Always required for treatment
            "neural_signals": True,  # Core BCI data
            "session_metadata": True,  # Required for safety
            "device_telemetry": True,  # Required for device management
        }

        # Optional data collection based on preferences
        optional_scope = {
            "detailed_analytics": settings.data_sharing_consent,
            "research_data": settings.research_participation,
            "quality_metrics": settings.data_sharing_consent,
            "usage_statistics": settings.marketing_communications,
        }

        return {**base_scope, **optional_scope}

    def _determine_retention_period(self, settings: PrivacySettings) -> Dict[str, int]:
        """Determine data retention periods based on preferences."""
        # Base retention periods (in days)
        if settings.data_retention_preference == "minimum":
            return {
                "clinical_data": 2555,  # 7 years (legal minimum)
                "neural_signals": 365,  # 1 year minimum
                "session_logs": 365,
                "audit_logs": 2555,
            }
        elif settings.data_retention_preference == "standard":
            return {
                "clinical_data": 3650,  # 10 years
                "neural_signals": 1825,  # 5 years
                "session_logs": 1095,  # 3 years
                "audit_logs": 2555,
            }
        else:  # extended
            return {
                "clinical_data": 7300,  # 20 years
                "neural_signals": 3650,  # 10 years
                "session_logs": 1825,  # 5 years
                "audit_logs": 2555,
            }

    def _determine_anonymization_rules(
        self, settings: PrivacySettings
    ) -> Dict[str, Any]:
        """Determine anonymization rules based on preferences."""
        if settings.anonymization_level == "none":
            return {
                "remove_identifiers": False,
                "pseudonymize": False,
                "aggregate_only": False,
                "k_anonymity": 1,
            }
        elif settings.anonymization_level == "partial":
            return {
                "remove_identifiers": True,
                "pseudonymize": True,
                "aggregate_only": False,
                "k_anonymity": 5,
                "remove_fields": ["name", "address", "phone", "email"],
            }
        else:  # full
            return {
                "remove_identifiers": True,
                "pseudonymize": True,
                "aggregate_only": True,
                "k_anonymity": 10,
                "remove_fields": ["name", "address", "phone", "email", "demographics"],
                "generalize_dates": True,
                "noise_injection": True,
            }

    def _determine_sharing_restrictions(
        self, settings: PrivacySettings
    ) -> Dict[str, Any]:
        """Determine data sharing restrictions."""
        restrictions = {
            "internal_sharing": True,  # Always allowed within care team
            "institutional_sharing": settings.data_sharing_consent,
            "research_sharing": settings.research_participation,
            "external_sharing": False,  # Generally prohibited
            "commercial_sharing": False,  # Always prohibited
            "international_sharing": settings.research_participation,
        }

        return restrictions

    def _calculate_deletion_schedule(self, settings: PrivacySettings) -> Dict[str, str]:
        """Calculate automatic deletion schedule."""
        retention_periods = self._determine_retention_period(settings)

        schedule = {}
        for data_type, days in retention_periods.items():
            deletion_date = datetime.now(timezone.utc).replace(
                year=datetime.now().year + (days // 365),
                month=datetime.now().month,
                day=datetime.now().day,
            )
            schedule[data_type] = deletion_date.isoformat()

        return schedule

    def _determine_access_controls(self, settings: PrivacySettings) -> Dict[str, Any]:
        """Determine access control requirements."""
        controls = {
            "require_audit": True,
            "minimum_necessary": True,
            "role_based_access": True,
            "family_access": settings.family_access_allowed,
            "patient_access": True,
            "research_access": settings.research_participation,
            "marketing_access": settings.marketing_communications,
        }

        return controls

    async def _enforce_data_policy(self, patient_id: str, policy: dict):
        """Enforce data policy rules."""
        # In production, this would:
        # 1. Configure database retention policies
        # 2. Set up automated deletion jobs
        # 3. Apply access control rules
        # 4. Configure anonymization pipelines

        logger.info(f"Data policy enforced for patient {patient_id}")

    def _calculate_privacy_score(self, settings: PrivacySettings) -> int:
        """Calculate privacy protection score (0-100)."""
        score = 0

        # Base score for having settings
        score += 20

        # Anonymization level
        if settings.anonymization_level == "full":
            score += 30
        elif settings.anonymization_level == "partial":
            score += 20

        # Data retention preference
        if settings.data_retention_preference == "minimum":
            score += 25
        elif settings.data_retention_preference == "standard":
            score += 15

        # Restrictive sharing preferences
        if not settings.data_sharing_consent:
            score += 10
        if not settings.research_participation:
            score += 5
        if not settings.marketing_communications:
            score += 5
        if not settings.family_access_allowed:
            score += 5

        return min(score, 100)

    async def _check_privacy_compliance(self, patient_id: str) -> Dict[str, Any]:
        """Check privacy compliance status."""
        compliance = {"compliant": True, "issues": [], "recommendations": []}

        settings = self._privacy_settings.get(patient_id)

        if not settings:
            compliance["compliant"] = False
            compliance["issues"].append("No privacy settings configured")
            compliance["recommendations"].append("Configure privacy preferences")

        # Add more compliance checks as needed

        return compliance

    def _load_data_policies(self) -> Dict[str, Any]:
        """Load data governance policies."""
        # In production, this would load from configuration files or database
        return {
            "hipaa_compliance": {
                "minimum_necessary": True,
                "audit_required": True,
                "breach_notification": True,
            },
            "gdpr_compliance": {
                "consent_required": True,
                "right_to_deletion": True,
                "data_portability": True,
            },
            "institutional_policies": {
                "retention_limits": True,
                "access_controls": True,
                "anonymization_required": True,
            },
        }
