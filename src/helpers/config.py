from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, DirectoryPath
from typing import List, Optional
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "Mini-RAG"
    APP_VERSION: str = "1.0.0"
    
    # German Language Default
    PRIMARY_LANG: str = "de"
    DEFAULT_LANG: str = "de"

    # Security
    JWT_SECRET_KEY: SecretStr
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # OpenAI / LLM
    OPENAI_API_KEY: Optional[SecretStr] = None
    OPENAI_API_URL: Optional[str] = None
    COHERE_API_KEY: Optional[SecretStr] = None
    
    # OpenAI Models
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # File Ingestion
    FILE_ALLOWED_TYPES: List[str] = [".txt", ".pdf"]
    FILE_MAX_SIZE: int = 10_000_000  # 10MB
    FILE_DEFAULT_CHUNK_SIZE: int = 512
    
    # Postgres
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_MAIN_DATABASE: str

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USERNAME}:"
            f"{self.POSTGRES_PASSWORD.get_secret_value()}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_MAIN_DATABASE}"
        )

    @property
    def SQLALCHEMY_DATABASE_URI_SYNC(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USERNAME}:"
            f"{self.POSTGRES_PASSWORD.get_secret_value()}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_MAIN_DATABASE}"
        )

    # Generation Config
    GENERATION_BACKEND: str
    GENERATION_MODEL_ID: str = "gpt-3.5-turbo"
    GENERATION_DEFAULT_MAX_TOKENS: int = 512
    GENERATION_DEFAULT_TEMPERATURE: float = 0.5

    # Embedding Config
    EMBEDDING_BACKEND: str
    EMBEDDING_MODEL_ID: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    EMBEDDING_MODEL_SIZE: int = 768

    # Vector DB
    VECTOR_DB_BACKEND: str
    VECTOR_DB_PATH: str = "chroma_db_data"
    VECTOR_DB_DISTANCE_METHOD: str = "cosine"
    VECTOR_DB_PGVEC_INDEX_THRESHOLD: int = 100

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_TASK_TIME_LIMIT: int = 600
    CELERY_WORKER_CONCURRENCY: int = 2
    CELERY_FLOWER_PASSWORD: Optional[SecretStr] = None

    # Freemium Quotas
    FREE_TIER_DAILY_MESSAGE_LIMIT: int = 20
    FREE_TIER_MAX_ASSETS: int = 5

def get_settings() -> Settings:
    return Settings()
