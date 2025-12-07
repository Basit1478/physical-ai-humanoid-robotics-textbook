import os
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    # Application settings
    app_name: str = "Physical AI & Humanoid Robotics Textbook Backend"
    app_version: str = "1.0.0"
    debug: bool = True  # Set to False in production

    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./textbook.db")
    database_echo: bool = False  # Set to True to log SQL statements

    # JWT settings
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # API settings
    api_prefix: str = "/api"
    allowed_origins: List[str] = ["*"]  # In production, specify exact origins

    # AI/ML settings
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    qdrant_url: Optional[str] = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key: Optional[str] = os.getenv("QDRANT_API_KEY")

    # Model settings
    embedding_model: str = "text-embedding-ada-002"
    llm_model: str = "gpt-3.5-turbo"

    # File upload settings
    max_upload_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: List[str] = [".txt", ".pdf", ".docx", ".md"]

    # Translation settings
    default_target_language: str = "ur"  # Urdu
    translation_service: str = "simulated"  # In production, use actual service

    # RAG settings
    vector_store_path: str = "./vector_store"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    similarity_top_k: int = 4

    # Personalization settings
    profile_completion_threshold: int = 70  # Percentage

    class Config:
        env_file = ".env"


settings = Settings()