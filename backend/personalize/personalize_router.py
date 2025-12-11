from fastapi import APIRouter, HTTPException, Depends
from .models import PersonalizeChapterRequest, PersonalizeChapterResponse, GetCachedPersonalizationRequest
from rag_chatbot.gemini_client import gemini_service
import uuid
from datetime import datetime, timedelta
import json
import os

router = APIRouter()

# In-memory storage for personalized content (in production, use a proper database)
personalized_content_db = {}

@router.post("/chapter", response_model=PersonalizeChapterResponse)
async def personalize_chapter(request: PersonalizeChapterRequest):
    """Personalize chapter content based on user background"""
    try:
        # Check if personalized content is already cached
        cache_key = f"{request.user_id}:{request.chapter_id}"

        if cache_key in personalized_content_db:
            cached = personalized_content_db[cache_key]
            # Check if cache is still valid (7 days)
            if datetime.fromisoformat(cached["created_at"]) + timedelta(days=7) > datetime.utcnow():
                return PersonalizeChapterResponse(
                    personalized_content=cached["content"],
                    adjustments_made=cached["adjustments_made"],
                    cache_key=cache_key
                )

        # Prepare the personalization prompt for Gemini
        background_info = f"""
        Software Experience: {request.user_background.get('software_background', 'Not specified')}
        Hardware Experience: {request.user_background.get('hardware_background', 'Not specified')}
        Programming Languages: {request.user_background.get('programming_languages', 'Not specified')}
        Robotics Experience: {request.user_background.get('robotics_experience', 'Not specified')}
        AI/ML Knowledge: {request.user_background.get('ai_ml_knowledge', 'Not specified')}
        """

        prompt = f"""
        Personalize the following chapter content based on the user's background:
        {background_info}

        Adjust the content to match the user's experience level:
        - For beginners: Add more explanations, examples, and step-by-step guidance
        - For advanced users: Include more technical details, advanced concepts, and references to cutting-edge research
        - Include relevant examples based on the user's programming language preferences
        - Adjust the complexity based on their software and hardware experience levels
        - Maintain the original structure and markdown formatting

        Original content:
        {request.original_content}

        Personalized content:
        """

        # Generate personalized content using Gemini
        personalized_content = gemini_service.generate_response(prompt)

        # Determine adjustments made based on user background
        adjustments_made = []
        if "beginner" in (request.user_background.get('software_background', '') or '').lower():
            adjustments_made.append("Added beginner-friendly explanations")
        elif "advanced" in (request.user_background.get('software_background', '') or '').lower():
            adjustments_made.append("Added advanced technical details")

        if request.user_background.get('programming_languages'):
            adjustments_made.append(f"Added examples in {', '.join(request.user_background.get('programming_languages', []))}")

        if request.user_background.get('hardware_experience'):
            adjustments_made.append(f"Included hardware-specific details for {request.user_background.get('hardware_experience')} level")

        # Store in cache
        personalized_content_db[cache_key] = {
            "user_id": request.user_id,
            "chapter_id": request.chapter_id,
            "content": personalized_content,
            "adjustments_made": adjustments_made,
            "created_at": datetime.utcnow().isoformat()
        }

        return PersonalizeChapterResponse(
            personalized_content=personalized_content,
            adjustments_made=adjustments_made,
            cache_key=cache_key
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error personalizing content: {str(e)}")

@router.get("/chapter/{chapter_id}/cached")
async def get_cached_personalization(chapter_id: str, user_id: str):
    """Retrieve previously personalized content"""
    cache_key = f"{user_id}:{chapter_id}"

    if cache_key in personalized_content_db:
        cached = personalized_content_db[cache_key]
        # Check if cache is still valid (7 days)
        if datetime.fromisoformat(cached["created_at"]) + timedelta(days=7) > datetime.utcnow():
            return {
                "personalized_content": cached["content"],
                "adjustments_made": cached["adjustments_made"],
                "cache_key": cache_key
            }

    raise HTTPException(status_code=404, detail="Cached personalization not found")

@router.get("/health")
async def personalize_health():
    """Health check for personalization service"""
    return {"status": "healthy", "service": "personalize"}