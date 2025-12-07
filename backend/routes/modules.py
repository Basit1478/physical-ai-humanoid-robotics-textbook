from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models.database import SessionLocal
from models.schemas import Module, Chapter, Progress, ProgressBase
from services.modules_service import (
    get_modules,
    get_module_by_id,
    get_chapters_by_module,
    get_chapter_by_id,
    get_user_progress,
    update_user_progress
)
from auth.better_auth import get_current_user, get_db
from models.database import User

router = APIRouter()

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/modules", response_model=List[Module])
def read_modules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    """Get all modules"""
    modules = get_modules(db, skip=skip, limit=limit)
    return modules

@router.get("/modules/{module_id}", response_model=Module)
def read_module(module_id: int, db: Session = Depends(get_db_session)):
    """Get a specific module by ID"""
    module = get_module_by_id(db, module_id=module_id)
    if module is None:
        raise HTTPException(status_code=404, detail="Module not found")
    return module

@router.get("/modules/{module_id}/chapters", response_model=List[Chapter])
def read_chapters(module_id: int, db: Session = Depends(get_db_session)):
    """Get all chapters for a specific module"""
    chapters = get_chapters_by_module(db, module_id=module_id)
    return chapters

@router.get("/chapters/{chapter_id}", response_model=Chapter)
def read_chapter(chapter_id: int, db: Session = Depends(get_db_session)):
    """Get a specific chapter by ID"""
    chapter = get_chapter_by_id(db, chapter_id=chapter_id)
    if chapter is None:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter

@router.get("/users/me/progress", response_model=List[Progress])
def read_user_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Get progress for the current user"""
    progress = get_user_progress(db, user_id=current_user.id)
    return progress

@router.post("/users/me/progress", response_model=Progress)
def update_user_progress_endpoint(
    progress: ProgressBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    """Update progress for the current user"""
    updated_progress = update_user_progress(
        db,
        user_id=current_user.id,
        chapter_id=progress.chapter_id,
        completed=progress.completed,
        notes=progress.notes,
        rating=progress.rating
    )
    return updated_progress