"""Patient management REST API endpoints."""

from fastapi import APIRouter, Depends
from typing import Dict, Any
import logging

from ...rest.middleware.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("")
async def list_patients(user: Dict[str, Any] = Depends(get_current_user)):
    """List patients."""
    # Placeholder implementation
    return {"message": "Patient list endpoint", "user": user.get("sub")}
