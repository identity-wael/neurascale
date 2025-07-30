"""GraphQL schema definitions."""

# Import types explicitly to avoid F403
from .types import (
    Device,
    DeviceType,
    DeviceStatus,
    Session,
    SessionStatus,
    SessionConnection,
    Patient,
    PatientConnection,
    NeuralData,
    NeuralDataFrame,
    Analysis,
    AnalysisConnection,
)
from .queries import Query
from .mutations import Mutation
from .subscriptions import Subscription
import strawberry

# Create the GraphQL schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
)

__all__ = ["Query", "Mutation", "Subscription", "schema"]
