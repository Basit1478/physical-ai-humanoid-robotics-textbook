"""
Configuration settings for the RAG Agent service
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Gemini configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "AIzaSyAEcBCmRFqdXPDUXeeOUg3d8oTcB6Tl4e4")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    COHERE_API_KEY: str = os.getenv ("COHERE_API_KEY","oiLIa9xzWPeCTQRmmszxfGLfO2qjA4JgWkOTKM1r")
    COHERE_MODEL: str = os.getenv ("COHERE_MODEL","embed-multilingual-v3.0")

    # Cohere configuration
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    COHERE_MODEL: str = os.getenv("COHERE_MODEL", "embed-multilingual-v2.0")

    # Qdrant configuration
    QDRANT_URL: str = os.getenv("QDRANT_URL", "https://912e150e-53c0-41d5-8bd5-62dc64dc85d0.europe-west3-0.gcp.cloud.qdrant.io:6333")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOlt7ImNvbGxlY3Rpb24iOiJoYWNrYXRob24tYm9vayIsImFjY2VzcyI6InJ3In1dfQ.WmMcvD4eBJE0zlPKdHnnY4aJcbE5XrtfozOHd5VJIys")
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "hackathon-book")

    # Agent configuration
    AGENT_SYSTEM_INSTRUCTIONS: str = os.getenv(
        "AGENT_SYSTEM_INSTRUCTIONS",
        "You are an AI assistant that answers questions based ONLY on the provided context. "
        "Do not use any prior knowledge or information not present in the provided context. "
        "If the context does not contain enough information to answer a question, say so clearly."
    )

    # Retrieval configuration
    RETRIEVAL_TOP_K: int = int(os.getenv("RETRIEVAL_TOP_K", "5"))
    RETRIEVAL_THRESHOLD: float = float(os.getenv("RETRIEVAL_THRESHOLD", "0.3"))

    # Server configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Selected text configuration
    SELECTED_TEXT_ENABLED: bool = os.getenv("SELECTED_TEXT_ENABLED", "true").lower() == "true"

    # Model parameters
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2048"))

    class Config:
        env_file = ".env"


# Create settings instance
settings = Settings()

# Only validate required settings when running the actual application, not during import/validation
def validate_required_settings():
    """Validate required settings are set, to be called when initializing services."""
    errors = []

    if not settings.GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY environment variable is required")

    if not settings.QDRANT_URL:
        errors.append("QDRANT_URL environment variable is required")

    # Note: COHERE_API_KEY is not required as we have a fallback mechanism
    # The system can work with other embedding methods if Cohere is not available

    if errors:
        raise ValueError("Configuration errors: " + "; ".join(errors))
