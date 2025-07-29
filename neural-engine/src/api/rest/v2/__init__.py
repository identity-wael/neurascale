"""REST API v2 routers."""

from .neural_data import router as neural_data_router
from .ml_models import router as ml_models_router
from .visualizations import router as visualizations_router
from .clinical import router as clinical_router
from .devices import router as devices_router
from .sessions import router as sessions_router
from .patients import router as patients_router
from .analysis import router as analysis_router

__all__ = [
    "neural_data_router",
    "ml_models_router",
    "visualizations_router",
    "clinical_router",
    "devices_router",
    "sessions_router",
    "patients_router",
    "analysis_router",
]
