from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import os
import uuid
from datetime import datetime

app = FastAPI(title="Personalization Service", version="1.0.0")

# User preferences storage (in production, use a proper database)
PREFERENCES_FILE = "user_preferences.json"

class PersonalizeRequest(BaseModel):
    user_id: str
    content_type: str
    user_preferences: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None

class PersonalizeResponse(BaseModel):
    personalized_content: str
    user_id: str
    content_type: str
    suggestions: List[str]

class UserPreferences(BaseModel):
    user_id: str
    preferences: Dict[str, Any]
    updated_at: str

@app.post("/personalize", response_model=PersonalizeResponse)
async def personalize_content(request: PersonalizeRequest):
    # In a real implementation, you would use the user preferences to personalize content
    # For now, return a mock personalized response
    suggestions = [
        "Based on your background, you might find this section interesting",
        "Recommended for users with similar interests",
        "Related content you may enjoy"
    ]

    return PersonalizeResponse(
        personalized_content=f"Personalized content for {request.content_type} based on user preferences",
        user_id=request.user_id,
        content_type=request.content_type,
        suggestions=suggestions
    )

@app.post("/preferences", response_model=UserPreferences)
async def set_user_preferences(request: UserPreferences):
    preferences = load_preferences()

    user_id = request.user_id
    preferences[user_id] = {
        "preferences": request.preferences,
        "updated_at": request.updated_at
    }

    save_preferences(preferences)

    return request

@app.get("/preferences/{user_id}", response_model=UserPreferences)
async def get_user_preferences(user_id: str):
    preferences = load_preferences()

    user_prefs = preferences.get(user_id)
    if not user_prefs:
        raise HTTPException(status_code=404, detail="User preferences not found")

    return UserPreferences(
        user_id=user_id,
        preferences=user_prefs["preferences"],
        updated_at=user_prefs["updated_at"]
    )

def load_preferences():
    if os.path.exists(PREFERENCES_FILE):
        with open(PREFERENCES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_preferences(preferences):
    with open(PREFERENCES_FILE, 'w') as f:
        json.dump(preferences, f)

@app.get("/")
async def root():
    return {"message": "Personalization Service", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)