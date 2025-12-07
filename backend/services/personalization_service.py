from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import json

from models.database import UserProfile, User
from models.schemas import PersonalizationRequest, Profile


class PersonalizationService:
    def __init__(self):
        pass

    def get_user_profile(self, db: Session, user_id: int):
        """Get user profile"""
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        return profile

    def create_or_update_profile(self, db: Session, user_id: int, profile_data: PersonalizationRequest):
        """Create or update user profile"""
        # Check if profile already exists
        profile = self.get_user_profile(db, user_id)

        if profile:
            # Update existing profile
            if profile_data.education_level is not None:
                profile.education_level = profile_data.education_level
            if profile_data.field_of_study is not None:
                profile.field_of_study = profile_data.field_of_study
            if profile_data.background is not None:
                profile.background = profile_data.background
            if profile_data.learning_preferences is not None:
                profile.learning_preferences = json.dumps(profile_data.learning_preferences)
        else:
            # Create new profile
            profile = UserProfile(
                user_id=user_id,
                education_level=profile_data.education_level,
                field_of_study=profile_data.field_of_study,
                background=profile_data.background,
                learning_preferences=json.dumps(profile_data.learning_preferences) if profile_data.learning_preferences else None
            )
            db.add(profile)

        db.commit()
        db.refresh(profile)
        return profile

    def get_personalized_content(self, db: Session, user_id: int, content_type: str = "chapter", module_id: Optional[int] = None):
        """Get personalized content based on user profile"""
        profile = self.get_user_profile(db, user_id)

        if not profile:
            # Return default content if no profile
            return {
                "message": "Default content provided. Create a profile for personalized experience.",
                "difficulty_level": "intermediate",
                "recommended_sections": ["introduction", "examples", "exercises"]
            }

        # Determine difficulty level based on education level
        difficulty_mapping = {
            "beginner": "basic concepts with detailed explanations",
            "intermediate": "standard explanations with examples",
            "advanced": "concise explanations with advanced concepts"
        }

        difficulty_level = profile.education_level if profile.education_level else "intermediate"

        # Customize recommendations based on user's field of study and background
        field_recommendations = {
            "computer science": ["algorithmic aspects", "programming examples"],
            "electrical engineering": ["hardware aspects", "circuit designs"],
            "mechanical engineering": ["kinematics", "dynamics"],
            "robotics": ["integration aspects", "control systems"]
        }

        recommended_sections = ["introduction", "examples", "exercises"]

        if profile.field_of_study and profile.field_of_study.lower() in field_recommendations:
            recommended_sections.extend(field_recommendations[profile.field_of_study.lower()])

        if profile.background and "mathematics" in profile.background.lower():
            recommended_sections.append("mathematical foundations")

        return {
            "message": f"Content personalized for {profile.education_level} level in {profile.field_of_study or 'general'} field",
            "difficulty_level": difficulty_mapping.get(difficulty_level, "standard explanations"),
            "recommended_sections": recommended_sections,
            "learning_style_suggestions": self._get_learning_style_suggestions(profile)
        }

    def _get_learning_style_suggestions(self, profile: UserProfile):
        """Get learning style suggestions based on profile"""
        if not profile.learning_preferences:
            return ["read text", "view diagrams", "try examples"]

        try:
            prefs = json.loads(profile.learning_preferences)
            suggestions = []

            if prefs.get("visual_learner", False):
                suggestions.append("focus on diagrams and visual aids")

            if prefs.get("hands_on", False):
                suggestions.append("try implementation examples")

            if prefs.get("theory_focused", False):
                suggestions.append("read mathematical foundations")

            if prefs.get("application_focused", False):
                suggestions.append("focus on practical examples")

            return suggestions
        except:
            return ["read text", "view diagrams", "try examples"]

    def get_adaptive_path(self, db: Session, user_id: int, current_module: int, current_chapter: int):
        """Get adaptive learning path based on user progress and profile"""
        profile = self.get_user_profile(db, user_id)

        # Default path
        adaptive_path = {
            "continue_with": f"module_{current_module}_chapter_{current_chapter + 1}",
            "alternatives": [],
            "difficulty_adjustment": "maintain"
        }

        if profile:
            # Adjust based on education level
            if profile.education_level == "beginner":
                adaptive_path["difficulty_adjustment"] = "reduce"
                adaptive_path["alternatives"].append("review_prerequisites")
            elif profile.education_level == "advanced":
                adaptive_path["difficulty_adjustment"] = "increase"
                adaptive_path["alternatives"].append("skip_basics")
                adaptive_path["alternatives"].append("advanced_topics")

            # Adjust based on field of study
            if profile.field_of_study and "robotics" in profile.field_of_study.lower():
                adaptive_path["alternatives"].append("more_practical_examples")

        return adaptive_path


# Global instance of the personalization service
personalization_service = PersonalizationService()