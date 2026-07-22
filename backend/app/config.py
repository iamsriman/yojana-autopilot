"""Application configuration."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    app_name: str = "Yojana Autopilot API"
    app_version: str = "1.0.0"
    environment: str = Field(default="development")
    api_prefix: str = ""

    groq_api_key: str | None = None
    groq_model: str = "llama-3.1-8b-instant"
    groq_base_url: str = "https://api.groq.com/openai/v1"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chroma_collection: str = "yojana_autopilot"
    rag_top_k: int = 5
    rag_min_confidence: float = 0.28
    web_search_max_results: int = 3
    groq_max_tokens: int = 900

    request_timeout_seconds: float = 20.0
    cors_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def backend_dir(self) -> Path:
        return Path(__file__).resolve().parents[1]

    @property
    def app_dir(self) -> Path:
        return Path(__file__).resolve().parent

    @property
    def data_dir(self) -> Path:
        return self.app_dir / "data"

    @property
    def vector_db_dir(self) -> Path:
        return self.app_dir / "vector_db"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings for dependency injection."""

    return Settings()
