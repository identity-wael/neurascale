"""GraphQL DataLoaders for N+1 query prevention."""

from .batch_loaders import (
    create_device_loader,
    create_session_loader,
    create_patient_loader,
    create_analysis_loader,
)

__all__ = [
    "create_device_loader",
    "create_session_loader",
    "create_patient_loader",
    "create_analysis_loader",
]
