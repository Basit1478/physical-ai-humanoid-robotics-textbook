from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from models.database import SessionLocal
from agents.main import create_agent_system
from auth.better_auth import get_current_user, get_db
from models.database import User

router = APIRouter()

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/agents/query")
def query_agent(
    query: str,
    module_id: int = None,
    chapter_id: int = None,
    agent_type: str = "textbook",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Query the appropriate agent for textbook content"""
    try:
        agent_system = create_agent_system(db)
        result = agent_system.route_query(query, agent_type)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying agent: {str(e)}"
        )

@router.get("/agents/skills")
def get_available_skills(
    current_user: User = Depends(get_current_user)
):
    """Get all available skills in the system"""
    try:
        from agents.registry.skill_registry import skill_registry
        return skill_registry.list_available_skills()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting available skills: {str(e)}"
        )

@router.post("/agents/personalized-query")
def query_with_personalization(
    query: str,
    module_id: int = None,
    chapter_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Query the textbook with personalization based on user profile"""
    try:
        from services.personalization_service import personalization_service

        # Get user profile
        user_profile = personalization_service.get_user_profile(db, current_user.id)

        # Create agent and get personalized response
        agent_system = create_agent_system(db)
        textbook_agent = agent_system.agents["textbook"]

        response = textbook_agent.get_personalized_response(query,
            {
                "education_level": user_profile.education_level if user_profile else "intermediate",
                "field_of_study": user_profile.field_of_study if user_profile else "general",
                "background": user_profile.background if user_profile else "general"
            } if user_profile else None
        )

        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying with personalization: {str(e)}"
        )

@router.get("/agents/learning-path/{topic}")
def get_learning_path(
    topic: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get a suggested learning path for a specific topic"""
    try:
        agent_system = create_agent_system(db)
        textbook_agent = agent_system.agents["textbook"]

        path = textbook_agent.get_learning_path(topic)
        return path
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting learning path: {str(e)}"
        )

@router.get("/agents/table-of-contents")
def get_table_of_contents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get the table of contents for the textbook"""
    try:
        agent_system = create_agent_system(db)
        navigation_agent = agent_system.agents["navigation"]

        toc = navigation_agent.get_table_of_contents()
        return {"table_of_contents": toc}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting table of contents: {str(e)}"
        )

@router.post("/agents/translate-query")
def query_with_translation(
    query: str,
    target_language: str = "ur",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Query the textbook and translate the response"""
    try:
        from services.translation_service import translation_service

        # First get the response in English
        agent_system = create_agent_system(db)
        textbook_agent = agent_system.agents["textbook"]

        response = textbook_agent.process_query(query)

        # Then translate the result
        if isinstance(response.get("result"), str):
            translated_result = translation_service.translate_text(
                response["result"],
                target_language
            )
            response["translated_result"] = translated_result
            response["target_language"] = target_language

        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error querying with translation: {str(e)}"
        )