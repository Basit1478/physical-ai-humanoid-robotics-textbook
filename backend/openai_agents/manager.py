from typing import Dict, Any, List, Optional
from openai import OpenAI
from openai.types.beta import Assistant
from openai.types.beta.threads import Thread, Message
from openai.types.beta.threads.run import Run
import json
from sqlalchemy.orm import Session

from config import settings
from models.database import User
from services.chat_service import rag_service
from services.personalization_service import personalization_service
from services.translation_service import translation_service

class OpenAIAgentManager:
    """Manager for OpenAI Agents SDK integration"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.assistants = {}

    def create_textbook_assistant(self) -> Assistant:
        """Create an assistant specialized for the textbook"""
        if "textbook_assistant" in self.assistants:
            return self.assistants["textbook_assistant"]

        assistant = self.client.beta.assistants.create(
            name="Physical AI Textbook Assistant",
            instructions="""You are an expert assistant for the Physical AI & Humanoid Robotics textbook.
            Your role is to help students understand concepts from the textbook, answer questions,
            and provide personalized learning experiences. Use the provided functions to retrieve
            content, personalize responses, and translate when needed.""",
            model="gpt-4-turbo",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "retrieve_textbook_content",
                        "description": "Retrieve relevant content from the textbook based on a query",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The search query for textbook content"
                                },
                                "module_id": {
                                    "type": "integer",
                                    "description": "Optional module ID to narrow search"
                                },
                                "chapter_id": {
                                    "type": "integer",
                                    "description": "Optional chapter ID to narrow search"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_personalized_content",
                        "description": "Get personalized content based on user profile",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {
                                    "type": "integer",
                                    "description": "User ID to get personalized content for"
                                },
                                "content_type": {
                                    "type": "string",
                                    "description": "Type of content to personalize"
                                }
                            },
                            "required": ["user_id"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "translate_content",
                        "description": "Translate content to a target language",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "text": {
                                    "type": "string",
                                    "description": "Text to translate"
                                },
                                "target_language": {
                                    "type": "string",
                                    "description": "Target language code (e.g., 'ur' for Urdu)"
                                }
                            },
                            "required": ["text", "target_language"]
                        }
                    }
                }
            ]
        )

        self.assistants["textbook_assistant"] = assistant
        return assistant

    def create_thread(self) -> Thread:
        """Create a new conversation thread"""
        return self.client.beta.threads.create()

    def add_message_to_thread(self, thread_id: str, content: str) -> Message:
        """Add a message to a thread"""
        return self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=content
        )

    def run_assistant(self, thread_id: str, assistant_id: str) -> Run:
        """Run the assistant on a thread"""
        return self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )

    def get_run_status(self, thread_id: str, run_id: str) -> Run:
        """Get the status of a run"""
        return self.client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )

    def get_messages(self, thread_id: str) -> List[Message]:
        """Get messages from a thread"""
        return self.client.beta.threads.messages.list(thread_id=thread_id).data

# Global instance
agent_manager = OpenAIAgentManager()