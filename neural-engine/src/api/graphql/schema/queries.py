"""GraphQL query resolvers."""

import strawberry
from typing import Optional, List
from datetime import datetime

from .types import (
    Device,
    DeviceConnection,
    Session,
    SessionConnection,
    Patient,
    Analysis,
    MLModel,
    DeviceFilter,
    SessionFilter,
    PaginationInput,
)
from ..resolvers.device_resolver import DeviceResolver
from ..resolvers.session_resolver import SessionResolver
from ..resolvers.patient_resolver import PatientResolver
from ..resolvers.analysis_resolver import AnalysisResolver


@strawberry.type
class Query:
    """Root query type."""

    # Device queries
    @strawberry.field
    async def device(self, id: str) -> Optional[Device]:
        """Get a device by ID."""
        resolver = DeviceResolver()
        return await resolver.get_device(id)

    @strawberry.field
    async def devices(
        self,
        filter: Optional[DeviceFilter] = None,
        pagination: Optional[PaginationInput] = None,
    ) -> DeviceConnection:
        """List devices with filtering and pagination."""
        resolver = DeviceResolver()
        return await resolver.list_devices(filter, pagination)

    # Session queries
    @strawberry.field
    async def session(self, id: str) -> Optional[Session]:
        """Get a session by ID."""
        resolver = SessionResolver()
        return await resolver.get_session(id)

    @strawberry.field
    async def sessions(
        self,
        filter: Optional[SessionFilter] = None,
        pagination: Optional[PaginationInput] = None,
    ) -> SessionConnection:
        """List sessions with filtering and pagination."""
        resolver = SessionResolver()
        return await resolver.list_sessions(filter, pagination)

    @strawberry.field
    async def active_sessions(self) -> List[Session]:
        """Get all currently active sessions."""
        resolver = SessionResolver()
        return await resolver.get_active_sessions()

    # Patient queries
    @strawberry.field
    async def patient(self, id: str) -> Optional[Patient]:
        """Get a patient by ID."""
        resolver = PatientResolver()
        return await resolver.get_patient(id)

    @strawberry.field
    async def patient_by_external_id(self, external_id: str) -> Optional[Patient]:
        """Get a patient by external ID."""
        resolver = PatientResolver()
        return await resolver.get_patient_by_external_id(external_id)

    # Analysis queries
    @strawberry.field
    async def analysis(self, id: str) -> Optional[Analysis]:
        """Get an analysis by ID."""
        resolver = AnalysisResolver()
        return await resolver.get_analysis(id)

    @strawberry.field
    async def analyses_by_session(self, session_id: str) -> List[Analysis]:
        """Get all analyses for a session."""
        resolver = AnalysisResolver()
        return await resolver.get_analyses_by_session(session_id)

    # ML Model queries
    @strawberry.field
    async def ml_model(self, id: str) -> Optional[MLModel]:
        """Get an ML model by ID."""
        # Mock implementation
        return MLModel(
            id=id,
            name="Neural State Classifier",
            type="classification",
            version="1.0.0",
            status="active",
            accuracy=0.95,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @strawberry.field
    async def ml_models(self, type: Optional[str] = None) -> List[MLModel]:
        """List ML models."""
        # Mock implementation
        models = [
            MLModel(
                id="model_001",
                name="Neural State Classifier",
                type="classification",
                version="1.0.0",
                status="active",
                accuracy=0.95,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
            MLModel(
                id="model_002",
                name="Seizure Predictor",
                type="prediction",
                version="2.1.0",
                status="active",
                accuracy=0.92,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            ),
        ]

        if type:
            models = [m for m in models if m.type == type]

        return models

    # Search
    @strawberry.field
    async def search(
        self,
        query: str,
        types: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[strawberry.scalars.JSON]:
        """Global search across resources."""
        # Mock implementation
        results = []

        # Search would be implemented with Elasticsearch or similar
        if "device" in query.lower():
            results.append(
                {
                    "type": "device",
                    "id": "dev_001",
                    "name": "EEG Device 1",
                    "score": 0.95,
                }
            )

        if "session" in query.lower():
            results.append(
                {
                    "type": "session",
                    "id": "ses_001",
                    "patient_id": "pat_001",
                    "score": 0.90,
                }
            )

        return results[:limit]

    # System status
    @strawberry.field
    async def system_status(self) -> strawberry.scalars.JSON:
        """Get system status and health metrics."""
        return {
            "status": "operational",
            "version": "2.0.0",
            "uptime": 86400,  # 24 hours
            "services": {
                "database": "healthy",
                "cache": "healthy",
                "storage": "healthy",
                "ml_engine": "healthy",
            },
            "metrics": {
                "active_sessions": 5,
                "total_devices": 25,
                "storage_used_gb": 1250,
                "api_calls_today": 15420,
            },
        }
