from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
from typing import Optional
import os

from routes import modules, chat, auth, personalization, translation, ingestion, agents, openai_agents
from models.database import engine, Base
from auth.better_auth import get_current_user
from config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="Backend API for Physical AI & Humanoid Robotics Textbook with RAG, authentication, personalization, and translation",
    version=settings.app_version,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Allow credentials for auth
    allow_credentials=True
)

# Include routers
app.include_router(modules.router, prefix="/api", tags=["modules"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(personalization.router, prefix="/api", tags=["personalization"])
app.include_router(translation.router, prefix="/api", tags=["translation"])
app.include_router(ingestion.router, prefix="/api", tags=["ingestion"])
app.include_router(agents.router, prefix="/api", tags=["agents"])
app.include_router(openai_agents.router, prefix="/api", tags=["openai-agents"])

@app.get("/")
def read_root():
    return {
        "message": "Physical AI & Humanoid Robotics Textbook API",
        "version": settings.app_version,
        "services": [
            "Authentication (JWT)",
            "Module/Chapter Management",
            "RAG Chatbot",
            "Personalization",
            "Translation (Urdu & others)",
            "Content Ingestion",
            "Reusable Intelligence Agents"
        ]
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }

@app.get("/api/config")
def get_client_config():
    """Provide configuration for client-side integration"""
    return {
        "api_base_url": "/api",
        "auth_enabled": True,
        "rag_enabled": True,
        "translation_enabled": True,
        "personalization_enabled": True,
        "supported_languages": ["en", "ur", "es", "fr", "de", "zh", "ja", "ar"],
        "default_language": "en"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )