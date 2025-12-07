from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    education_level: Optional[str] = None
    field_of_study: Optional[str] = None
    background: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Module Schemas
class ModuleBase(BaseModel):
    name: str
    description: str
    order: int

class Module(ModuleBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Chapter Schemas
class ChapterBase(BaseModel):
    module_id: int
    title: str
    content: str
    order: int
    learning_outcomes: Optional[str] = None
    summary: Optional[str] = None

class Chapter(ChapterBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Progress Schemas
class ProgressBase(BaseModel):
    chapter_id: int
    completed: bool = False
    notes: Optional[str] = None
    rating: Optional[int] = None

class Progress(ProgressBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Profile Schemas
class ProfileBase(BaseModel):
    name: Optional[str] = None
    education_level: Optional[str] = None
    field_of_study: Optional[str] = None
    background: Optional[str] = None
    learning_preferences: Optional[str] = None

class Profile(ProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Translation Schemas
class TranslationBase(BaseModel):
    content_id: int
    content_type: str
    language: str
    translated_content: str

class Translation(TranslationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Chat Schemas
class ChatMessageBase(BaseModel):
    session_id: int
    sender_type: str
    content: str

class ChatMessage(ChatMessageBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class ChatSessionBase(BaseModel):
    user_id: Optional[int] = None
    session_title: Optional[str] = None

class ChatSession(ChatSessionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None
    module_id: Optional[int] = None
    chapter_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    session_id: int
    message_id: int

# Embedding Schemas
class EmbeddingBase(BaseModel):
    content_id: int
    content_type: str
    embedding_vector: str
    metadata_json: Optional[str] = None

class Embedding(EmbeddingBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Personalization Schemas
class PersonalizationRequest(BaseModel):
    education_level: Optional[str] = None
    field_of_study: Optional[str] = None
    learning_preferences: Optional[dict] = None
    background: Optional[str] = None

class PersonalizationResponse(BaseModel):
    message: str
    updated_profile: Optional[Profile] = None

# Translation Request/Response
class TranslationRequest(BaseModel):
    content: str
    source_language: str = "en"
    target_language: str = "ur"

class TranslationResponse(BaseModel):
    translated_content: str
    source_language: str
    target_language: str