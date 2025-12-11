from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PersonalizeChapterRequest(BaseModel):
    user_id: str
    chapter_id: str
    original_content: str
    user_background: dict

class PersonalizeChapterResponse(BaseModel):
    personalized_content: str
    adjustments_made: List[str]
    cache_key: str

class GetCachedPersonalizationRequest(BaseModel):
    user_id: str
    chapter_id: str