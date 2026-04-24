from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class AppConfig(BaseSettings):
    """Central application settings loaded from environment variables."""

    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_chat_model: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_CHAT_MODEL")
    embedding_model: str = Field(
        default="sentence-transformers/all-mpnet-base-v2",
        alias="EMBEDDING_MODEL",
    )
    chroma_persist_directory: str = Field(
        default="storage/chroma",
        alias="CHROMA_PERSIST_DIRECTORY",
    )
    upload_directory: str = Field(default="storage/uploads", alias="UPLOAD_DIRECTORY")
    max_context_chunks: int = Field(default=8, alias="MAX_CONTEXT_CHUNKS")
    max_chunk_size: int = Field(default=1200, alias="MAX_CHUNK_SIZE")
    chunk_overlap: int = Field(default=180, alias="CHUNK_OVERLAP")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def chroma_path(self) -> Path:
        return BASE_DIR / self.chroma_persist_directory

    @property
    def uploads_path(self) -> Path:
        return BASE_DIR / self.upload_directory


def get_config() -> AppConfig:
    return AppConfig()
