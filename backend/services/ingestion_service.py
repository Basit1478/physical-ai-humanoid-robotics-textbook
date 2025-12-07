import asyncio
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import os
import hashlib
from pathlib import Path

from models.database import Chapter, Module, Embedding
from services.chat_service import rag_service


class IngestionService:
    def __init__(self):
        self.supported_formats = ['.md', '.txt', '.pdf', '.docx']  # Supported document formats

    def ingest_chapter_content(self, db: Session, module_id: int, title: str, content: str, order: int = 1):
        """Ingest a new chapter into the system"""
        # Create a new chapter
        chapter = Chapter(
            module_id=module_id,
            title=title,
            content=content,
            order=order
        )
        db.add(chapter)
        db.commit()
        db.refresh(chapter)

        # Generate embeddings for the chapter
        rag_service.create_embeddings_for_chapter(db, chapter.id)

        return chapter

    def ingest_module(self, db: Session, name: str, description: str, order: int):
        """Ingest a new module into the system"""
        module = Module(
            name=name,
            description=description,
            order=order
        )
        db.add(module)
        db.commit()
        db.refresh(module)

        return module

    def bulk_ingest_chapters(self, db: Session, module_id: int, chapters_data: List[Dict[str, Any]]):
        """Bulk ingest multiple chapters for a module"""
        created_chapters = []
        for idx, chapter_data in enumerate(chapters_data):
            chapter = self.ingest_chapter_content(
                db=db,
                module_id=module_id,
                title=chapter_data.get('title', f'Chapter {idx+1}'),
                content=chapter_data.get('content', ''),
                order=chapter_data.get('order', idx+1)
            )
            created_chapters.append(chapter)

        return created_chapters

    def ingest_from_file(self, db: Session, file_path: str, module_id: int, title: str = None):
        """Ingest content from a file"""
        file_ext = Path(file_path).suffix.lower()

        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}. Supported formats: {self.supported_formats}")

        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Use filename as title if not provided
        if title is None:
            title = Path(file_path).stem

        # Get the order based on existing chapters in the module
        existing_chapters = db.query(Chapter).filter(Chapter.module_id == module_id).all()
        order = len(existing_chapters) + 1

        # Ingest the content
        return self.ingest_chapter_content(
            db=db,
            module_id=module_id,
            title=title,
            content=content,
            order=order
        )

    def update_chapter_content(self, db: Session, chapter_id: int, new_content: str):
        """Update an existing chapter and regenerate embeddings"""
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            raise ValueError(f"Chapter with id {chapter_id} not found")

        # Update the content
        chapter.content = new_content
        db.commit()

        # Regenerate embeddings for the updated chapter
        rag_service.create_embeddings_for_chapter(db, chapter_id)

        return chapter

    def ingest_textbook_structure(self, db: Session, textbook_data: Dict[str, Any]):
        """Ingest an entire textbook structure with modules and chapters"""
        created_modules = []
        created_chapters = []

        for module_data in textbook_data.get('modules', []):
            # Create module
            module = self.ingest_module(
                db=db,
                name=module_data['name'],
                description=module_data.get('description', ''),
                order=module_data['order']
            )
            created_modules.append(module)

            # Create chapters for the module
            for chapter_data in module_data.get('chapters', []):
                chapter = self.ingest_chapter_content(
                    db=db,
                    module_id=module.id,
                    title=chapter_data['title'],
                    content=chapter_data['content'],
                    order=chapter_data.get('order', 1)
                )
                created_chapters.append(chapter)

        return {
            "modules": created_modules,
            "chapters": created_chapters
        }

    def validate_content(self, content: str) -> Dict[str, Any]:
        """Validate content before ingestion"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "content_length": len(content),
            "word_count": len(content.split()),
            "contains_code": "```" in content or "`" in content,
            "contains_diagrams": "diagram" in content.lower() or "figure" in content.lower()
        }

        # Check for minimum content length
        if len(content) < 50:
            validation_result["warnings"].append("Content is quite short (< 50 characters)")

        # Check for excessive length
        if len(content) > 100000:  # 100k characters
            validation_result["warnings"].append("Content is very long (> 100k characters)")

        # Check for balanced markdown elements
        if content.count("#") != content.count("\n#") + 1:  # Basic header check
            validation_result["warnings"].append("Potential markdown formatting issues")

        return validation_result

    def hash_content(self, content: str) -> str:
        """Generate a hash for content to check for duplicates"""
        return hashlib.sha256(content.encode()).hexdigest()

    def check_duplicate_content(self, db: Session, content: str) -> bool:
        """Check if content already exists in the database"""
        content_hash = self.hash_content(content)
        # This would require adding a content_hash field to Chapter table
        # For now, we'll do a simple check based on title and approximate length
        chapters = db.query(Chapter).all()
        for chapter in chapters:
            if (abs(len(chapter.content) - len(content)) < 100 and  # Length within 100 chars
                chapter.content[:50] == content[:50]):  # First 50 chars match
                return True
        return False

    def ingest_with_validation(self, db: Session, module_id: int, title: str, content: str, order: int = 1):
        """Ingest content with validation"""
        # Validate content
        validation = self.validate_content(content)
        if not validation["valid"]:
            raise ValueError(f"Content validation failed: {validation['errors']}")

        # Check for duplicates
        if self.check_duplicate_content(db, content):
            raise ValueError("Content appears to be a duplicate of existing content")

        # Ingest the validated content
        return self.ingest_chapter_content(db, module_id, title, content, order)


# Global instance of the ingestion service
ingestion_service = IngestionService()