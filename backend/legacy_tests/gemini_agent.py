#!/usr/bin/env python3
"""
Gemini API Agent using Google Generative AI SDK
"""

import google.generativeai as genai
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it in your .env file.")
genai.configure(api_key=GEMINI_API_KEY)

class GeminiAgent:
    def __init__(self, model_name="gemini-pro"):
        """
        Initialize Gemini Agent
        """
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        self.chat = self.model.start_chat(history=[])

    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text response from Gemini
        """
        try:
            response = self.model.generate_content(prompt, **kwargs)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def chat_message(self, message: str) -> str:
        """
        Send message in chat context
        """
        try:
            response = self.chat.send_message(message)
            return response.text
        except Exception as e:
            return f"Error in chat: {str(e)}"

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model
        """
        return {
            "model_name": self.model_name,
            "api_key_configured": bool(GEMINI_API_KEY),
            "available_models": [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        }

class UrduTranslationAgent(GeminiAgent):
    def __init__(self):
        super().__init__("gemini-pro")

    def translate_to_urdu(self, text: str) -> str:
        """
        Translate English text to Urdu using Gemini
        """
        prompt = f"""
        Translate the following English text to Urdu:
        "{text}"

        Provide only the Urdu translation without any additional explanation.
        """
        return self.generate_text(prompt)

class PersonalizationAgent(GeminiAgent):
    def __init__(self):
        super().__init__("gemini-pro")
        self.user_profiles = {}

    def create_user_profile(self, user_id: str, interests: List[str], level: str = "beginner") -> Dict:
        """
        Create a user profile for personalization
        """
        self.user_profiles[user_id] = {
            "interests": interests,
            "level": level,
            "preferences": {}
        }
        return self.user_profiles[user_id]

    def personalize_content(self, user_id: str, content: str) -> str:
        """
        Personalize content based on user profile
        """
        if user_id not in self.user_profiles:
            return content

        profile = self.user_profiles[user_id]
        prompt = f"""
        Personalize the following content for a user with:
        - Interests: {', '.join(profile['interests'])}
        - Level: {profile['level']}

        Content: "{content}"

        Provide personalized content that matches their interests and level.
        """
        return self.generate_text(prompt)

class AuthAgent(GeminiAgent):
    def __init__(self):
        super().__init__("gemini-pro")
        self.users = {}

    def signup(self, username: str, email: str, password_hint: str) -> Dict[str, Any]:
        """
        Simulate user signup (in production, integrate with secure auth system)
        """
        if username in self.users:
            return {"success": False, "message": "Username already exists"}

        self.users[username] = {
            "email": email,
            "password_hint": password_hint,  # In production, hash this properly
            "created_at": "2025-01-01"
        }

        return {"success": True, "message": "User registered successfully", "user_id": username}

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Simulate user login
        """
        if username not in self.users:
            return {"success": False, "message": "Invalid credentials"}

        # In production, verify hashed password
        return {"success": True, "message": "Login successful", "user_id": username}

# RAG Chatbot with Qdrant using Gemini
class RAGChatbotAgent(GeminiAgent):
    def __init__(self):
        super().__init__("gemini-pro")
        # In a full implementation, this would connect to Qdrant
        self.knowledge_base = []

    def add_document(self, content: str, metadata: Dict = None):
        """
        Add document to knowledge base (simulated)
        """
        self.knowledge_base.append({
            "content": content,
            "metadata": metadata or {}
        })

    def search_relevant_documents(self, query: str, top_k: int = 3) -> List[str]:
        """
        Search for relevant documents (simulated)
        """
        # In a real implementation, this would use Qdrant vector search
        # For now, we'll return a sample of documents
        return [doc["content"] for doc in self.knowledge_base[:top_k]]

    def rag_response(self, query: str) -> str:
        """
        Generate RAG response using retrieved documents
        """
        relevant_docs = self.search_relevant_documents(query)

        if not relevant_docs:
            return "I don't have enough information to answer that question."

        context = "\n".join(relevant_docs)
        prompt = f"""
        Based on the following context, answer the question: "{query}"

        Context:
        {context}

        Answer:
        """
        return self.generate_text(prompt)

# Usage Examples
if __name__ == "__main__":
    print("=== GEMINI AGENT INITIALIZATION ===")
    agent = GeminiAgent()
    print("Agent initialized successfully")
    print(f"Model Info: {agent.get_model_info()}")

    print("\n=== BASIC TEXT GENERATION ===")
    response = agent.generate_text("Explain what artificial intelligence is in one sentence.")
    print(f"AI Explanation: {response}")

    print("\n=== URDU TRANSLATION AGENT ===")
    translator = UrduTranslationAgent()
    english_text = "Hello, how are you today?"
    urdu_translation = translator.translate_to_urdu(english_text)
    print(f"English: {english_text}")
    print(f"Urdu: {urdu_translation}")

    print("\n=== PERSONALIZATION AGENT ===")
    personalizer = PersonalizationAgent()
    user_profile = personalizer.create_user_profile("user123", ["robotics", "AI", "programming"], "intermediate")
    print(f"User Profile Created: {user_profile}")

    content = "Learn about machine learning algorithms"
    personalized = personalizer.personalize_content("user123", content)
    print(f"Personalized Content: {personalized}")

    print("\n=== AUTH AGENT ===")
    auth = AuthAgent()
    signup_result = auth.signup("alice", "alice@example.com", "password123")
    print(f"Signup Result: {signup_result}")

    login_result = auth.login("alice", "password123")
    print(f"Login Result: {login_result}")

    print("\n=== RAG CHATBOT AGENT ===")
    rag_bot = RAGChatbotAgent()
    rag_bot.add_document("Robots are programmable machines that can perform tasks automatically.")
    rag_bot.add_document("Machine learning is a subset of AI that enables computers to learn from data.")
    rag_bot.add_document("Neural networks are computing systems inspired by the human brain.")

    query = "What is machine learning?"
    rag_answer = rag_bot.rag_response(query)
    print(f"Query: {query}")
    print(f"RAG Response: {rag_answer}")