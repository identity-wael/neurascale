"""Main FastAPI application for NeuraScale Neural Engine API v2."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import logging
from typing import Dict, Any
import time

from .rest.v2 import (
    neural_data_router,
    ml_models_router,
    visualizations_router,
    clinical_router,
    devices_router,
    sessions_router,
    patients_router,
    analysis_router,
)
from .graphql.app import graphql_router
from .rest.middleware.rate_limiter import RateLimitMiddleware
from .rest.middleware.error_handler import error_handler
from .rest.middleware.auth import AuthMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="NeuraScale Neural Engine API",
    version="2.0.0",
    description="Brain-Computer Interface API for neural data processing and analysis",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RateLimitMiddleware, calls=1000, period=60)  # 1000 calls per minute
app.add_middleware(AuthMiddleware)

# Add error handler
app.add_exception_handler(Exception, error_handler)

# Include REST routers
app.include_router(
    neural_data_router, prefix="/api/v2/neural-data", tags=["Neural Data"]
)
app.include_router(ml_models_router, prefix="/api/v2/ml-models", tags=["ML Models"])
app.include_router(
    visualizations_router, prefix="/api/v2/visualizations", tags=["Visualizations"]
)
app.include_router(clinical_router, prefix="/api/v2/clinical", tags=["Clinical"])
app.include_router(devices_router, prefix="/api/v2/devices", tags=["Devices"])
app.include_router(sessions_router, prefix="/api/v2/sessions", tags=["Sessions"])
app.include_router(patients_router, prefix="/api/v2/patients", tags=["Patients"])
app.include_router(analysis_router, prefix="/api/v2/analysis", tags=["Analysis"])

# Include GraphQL router
app.include_router(graphql_router, prefix="/graphql", tags=["GraphQL"])


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {
        "service": "NeuraScale Neural Engine API",
        "version": "2.0.0",
        "status": "operational",
        "documentation": "/api/docs",
    }


@app.get("/health")
async def health() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "2.0.0",
    }


@app.get("/api/v2")
async def api_info() -> Dict[str, Any]:
    """API information endpoint with HATEOAS links."""
    return {
        "version": "2.0.0",
        "description": "NeuraScale Neural Engine REST API",
        "_links": {
            "self": {"href": "/api/v2"},
            "devices": {"href": "/api/v2/devices"},
            "sessions": {"href": "/api/v2/sessions"},
            "patients": {"href": "/api/v2/patients"},
            "neural-data": {"href": "/api/v2/neural-data"},
            "ml-models": {"href": "/api/v2/ml-models"},
            "visualizations": {"href": "/api/v2/visualizations"},
            "clinical": {"href": "/api/v2/clinical"},
            "analysis": {"href": "/api/v2/analysis"},
            "graphql": {"href": "/graphql"},
            "docs": {"href": "/api/docs"},
            "openapi": {"href": "/api/openapi.json"},
        },
    }


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("NeuraScale Neural Engine API v2.0.0 starting up...")
    # Initialize database connections, caches, etc.


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("NeuraScale Neural Engine API shutting down...")
    # Close database connections, flush caches, etc.


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
