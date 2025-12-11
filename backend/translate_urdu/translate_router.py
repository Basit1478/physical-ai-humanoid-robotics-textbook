from fastapi import APIRouter, HTTPException, Depends
from .models import TranslateChapterRequest, TranslateChapterResponse, GetCachedTranslationRequest
from rag_chatbot.gemini_client import gemini_service
import uuid
from datetime import datetime, timedelta
import json
import os

router = APIRouter()

# In-memory storage for translations (in production, use a proper database)
translations_db = {}

@router.post("/chapter", response_model=TranslateChapterResponse)
async def translate_chapter(request: TranslateChapterRequest):
    """Translate chapter content to Urdu"""
    try:
        # Check if translation is already cached
        cache_key = f"{request.user_id}:{request.chapter_id}:{request.target_language}"

        if cache_key in translations_db:
            cached = translations_db[cache_key]
            # Check if cache is still valid (30 days)
            if datetime.fromisoformat(cached["created_at"]) + timedelta(days=30) > datetime.utcnow():
                return TranslateChapterResponse(
                    translated_content=cached["content"],
                    cache_key=cache_key
                )

        # Prepare the translation prompt for Gemini
        prompt = f"""
        Translate the following content to {request.target_language}.
        Preserve the markdown formatting and structure.
        Keep code blocks, technical terms, and programming syntax in English.
        Translate only the natural language content.

        Content to translate:
        {request.content}

        Translated content:
        """

        # Generate translation using Gemini
        translated_content = gemini_service.generate_response(prompt)

        # Store in cache
        translations_db[cache_key] = {
            "user_id": request.user_id,
            "chapter_id": request.chapter_id,
            "language": request.target_language,
            "content": translated_content,
            "created_at": datetime.utcnow().isoformat()
        }

        return TranslateChapterResponse(
            translated_content=translated_content,
            cache_key=cache_key
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error translating content: {str(e)}")

@router.get("/chapter/{chapter_id}/cached")
async def get_cached_translation(chapter_id: str, user_id: str, lang: str = "ur"):
    """Retrieve previously translated content"""
    cache_key = f"{user_id}:{chapter_id}:{lang}"

    if cache_key in translations_db:
        cached = translations_db[cache_key]
        # Check if cache is still valid (30 days)
        if datetime.fromisoformat(cached["created_at"]) + timedelta(days=30) > datetime.utcnow():
            return {"translated_content": cached["content"], "cache_key": cache_key}

    raise HTTPException(status_code=404, detail="Cached translation not found")

@router.get("/health")
async def translate_health():
    """Health check for translation service"""
    return {"status": "healthy", "service": "translate-urdu"}