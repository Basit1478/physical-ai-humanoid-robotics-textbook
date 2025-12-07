from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from datetime import datetime

from models.database import Module, Chapter, UserProgress
from models.schemas import ProgressBase


def get_modules(db: Session, skip: int = 0, limit: int = 100):
    """Get all modules"""
    return db.query(Module).offset(skip).limit(limit).all()


def get_module_by_id(db: Session, module_id: int):
    """Get a specific module by ID"""
    return db.query(Module).filter(Module.id == module_id).first()


def get_chapters_by_module(db: Session, module_id: int):
    """Get all chapters for a specific module"""
    return db.query(Chapter).filter(Chapter.module_id == module_id).order_by(Chapter.order).all()


def get_chapter_by_id(db: Session, chapter_id: int):
    """Get a specific chapter by ID"""
    return db.query(Chapter).filter(Chapter.id == chapter_id).first()


def get_user_progress(db: Session, user_id: int):
    """Get progress for a specific user"""
    return db.query(UserProgress).filter(UserProgress.user_id == user_id).all()


def update_user_progress(
    db: Session,
    user_id: int,
    chapter_id: int,
    completed: bool,
    notes: str = None,
    rating: int = None
):
    """Update or create progress for a user and chapter"""
    # Check if progress record already exists
    progress = db.query(UserProgress).filter(
        and_(
            UserProgress.user_id == user_id,
            UserProgress.chapter_id == chapter_id
        )
    ).first()

    if progress:
        # Update existing progress
        progress.completed = completed
        progress.notes = notes
        progress.rating = rating
        progress.updated_at = datetime.utcnow()
    else:
        # Create new progress record
        progress = UserProgress(
            user_id=user_id,
            chapter_id=chapter_id,
            completed=completed,
            notes=notes,
            rating=rating
        )
        db.add(progress)

    db.commit()
    db.refresh(progress)
    return progress


def get_completed_chapters(db: Session, user_id: int):
    """Get all completed chapters for a user"""
    return db.query(UserProgress).filter(
        and_(
            UserProgress.user_id == user_id,
            UserProgress.completed == True
        )
    ).all()


def get_chapter_content(db: Session, chapter_id: int):
    """Get the content of a specific chapter"""
    chapter = get_chapter_by_id(db, chapter_id)
    if chapter:
        return chapter.content
    return None


def get_learning_outcomes(db: Session, chapter_id: int):
    """Get the learning outcomes of a specific chapter"""
    chapter = get_chapter_by_id(db, chapter_id)
    if chapter:
        return chapter.learning_outcomes
    return None


def get_chapter_summary(db: Session, chapter_id: int):
    """Get the summary of a specific chapter"""
    chapter = get_chapter_by_id(db, chapter_id)
    if chapter:
        return chapter.summary
    return None