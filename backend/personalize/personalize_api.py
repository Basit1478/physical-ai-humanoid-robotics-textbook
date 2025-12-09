from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import json

# Import the OpenAI Agents SDK with Gemini from the utils module
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.gemini_agent import OpenAI_Agents_Gemini

personalize_router = APIRouter()

class UserPreferences(BaseModel):
    user_id: str
    interests: List[str]
    level: str = "beginner"  # beginner, intermediate, advanced
    learning_style: str = "visual"  # visual, auditory, reading, kinesthetic
    preferred_language: str = "en"
    additional_preferences: Optional[Dict] = {}

class PersonalizeRequest(BaseModel):
    user_id: str
    content: str
    content_type: str = "text"  # text, code, explanation, example

class PersonalizeResponse(BaseModel):
    original_content: str
    personalized_content: str
    user_id: str

# File to store user preferences
PREFERENCES_FILE = "user_preferences.json"

def load_preferences():
    """Load user preferences from JSON file"""
    if os.path.exists(PREFERENCES_FILE):
        with open(PREFERENCES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_preferences(preferences):
    """Save user preferences to JSON file"""
    with open(PREFERENCES_FILE, 'w') as f:
        json.dump(preferences, f, indent=2)

# Initialize the Gemini agent
gemini_agent = OpenAI_Agents_Gemini()

@personalize_router.post("/preferences")
async def set_user_preferences(user_prefs: UserPreferences):
    """Set user preferences for personalization"""
    try:
        preferences = load_preferences()
        
        preferences[user_prefs.user_id] = {
            "interests": user_prefs.interests,
            "level": user_prefs.level,
            "learning_style": user_prefs.learning_style,
            "preferred_language": user_prefs.preferred_language,
            "additional_preferences": user_prefs.additional_preferences or {},
            "updated_at": "2025-01-01T00:00:00Z"  # In practice, use current timestamp
        }
        
        save_preferences(preferences)
        
        return {
            "user_id": user_prefs.user_id,
            "status": "preferences saved",
            "message": "User preferences updated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving preferences: {str(e)}")

@personalize_router.post("/content", response_model=PersonalizeResponse)
async def personalize_content(request: PersonalizeRequest):
    """Personalize content based on user preferences"""
    try:
        # Load user preferences
        preferences = load_preferences()
        
        user_profile = preferences.get(request.user_id, {})
        
        # Create prompt for content personalization
        if user_profile:
            prompt = f"""
            Personalize the following content for a user with these preferences:
            
            Interests: {', '.join(user_profile.get('interests', []))}
            Level: {user_profile.get('level', 'beginner')}
            Learning Style: {user_profile.get('learning_style', 'visual')}
            Preferred Language: {user_profile.get('preferred_language', 'en')}
            
            Original Content: "{request.content}"
            
            Personalized Content:
            """
        else:
            # If no profile exists, return original content
            return PersonalizeResponse(
                original_content=request.content,
                personalized_content=request.content,
                user_id=request.user_id
            )
        
        # Use Gemini to personalize content
        messages = [
            {"role": "system", "content": f"""You are a content personalization expert. Adapt the content to match the user's interests, skill level, and learning style. 
            Make the content more engaging and appropriate for their level (e.g., add examples for beginners, deeper explanations for advanced users). 
            Return only the personalized content without any additional explanation."""},
            {"role": "user", "content": prompt}
        ]
        
        response_data = gemini_agent.chat_completion(
            messages=messages,
            model="gemini-pro"
        )
        
        if "error" in response_data:
            raise HTTPException(status_code=500, detail=f"Gemini API error: {response_data['error']}")
        
        personalized_content = response_data["choices"][0]["message"]["content"]
        
        return PersonalizeResponse(
            original_content=request.content,
            personalized_content=personalized_content,
            user_id=request.user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error personalizing content: {str(e)}")

@personalize_router.get("/profile/{user_id}")
async def get_user_profile(user_id: str):
    """Get user preferences/profile"""
    try:
        preferences = load_preferences()
        
        if user_id not in preferences:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        user_profile = preferences[user_id]
        user_profile["user_id"] = user_id
        
        return user_profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving profile: {str(e)}")