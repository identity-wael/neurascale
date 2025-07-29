"""Analysis REST API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import logging

from ...rest.middleware.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("")
async def list_analyses(user: Dict[str, Any] = Depends(get_current_user)):
    """List analyses."""
    # Placeholder implementation
    return {"message": "Analysis list endpoint", "user": user.get("sub")}
