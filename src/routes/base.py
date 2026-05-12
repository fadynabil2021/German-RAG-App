from fastapi import APIRouter, Depends, Response, status
import structlog
from helpers.config import get_settings, Settings
from core.container import container
from sqlalchemy import text

logger = structlog.get_logger(__name__)

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)

@base_router.get("/")
async def welcome(app_settings: Settings = Depends(get_settings)):
    return {
        "app_name": app_settings.APP_NAME,
        "app_version": app_settings.APP_VERSION,
    }

@base_router.get("/health/simple")
async def health_check_simple():
    return {"status": "ok"}

@base_router.get("/readiness")
async def readiness_check():
    try:
        async with container.db_session_factory() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        logger.error("Readiness check failed", error=str(e))
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
