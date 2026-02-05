from fastapi import FastAPI, APIRouter, Depends, Response, status
import os
from helpers.config import get_settings, Settings
from time import sleep
import logging

logger = logging.getLogger('uvicorn.error')

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)

@base_router.get("/")
async def welcome(app_settings: Settings = Depends(get_settings)):

    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION

    return {
        "app_name": app_name,
        "app_version": app_version,
    }

@base_router.get("/health/simple")
async def health_check_simple():
    return {"status": "ok"}

@base_router.get("/readiness")
async def readiness_check():
    try:
        from core.container import container
        from sqlalchemy import text
        
        async with container.db_session_factory() as session:
            await session.execute(text("SELECT 1"))
        
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
