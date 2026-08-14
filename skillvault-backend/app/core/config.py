import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "SkillVault"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Database Settings
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/skillvault"
    SYNC_DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/skillvault"

    # LLM & Embedding Settings
    OPENAI_API_KEY: str = "mock-key"
    OPENAI_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    SKILL_EMBEDDING_DIMENSION: int = 1536

    # Agent & Retrieval Thresholds
    SKILL_MATCH_THRESHOLD: float = 0.50
    TOP_K_SKILLS: int = 5

    # Reranking Weights
    SEMANTIC_WEIGHT: float = 0.70
    RELIABILITY_WEIGHT: float = 0.15
    SUCCESS_RATE_WEIGHT: float = 0.10
    COMPATIBILITY_WEIGHT: float = 0.05

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
