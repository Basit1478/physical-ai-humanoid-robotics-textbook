from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models.database import SessionLocal
from models.schemas import TranslationRequest, TranslationResponse
from services.translation_service import translation_service
from auth.better_auth import get_current_user, get_db
from models.database import User, Chapter

router = APIRouter()

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/translation/translate", response_model=TranslationResponse)
def translate_content(
    request: TranslationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Translate content from source language to target language"""
    try:
        translated_content = translation_service.translate_text(
            request.content,
            request.target_language,
            request.source_language
        )

        return TranslationResponse(
            translated_content=translated_content,
            source_language=request.source_language,
            target_language=request.target_language
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error translating content: {str(e)}"
        )

@router.get("/translation/chapter/{chapter_id}")
def translate_chapter(
    chapter_id: int,
    target_language: str = "ur",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Translate an entire chapter to the target language"""
    try:
        # Check if chapter exists
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chapter with id {chapter_id} not found"
            )

        # Try to get existing translation first
        existing_translation = translation_service.get_existing_translation(
            db, chapter_id, "chapter", target_language
        )

        if existing_translation:
            return {
                "chapter_id": chapter_id,
                "original_title": chapter.title,
                "translated_content": existing_translation,
                "target_language": target_language
            }

        # If no existing translation, create new one
        translated_content = translation_service.translate_chapter(
            db, chapter_id, target_language
        )

        return {
            "chapter_id": chapter_id,
            "original_title": chapter.title,
            "translated_content": translated_content,
            "target_language": target_language
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error translating chapter: {str(e)}"
        )

@router.get("/translation/module/{module_id}")
def translate_module(
    module_id: int,
    target_language: str = "ur",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Translate an entire module (all chapters in the module) to the target language"""
    try:
        # Get all chapters in the module
        chapters = db.query(Chapter).filter(Chapter.module_id == module_id).all()

        if not chapters:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No chapters found for module with id {module_id}"
            )

        translated_module = {
            "module_id": module_id,
            "target_language": target_language,
            "chapters": []
        }

        for chapter in chapters:
            # Try to get existing translation first
            existing_translation = translation_service.get_existing_translation(
                db, chapter.id, "chapter", target_language
            )

            if existing_translation:
                translated_content = existing_translation
            else:
                # Create new translation
                translated_content = translation_service.translate_chapter(
                    db, chapter.id, target_language
                )

            translated_module["chapters"].append({
                "chapter_id": chapter.id,
                "original_title": chapter.title,
                "translated_content": translated_content
            })

        return translated_module
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error translating module: {str(e)}"
        )

@router.post("/translation/batch")
def batch_translate(
    contents: list,
    target_language: str = "ur",
    current_user: User = Depends(get_current_user)
):
    """Translate multiple contents at once"""
    try:
        translated_contents = translation_service.batch_translate(contents, target_language)

        return {
            "target_language": target_language,
            "translations": [
                {"original": original, "translated": translated}
                for original, translated in zip(contents, translated_contents)
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error batch translating: {str(e)}"
        )

@router.get("/translation/languages")
def get_supported_languages():
    """Get list of supported languages for translation"""
    return {
        "supported_languages": [
            {"code": "ur", "name": "Urdu"},
            {"code": "es", "name": "Spanish"},
            {"code": "fr", "name": "French"},
            {"code": "de", "name": "German"},
            {"code": "zh", "name": "Chinese"},
            {"code": "ja", "name": "Japanese"},
            {"code": "ar", "name": "Arabic"}
        ],
        "default_target": "ur"
    }

@router.get("/translation/history")
def get_translation_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get user's translation history"""
    try:
        # Get all translations associated with user's activities
        # This could be expanded to track user's translation requests
        return {
            "user_id": current_user.id,
            "message": "Translation history feature - in a full implementation, this would track user's translation activities"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving translation history: {str(e)}"
        )