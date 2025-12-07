from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models.database import SessionLocal
from models.schemas import PersonalizationRequest, PersonalizationResponse, Profile
from services.personalization_service import personalization_service
from auth.better_auth import get_current_user, get_db
from models.database import User

router = APIRouter()

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/personalization/profile", response_model=Profile)
def set_user_profile(
    profile_data: PersonalizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Set or update user profile for personalization"""
    try:
        profile = personalization_service.create_or_update_profile(db, current_user.id, profile_data)
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error setting user profile: {str(e)}"
        )

@router.get("/personalization/profile", response_model=Profile)
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get user profile"""
    try:
        profile = personalization_service.get_user_profile(db, current_user.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user profile: {str(e)}"
        )

@router.get("/personalization/content")
def get_personalized_content(
    content_type: str = "chapter",
    module_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get personalized content recommendations"""
    try:
        personalized_content = personalization_service.get_personalized_content(
            db, current_user.id, content_type, module_id
        )
        return personalized_content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting personalized content: {str(e)}"
        )

@router.get("/personalization/path")
def get_adaptive_learning_path(
    current_module: int = 1,
    current_chapter: int = 1,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get adaptive learning path based on user profile and progress"""
    try:
        path = personalization_service.get_adaptive_path(
            db, current_user.id, current_module, current_chapter
        )
        return path
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting adaptive learning path: {str(e)}"
        )

@router.post("/personalization/preferences")
def update_learning_preferences(
    preferences: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Update learning preferences without affecting other profile data"""
    try:
        # Get existing profile
        profile = personalization_service.get_user_profile(db, current_user.id)

        if not profile:
            # Create a new profile with just the preferences
            profile_data = PersonalizationRequest(
                learning_preferences=preferences
            )
            profile = personalization_service.create_or_update_profile(db, current_user.id, profile_data)
        else:
            # Update just the learning preferences
            profile.learning_preferences = str(preferences)
            db.commit()
            db.refresh(profile)

        return {"message": "Learning preferences updated successfully", "profile": profile}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating learning preferences: {str(e)}"
        )