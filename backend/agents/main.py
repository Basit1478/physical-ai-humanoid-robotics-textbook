from typing import Dict, Any, List
from sqlalchemy.orm import Session

from agents.registry.skill_registry import skill_registry
from agents.skills.content_retrieval_skill import ContentRetrievalSkill, ChapterRetrievalSkill, ModuleRetrievalSkill


class TextbookAgent:
    """Main agent for the Physical AI & Humanoid Robotics textbook"""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.skill_registry = skill_registry

    def process_query(self, query: str, module_id: int = None, chapter_id: int = None) -> Dict[str, Any]:
        """Process a user query using appropriate skills"""
        # Determine which skill to use based on the query
        query_lower = query.lower()

        # Determine the most appropriate skill
        if any(word in query_lower for word in ['chapter', 'section', 'specific']):
            skill_name = 'chapter_retrieval'
        elif any(word in query_lower for word in ['module', 'part', 'topic']):
            skill_name = 'module_retrieval'
        else:
            skill_name = 'content_retrieval'

        # Execute the skill
        result = self.skill_registry.execute_skill(
            skill_name,
            self.db,
            query=query,
            module_id=module_id,
            chapter_id=chapter_id
        )

        return {
            "query": query,
            "skill_used": skill_name,
            "result": result,
            "module_id": module_id,
            "chapter_id": chapter_id
        }

    def get_available_skills(self) -> Dict[str, List[Dict[str, str]]]:
        """Get all available skills in the system"""
        return self.skill_registry.list_available_skills()

    def execute_specific_skill(self, skill_name: str, **params) -> str:
        """Execute a specific skill with provided parameters"""
        return self.skill_registry.execute_skill(skill_name, self.db, **params)

    def search_content(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for content across the textbook"""
        # This would use the RAG system to find relevant content
        from services.chat_service import rag_service

        # For now, we'll use the content retrieval skill
        result = self.skill_registry.execute_skill(
            'content_retrieval',
            self.db,
            query=query,
            module_id=None,
            chapter_id=None
        )

        # Return the result as a list of hits
        return [{
            "score": 1.0,  # Placeholder score
            "content": result,
            "metadata": {"type": "textbook_content"}
        }]

    def get_personalized_response(self, query: str, user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get a response that takes into account the user's profile"""
        # Process the query normally
        response = self.process_query(query)

        # If we have a user profile, we could customize the response
        if user_profile:
            education_level = user_profile.get('education_level', 'intermediate')

            # Customize the response based on education level
            if education_level == 'beginner':
                response['note'] = "Explanation simplified for beginners"
            elif education_level == 'advanced':
                response['note'] = "Technical details included for advanced users"

        return response

    def get_learning_path(self, topic: str) -> Dict[str, Any]:
        """Suggest a learning path for a given topic"""
        # This would analyze the textbook structure and suggest a path
        from services.modules_service import get_modules, get_chapters_by_module

        modules = get_modules(self.db)
        path_suggestions = []

        for module in modules:
            chapters = get_chapters_by_module(self.db, module.id)
            module_contains_topic = any(topic.lower() in chapter.title.lower() or topic.lower() in chapter.content.lower() for chapter in chapters)

            if module_contains_topic:
                path_suggestions.append({
                    "module_id": module.id,
                    "module_name": module.name,
                    "relevant_chapters": [
                        {
                            "chapter_id": chapter.id,
                            "chapter_title": chapter.title,
                            "relevance_score": 1.0 if topic.lower() in chapter.title.lower() else 0.5
                        }
                        for chapter in chapters
                        if topic.lower() in chapter.title.lower() or topic.lower() in chapter.content.lower()
                    ]
                })

        return {
            "topic": topic,
            "suggested_path": path_suggestions,
            "total_modules": len(path_suggestions)
        }


class MultiAgentSystem:
    """System for managing multiple agents with different specializations"""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.agents = {
            "textbook": TextbookAgent(db_session),
            "navigation": self._create_navigation_agent(db_session),
            "personalization": self._create_personalization_agent(db_session),
            "translation": self._create_translation_agent(db_session)
        }

    def _create_navigation_agent(self, db_session):
        """Create an agent specialized in navigation and structure"""
        class NavigationAgent:
            def __init__(self, db):
                self.db = db

            def get_table_of_contents(self):
                from services.modules_service import get_modules, get_chapters_by_module
                modules = get_modules(self.db)
                toc = []
                for module in modules:
                    chapters = get_chapters_by_module(self.db, module.id)
                    toc.append({
                        "module": module.name,
                        "module_id": module.id,
                        "chapters": [{"id": ch.id, "title": ch.title, "order": ch.order} for ch in chapters]
                    })
                return toc

        return NavigationAgent(db_session)

    def _create_personalization_agent(self, db_session):
        """Create an agent specialized in personalization"""
        class PersonalizationAgent:
            def __init__(self, db):
                self.db = db

            def get_personalized_content(self, user_id: int, content_type: str = "chapter"):
                from services.personalization_service import personalization_service
                return personalization_service.get_personalized_content(
                    self.db, user_id, content_type
                )

        return PersonalizationAgent(db_session)

    def _create_translation_agent(self, db_session):
        """Create an agent specialized in translation"""
        class TranslationAgent:
            def __init__(self, db):
                self.db = db

            def translate_content(self, content: str, target_lang: str = "ur"):
                from services.translation_service import translation_service
                return translation_service.translate_text(content, target_lang)

        return TranslationAgent(db_session)

    def route_query(self, query: str, agent_type: str = None) -> Dict[str, Any]:
        """Route a query to the appropriate agent"""
        if agent_type and agent_type in self.agents:
            agent = self.agents[agent_type]
        else:
            # Default to textbook agent
            agent = self.agents["textbook"]

        # Call the appropriate method based on the agent type
        if agent_type == "navigation":
            return agent.get_table_of_contents()
        elif agent_type == "personalization":
            # Need user context for personalization
            return {"error": "User context required for personalization agent"}
        elif agent_type == "translation":
            return {"error": "Content required for translation agent"}
        else:
            # Default behavior for textbook agent
            return agent.process_query(query)


# Global instance of the multi-agent system
def create_agent_system(db_session):
    return MultiAgentSystem(db_session)