from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from domains.identity import get_current_user
from security.authentication import requires_role
from models.db_schemes import User
from models import ResponseSignal

admin_router = APIRouter(
    prefix="/api/v1/admin",
    tags=["admin"],
    dependencies=[Depends(requires_role(["admin"]))]
)

@admin_router.get("/stats")
async def get_system_stats(current_user: User = Depends(get_current_user)):
    """Only admins can see system-wide stats."""
    return JSONResponse(
        content={
            "signal": "ADMIN_STATS_RETRIEVED",
            "active_users": 100,  # Mock data
            "total_queries": 5000,
            "system_health": "perfect"
        }
    )

@admin_router.post("/users/{user_id}/deactivate")
async def deactivate_user(user_id: int):
    """Only admins can deactivate users."""
    return JSONResponse(
        content={
            "signal": "USER_DEACTIVATED",
            "user_id": user_id
        }
    )
