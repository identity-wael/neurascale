"""FHIR client for standards-based healthcare data exchange."""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from uuid import uuid4

from ..types import ClinicalConfig

logger = logging.getLogger(__name__)


class FHIRClient:
    """FHIR (Fast Healthcare Interoperability Resources) client.

    Provides standards-compliant healthcare data exchange using FHIR R4
    specification for interoperability with healthcare systems.
    """

    def __init__(self, config: ClinicalConfig):
        """Initialize FHIR client."""
        self.config = config

        # FHIR server configurations
        self.fhir_servers = self._load_fhir_server_configs()
        self.resource_templates = self._load_fhir_resource_templates()

        # Authentication and security
        self.auth_tokens = {}
        self.capability_statements = {}

        logger.info("FHIR client initialized")

    async def get_capability_statement(self, server_id: str) -> Dict[str, Any]:
        """Get FHIR server capability statement.

        Args:
            server_id: FHIR server identifier

        Returns:
            Capability statement from server
        """
        try:
            if server_id not in self.fhir_servers:
                raise ValueError(f"Unknown FHIR server: {server_id}")

            # Simulate capability statement retrieval
            capability_statement = {
                "resourceType": "CapabilityStatement",
                "id": f"capability-{server_id}",
                "url": f"{self.fhir_servers[server_id]['base_url']}/metadata",
                "version": "R4",
                "name": f"{server_id.upper()}CapabilityStatement",
                "status": "active",
                "date": datetime.now(timezone.utc).isoformat(),
                "publisher": "NeuraScale",
                "fhirVersion": "4.0.1",
                "format": ["json", "xml"],
                "rest": [
                    {
                        "mode": "server",
                        "resource": [
                            {
                                "type": "Patient",
                                "interaction": [
                                    {"code": "read"},
                                    {"code": "search-type"},
                                    {"code": "create"},
                                    {"code": "update"},
                                ],
                                "searchParam": [
                                    {"name": "identifier", "type": "token"},
                                    {"name": "name", "type": "string"},
                                    {"name": "birthdate", "type": "date"},
                                ],
                            },
                            {
                                "type": "Observation",
                                "interaction": [
                                    {"code": "read"},
                                    {"code": "search-type"},
                                    {"code": "create"},
                                ],
                                "searchParam": [
                                    {"name": "patient", "type": "reference"},
                                    {"name": "category", "type": "token"},
                                    {"name": "code", "type": "token"},
                                    {"name": "date", "type": "date"},
                                ],
                            },
                            {
                                "type": "Encounter",
                                "interaction": [
                                    {"code": "read"},
                                    {"code": "search-type"},
                                    {"code": "create"},
                                ],
                            },
                        ],
                    }
                ],
            }

            # Cache capability statement
            self.capability_statements[server_id] = capability_statement

            logger.info(f"Capability statement retrieved for {server_id}")

            return capability_statement

        except Exception as e:
            logger.error(f"Failed to get capability statement for {server_id}: {e}")
            raise

    async def create_patient_resource(
        self, server_id: str, patient_data: dict
    ) -> Dict[str, Any]:
        """Create FHIR Patient resource.

        Args:
            server_id: FHIR server identifier
            patient_data: Patient information

        Returns:
            Created Patient resource
        """
        try:
            # Build FHIR Patient resource
            patient_resource = {
                "resourceType": "Patient",
                "id": str(uuid4()),
                "meta": {
                    "versionId": "1",
                    "lastUpdated": datetime.now(timezone.utc).isoformat(),
                    "profile": ["http://hl7.org/fhir/StructureDefinition/Patient"],
                },
                "identifier": [
                    {
                        "use": "usual",
                        "type": {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                                    "code": "MR",
                                    "display": "Medical record number",
                                }
                            ]
                        },
                        "system": "https://neurascale.com/patient-id",
                        "value": patient_data.get("patient_id", str(uuid4())),
                    }
                ],
                "active": True,
                "name": [
                    {
                        "use": "official",
                        "family": patient_data.get("last_name", ""),
                        "given": [patient_data.get("first_name", "")],
                    }
                ],
                "gender": self._map_gender_to_fhir(patient_data.get("gender", "")),
                "birthDate": patient_data.get("date_of_birth", ""),
            }

            # Add contact information if available
            if patient_data.get("phone") or patient_data.get("email"):
                patient_resource["telecom"] = []

                if patient_data.get("phone"):
                    patient_resource["telecom"].append(
                        {
                            "system": "phone",
                            "value": patient_data["phone"],
                            "use": "home",
                        }
                    )

                if patient_data.get("email"):
                    patient_resource["telecom"].append(
                        {
                            "system": "email",
                            "value": patient_data["email"],
                            "use": "home",
                        }
                    )

            # Add address if available
            if patient_data.get("address"):
                patient_resource["address"] = [
                    {
                        "use": "home",
                        "type": "both",
                        "text": patient_data["address"],
                    }
                ]

            # Validate resource
            validation_result = self._validate_fhir_resource(patient_resource)
            if not validation_result["valid"]:
                raise ValueError(
                    f"Invalid Patient resource: {validation_result['errors']}"
                )

            # Simulate resource creation
            creation_result = await self._create_fhir_resource(
                server_id, patient_resource
            )

            logger.info(f"Patient resource created: {patient_resource['id']}")

            return creation_result

        except Exception as e:
            logger.error(f"Failed to create Patient resource: {e}")
            raise

    async def create_observation_resource(
        self, server_id: str, observation_data: dict
    ) -> Dict[str, Any]:
        """Create FHIR Observation resource for BCI session data.

        Args:
            server_id: FHIR server identifier
            observation_data: BCI observation data

        Returns:
            Created Observation resource
        """
        try:
            # Build FHIR Observation resource
            observation_resource = {
                "resourceType": "Observation",
                "id": str(uuid4()),
                "meta": {
                    "versionId": "1",
                    "lastUpdated": datetime.now(timezone.utc).isoformat(),
                    "profile": ["http://hl7.org/fhir/StructureDefinition/Observation"],
                },
                "status": "final",
                "category": [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                "code": "procedure",
                                "display": "Procedure",
                            }
                        ]
                    }
                ],
                "code": {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "182836005",
                            "display": "Review of neurological system",
                        }
                    ],
                    "text": "BCI Session Performance",
                },
                "subject": {
                    "reference": f"Patient/{observation_data.get('patient_id')}",
                    "display": "Patient",
                },
                "effectiveDateTime": observation_data.get(
                    "session_start", datetime.now(timezone.utc).isoformat()
                ),
                "issued": datetime.now(timezone.utc).isoformat(),
                "performer": [
                    {
                        "reference": f"Practitioner/{observation_data.get('provider_id', 'unknown')}",
                        "display": "BCI Therapist",
                    }
                ],
            }

            # Add value based on observation type
            if "performance_score" in observation_data:
                observation_resource["valueQuantity"] = {
                    "value": observation_data["performance_score"],
                    "unit": "percent",
                    "system": "http://unitsofmeasure.org",
                    "code": "%",
                }

            # Add components for multiple measurements
            if "session_metrics" in observation_data:
                observation_resource["component"] = []
                metrics = observation_data["session_metrics"]

                for metric_name, metric_value in metrics.items():
                    component = {
                        "code": {
                            "coding": [
                                {
                                    "system": "https://neurascale.com/fhir/CodeSystem/bci-metrics",
                                    "code": metric_name,
                                    "display": metric_name.replace("_", " ").title(),
                                }
                            ]
                        },
                        "valueQuantity": {
                            "value": metric_value,
                            "system": "http://unitsofmeasure.org",
                        },
                    }
                    observation_resource["component"].append(component)

            # Add session context
            if "session_id" in observation_data:
                observation_resource["encounter"] = {
                    "reference": f"Encounter/{observation_data['session_id']}",
                    "display": "BCI Session",
                }

            # Validate resource
            validation_result = self._validate_fhir_resource(observation_resource)
            if not validation_result["valid"]:
                raise ValueError(
                    f"Invalid Observation resource: {validation_result['errors']}"
                )

            # Create resource
            creation_result = await self._create_fhir_resource(
                server_id, observation_resource
            )

            logger.info(f"Observation resource created: {observation_resource['id']}")

            return creation_result

        except Exception as e:
            logger.error(f"Failed to create Observation resource: {e}")
            raise

    async def create_encounter_resource(
        self, server_id: str, encounter_data: dict
    ) -> Dict[str, Any]:
        """Create FHIR Encounter resource for BCI session.

        Args:
            server_id: FHIR server identifier
            encounter_data: BCI session encounter data

        Returns:
            Created Encounter resource
        """
        try:
            encounter_resource = {
                "resourceType": "Encounter",
                "id": encounter_data.get("session_id", str(uuid4())),
                "meta": {
                    "versionId": "1",
                    "lastUpdated": datetime.now(timezone.utc).isoformat(),
                },
                "status": self._map_session_status_to_fhir(
                    encounter_data.get("status", "planned")
                ),
                "class": {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                    "code": "AMB",
                    "display": "ambulatory",
                },
                "type": [
                    {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": "410620009",
                                "display": "Well child visit",
                            }
                        ],
                        "text": "BCI Therapy Session",
                    }
                ],
                "subject": {
                    "reference": f"Patient/{encounter_data.get('patient_id')}",
                    "display": "Patient",
                },
                "participant": [
                    {
                        "type": [
                            {
                                "coding": [
                                    {
                                        "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                                        "code": "PPRF",
                                        "display": "primary performer",
                                    }
                                ]
                            }
                        ],
                        "individual": {
                            "reference": f"Practitioner/{encounter_data.get('provider_id', 'unknown')}",
                            "display": "BCI Therapist",
                        },
                    }
                ],
                "period": {
                    "start": encounter_data.get(
                        "start_time", datetime.now(timezone.utc).isoformat()
                    ),
                },
                "serviceProvider": {
                    "reference": "Organization/neurascale",
                    "display": "NeuraScale BCI Center",
                },
            }

            # Add end time if session is completed
            if encounter_data.get("end_time"):
                encounter_resource["period"]["end"] = encounter_data["end_time"]

            # Add location if specified
            if encounter_data.get("location"):
                encounter_resource["location"] = [
                    {
                        "location": {
                            "reference": f"Location/{encounter_data['location']}",
                            "display": encounter_data.get("location_name", "BCI Lab"),
                        }
                    }
                ]

            # Validate and create resource
            validation_result = self._validate_fhir_resource(encounter_resource)
            if not validation_result["valid"]:
                raise ValueError(
                    f"Invalid Encounter resource: {validation_result['errors']}"
                )

            creation_result = await self._create_fhir_resource(
                server_id, encounter_resource
            )

            logger.info(f"Encounter resource created: {encounter_resource['id']}")

            return creation_result

        except Exception as e:
            logger.error(f"Failed to create Encounter resource: {e}")
            raise

    async def search_resources(
        self, server_id: str, resource_type: str, search_params: dict
    ) -> Dict[str, Any]:
        """Search for FHIR resources.

        Args:
            server_id: FHIR server identifier
            resource_type: Type of resource to search
            search_params: Search parameters

        Returns:
            Search results bundle
        """
        try:
            # Build search query
            search_url = f"{self.fhir_servers[server_id]['base_url']}/{resource_type}"

            # Simulate search operation
            search_results = {
                "resourceType": "Bundle",
                "id": str(uuid4()),
                "meta": {
                    "lastUpdated": datetime.now(timezone.utc).isoformat(),
                },
                "type": "searchset",
                "total": 0,
                "link": [
                    {
                        "relation": "self",
                        "url": search_url,
                    }
                ],
                "entry": [],
            }

            # Mock search results based on parameters
            if resource_type == "Patient" and "identifier" in search_params:
                # Return mock patient
                mock_patient = await self._get_mock_patient(search_params["identifier"])
                if mock_patient:
                    search_results["total"] = 1
                    search_results["entry"] = [
                        {
                            "fullUrl": f"{search_url}/{mock_patient['id']}",
                            "resource": mock_patient,
                            "search": {"mode": "match"},
                        }
                    ]

            logger.info(
                f"Resource search completed: {resource_type}, found: {search_results['total']}"
            )

            return search_results

        except Exception as e:
            logger.error(f"Resource search failed: {e}")
            raise

    def _map_gender_to_fhir(self, gender: str) -> str:
        """Map gender value to FHIR standard."""
        gender_mapping = {
            "M": "male",
            "F": "female",
            "O": "other",
            "U": "unknown",
            "male": "male",
            "female": "female",
            "other": "other",
            "unknown": "unknown",
        }
        return gender_mapping.get(gender.upper(), "unknown")

    def _map_session_status_to_fhir(self, status: str) -> str:
        """Map BCI session status to FHIR Encounter status."""
        status_mapping = {
            "scheduled": "planned",
            "in_progress": "in-progress",
            "completed": "finished",
            "cancelled": "cancelled",
            "paused": "onhold",
        }
        return status_mapping.get(status.lower(), "planned")

    def _validate_fhir_resource(self, resource: dict) -> Dict[str, Any]:
        """Validate FHIR resource structure."""
        validation = {"valid": True, "errors": [], "warnings": []}

        # Check basic required fields
        self._validate_basic_fields(resource, validation)

        # Resource-specific validation
        resource_type = resource.get("resourceType")
        self._validate_resource_type_specific(resource, resource_type, validation)

        return validation

    def _validate_basic_fields(self, resource: dict, validation: Dict[str, Any]):
        """Validate basic FHIR resource fields."""
        if "resourceType" not in resource:
            validation["valid"] = False
            validation["errors"].append("Missing resourceType")

        if "id" not in resource:
            validation["warnings"].append("Missing resource id")

    def _validate_resource_type_specific(
        self, resource: dict, resource_type: str, validation: Dict[str, Any]
    ):
        """Validate resource type specific requirements."""
        if resource_type == "Patient":
            self._validate_patient_resource(resource, validation)
        elif resource_type == "Observation":
            self._validate_observation_resource(resource, validation)
        elif resource_type == "Encounter":
            self._validate_encounter_resource(resource, validation)

    def _validate_patient_resource(self, resource: dict, validation: Dict[str, Any]):
        """Validate Patient resource fields."""
        if "identifier" not in resource:
            validation["warnings"].append("Patient should have identifier")

    def _validate_observation_resource(
        self, resource: dict, validation: Dict[str, Any]
    ):
        """Validate Observation resource fields."""
        required_fields = ["status", "code", "subject"]
        for field in required_fields:
            if field not in resource:
                validation["valid"] = False
                validation["errors"].append(
                    f"Observation missing required field: {field}"
                )

    def _validate_encounter_resource(self, resource: dict, validation: Dict[str, Any]):
        """Validate Encounter resource fields."""
        required_fields = ["status", "class", "subject"]
        for field in required_fields:
            if field not in resource:
                validation["valid"] = False
                validation["errors"].append(
                    f"Encounter missing required field: {field}"
                )

    async def _create_fhir_resource(
        self, server_id: str, resource: dict
    ) -> Dict[str, Any]:
        """Create FHIR resource on server."""
        # Simulate resource creation
        creation_result = {
            "resourceType": resource["resourceType"],
            "id": resource["id"],
            "meta": {
                "versionId": "1",
                "lastUpdated": datetime.now(timezone.utc).isoformat(),
                "source": "NeuraScale BCI System",
            },
            "created": True,
            "location": f"{self.fhir_servers[server_id]['base_url']}/{resource['resourceType']}/{resource['id']}",
        }

        return creation_result

    async def _get_mock_patient(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Get mock patient data for testing."""
        # Return mock patient data
        return {
            "resourceType": "Patient",
            "id": identifier,
            "identifier": [
                {
                    "use": "usual",
                    "system": "https://neurascale.com/patient-id",
                    "value": identifier,
                }
            ],
            "name": [
                {
                    "use": "official",
                    "family": "TestPatient",
                    "given": ["John"],
                }
            ],
            "gender": "male",
            "birthDate": "1980-01-01",
        }

    def _load_fhir_server_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load FHIR server configurations."""
        return {
            "local": {
                "name": "Local FHIR Server",
                "base_url": "http://localhost:8080/fhir",
                "version": "R4",
                "auth_type": "none",
            },
            "hapi": {
                "name": "HAPI FHIR Server",
                "base_url": "http://hapi.fhir.org/baseR4",
                "version": "R4",
                "auth_type": "none",
            },
            "azure": {
                "name": "Azure FHIR Service",
                "base_url": "https://neurascale-fhir.azurehealthcareapis.com",
                "version": "R4",
                "auth_type": "oauth2",
            },
        }

    def _load_fhir_resource_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load FHIR resource templates."""
        return {
            "Patient": {
                "required_fields": ["resourceType", "identifier"],
                "optional_fields": [
                    "name",
                    "gender",
                    "birthDate",
                    "telecom",
                    "address",
                ],
            },
            "Observation": {
                "required_fields": ["resourceType", "status", "code", "subject"],
                "optional_fields": [
                    "category",
                    "effectiveDateTime",
                    "valueQuantity",
                    "component",
                ],
            },
            "Encounter": {
                "required_fields": ["resourceType", "status", "class", "subject"],
                "optional_fields": ["type", "participant", "period", "location"],
            },
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get FHIR client statistics."""
        return {
            "configured_servers": len(self.fhir_servers),
            "supported_resources": list(self.resource_templates.keys()),
            "fhir_version": "R4",
            "last_operations": {},
        }
