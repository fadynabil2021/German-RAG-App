from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, Field
from typing import List, Optional
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "mini-RAG"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "CHANGE_ME_32CHARS"
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    FILE_ALLOWED_TYPES: List[str] = ["text/plain", "application/pdf"]
    FILE_MAX_SIZE: int = 10 # MB
    FILE_DEFAULT_CHUNK_SIZE: int = 512000 # 512KB

    # ── Database ─────────────────────────────────────────────────
    # We use DATABASE_URL as the primary source of truth per PRD
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/grag"

    # ── Redis ────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Celery ───────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "amqp://guest:guest@localhost:5672//"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_TASK_TIME_LIMIT: int = 300
    CELERY_WORKER_CONCURRENCY: int = 4

    # ── LLM Providers ────────────────────────────────────────────
    GENERATION_BACKEND: str = "openai"
    GENERATION_MODEL_ID: str = "gpt-4o-mini"
    EMBEDDING_BACKEND: str = "openai"
    EMBEDDING_MODEL_ID: str = "text-embedding-3-small"
    EMBEDDING_MODEL_SIZE: int = 1536
    OPENAI_API_KEY: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None

    # ── Vector DB ────────────────────────────────────────────────
    VECTORDB_BACKEND: str = "pgvector"
    QDRANT_URL: Optional[str] = None
    QDRANT_API_KEY: Optional[str] = None

    # ── Observability ────────────────────────────────────────────
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"

    # ── Rate Limiting ────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE_FREE: int = 20
    RATE_LIMIT_PER_MINUTE_PRO: int = 200

    # ── Flower ───────────────────────────────────────────────────
    FLOWER_USER: str = "admin"
    FLOWER_PASSWORD: str = "CHANGE_ME"

    # Backward compatibility properties if needed
    @property
    def SQLALCHEMY_DATABASE_URI_SYNC(self) -> str:
        return self.DATABASE_URL.replace("+asyncpg", "")

    @property
    def PRIMARY_LANG(self) -> str:
        return "de"

    @property
    def DEFAULT_LANG(self) -> str:
        return "de"

def get_settings() -> Settings:
    return Settings()
