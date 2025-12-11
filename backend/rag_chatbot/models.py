from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatQueryRequest(BaseModel):
    question: str
    context: Optional[str] = None
    conversation_id: Optional[str] = None
    user_id: str

class ChatQueryResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: float
    conversation_id: str

class EmbedContentRequest(BaseModel):
    content: str
    chapter_id: str
    chapter_title: str
    section_title: str
    page_url: str

class EmbedContentResponse(BaseModel):
    success: bool
    content_id: str