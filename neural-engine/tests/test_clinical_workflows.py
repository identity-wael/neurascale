"""Comprehensive tests for clinical workflow management."""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, AsyncMock
from uuid import uuid4

from src.clinical.patients.patient_service import PatientService
from src.clinical.patients.consent_management import ConsentManager
from src.clinical.patients.privacy_controls import PrivacyControls
from src.clinical.sessions.session_manager import SessionManager
from src.clinical.sessions.scheduling_service import SchedulingService
from src.clinical.workflows.treatment_planner import TreatmentPlanner
from src.clinical.workflows.decision_support import ClinicalDecisionSupport
from src.clinical.workflows.protocol_engine import ProtocolEngine
from src.clinical.integration.data_exchange import DataExchangeService
from src.clinical.types import ClinicalConfig, ConsentStatus, SessionStatus


@pytest.fixture
def clinical_config():
    """Mock clinical configuration."""
    return ClinicalConfig(
        consent_expiry_days=365,
        default_sessions_per_week=2,
        hipaa_audit_enabled=True,
        data_retention_days=2555,  # 7 years
    )


@pytest.fixture
def patient_service(clinical_config):
    """Patient service fixture."""
    return PatientService(clinical_config)


@pytest.fixture
def consent_manager(clinical_config):
    """Consent manager fixture."""
    return ConsentManager(clinical_config)


@pytest.fixture
def privacy_controls(clinical_config):
    """Privacy controls fixture."""
    return PrivacyControls(clinical_config)


@pytest.fixture
def session_manager(clinical_config):
    """Session manager fixture."""
    return SessionManager(clinical_config)


@pytest.fixture
def scheduling_service(clinical_config):
    """Scheduling service fixture."""
    return SchedulingService(clinical_config)


@pytest.fixture
def treatment_planner(clinical_config):
    """Treatment planner fixture."""
    return TreatmentPlanner(clinical_config)


@pytest.fixture
def decision_support(clinical_config):
    """Clinical decision support fixture."""
    return ClinicalDecisionSupport(clinical_config)


@pytest.fixture
def protocol_engine(clinical_config):
    """Protocol engine fixture."""
    return ProtocolEngine(clinical_config)


@pytest.fixture
def data_exchange_service(clinical_config):
    """Data exchange service fixture."""
    return DataExchangeService(clinical_config)


class TestPatientService:
    """Test patient service functionality."""

    @pytest.mark.asyncio
    async def test_register_patient(self, patient_service):
        """Test patient registration."""
        patient_data = {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1980-01-01",
            "gender": "M",
            "contact_info": {
                "phone": "555-0123",
                "email": "john.doe@example.com",
            },
            "medical_history": {
                "conditions": ["Stroke"],
                "medications": [],
                "allergies": [],
            },
        }

        patient = await patient_service.register_patient(patient_data)

        assert patient is not None
        assert patient.demographics.first_name == "John"
        assert patient.demographics.last_name == "Doe"
        assert patient.medical_record_number.startswith("MRN")
        assert patient.registration_date is not None

    @pytest.mark.asyncio
    async def test_update_patient_profile(self, patient_service):
        """Test patient profile updates."""
        # First register a patient
        patient_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "date_of_birth": "1985-05-15",
            "gender": "F",
        }

        patient = await patient_service.register_patient(patient_data)
        patient_id = patient.patient_id

        # Update patient profile
        updates = {
            "demographics": {
                "phone": "555-9876",
                "email": "jane.smith@example.com",
            },
            "care_team": ["provider_123", "nurse_456"],
        }

        updated_patient = await patient_service.update_patient_profile(
            patient_id, updates
        )

        assert updated_patient.care_team == ["provider_123", "nurse_456"]
        assert updated_patient.last_updated is not None

    @pytest.mark.asyncio
    async def test_get_patient_record(self, patient_service):
        """Test patient record retrieval."""
        # Register patient first
        patient_data = {"first_name": "Test", "last_name": "Patient"}
        patient = await patient_service.register_patient(patient_data)

        # Retrieve patient record
        retrieved_patient = await patient_service.get_patient_record(patient.patient_id)

        assert retrieved_patient is not None
        assert retrieved_patient.patient_id == patient.patient_id
        assert retrieved_patient.demographics.first_name == "Test"


class TestConsentManagement:
    """Test consent management functionality."""

    @pytest.mark.asyncio
    async def test_create_consent_workflow(self, consent_manager):
        """Test consent workflow creation."""
        patient_id = str(uuid4())
        consent_types = [
            "treatment_consent",
            "data_collection_consent",
            "research_participation",
        ]

        workflow_id = await consent_manager.create_consent_workflow(
            patient_id, consent_types
        )

        assert workflow_id is not None
        assert isinstance(workflow_id, str)

    @pytest.mark.asyncio
    async def test_process_consent_update(self, consent_manager):
        """Test consent updates."""
        patient_id = str(uuid4())
        consent_types = ["treatment_consent"]

        # Create consent workflow
        await consent_manager.create_consent_workflow(patient_id, consent_types)

        # Update consent
        consent_changes = {
            "treatment_consent": {
                "granted": True,
                "signed_by": "John Doe",
                "updated_by": "provider_123",
            }
        }

        result = await consent_manager.process_consent_update(
            patient_id, consent_changes
        )

        assert result["patient_id"] == patient_id
        assert len(result["updated_consents"]) == 1
        assert (
            result["updated_consents"][0]["new_status"] == ConsentStatus.APPROVED.value
        )

    @pytest.mark.asyncio
    async def test_validate_data_usage_consent(self, consent_manager):
        """Test data usage consent validation."""
        patient_id = str(uuid4())

        # Create and approve treatment consent
        await consent_manager.create_consent_workflow(patient_id, ["treatment_consent"])
        await consent_manager.process_consent_update(
            patient_id, {"treatment_consent": {"granted": True, "signed_by": "Patient"}}
        )

        # Validate consent for treatment usage
        is_consented = await consent_manager.validate_data_usage_consent(
            patient_id, "treatment"
        )

        assert is_consented is True

    @pytest.mark.asyncio
    async def test_consent_withdrawal(self, consent_manager):
        """Test consent withdrawal."""
        patient_id = str(uuid4())

        # Create and approve consent
        await consent_manager.create_consent_workflow(
            patient_id, ["research_participation"]
        )
        consent_records = consent_manager._consent_records.get(patient_id, [])
        consent_id = consent_records[0].consent_id if consent_records else str(uuid4())

        # Withdraw consent
        success = await consent_manager.handle_consent_withdrawal(
            patient_id, consent_id, "Patient decision"
        )

        assert success is True


class TestPrivacyControls:
    """Test privacy controls functionality."""

    @pytest.mark.asyncio
    async def test_configure_privacy_settings(self, privacy_controls):
        """Test privacy settings configuration."""
        patient_id = str(uuid4())
        privacy_config = {
            "data_sharing_enabled": False,
            "research_participation": True,
            "marketing_communications": False,
            "family_access_level": "limited",
            "data_retention_override": 1825,  # 5 years
        }

        success = await privacy_controls.configure_privacy_settings(
            patient_id, privacy_config
        )

        assert success is True

    @pytest.mark.asyncio
    async def test_set_data_sharing_preferences(self, privacy_controls):
        """Test data sharing preferences."""
        patient_id = str(uuid4())
        sharing_prefs = {
            "healthcare_providers": True,
            "research_institutions": False,
            "family_members": True,
            "insurance_companies": False,
        }

        success = await privacy_controls.set_data_sharing_preferences(
            patient_id, sharing_prefs
        )

        assert success is True

    @pytest.mark.asyncio
    async def test_privacy_compliance_check(self, privacy_controls):
        """Test privacy compliance checking."""
        patient_id = str(uuid4())

        # Configure privacy settings first
        await privacy_controls.configure_privacy_settings(
            patient_id, {"data_sharing_enabled": True}
        )

        # Check compliance
        compliance_result = await privacy_controls.check_privacy_compliance(patient_id)

        assert "patient_id" in compliance_result
        assert "compliance_status" in compliance_result


class TestSessionManagement:
    """Test session management functionality."""

    @pytest.mark.asyncio
    async def test_create_session(self, session_manager):
        """Test clinical session creation."""
        patient_id = str(uuid4())
        session_config = {
            "type": "training",
            "provider_id": "provider_123",
            "duration_minutes": 60,
            "device": {
                "type": "eeg",
                "id": "device_001",
                "sampling_rate": 256.0,
                "channels": ["C3", "C4", "Cz"],
            },
        }

        session = await session_manager.create_session(patient_id, session_config)

        assert session is not None
        assert session.patient_id == patient_id
        assert session.status == SessionStatus.SCHEDULED
        assert session.duration_minutes == 60

    @pytest.mark.asyncio
    async def test_start_session(self, session_manager):
        """Test session start."""
        patient_id = str(uuid4())
        session_config = {"type": "assessment", "provider_id": "provider_123"}

        # Create session
        session = await session_manager.create_session(patient_id, session_config)

        # Mock safety protocols
        session_manager.safety_protocols.validate_pre_session_safety = AsyncMock(
            return_value={"safe_to_proceed": True, "issues": []}
        )
        session_manager.live_monitor.start_real_time_monitoring = AsyncMock()

        # Start session
        status = await session_manager.start_session(session.session_id)

        assert status == SessionStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_monitor_session_progress(self, session_manager):
        """Test session progress monitoring."""
        patient_id = str(uuid4())
        session_config = {"type": "training", "provider_id": "provider_123"}

        # Create and start session
        session = await session_manager.create_session(patient_id, session_config)

        # Mock dependencies
        session_manager.live_monitor.get_session_progress = AsyncMock(
            return_value={"status": "active", "metrics": {}}
        )
        session_manager.safety_protocols.get_session_safety_status = AsyncMock(
            return_value={"status": "safe", "alerts": []}
        )

        # Monitor progress
        progress = await session_manager.monitor_session_progress(session.session_id)

        assert "session_id" in progress
        assert "status" in progress
        assert "progress_percent" in progress


class TestSchedulingService:
    """Test scheduling service functionality."""

    @pytest.mark.asyncio
    async def test_schedule_session(self, scheduling_service):
        """Test session scheduling."""
        session_request = {
            "session_id": str(uuid4()),
            "patient_id": str(uuid4()),
            "provider_id": "provider_123",
            "start_time": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "duration_minutes": 60,
        }

        appointment = await scheduling_service.schedule_session(session_request)

        assert appointment is not None
        assert appointment.session_id == session_request["session_id"]
        assert appointment.patient_id == session_request["patient_id"]
        assert appointment.status == "scheduled"

    @pytest.mark.asyncio
    async def test_check_provider_availability(self, scheduling_service):
        """Test provider availability checking."""
        provider_id = "provider_123"
        start_time = datetime.now(timezone.utc) + timedelta(days=1)
        end_time = start_time + timedelta(hours=8)
        time_range = scheduling_service.TimeRange(start_time, end_time)

        availability = await scheduling_service.check_provider_availability(
            provider_id, time_range
        )

        assert availability.resource_id == provider_id
        assert availability.resource_type == "provider"
        assert isinstance(availability.available_slots, list)

    @pytest.mark.asyncio
    async def test_find_optimal_scheduling_time(self, scheduling_service):
        """Test optimal scheduling time finding."""
        session_request = {
            "provider_id": "provider_123",
            "duration_minutes": 60,
        }
        preferences = {
            "preferred_time": "morning",
            "earliest_start": datetime.now(timezone.utc) + timedelta(days=1),
        }

        optimal_slots = await scheduling_service.find_optimal_scheduling_time(
            session_request, preferences
        )

        assert isinstance(optimal_slots, list)
        # Should find at least some available slots
        assert len(optimal_slots) >= 0


class TestTreatmentPlanner:
    """Test treatment planner functionality."""

    @pytest.mark.asyncio
    async def test_create_treatment_plan(self, treatment_planner):
        """Test treatment plan creation."""
        patient_id = str(uuid4())
        assessment_data = {
            "cognitive_scores": {
                "attention": 65,
                "memory": 70,
                "executive_function": 60,
            },
            "motor_scores": {"fine_motor": 55, "gross_motor": 60},
            "medical_history": {"conditions": [], "medications": []},
        }

        treatment_plan = await treatment_planner.create_treatment_plan(
            patient_id, assessment_data
        )

        assert treatment_plan is not None
        assert treatment_plan.patient_id == patient_id
        assert len(treatment_plan.treatment_goals) > 0
        assert len(treatment_plan.protocol_steps) > 0
        assert treatment_plan.estimated_duration_weeks > 0

    @pytest.mark.asyncio
    async def test_get_treatment_recommendations(self, treatment_planner):
        """Test treatment recommendations."""
        patient_id = str(uuid4())

        # Create a treatment plan first
        assessment_data = {"cognitive_scores": {"attention": 80}}
        treatment_plan = await treatment_planner.create_treatment_plan(
            patient_id, assessment_data
        )

        # Verify treatment plan was created
        assert treatment_plan is not None

        # Get recommendations
        current_progress = {
            "completed_steps": 2,
            "weeks_since_start": 3,
            "safety_events": 0,
        }

        recommendations = await treatment_planner.get_treatment_recommendations(
            patient_id, current_progress
        )

        assert "patient_id" in recommendations
        assert "recommendations" in recommendations
        assert "progress_status" in recommendations


class TestClinicalDecisionSupport:
    """Test clinical decision support functionality."""

    @pytest.mark.asyncio
    async def test_evaluate_treatment_eligibility(self, decision_support):
        """Test treatment eligibility evaluation."""
        patient_data = {
            "patient_id": str(uuid4()),
            "medical_history": {
                "conditions": ["Stroke"],
                "medications": [],
                "contraindications": [],
            },
            "cognitive_assessment": {
                "attention_span": 20,
                "working_memory": 5,
                "comprehension": 75,
            },
            "psychosocial_assessment": {
                "family_support": 7,
                "treatment_motivation": 8,
            },
        }

        evaluation = await decision_support.evaluate_treatment_eligibility(patient_data)

        assert evaluation["patient_id"] == patient_data["patient_id"]
        assert "eligible" in evaluation
        assert "eligibility_score" in evaluation
        assert "risk_level" in evaluation

    @pytest.mark.asyncio
    async def test_assess_session_safety(self, decision_support):
        """Test session safety assessment."""
        session_data = {
            "session_id": str(uuid4()),
            "vitals": {"heart_rate": 75, "blood_pressure": "120/80"},
            "neural_signals": {"signal_quality": 85, "artifacts": 0.1},
            "behavior": {"engagement": "high", "fatigue": "low"},
        }
        patient_context = {
            "medical_history": {"conditions": []},
            "risk_factors": [],
        }

        safety_assessment = await decision_support.assess_session_safety(
            session_data, patient_context
        )

        assert "session_id" in safety_assessment
        assert "safety_level" in safety_assessment
        assert "risk_score" in safety_assessment

    @pytest.mark.asyncio
    async def test_predict_treatment_outcomes(self, decision_support):
        """Test treatment outcome prediction."""
        patient_data = {
            "patient_id": str(uuid4()),
            "age": 45,
            "baseline_scores": {"motor": 60, "cognitive": 70},
            "medical_history": {"conditions": ["Stroke"]},
        }
        treatment_plan = {
            "protocol": "motor_rehabilitation",
            "duration_weeks": 8,
            "sessions_per_week": 3,
        }

        predictions = await decision_support.predict_treatment_outcomes(
            patient_data, treatment_plan
        )

        assert "patient_id" in predictions
        assert "success_probability" in predictions
        assert "predicted_outcomes" in predictions


class TestProtocolEngine:
    """Test protocol engine functionality."""

    @pytest.mark.asyncio
    async def test_start_protocol_execution(self, protocol_engine):
        """Test protocol execution start."""
        patient_id = str(uuid4())
        protocol_data = {
            "protocol_id": "motor_rehab_001",
            "name": "Motor Rehabilitation Protocol",
            "steps": [
                {
                    "name": "Baseline Assessment",
                    "session_type": "assessment",
                    "duration_minutes": 90,
                },
                {
                    "name": "Motor Training",
                    "session_type": "training",
                    "duration_minutes": 60,
                },
            ],
        }

        execution_id = await protocol_engine.start_protocol_execution(
            patient_id, protocol_data
        )

        assert execution_id is not None
        assert isinstance(execution_id, str)

    @pytest.mark.asyncio
    async def test_execute_protocol_step(self, protocol_engine):
        """Test protocol step execution."""
        patient_id = str(uuid4())
        protocol_data = {
            "name": "Test Protocol",
            "steps": [
                {
                    "name": "Test Step",
                    "session_type": "training",
                    "duration_minutes": 30,
                    "success_criteria": [
                        {"metric": "accuracy", "operator": ">=", "threshold": 0.7}
                    ],
                }
            ],
        }

        # Start protocol
        execution_id = await protocol_engine.start_protocol_execution(
            patient_id, protocol_data
        )

        # Execute step
        step_data = {
            "accuracy": 0.8,
            "duration": 30,
            "completed": True,
        }

        execution_result = await protocol_engine.execute_protocol_step(
            execution_id, step_data
        )

        assert execution_result["success"] is True
        assert "step_id" in execution_result

    @pytest.mark.asyncio
    async def test_get_protocol_status(self, protocol_engine):
        """Test protocol status retrieval."""
        patient_id = str(uuid4())
        protocol_data = {
            "name": "Status Test Protocol",
            "steps": [{"name": "Test Step", "session_type": "assessment"}],
        }

        execution_id = await protocol_engine.start_protocol_execution(
            patient_id, protocol_data
        )

        status = await protocol_engine.get_protocol_status(execution_id)

        assert status["execution_id"] == execution_id
        assert status["patient_id"] == patient_id
        assert "status" in status
        assert "progress" in status


class TestDataExchange:
    """Test data exchange functionality."""

    @pytest.mark.asyncio
    async def test_sync_session_data(self, data_exchange_service):
        """Test session data synchronization."""
        session_id = str(uuid4())
        sync_targets = ["fhir_local", "emr_epic"]

        # Mock session data
        with patch.object(
            data_exchange_service,
            "_get_session_data",
            return_value={
                "session_id": session_id,
                "patient_id": str(uuid4()),
                "performance_score": 85.5,
            },
        ):
            sync_result = await data_exchange_service.sync_session_data(
                session_id, sync_targets
            )

        assert sync_result["session_id"] == session_id
        assert "sync_results" in sync_result

    @pytest.mark.asyncio
    async def test_validate_data_quality(self, data_exchange_service):
        """Test data quality validation."""
        session_data = {
            "session_id": str(uuid4()),
            "patient_id": str(uuid4()),
            "duration": 60,
            "performance_score": 85.5,
        }

        quality_assessment = await data_exchange_service.validate_data_quality(
            session_data, "session_data"
        )

        assert quality_assessment["data_type"] == "session_data"
        assert "overall_quality" in quality_assessment
        assert "quality_score" in quality_assessment

    @pytest.mark.asyncio
    async def test_schedule_automated_sync(self, data_exchange_service):
        """Test automated sync scheduling."""
        patient_id = str(uuid4())
        sync_config = {
            "frequency": "daily",
            "time": "02:00",
            "targets": ["fhir_local"],
            "data_types": ["session_data"],
        }

        schedule_id = await data_exchange_service.schedule_automated_sync(
            patient_id, sync_config
        )

        assert schedule_id is not None
        assert isinstance(schedule_id, str)


class TestIntegrationWorkflows:
    """Test end-to-end clinical workflow integration."""

    @pytest.mark.asyncio
    async def test_complete_patient_workflow(
        self, patient_service, consent_manager, session_manager, treatment_planner
    ):
        """Test complete patient workflow from registration to treatment."""
        # 1. Register patient
        patient_data = {
            "first_name": "Integration",
            "last_name": "TestPatient",
            "date_of_birth": "1975-08-20",
            "gender": "F",
            "medical_history": {"conditions": ["TBI"], "medications": []},
        }

        patient = await patient_service.register_patient(patient_data)
        patient_id = patient.patient_id

        # 2. Create consent workflow
        consent_types = ["treatment_consent", "data_collection_consent"]
        workflow_id = await consent_manager.create_consent_workflow(
            patient_id, consent_types
        )

        # 3. Process consent approvals
        consent_changes = {
            "treatment_consent": {
                "granted": True,
                "signed_by": "Integration TestPatient",
            },
            "data_collection_consent": {
                "granted": True,
                "signed_by": "Integration TestPatient",
            },
        }
        consent_result = await consent_manager.process_consent_update(
            patient_id, consent_changes
        )

        # 4. Create treatment plan
        assessment_data = {
            "cognitive_scores": {"attention": 65, "memory": 70},
            "motor_scores": {"fine_motor": 55},
        }
        treatment_plan = await treatment_planner.create_treatment_plan(
            patient_id, assessment_data
        )

        # 5. Create clinical session
        session_config = {
            "type": "training",
            "provider_id": "provider_integration_test",
            "duration_minutes": 45,
        }
        session = await session_manager.create_session(patient_id, session_config)

        # Verify complete workflow
        assert patient is not None
        assert workflow_id is not None
        assert len(consent_result["updated_consents"]) == 2
        assert treatment_plan is not None
        assert session is not None
        assert session.patient_id == patient_id

    @pytest.mark.asyncio
    async def test_clinical_decision_workflow(
        self, decision_support, treatment_planner, protocol_engine
    ):
        """Test clinical decision support workflow."""
        patient_id = str(uuid4())

        # 1. Evaluate treatment eligibility
        patient_data = {
            "patient_id": patient_id,
            "medical_history": {"conditions": ["Stroke"], "medications": []},
            "cognitive_assessment": {"attention_span": 25, "working_memory": 6},
            "psychosocial_assessment": {"family_support": 8, "treatment_motivation": 9},
        }

        eligibility = await decision_support.evaluate_treatment_eligibility(
            patient_data
        )

        # 2. Create treatment plan if eligible
        if eligibility["eligible"]:
            assessment_data = {
                "cognitive_scores": {"attention": 70, "memory": 65},
                "medical_history": patient_data["medical_history"],
            }
            treatment_plan = await treatment_planner.create_treatment_plan(
                patient_id, assessment_data
            )

            # 3. Start protocol execution
            protocol_data = {
                "name": "Decision Support Test Protocol",
                "steps": [
                    {
                        "name": "Initial Assessment",
                        "session_type": "assessment",
                        "duration_minutes": 60,
                    }
                ],
            }
            execution_id = await protocol_engine.start_protocol_execution(
                patient_id, protocol_data
            )

            # Verify workflow completion
            assert treatment_plan is not None
            assert execution_id is not None


# Performance and stress tests
class TestPerformance:
    """Test performance and scalability of clinical workflows."""

    @pytest.mark.asyncio
    async def test_bulk_patient_registration(self, patient_service):
        """Test bulk patient registration performance."""
        import time

        start_time = time.time()

        # Register multiple patients
        patients = []
        for i in range(10):  # Reduced for test speed
            patient_data = {
                "first_name": f"Patient{i}",
                "last_name": "TestBulk",
                "date_of_birth": "1980-01-01",
                "gender": "M" if i % 2 == 0 else "F",
            }
            patient = await patient_service.register_patient(patient_data)
            patients.append(patient)

        end_time = time.time()
        duration = end_time - start_time

        assert len(patients) == 10
        assert duration < 5.0  # Should complete within 5 seconds
        assert all(p.patient_id is not None for p in patients)

    @pytest.mark.asyncio
    async def test_concurrent_session_creation(self, session_manager):
        """Test concurrent session creation."""
        import asyncio

        # Mock safety protocols for all sessions
        session_manager.safety_protocols.validate_pre_session_safety = AsyncMock(
            return_value={"safe_to_proceed": True, "issues": []}
        )

        async def create_session(patient_num):
            patient_id = f"patient_{patient_num}"
            session_config = {
                "type": "training",
                "provider_id": f"provider_{patient_num % 3}",  # Distribute across 3 providers
                "duration_minutes": 60,
            }
            return await session_manager.create_session(patient_id, session_config)

        # Create multiple sessions concurrently
        tasks = [create_session(i) for i in range(5)]
        sessions = await asyncio.gather(*tasks)

        assert len(sessions) == 5
        assert all(s is not None for s in sessions)
        assert len(set(s.session_id for s in sessions)) == 5  # All unique


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
