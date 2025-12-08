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

@router.post("/personalization/urdu-mode")
def enable_urdu_personalization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Enable Urdu personalization mode for the user"""
    try:
        # Get existing profile or create new one
        profile = personalization_service.get_user_profile(db, current_user.id)

        if not profile:
            # Create a new profile with Urdu preferences
            profile_data = PersonalizationRequest(
                education_level="intermediate",
                field_of_study="robotics",
                background="general",
                learning_preferences={
                    "language_preference": "urdu",
                    "visual_learner": True,
                    "hands_on": True
                }
            )
            profile = personalization_service.create_or_update_profile(db, current_user.id, profile_data)
        else:
            # Update existing profile to include Urdu preferences
            learning_prefs = {}
            if profile.learning_preferences:
                try:
                    import json
                    learning_prefs = json.loads(profile.learning_preferences)
                except:
                    pass

            learning_prefs["language_preference"] = "urdu"
            learning_prefs["visual_learner"] = True
            learning_prefs["hands_on"] = True

            profile.learning_preferences = str(learning_prefs)
            profile.field_of_study = profile.field_of_study or "robotics"
            profile.education_level = profile.education_level or "intermediate"
            db.commit()
            db.refresh(profile)

        return {
            "message": "Urdu personalization mode enabled successfully",
            "profile": {
                "id": profile.id,
                "user_id": profile.user_id,
                "name": getattr(profile, 'name', None),
                "education_level": profile.education_level,
                "field_of_study": profile.field_of_study,
                "background": profile.background,
                "language_preference": "urdu"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enabling Urdu personalization: {str(e)}"
        )

@router.get("/personalization/urdu-status")
def get_urdu_personalization_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get the current Urdu personalization status for the user"""
    try:
        profile = personalization_service.get_user_profile(db, current_user.id)

        if not profile:
            return {
                "urdu_mode_enabled": False,
                "message": "No profile found. Create a profile to enable Urdu personalization."
            }

        # Check if Urdu preference is set
        is_urdu_enabled = False
        if profile.learning_preferences:
            try:
                import json
                prefs = json.loads(profile.learning_preferences)
                is_urdu_enabled = prefs.get("language_preference") == "urdu"
            except:
                pass

        return {
            "urdu_mode_enabled": is_urdu_enabled,
            "profile": {
                "id": profile.id,
                "user_id": profile.user_id,
                "name": getattr(profile, 'name', None),
                "education_level": profile.education_level,
                "field_of_study": profile.field_of_study,
                "background": profile.background
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting Urdu personalization status: {str(e)}"
        )