from helpers.config import get_settings
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from infrastructure.llm.async_openai_provider import AsyncOpenAIProvider
from stores.llm.templates.template_parser import TemplateParser
from domains.tutor.service import TutorService
from stores.llm.semantic_cache import SemanticCache
import structlog

logger = structlog.get_logger(__name__)

class Container:
    """Dependency Injection Container - Singleton pattern."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.settings = get_settings()
        
        # Database Engine (Async)
        postgres_conn = self.settings.DATABASE_URL
        self.db_engine = create_async_engine(
            postgres_conn, 
            pool_pre_ping=True,
            pool_size=self.settings.CELERY_WORKER_CONCURRENCY * 2,
            max_overflow=10
        )
        self.db_session_factory = sessionmaker(
            self.db_engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Redis Client (Async)
        self.redis_client = redis.from_url(
            self.settings.REDIS_URL,
            decode_responses=True
        )
        
        # LLM and VectorDB Factories (Legacy - for backward compatibility)
        self.llm_provider_factory = LLMProviderFactory(self.settings)
        self.vectordb_provider_factory = VectorDBProviderFactory(
            config=self.settings, 
            db_client=self.db_session_factory
        )
        
        # LLM Cache
        self.llm_cache = SemanticCache(redis_url=self.settings.CELERY_RESULT_BACKEND)

        # NEW: Async LLM Provider (P0 Fix for blocking I/O)
        self.async_llm_provider = AsyncOpenAIProvider(
            config=self.settings,
            cache=self.llm_cache
        )
        
        # Guard: Validate OpenAI models if using OpenAI backend
        if self.settings.GENERATION_BACKEND == "openai":
            gen_model = self.settings.GENERATION_MODEL_ID
            self.async_llm_provider.set_generation_model(gen_model)
            logger.info(f"LLM Generation Provider: OpenAI | Model: {gen_model}")
            
        if self.settings.EMBEDDING_BACKEND == "openai":
            embed_model = self.settings.EMBEDDING_MODEL_ID
            self.async_llm_provider.set_embedding_model(
                embed_model,
                self.settings.EMBEDDING_MODEL_SIZE
            )
            logger.info(f"LLM Embedding Provider: OpenAI | Model: {embed_model}")
        elif self.settings.EMBEDDING_BACKEND == "COHERE":
            logger.warning("Cohere embedding backend selected but using AsyncOpenAIProvider as fallback/placeholder. Ensure Cohere SDK is integrated.")
            self.async_llm_provider.set_embedding_model(
                self.settings.EMBEDDING_MODEL_ID,
                self.settings.EMBEDDING_MODEL_SIZE
            )
        
        # Template Parser
        self.template_parser = TemplateParser(
            language=self.settings.PRIMARY_LANG,
            default_language=self.settings.DEFAULT_LANG,
        )

        # Vector DB Client
        self.vectordb_client = self.vectordb_provider_factory.create(
            provider=self.settings.VECTOR_DB_BACKEND
        )
        
        # Domain Services
        self.tutor_service = TutorService(
            llm_provider=self.async_llm_provider,
            vectordb_client=self.vectordb_client,
            embedding_client=self.async_llm_provider,
            template_parser=self.template_parser
        )
        
        self._initialized = True
    
    async def dispose(self):
        """Cleanup resources."""
        if hasattr(self, 'db_engine'):
            await self.db_engine.dispose()

# Global singleton instance
container = Container()
