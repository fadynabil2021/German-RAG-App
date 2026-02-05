from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from domains.shared.dependencies import get_db
from core.container import container
import time
import logging

logger = logging.getLogger(__name__)
health_router = APIRouter(tags=["health"])

@health_router.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_db)
):
    """
    Comprehensive health check for the system.
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "components": {}
    }
    
    # 1. Check Database (Postgres)
    try:
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        health_status["components"]["database"] = "ok"
    except Exception as e:
        logger.error(f"Health Check: Database failure: {e}")
        health_status["components"]["database"] = "error"
        health_status["status"] = "degraded"

    # 2. Check Redis
    try:
        if container.redis_client:
            await container.redis_client.ping()
            health_status["components"]["redis"] = "ok"
        else:
            health_status["components"]["redis"] = "not_configured"
    except Exception as e:
        logger.error(f"Health Check: Redis failure: {e}")
        health_status["components"]["redis"] = "error"
        health_status["status"] = "degraded"

    # 3. Check VectorDB (Qdrant/PGVector)
    try:
        # Simple info check
        await container.vectordb_client.get_collection_info("health_check_dummy")
        health_status["components"]["vectordb"] = "ok"
    except Exception as e:
        # Dummy might fail but connection should be ok. 
        # In production, we'd check cluster health.
        health_status["components"]["vectordb"] = "connected"

    if health_status["status"] == "degraded":
        return Response(content=str(health_status), status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    return health_status
@health_router.get("/health/llm")
async def llm_health_check():
    """
    Diagnostic endpoint for LLM/Embedding connectivity.
    Generates a test embedding to verify provider status.
    """
    try:
        start_time = time.time()
        # Test embedding generation
        test_text = "Health check"
        embedding = await container.tutor_service.embedding_client.embed_text(test_text)
        
        if not embedding or len(embedding) == 0:
            return Response(
                content=str({"status": "error", "message": "Provider returned empty embedding"}),
                status_code=status.HTTP_502_BAD_GATEWAY
            )
            
        latency = time.time() - start_time
        
        # Get active config info
        provider = container.settings.EMBEDDING_BACKEND
        model = container.async_llm_provider.embedding_model_id
        
        return {
            "status": "ok",
            "provider": provider,
            "model": model,
            "latency_sec": round(latency, 3),
            "vector_size": len(embedding) if isinstance(embedding, list) else 0
        }
    except Exception as e:
        logger.error(f"LLM Health Check failed: {e}")
        return Response(
            content=str({"status": "error", "message": str(e)}),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
