"""Data exchange service for clinical integration."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from uuid import uuid4

from ..types import ClinicalConfig
from .emr_connector import EMRConnector
from .fhir_client import FHIRClient

logger = logging.getLogger(__name__)


class DataExchangeService:
    """Orchestrates data exchange between NeuraScale and external systems.

    Manages bi-directional data flow, transformation, synchronization,
    and ensures data integrity across clinical systems.
    """

    def __init__(self, config: ClinicalConfig):
        """Initialize data exchange service."""
        self.config = config

        # Initialize connectors
        self.emr_connector = EMRConnector(config)
        self.fhir_client = FHIRClient(config)

        # Exchange configurations
        self.exchange_rules = self._load_exchange_rules()
        self.sync_schedules = self._load_sync_schedules()
        self.data_quality_rules = self._load_data_quality_rules()

        # Exchange history and monitoring
        self._exchange_history: List[Dict[str, Any]] = []
        self._active_exchanges: Dict[str, Dict[str, Any]] = {}

        logger.info("Data exchange service initialized")

    async def initiate_patient_data_exchange(
        self, patient_id: str, exchange_config: dict
    ) -> str:
        """Initiate comprehensive patient data exchange.

        Args:
            patient_id: Patient identifier
            exchange_config: Exchange configuration

        Returns:
            Exchange operation ID
        """
        exchange_id = str(uuid4())

        try:
            exchange_operation = {
                "exchange_id": exchange_id,
                "patient_id": patient_id,
                "started_at": datetime.now(timezone.utc),
                "status": "in_progress",
                "type": exchange_config.get("type", "bidirectional"),
                "source_systems": exchange_config.get("source_systems", []),
                "target_systems": exchange_config.get("target_systems", []),
                "data_types": exchange_config.get("data_types", []),
                "operations": [],
                "errors": [],
                "warnings": [],
                "metrics": {
                    "records_processed": 0,
                    "records_created": 0,
                    "records_updated": 0,
                    "data_quality_issues": 0,
                },
            }

            self._active_exchanges[exchange_id] = exchange_operation

            # Execute exchange operations
            if exchange_operation["type"] in ["pull", "bidirectional"]:
                await self._execute_data_pull(exchange_id, exchange_config)

            if exchange_operation["type"] in ["push", "bidirectional"]:
                await self._execute_data_push(exchange_id, exchange_config)

            # Finalize exchange
            await self._finalize_exchange(exchange_id)

            logger.info(f"Patient data exchange initiated: {exchange_id}")

            return exchange_id

        except Exception as e:
            logger.error(f"Failed to initiate patient data exchange: {e}")
            if exchange_id in self._active_exchanges:
                self._active_exchanges[exchange_id]["status"] = "failed"
                self._active_exchanges[exchange_id]["error"] = str(e)
            raise

    async def sync_session_data(
        self, session_id: str, sync_targets: List[str]
    ) -> Dict[str, Any]:
        """Synchronize BCI session data to external systems.

        Args:
            session_id: BCI session identifier
            sync_targets: List of target systems

        Returns:
            Synchronization result
        """
        try:
            sync_result = {
                "session_id": session_id,
                "sync_id": str(uuid4()),
                "started_at": datetime.now(timezone.utc),
                "targets": sync_targets,
                "success": False,
                "sync_results": {},
                "errors": [],
                "warnings": [],
            }

            # Get session data (would normally fetch from database)
            session_data = await self._get_session_data(session_id)

            if not session_data:
                sync_result["errors"].append("Session data not found")
                return sync_result

            # Sync to each target system
            for target in sync_targets:
                try:
                    if target.startswith("emr_"):
                        # Sync to EMR system
                        emr_system = target.replace("emr_", "")
                        result = await self.emr_connector.push_session_data(
                            emr_system, session_data["patient_id"], session_data
                        )
                        sync_result["sync_results"][target] = result

                    elif target.startswith("fhir_"):
                        # Sync to FHIR server
                        fhir_server = target.replace("fhir_", "")
                        result = await self._sync_session_to_fhir(
                            fhir_server, session_data
                        )
                        sync_result["sync_results"][target] = result

                    else:
                        sync_result["warnings"].append(
                            f"Unknown target system: {target}"
                        )

                except Exception as e:
                    sync_result["errors"].append(f"Sync to {target} failed: {str(e)}")

            # Check overall success
            successful_syncs = sum(
                1
                for result in sync_result["sync_results"].values()
                if result.get("success", False)
            )
            sync_result["success"] = (
                successful_syncs > 0 and len(sync_result["errors"]) == 0
            )

            sync_result["completed_at"] = datetime.now(timezone.utc)

            # Log sync operation
            self._exchange_history.append(
                {
                    "timestamp": datetime.now(timezone.utc),
                    "operation": "session_sync",
                    "session_id": session_id,
                    "result": sync_result,
                }
            )

            logger.info(
                f"Session data sync completed: {session_id}, "
                f"targets: {len(sync_targets)}, success: {sync_result['success']}"
            )

            return sync_result

        except Exception as e:
            logger.error(f"Session data sync failed: {e}")
            return {
                "session_id": session_id,
                "success": False,
                "error": str(e),
            }

    async def validate_data_quality(self, data: dict, data_type: str) -> Dict[str, Any]:
        """Validate data quality before exchange.

        Args:
            data: Data to validate
            data_type: Type of data being validated

        Returns:
            Data quality assessment
        """
        try:
            quality_assessment = self._initialize_quality_assessment(data_type)
            rules = self.data_quality_rules.get(data_type, [])

            if not rules:
                return self._handle_missing_rules(quality_assessment, data_type)

            # Apply quality rules and calculate results
            passed_rules = await self._apply_quality_rules(
                quality_assessment, rules, data
            )

            # Calculate final quality metrics
            self._calculate_quality_metrics(
                quality_assessment, passed_rules, len(rules)
            )

            logger.info(
                f"Data quality validation completed: {data_type}, "
                f"quality: {quality_assessment['overall_quality']}, "
                f"score: {quality_assessment['quality_score']:.2f}"
            )

            return quality_assessment

        except Exception as e:
            logger.error(f"Data quality validation failed: {e}")
            return {
                "data_type": data_type,
                "overall_quality": "error",
                "error": str(e),
            }

    def _initialize_quality_assessment(self, data_type: str) -> Dict[str, Any]:
        """Initialize quality assessment structure."""
        return {
            "data_type": data_type,
            "validation_timestamp": datetime.now(timezone.utc),
            "overall_quality": "unknown",
            "quality_score": 0.0,
            "issues": [],
            "warnings": [],
            "recommendations": [],
            "passed_rules": [],
            "failed_rules": [],
        }

    def _handle_missing_rules(
        self, quality_assessment: Dict[str, Any], data_type: str
    ) -> Dict[str, Any]:
        """Handle case where no quality rules are defined."""
        quality_assessment["warnings"].append(
            f"No quality rules defined for {data_type}"
        )
        quality_assessment["overall_quality"] = "unknown"
        return quality_assessment

    async def _apply_quality_rules(
        self, quality_assessment: Dict[str, Any], rules: list, data: dict
    ) -> int:
        """Apply all quality rules and return count of passed rules."""
        passed_rules = 0

        for rule in rules:
            rule_result = await self._apply_quality_rule(rule, data)

            if rule_result["passed"]:
                passed_rules += 1
                quality_assessment["passed_rules"].append(rule["name"])
            else:
                quality_assessment["failed_rules"].append(rule["name"])
                quality_assessment["issues"].extend(rule_result.get("issues", []))

            if rule_result.get("warnings"):
                quality_assessment["warnings"].extend(rule_result["warnings"])

            if rule_result.get("recommendations"):
                quality_assessment["recommendations"].extend(
                    rule_result["recommendations"]
                )

        return passed_rules

    def _calculate_quality_metrics(
        self, quality_assessment: Dict[str, Any], passed_rules: int, total_rules: int
    ):
        """Calculate quality score and overall quality level."""
        # Calculate quality score
        quality_assessment["quality_score"] = (
            passed_rules / total_rules if total_rules > 0 else 0.0
        )

        # Determine overall quality level
        score = quality_assessment["quality_score"]
        if score >= 0.9:
            quality_assessment["overall_quality"] = "excellent"
        elif score >= 0.8:
            quality_assessment["overall_quality"] = "good"
        elif score >= 0.6:
            quality_assessment["overall_quality"] = "acceptable"
        elif score >= 0.4:
            quality_assessment["overall_quality"] = "poor"
        else:
            quality_assessment["overall_quality"] = "unacceptable"

    async def schedule_automated_sync(self, patient_id: str, sync_config: dict) -> str:
        """Schedule automated data synchronization.

        Args:
            patient_id: Patient identifier
            sync_config: Synchronization configuration

        Returns:
            Scheduled sync ID
        """
        try:
            schedule_id = str(uuid4())

            scheduled_sync = {
                "schedule_id": schedule_id,
                "patient_id": patient_id,
                "created_at": datetime.now(timezone.utc),
                "sync_frequency": sync_config.get("frequency", "daily"),
                "sync_time": sync_config.get("time", "02:00"),
                "target_systems": sync_config.get("targets", []),
                "data_types": sync_config.get("data_types", []),
                "enabled": True,
                "last_sync": None,
                "next_sync": self._calculate_next_sync_time(sync_config),
                "sync_history": [],
            }

            # Store schedule
            self.sync_schedules[schedule_id] = scheduled_sync

            logger.info(
                f"Automated sync scheduled: {schedule_id} for patient {patient_id}"
            )

            return schedule_id

        except Exception as e:
            logger.error(f"Failed to schedule automated sync: {e}")
            raise

    async def get_exchange_status(self, exchange_id: str) -> Dict[str, Any]:
        """Get status of data exchange operation.

        Args:
            exchange_id: Exchange operation identifier

        Returns:
            Exchange status information
        """
        try:
            # Check active exchanges first
            if exchange_id in self._active_exchanges:
                exchange = self._active_exchanges[exchange_id]

                status_info = {
                    "exchange_id": exchange_id,
                    "status": exchange["status"],
                    "patient_id": exchange["patient_id"],
                    "type": exchange["type"],
                    "started_at": exchange["started_at"],
                    "progress": self._calculate_exchange_progress(exchange),
                    "metrics": exchange["metrics"],
                    "errors": exchange["errors"],
                    "warnings": exchange["warnings"],
                }

                if exchange["status"] in ["completed", "failed"]:
                    status_info["completed_at"] = exchange.get("completed_at")
                    status_info["duration"] = (
                        exchange.get("completed_at", datetime.now(timezone.utc))
                        - exchange["started_at"]
                    ).total_seconds()

                return status_info

            # Check exchange history
            historical_exchange = next(
                (
                    record
                    for record in self._exchange_history
                    if record.get("exchange_id") == exchange_id
                ),
                None,
            )

            if historical_exchange:
                return {
                    "exchange_id": exchange_id,
                    "status": "completed",
                    "found_in": "history",
                    "record": historical_exchange,
                }

            return {
                "exchange_id": exchange_id,
                "status": "not_found",
                "error": "Exchange operation not found",
            }

        except Exception as e:
            logger.error(f"Failed to get exchange status: {e}")
            return {
                "exchange_id": exchange_id,
                "status": "error",
                "error": str(e),
            }

    async def _execute_data_pull(self, exchange_id: str, config: dict):
        """Execute data pull operations."""
        exchange = self._active_exchanges[exchange_id]

        for source_system in config.get("source_systems", []):
            try:
                if source_system.startswith("emr_"):
                    # Pull from EMR system
                    emr_system = source_system.replace("emr_", "")
                    result = await self.emr_connector.fetch_patient_data(
                        emr_system, exchange["patient_id"], config.get("data_types")
                    )

                    if result["success"]:
                        # Process and store pulled data
                        await self._process_pulled_data(exchange_id, result["data"])
                        exchange["metrics"]["records_processed"] += len(result["data"])
                    else:
                        exchange["errors"].extend(result["errors"])

                elif source_system.startswith("fhir_"):
                    # Pull from FHIR server
                    fhir_server = source_system.replace("fhir_", "")
                    result = await self._pull_from_fhir(
                        fhir_server, exchange["patient_id"], config
                    )

                    if result["success"]:
                        await self._process_pulled_data(exchange_id, result["data"])
                        exchange["metrics"]["records_processed"] += result[
                            "record_count"
                        ]
                    else:
                        exchange["errors"].extend(result["errors"])

                exchange["operations"].append(
                    {
                        "type": "pull",
                        "source": source_system,
                        "timestamp": datetime.now(timezone.utc),
                        "success": len(exchange["errors"]) == 0,
                    }
                )

            except Exception as e:
                exchange["errors"].append(f"Pull from {source_system} failed: {str(e)}")

    async def _execute_data_push(self, exchange_id: str, config: dict):
        """Execute data push operations."""
        exchange = self._active_exchanges[exchange_id]

        # Get patient data to push
        patient_data = await self._get_patient_data_for_push(
            exchange["patient_id"], config.get("data_types", [])
        )

        for target_system in config.get("target_systems", []):
            try:
                if target_system.startswith("emr_"):
                    # Push to EMR system
                    emr_system = target_system.replace("emr_", "")

                    # Push each data type
                    for data_type, data in patient_data.items():
                        result = await self.emr_connector.push_session_data(
                            emr_system, exchange["patient_id"], {data_type: data}
                        )

                        if result["success"]:
                            exchange["metrics"]["records_updated"] += 1
                        else:
                            exchange["errors"].append(f"Push to {emr_system} failed")

                elif target_system.startswith("fhir_"):
                    # Push to FHIR server
                    fhir_server = target_system.replace("fhir_", "")
                    result = await self._push_to_fhir(
                        fhir_server, exchange["patient_id"], patient_data
                    )

                    if result["success"]:
                        exchange["metrics"]["records_created"] += result[
                            "records_created"
                        ]
                    else:
                        exchange["errors"].extend(result["errors"])

                exchange["operations"].append(
                    {
                        "type": "push",
                        "target": target_system,
                        "timestamp": datetime.now(timezone.utc),
                        "success": len(exchange["errors"]) == 0,
                    }
                )

            except Exception as e:
                exchange["errors"].append(f"Push to {target_system} failed: {str(e)}")

    async def _sync_session_to_fhir(
        self, fhir_server: str, session_data: dict
    ) -> Dict[str, Any]:
        """Sync BCI session data to FHIR server."""
        try:
            sync_result = {
                "success": False,
                "fhir_server": fhir_server,
                "resources_created": [],
                "errors": [],
            }

            # Create Encounter resource
            encounter_result = await self.fhir_client.create_encounter_resource(
                fhir_server, session_data
            )
            sync_result["resources_created"].append(encounter_result)

            # Create Observation resources for session metrics
            if "session_metrics" in session_data:
                observation_result = await self.fhir_client.create_observation_resource(
                    fhir_server, session_data
                )
                sync_result["resources_created"].append(observation_result)

            sync_result["success"] = len(sync_result["errors"]) == 0

            return sync_result

        except Exception as e:
            return {
                "success": False,
                "fhir_server": fhir_server,
                "error": str(e),
            }

    async def _apply_quality_rule(self, rule: dict, data: dict) -> Dict[str, Any]:
        """Apply a single data quality rule."""
        rule_result = {
            "rule_name": rule["name"],
            "passed": True,
            "issues": [],
            "warnings": [],
            "recommendations": [],
        }

        rule_type = rule.get("type", "unknown")

        if rule_type == "required_field":
            self._validate_required_field(rule, data, rule_result)
        elif rule_type == "data_type":
            self._validate_data_type(rule, data, rule_result)
        elif rule_type == "value_range":
            self._validate_value_range(rule, data, rule_result)

        return rule_result

    def _validate_required_field(
        self, rule: dict, data: dict, rule_result: Dict[str, Any]
    ):
        """Validate required field rule."""
        field_path = rule["field_path"]
        if not self._get_nested_field(data, field_path):
            rule_result["passed"] = False
            rule_result["issues"].append(f"Required field missing: {field_path}")

    def _validate_data_type(self, rule: dict, data: dict, rule_result: Dict[str, Any]):
        """Validate data type rule."""
        field_path = rule["field_path"]
        expected_type = rule["expected_type"]
        field_value = self._get_nested_field(data, field_path)

        if field_value is not None:
            if expected_type == "string" and not isinstance(field_value, str):
                rule_result["passed"] = False
                rule_result["issues"].append(f"Field {field_path} should be string")
            elif expected_type == "number" and not isinstance(
                field_value, (int, float)
            ):
                rule_result["passed"] = False
                rule_result["issues"].append(f"Field {field_path} should be number")

    def _validate_value_range(
        self, rule: dict, data: dict, rule_result: Dict[str, Any]
    ):
        """Validate value range rule."""
        field_path = rule["field_path"]
        min_value = rule.get("min_value")
        max_value = rule.get("max_value")
        field_value = self._get_nested_field(data, field_path)

        if field_value is not None and isinstance(field_value, (int, float)):
            if min_value is not None and field_value < min_value:
                rule_result["passed"] = False
                rule_result["issues"].append(
                    f"Field {field_path} below minimum: {min_value}"
                )
            if max_value is not None and field_value > max_value:
                rule_result["passed"] = False
                rule_result["issues"].append(
                    f"Field {field_path} above maximum: {max_value}"
                )

    def _get_nested_field(self, data: dict, field_path: str) -> Any:
        """Get nested field value using dot notation."""
        try:
            value = data
            for key in field_path.split("."):
                value = value[key]
            return value
        except (KeyError, TypeError):
            return None

    async def _get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get BCI session data (mock implementation)."""
        # In production, this would fetch from database
        return {
            "session_id": session_id,
            "patient_id": "patient_123",
            "start_time": datetime.now(timezone.utc).isoformat(),
            "duration": 60,
            "performance_score": 85.5,
            "session_metrics": {
                "accuracy": 0.78,
                "reaction_time": 450,
                "signal_quality": 92.3,
            },
        }

    def _calculate_next_sync_time(self, sync_config: dict) -> datetime:
        """Calculate next synchronization time."""
        frequency = sync_config.get("frequency", "daily")
        sync_time = sync_config.get("time", "02:00")

        now = datetime.now(timezone.utc)

        if frequency == "hourly":
            return now + timedelta(hours=1)
        elif frequency == "daily":
            # Next occurrence of sync_time
            hour, minute = map(int, sync_time.split(":"))
            next_sync = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_sync <= now:
                next_sync += timedelta(days=1)
            return next_sync
        elif frequency == "weekly":
            # Next week same time
            return now + timedelta(weeks=1)
        else:
            return now + timedelta(days=1)

    def _load_exchange_rules(self) -> Dict[str, Any]:
        """Load data exchange rules."""
        return {
            "max_retry_attempts": 3,
            "retry_delay_seconds": 30,
            "batch_size": 100,
            "timeout_seconds": 300,
            "data_encryption_required": True,
        }

    def _load_sync_schedules(self) -> Dict[str, Dict[str, Any]]:
        """Load existing sync schedules."""
        return {}

    def _load_data_quality_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load data quality validation rules."""
        return {
            "patient_data": [
                {
                    "name": "patient_id_required",
                    "type": "required_field",
                    "field_path": "patient_id",
                },
                {
                    "name": "patient_id_format",
                    "type": "data_type",
                    "field_path": "patient_id",
                    "expected_type": "string",
                },
            ],
            "session_data": [
                {
                    "name": "session_id_required",
                    "type": "required_field",
                    "field_path": "session_id",
                },
                {
                    "name": "performance_score_range",
                    "type": "value_range",
                    "field_path": "performance_score",
                    "min_value": 0,
                    "max_value": 100,
                },
                {
                    "name": "duration_positive",
                    "type": "value_range",
                    "field_path": "duration",
                    "min_value": 1,
                },
            ],
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get data exchange statistics."""
        return {
            "total_exchanges": len(self._exchange_history),
            "active_exchanges": len(self._active_exchanges),
            "scheduled_syncs": len(self.sync_schedules),
            "average_exchange_duration": 45.2,  # Would calculate from actual data
            "data_quality_average": 0.87,
        }
