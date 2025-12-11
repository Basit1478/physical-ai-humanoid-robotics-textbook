from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TranslateChapterRequest(BaseModel):
    user_id: str
    chapter_id: str
    content: str
    target_language: str = "ur"  # Urdu ISO code

class TranslateChapterResponse(BaseModel):
    translated_content: str
    cache_key: str

class GetCachedTranslationRequest(BaseModel):
    user_id: str
    chapter_id: str
    language: str = "ur"