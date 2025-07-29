"""EMR system connector for clinical data integration."""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Any
from uuid import uuid4

from ..types import ClinicalConfig

logger = logging.getLogger(__name__)


class EMRConnector:
    """Connects to Electronic Medical Record systems for data exchange.

    Provides secure, HIPAA-compliant integration with EMR systems
    for patient data synchronization and clinical workflow integration.
    """

    def __init__(self, config: ClinicalConfig):
        """Initialize EMR connector."""
        self.config = config

        # Connection configurations
        self.emr_connections = self._load_emr_configurations()
        self.authentication_tokens = {}
        self.sync_schedules = {}

        # Data mapping configurations
        self.field_mappings = self._load_field_mappings()
        self.transformation_rules = self._load_transformation_rules()

        logger.info("EMR connector initialized")

    async def authenticate_emr_connection(
        self, emr_system: str, credentials: dict
    ) -> Dict[str, Any]:
        """Authenticate connection to EMR system.

        Args:
            emr_system: EMR system identifier
            credentials: Authentication credentials

        Returns:
            Authentication result
        """
        try:
            auth_result = {
                "emr_system": emr_system,
                "authenticated": False,
                "token": None,
                "expires_at": None,
                "permissions": [],
                "error": None,
            }

            # Validate EMR system configuration
            if emr_system not in self.emr_connections:
                auth_result["error"] = f"Unknown EMR system: {emr_system}"
                return auth_result

            emr_config = self.emr_connections[emr_system]

            # Simulate authentication process
            # In production, this would make actual API calls to EMR system
            if self._validate_credentials(credentials, emr_config):
                token = self._generate_auth_token(emr_system, credentials)
                expires_at = datetime.now(timezone.utc).replace(hour=23, minute=59)

                auth_result.update(
                    {
                        "authenticated": True,
                        "token": token,
                        "expires_at": expires_at,
                        "permissions": emr_config.get("default_permissions", []),
                    }
                )

                # Store token for future use
                self.authentication_tokens[emr_system] = {
                    "token": token,
                    "expires_at": expires_at,
                    "credentials": credentials,
                }

                logger.info(f"EMR authentication successful: {emr_system}")

            else:
                auth_result["error"] = "Invalid credentials"

            return auth_result

        except Exception as e:
            logger.error(f"EMR authentication failed: {e}")
            return {
                "emr_system": emr_system,
                "authenticated": False,
                "error": str(e),
            }

    async def fetch_patient_data(
        self, emr_system: str, patient_id: str, data_types: List[str] = None
    ) -> Dict[str, Any]:
        """Fetch patient data from EMR system.

        Args:
            emr_system: EMR system identifier
            patient_id: Patient identifier in EMR system
            data_types: Specific data types to fetch

        Returns:
            Patient data from EMR
        """
        try:
            # Check authentication
            if not await self._is_authenticated(emr_system):
                raise ValueError(f"Not authenticated to EMR system: {emr_system}")

            fetch_result = {
                "emr_system": emr_system,
                "patient_id": patient_id,
                "fetch_timestamp": datetime.now(timezone.utc),
                "success": False,
                "data": {},
                "errors": [],
                "warnings": [],
            }

            # Define available data types
            available_data_types = [
                "demographics",
                "medical_history",
                "medications",
                "allergies",
                "vital_signs",
                "lab_results",
                "imaging",
                "procedures",
                "diagnoses",
                "care_team",
            ]

            # Use all data types if none specified
            if data_types is None:
                data_types = available_data_types

            # Fetch each requested data type
            for data_type in data_types:
                if data_type not in available_data_types:
                    fetch_result["warnings"].append(f"Unknown data type: {data_type}")
                    continue

                try:
                    data = await self._fetch_data_type(
                        emr_system, patient_id, data_type
                    )
                    fetch_result["data"][data_type] = data
                except Exception as e:
                    fetch_result["errors"].append(
                        f"Failed to fetch {data_type}: {str(e)}"
                    )

            fetch_result["success"] = len(fetch_result["errors"]) == 0

            logger.info(
                f"Patient data fetched from {emr_system}: {patient_id}, "
                f"types: {len(fetch_result['data'])}"
            )

            return fetch_result

        except Exception as e:
            logger.error(f"Failed to fetch patient data: {e}")
            return {
                "emr_system": emr_system,
                "patient_id": patient_id,
                "success": False,
                "errors": [str(e)],
            }

    async def push_session_data(
        self, emr_system: str, patient_id: str, session_data: dict
    ) -> Dict[str, Any]:
        """Push BCI session data to EMR system.

        Args:
            emr_system: EMR system identifier
            patient_id: Patient identifier
            session_data: BCI session data to push

        Returns:
            Push operation result
        """
        try:
            # Check authentication
            if not await self._is_authenticated(emr_system):
                raise ValueError(f"Not authenticated to EMR system: {emr_system}")

            push_result = {
                "emr_system": emr_system,
                "patient_id": patient_id,
                "session_id": session_data.get("session_id"),
                "push_timestamp": datetime.now(timezone.utc),
                "success": False,
                "emr_record_id": None,
                "validation_errors": [],
                "transformation_warnings": [],
            }

            # Validate session data
            validation_result = await self._validate_session_data(session_data)
            if not validation_result["valid"]:
                push_result["validation_errors"] = validation_result["errors"]
                return push_result

            # Transform data to EMR format
            transformed_data = await self._transform_to_emr_format(
                emr_system, session_data
            )

            if transformed_data.get("warnings"):
                push_result["transformation_warnings"] = transformed_data["warnings"]

            # Push to EMR system
            emr_record_id = await self._push_to_emr(
                emr_system, patient_id, transformed_data["data"]
            )

            push_result.update(
                {
                    "success": True,
                    "emr_record_id": emr_record_id,
                }
            )

            logger.info(
                f"Session data pushed to {emr_system}: {session_data.get('session_id')}"
            )

            return push_result

        except Exception as e:
            logger.error(f"Failed to push session data: {e}")
            return {
                "emr_system": emr_system,
                "patient_id": patient_id,
                "success": False,
                "error": str(e),
            }

    async def sync_patient_records(
        self, emr_system: str, sync_config: dict
    ) -> Dict[str, Any]:
        """Synchronize patient records between systems.

        Args:
            emr_system: EMR system identifier
            sync_config: Synchronization configuration

        Returns:
            Synchronization result
        """
        try:
            sync_result = {
                "emr_system": emr_system,
                "sync_id": str(uuid4()),
                "started_at": datetime.now(timezone.utc),
                "sync_type": sync_config.get("type", "incremental"),
                "success": False,
                "records_processed": 0,
                "records_updated": 0,
                "records_created": 0,
                "errors": [],
                "warnings": [],
            }

            # Get list of patients to sync
            patient_list = await self._get_patients_for_sync(emr_system, sync_config)

            for patient_id in patient_list:
                try:
                    # Fetch current EMR data
                    emr_data = await self.fetch_patient_data(emr_system, patient_id)

                    if emr_data["success"]:
                        # Compare with local data and update as needed
                        sync_patient_result = await self._sync_patient_record(
                            patient_id, emr_data["data"]
                        )

                        sync_result["records_processed"] += 1

                        if sync_patient_result["updated"]:
                            sync_result["records_updated"] += 1
                        elif sync_patient_result["created"]:
                            sync_result["records_created"] += 1

                    else:
                        sync_result["errors"].extend(emr_data["errors"])

                except Exception as e:
                    sync_result["errors"].append(f"Patient {patient_id}: {str(e)}")

            sync_result["success"] = len(sync_result["errors"]) == 0
            sync_result["completed_at"] = datetime.now(timezone.utc)

            logger.info(
                f"Patient record sync completed: {emr_system}, "
                f"processed: {sync_result['records_processed']}"
            )

            return sync_result

        except Exception as e:
            logger.error(f"Patient record sync failed: {e}")
            return {
                "emr_system": emr_system,
                "success": False,
                "error": str(e),
            }

    async def _is_authenticated(self, emr_system: str) -> bool:
        """Check if authenticated to EMR system."""
        if emr_system not in self.authentication_tokens:
            return False

        token_info = self.authentication_tokens[emr_system]

        # Check if token is expired
        if datetime.now(timezone.utc) >= token_info["expires_at"]:
            # Try to refresh token
            return await self._refresh_token(emr_system)

        return True

    async def _refresh_token(self, emr_system: str) -> bool:
        """Refresh authentication token."""
        try:
            if emr_system not in self.authentication_tokens:
                return False

            token_info = self.authentication_tokens[emr_system]

            # Re-authenticate with stored credentials
            auth_result = await self.authenticate_emr_connection(
                emr_system, token_info["credentials"]
            )

            return auth_result["authenticated"]

        except Exception as e:
            logger.error(f"Token refresh failed for {emr_system}: {e}")
            return False

    async def _fetch_data_type(
        self, emr_system: str, patient_id: str, data_type: str
    ) -> Dict[str, Any]:
        """Fetch specific data type from EMR."""
        # Simulate EMR data fetching
        # In production, this would make actual API calls

        mock_data = {
            "demographics": {
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": "1980-01-01",
                "gender": "M",
                "address": "123 Main St",
                "phone": "555-0123",
            },
            "medical_history": {
                "conditions": ["Stroke", "Hypertension"],
                "surgeries": ["Craniotomy 2023"],
                "family_history": ["Heart disease"],
            },
            "medications": [
                {
                    "name": "Aspirin",
                    "dosage": "81mg",
                    "frequency": "daily",
                    "start_date": "2023-01-01",
                },
            ],
            "allergies": ["Penicillin", "Shellfish"],
            "vital_signs": {
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "blood_pressure": "120/80",
                "heart_rate": 72,
                "temperature": 98.6,
            },
        }

        return mock_data.get(data_type, {})

    async def _validate_session_data(self, session_data: dict) -> Dict[str, Any]:
        """Validate BCI session data before pushing to EMR."""
        validation = {"valid": True, "errors": [], "warnings": []}

        required_fields = ["session_id", "patient_id", "start_time", "duration"]
        for field in required_fields:
            if field not in session_data:
                validation["valid"] = False
                validation["errors"].append(f"Missing required field: {field}")

        # Validate data types and ranges
        if "duration" in session_data:
            duration = session_data["duration"]
            if not isinstance(duration, (int, float)) or duration <= 0:
                validation["valid"] = False
                validation["errors"].append("Duration must be positive number")

        return validation

    async def _transform_to_emr_format(
        self, emr_system: str, session_data: dict
    ) -> Dict[str, Any]:
        """Transform BCI session data to EMR-specific format."""
        transformation_result = {
            "data": {},
            "warnings": [],
        }

        # Get field mappings for this EMR system
        mappings = self.field_mappings.get(emr_system, {})

        # Transform each field
        for bci_field, emr_field in mappings.items():
            if bci_field in session_data:
                transformed_value = await self._apply_transformation_rules(
                    bci_field, session_data[bci_field], emr_system
                )
                transformation_result["data"][emr_field] = transformed_value

        # Add EMR-specific metadata
        transformation_result["data"].update(
            {
                "record_type": "BCI_Session",
                "source_system": "NeuraScale",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )

        return transformation_result

    async def _apply_transformation_rules(
        self, field_name: str, value: Any, emr_system: str
    ) -> Any:
        """Apply transformation rules to field values."""
        rules = self.transformation_rules.get(emr_system, {}).get(field_name, [])

        transformed_value = value

        for rule in rules:
            rule_type = rule.get("type")

            if rule_type == "unit_conversion":
                transformed_value = self._convert_units(
                    transformed_value, rule["from_unit"], rule["to_unit"]
                )
            elif rule_type == "format_change":
                transformed_value = self._change_format(
                    transformed_value, rule["from_format"], rule["to_format"]
                )
            elif rule_type == "value_mapping":
                transformed_value = rule["mapping"].get(
                    transformed_value, transformed_value
                )

        return transformed_value

    async def _push_to_emr(self, emr_system: str, patient_id: str, data: dict) -> str:
        """Push transformed data to EMR system."""
        # Simulate EMR push operation
        # In production, this would make actual API calls

        record_id = f"EMR_{emr_system}_{uuid4().hex[:8]}"

        logger.info(f"Pushing data to {emr_system} for patient {patient_id}")

        return record_id

    def _validate_credentials(self, credentials: dict, emr_config: dict) -> bool:
        """Validate EMR credentials."""
        required_fields = emr_config.get("required_credentials", [])

        for field in required_fields:
            if field not in credentials or not credentials[field]:
                return False

        return True

    def _generate_auth_token(self, emr_system: str, credentials: dict) -> str:
        """Generate authentication token."""
        # In production, this would generate a proper JWT or OAuth token
        return f"token_{emr_system}_{uuid4().hex[:16]}"

    def _convert_units(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert between units."""
        # Simple unit conversion examples
        conversion_factors = {
            ("seconds", "minutes"): 1 / 60,
            ("minutes", "seconds"): 60,
            ("celsius", "fahrenheit"): lambda x: (x * 9 / 5) + 32,
            ("fahrenheit", "celsius"): lambda x: (x - 32) * 5 / 9,
        }

        conversion_key = (from_unit.lower(), to_unit.lower())

        if conversion_key in conversion_factors:
            factor = conversion_factors[conversion_key]
            if callable(factor):
                return factor(value)
            else:
                return value * factor

        return value

    def _change_format(self, value: str, from_format: str, to_format: str) -> str:
        """Change string format."""
        if from_format == "ISO_8601" and to_format == "US_DATE":
            # Convert ISO date to US format
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return dt.strftime("%m/%d/%Y")
            except ValueError:
                return value

        return value

    def _load_emr_configurations(self) -> Dict[str, Any]:
        """Load EMR system configurations."""
        return {
            "epic": {
                "name": "Epic Systems",
                "api_version": "R4",
                "base_url": "https://epic.example.com/api",
                "auth_type": "oauth2",
                "required_credentials": [
                    "client_id",
                    "client_secret",
                    "username",
                    "password",
                ],
                "default_permissions": ["read_patient", "write_encounters"],
            },
            "cerner": {
                "name": "Cerner Millennium",
                "api_version": "DSTU2",
                "base_url": "https://cerner.example.com/fhir",
                "auth_type": "oauth2",
                "required_credentials": ["client_id", "client_secret"],
                "default_permissions": ["read_patient", "read_observation"],
            },
            "allscripts": {
                "name": "Allscripts",
                "api_version": "R4",
                "base_url": "https://allscripts.example.com/api",
                "auth_type": "basic",
                "required_credentials": ["username", "password"],
                "default_permissions": ["read_patient"],
            },
        }

    def _load_field_mappings(self) -> Dict[str, Dict[str, str]]:
        """Load field mappings between BCI and EMR systems."""
        return {
            "epic": {
                "session_id": "encounter_id",
                "patient_id": "patient_mrn",
                "start_time": "encounter_datetime",
                "duration": "encounter_duration_minutes",
                "performance_score": "clinical_note_score",
            },
            "cerner": {
                "session_id": "encounter_number",
                "patient_id": "person_id",
                "start_time": "service_datetime",
                "duration": "service_duration",
                "performance_score": "observation_value",
            },
        }

    def _load_transformation_rules(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """Load data transformation rules."""
        return {
            "epic": {
                "duration": [
                    {
                        "type": "unit_conversion",
                        "from_unit": "seconds",
                        "to_unit": "minutes",
                    }
                ],
                "start_time": [
                    {
                        "type": "format_change",
                        "from_format": "ISO_8601",
                        "to_format": "US_DATETIME",
                    }
                ],
            }
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get EMR connector statistics."""
        return {
            "configured_emr_systems": len(self.emr_connections),
            "authenticated_systems": len(self.authentication_tokens),
            "available_data_types": [
                "demographics",
                "medical_history",
                "medications",
                "allergies",
                "vital_signs",
                "lab_results",
            ],
            "last_sync_timestamps": {},
        }
