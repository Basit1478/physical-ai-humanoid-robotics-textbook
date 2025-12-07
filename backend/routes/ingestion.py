from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import tempfile
import os

from models.database import SessionLocal
from models.schemas import Module, Chapter
from services.ingestion_service import ingestion_service
from auth.better_auth import get_current_user, get_db
from models.database import User

router = APIRouter()

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/ingestion/module", response_model=Module)
def create_module(
    name: str,
    description: str,
    order: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Create a new module in the textbook"""
    try:
        from services.ingestion_service import ingestion_service
        module = ingestion_service.ingest_module(db, name, description, order)
        return module
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating module: {str(e)}"
        )

@router.post("/ingestion/chapter", response_model=Chapter)
def create_chapter(
    module_id: int,
    title: str,
    content: str,
    order: int = 1,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Create a new chapter in a module"""
    try:
        chapter = ingestion_service.ingest_with_validation(db, module_id, title, content, order)
        return chapter
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating chapter: {str(e)}"
        )

@router.post("/ingestion/chapters/bulk")
def bulk_create_chapters(
    module_id: int,
    chapters_data: List[dict],  # Using dict instead of Pydantic model for flexibility
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Create multiple chapters in a module at once"""
    try:
        chapters = ingestion_service.bulk_ingest_chapters(db, module_id, chapters_data)
        return {"message": f"Successfully created {len(chapters)} chapters", "chapters": chapters}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating chapters in bulk: {str(e)}"
        )

@router.post("/ingestion/upload")
def upload_file(
    file: UploadFile = File(...),
    module_id: int = None,
    title: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Upload a file and ingest its content"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file.write(file.file.read())
            temp_file_path = temp_file.name

        try:
            # Ingest the file content
            chapter = ingestion_service.ingest_from_file(db, temp_file_path, module_id, title)
            return {
                "message": f"Successfully ingested {file.filename}",
                "chapter": chapter
            }
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading and ingesting file: {str(e)}"
        )

@router.put("/ingestion/chapter/{chapter_id}")
def update_chapter(
    chapter_id: int,
    content: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Update an existing chapter and regenerate embeddings"""
    try:
        updated_chapter = ingestion_service.update_chapter_content(db, chapter_id, content)
        return {
            "message": f"Successfully updated chapter {chapter_id}",
            "chapter": updated_chapter
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating chapter: {str(e)}"
        )

@router.post("/ingestion/validate")
def validate_content(
    content: str,
    current_user: User = Depends(get_current_user)
):
    """Validate content without ingesting it"""
    try:
        validation_result = ingestion_service.validate_content(content)
        return validation_result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating content: {str(e)}"
        )

@router.post("/ingestion/textbook-structure")
def ingest_textbook_structure(
    textbook_data: dict,  # Using dict for flexibility
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Ingest an entire textbook structure with modules and chapters"""
    try:
        result = ingestion_service.ingest_textbook_structure(db, textbook_data)
        return {
            "message": "Successfully ingested textbook structure",
            "modules_created": len(result["modules"]),
            "chapters_created": len(result["chapters"]),
            "details": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting textbook structure: {str(e)}"
        )

@router.get("/ingestion/status")
def ingestion_status():
    """Get ingestion service status"""
    return {
        "status": "available",
        "supported_formats": ingestion_service.supported_formats,
        "message": "Ingestion service is ready to accept content"
    }