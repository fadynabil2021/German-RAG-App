from fastapi import FastAPI
from routes import base, data, nlp, admin, auth
from routes.dashboard import dashboard_router
from routes.projects import projects_router
from core.container import container
from utils.metrics import setup_metrics
from stores.llm.templates.template_parser import TemplateParser
from security.rate_limit import RateLimitMiddleware
from fastapi.middleware.cors import CORSMiddleware
from utils.logger import setup_logging
from routes.health import health_router
import os

# Setup Structured Logging
logger = setup_logging()

app = FastAPI()

# Integrated Error Tracking (e.g. Sentry)
# if os.getenv("SENTRY_DSN"):
#     import sentry_sdk
#     sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), traces_sample_rate=1.0)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

# Setup Prometheus metrics
setup_metrics(app)

async def startup_span():
    # Warmup and Mapping for Backward Compatibility
    app.db_engine = container.db_engine
    app.db_client = container.db_session_factory

    # Generation client (Legacy)
    app.generation_client = container.llm_provider_factory.create(provider=container.settings.GENERATION_BACKEND)
    if app.generation_client:
        app.generation_client.set_generation_model(model_id = container.settings.GENERATION_MODEL_ID)

    # Embedding client (Legacy)
    app.embedding_client = container.llm_provider_factory.create(provider=container.settings.EMBEDDING_BACKEND)
    if app.embedding_client:
        app.embedding_client.set_embedding_model(
            model_id=container.settings.EMBEDDING_MODEL_ID,
            embedding_size=container.settings.EMBEDDING_MODEL_SIZE
        )
    
    # Vector db client - Use the one from container and connect
    app.vectordb_client = container.vectordb_client
    await app.vectordb_client.connect()

    app.template_parser = container.template_parser
    
    # Domain Services
    app.tutor_service = container.tutor_service


async def shutdown_span():
    await container.dispose()

app.add_event_handler("startup", startup_span)
app.add_event_handler("shutdown", shutdown_span)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
app.include_router(admin.admin_router)
app.include_router(auth.auth_router)
app.include_router(dashboard_router)
app.include_router(projects_router)
app.include_router(health_router)
