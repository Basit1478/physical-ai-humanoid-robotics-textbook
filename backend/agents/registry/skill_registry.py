from typing import Dict, List, Type, Callable
from abc import ABC
from langchain.tools import BaseTool

from agents.skills.content_retrieval_skill import (
    ContentRetrievalSkill,
    ChapterRetrievalSkill,
    ModuleRetrievalSkill
)


class SkillRegistry:
    """Registry for managing and accessing skills across the system"""

    def __init__(self):
        self._skills: Dict[str, Type[BaseTool]] = {}
        self._instances: Dict[str, BaseTool] = {}
        self._skill_categories: Dict[str, List[str]] = {}

        # Register default skills
        self.register_skill("content_retrieval", ContentRetrievalSkill)
        self.register_skill("chapter_retrieval", ChapterRetrievalSkill)
        self.register_skill("module_retrieval", ModuleRetrievalSkill)

    def register_skill(self, name: str, skill_class: Type[BaseTool], category: str = "general"):
        """Register a new skill with the registry"""
        self._skills[name] = skill_class

        # Add to category
        if category not in self._skill_categories:
            self._skill_categories[category] = []
        self._skill_categories[category].append(name)

        # Clear any existing instance
        if name in self._instances:
            del self._instances[name]

    def get_skill_class(self, name: str) -> Type[BaseTool]:
        """Get the class of a registered skill"""
        if name not in self._skills:
            raise KeyError(f"Skill '{name}' is not registered")
        return self._skills[name]

    def create_skill_instance(self, name: str, **kwargs) -> BaseTool:
        """Create an instance of a registered skill"""
        skill_class = self.get_skill_class(name)

        # Create instance with provided kwargs
        instance = skill_class(**kwargs)
        self._instances[name] = instance

        return instance

    def get_skill_instance(self, name: str, **kwargs) -> BaseTool:
        """Get an instance of a skill, creating it if it doesn't exist"""
        if name in self._instances:
            return self._instances[name]

        # Create new instance if it doesn't exist
        return self.create_skill_instance(name, **kwargs)

    def get_skills_by_category(self, category: str) -> List[str]:
        """Get all skills in a specific category"""
        return self._skill_categories.get(category, [])

    def get_all_skill_names(self) -> List[str]:
        """Get all registered skill names"""
        return list(self._skills.keys())

    def get_all_categories(self) -> List[str]:
        """Get all skill categories"""
        return list(self._skill_categories.keys())

    def unregister_skill(self, name: str):
        """Remove a skill from the registry"""
        if name in self._skills:
            del self._skills[name]

        if name in self._instances:
            del self._instances[name]

        # Remove from categories
        for category, skills in self._skill_categories.items():
            if name in skills:
                skills.remove(name)

    def get_skill_description(self, name: str) -> str:
        """Get the description of a registered skill"""
        skill_class = self.get_skill_class(name)
        return getattr(skill_class, 'description', 'No description available')

    def get_skill_info(self, name: str) -> Dict[str, str]:
        """Get comprehensive information about a skill"""
        skill_class = self.get_skill_class(name)

        return {
            'name': name,
            'description': getattr(skill_class, 'description', 'No description available'),
            'category': self._get_skill_category(name),
            'class_name': skill_class.__name__
        }

    def _get_skill_category(self, name: str) -> str:
        """Get the category of a skill"""
        for category, skills in self._skill_categories.items():
            if name in skills:
                return category
        return "uncategorized"

    def execute_skill(self, name: str, db_session, **params) -> str:
        """Execute a skill with the given parameters"""
        skill_instance = self.get_skill_instance(name, db_session=db_session)

        try:
            # For LangChain tools, use the .run() method
            if hasattr(skill_instance, 'run'):
                return skill_instance.run(**params)
            elif hasattr(skill_instance, '_run'):
                return skill_instance._run(**params)
            else:
                raise AttributeError(f"Skill {name} doesn't have a run method")
        except Exception as e:
            return f"Error executing skill {name}: {str(e)}"

    def list_available_skills(self) -> Dict[str, List[Dict[str, str]]]:
        """List all available skills with their information"""
        result = {}

        for category in self.get_all_categories():
            skills_in_category = self.get_skills_by_category(category)
            result[category] = [
                self.get_skill_info(skill_name)
                for skill_name in skills_in_category
            ]

        # Add uncategorized skills
        categorized_skills = set()
        for skills in self._skill_categories.values():
            categorized_skills.update(skills)

        uncategorized = [name for name in self.get_all_skill_names() if name not in categorized_skills]
        if uncategorized:
            result['uncategorized'] = [
                self.get_skill_info(skill_name)
                for skill_name in uncategorized
            ]

        return result


# Global instance of the skill registry
skill_registry = SkillRegistry()