from helpers.config import get_settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from infrastructure.llm.async_openai_provider import AsyncOpenAIProvider
from stores.llm.templates.template_parser import TemplateParser
from domains.tutor.service import TutorService
from stores.llm.semantic_cache import SemanticCache

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
        postgres_conn = (
            f"postgresql+asyncpg://{self.settings.POSTGRES_USERNAME}:"
            f"{self.settings.POSTGRES_PASSWORD.get_secret_value()}@"
            f"{self.settings.POSTGRES_HOST}:{self.settings.POSTGRES_PORT}/"
            f"{self.settings.POSTGRES_MAIN_DATABASE}"
        )
        self.db_engine = create_async_engine(
            postgres_conn, 
            pool_pre_ping=True,
            pool_size=self.settings.CELERY_WORKER_CONCURRENCY * 2,
            max_overflow=10
        )
        self.db_session_factory = sessionmaker(
            self.db_engine, class_=AsyncSession, expire_on_commit=False
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
        self.async_llm_provider.set_generation_model(self.settings.GENERATION_MODEL_ID)
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
