from fastapi import FastAPI
from routes import base, data, nlp
from core.container import container
from utils.metrics import setup_metrics
from stores.llm.templates.template_parser import TemplateParser

app = FastAPI()

# Setup Prometheus metrics
setup_metrics(app)

async def startup_span():
    # Warmup and Mapping for Backward Compatibility
    app.db_engine = container.db_engine
    app.db_client = container.db_session_factory

    # Generation client
    app.generation_client = container.llm_provider_factory.create(provider=container.settings.GENERATION_BACKEND)
    if app.generation_client:
        app.generation_client.set_generation_model(model_id = container.settings.GENERATION_MODEL_ID)

    # Embedding client
    app.embedding_client = container.llm_provider_factory.create(provider=container.settings.EMBEDDING_BACKEND)
    if app.embedding_client:
        app.embedding_client.set_embedding_model(
            model_id=container.settings.EMBEDDING_MODEL_ID,
            embedding_size=container.settings.EMBEDDING_MODEL_SIZE
        )
    
    # Vector db client
    app.vectordb_client = container.vectordb_provider_factory.create(
        provider=container.settings.VECTOR_DB_BACKEND
    )
    await app.vectordb_client.connect()

    app.template_parser = TemplateParser(
        language=container.settings.PRIMARY_LANG,
        default_language=container.settings.DEFAULT_LANG,
    )


async def shutdown_span():
    await container.dispose()

app.add_event_handler("startup", startup_span)
app.add_event_handler("shutdown", shutdown_span)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
