from abc import ABC, abstractmethod
from typing import Dict, Any, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from models.database import Chapter
from services.chat_service import rag_service


class ContentRetrievalSkillInput(BaseModel):
    query: str = Field(description="The search query for textbook content")
    module_id: int = Field(default=None, description="Optional module ID to narrow search")
    chapter_id: int = Field(default=None, description="Optional chapter ID to narrow search")


class ContentRetrievalSkill(BaseTool, ABC):
    """Skill for retrieving relevant content from the textbook"""

    name: str = "content_retrieval"
    description: str = "Retrieves relevant content from the Physical AI & Humanoid Robotics textbook based on a query"
    args_schema: type = ContentRetrievalSkillInput

    def __init__(self, db_session: Session):
        super().__init__()
        self.db = db_session

    def _run(self, query: str, module_id: int = None, chapter_id: int = None) -> str:
        """Execute the content retrieval skill"""
        try:
            # Get relevant context using the RAG service
            context = rag_service.get_relevant_context(
                db=self.db,
                query=query,
                module_id=module_id,
                chapter_id=chapter_id
            )

            if not context.strip():
                return f"No relevant content found for query: '{query}'"

            return context
        except Exception as e:
            return f"Error retrieving content: {str(e)}"

    async def _arun(self, query: str, module_id: int = None, chapter_id: int = None) -> str:
        """Async version of content retrieval"""
        return self._run(query, module_id, chapter_id)


class ChapterRetrievalSkill(ContentRetrievalSkill):
    """Specialized skill for retrieving specific chapters"""

    name: str = "chapter_retrieval"
    description: str = "Retrieves a specific chapter from the textbook by ID or title"

    def _run(self, query: str, module_id: int = None, chapter_id: int = None) -> str:
        """Retrieve a specific chapter"""
        try:
            if chapter_id:
                # Direct chapter retrieval
                chapter = self.db.query(Chapter).filter(Chapter.id == chapter_id).first()
                if chapter:
                    return f"## {chapter.title}\n\n{chapter.content}"
                else:
                    return f"Chapter with ID {chapter_id} not found"

            elif query:
                # Search by title
                chapter = self.db.query(Chapter).filter(Chapter.title.contains(query)).first()
                if chapter:
                    return f"## {chapter.title}\n\n{chapter.content}"
                else:
                    # Use RAG to find relevant content if chapter not found by title
                    return super()._run(query, module_id, chapter_id)

            return "Please provide either a chapter_id or a query to search for chapters"
        except Exception as e:
            return f"Error retrieving chapter: {str(e)}"


class ModuleRetrievalSkill(ContentRetrievalSkill):
    """Specialized skill for retrieving module information"""

    name: str = "module_retrieval"
    description: str = "Retrieves information about a specific module from the textbook"

    def _run(self, query: str, module_id: int = None, chapter_id: int = None) -> str:
        """Retrieve module information"""
        try:
            # If module_id is provided, retrieve specific module
            if module_id:
                # Get all chapters in the module
                chapters = self.db.query(Chapter).filter(Chapter.module_id == module_id).all()

                if chapters:
                    module_info = f"Module {module_id} contains {len(chapters)} chapters:\n\n"
                    for chapter in chapters:
                        module_info += f"- {chapter.title} (Chapter {chapter.order})\n"
                        module_info += f"  Preview: {chapter.content[:200]}...\n\n"

                    return module_info
                else:
                    return f"No chapters found for module {module_id}"

            # Otherwise, use the parent class method for general content retrieval
            return super()._run(query, module_id, chapter_id)
        except Exception as e:
            return f"Error retrieving module information: {str(e)}"