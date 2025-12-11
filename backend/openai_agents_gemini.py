#!/usr/bin/env python3
"""
OpenAI Agents SDK configured with Gemini API
"""

import os
import time
from typing import Dict, List, Any
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gemini API Configuration - loaded from .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

class OpenAI_Agents_Gemini:
    def __init__(self):
        """
        Initialize OpenAI Agents SDK with Gemini API configuration
        """
        self.api_key = GEMINI_API_KEY
        self.base_url = GEMINI_API_BASE
        self.default_model = "gemini-pro"

    def chat_completion(self, messages: List[Dict[str, str]], model: str = None) -> Dict[str, Any]:
        """
        Simulate OpenAI chat completion API using Gemini
        """
        if model is None:
            model = self.default_model

        # Convert OpenAI message format to Gemini format
        gemini_messages = []
        for msg in messages:
            if msg["role"] == "system":
                # Add system message as a user message (Gemini doesn't have system role)
                gemini_messages.append({"role": "user", "parts": [{"text": f"System: {msg['content']}"}]})
            else:
                gemini_messages.append({"role": msg["role"], "parts": [{"text": msg["content"]}]})

        # Prepare Gemini API request
        url = f"{self.base_url}/models/{model}:generateContent?key={self.api_key}"

        payload = {
            "contents": gemini_messages,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1024,
                "topP": 0.8,
                "topK": 40
            }
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()

            gemini_response = response.json()

            # Convert Gemini response to OpenAI format
            if "candidates" in gemini_response and len(gemini_response["candidates"]) > 0:
                content = gemini_response["candidates"][0]["content"]["parts"][0]["text"]
                return {
                    "id": "chatcmpl-" + gemini_response.get("id", "gemini"),
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": model,
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": content
                        },
                        "finish_reason": "stop"
                    }],
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0
                    }
                }
            else:
                return {"error": "No candidates in response"}

        except Exception as e:
            return {"error": str(e)}

class UrduTranslationButton:
    def __init__(self, agent):
        self.agent = agent

    def translate_selected_text(self, text: str) -> str:
        """
        Translate selected text to Urdu using Gemini via OpenAI Agents SDK
        """
        messages = [
            {"role": "system", "content": "You are a professional translator. Translate the following English text to Urdu."},
            {"role": "user", "content": f"Translate this to Urdu: '{text}'"}
        ]

        response = self.agent.chat_completion(messages)

        if "error" in response:
            return f"Translation error: {response['error']}"

        return response["choices"][0]["message"]["content"]

class PersonalizationButton:
    def __init__(self, agent):
        self.agent = agent
        self.user_profiles = {}

    def create_profile(self, user_id: str, preferences: Dict) -> Dict:
        """
        Create user profile for personalization
        """
        self.user_profiles[user_id] = preferences
        return {"status": "success", "profile": preferences}

    def personalize_content(self, user_id: str, content: str) -> str:
        """
        Personalize content based on user profile
        """
        if user_id not in self.user_profiles:
            return content

        preferences = self.user_profiles[user_id]

        messages = [
            {"role": "system", "content": "You are a content personalization assistant."},
            {"role": "user", "content": f"""
            Personalize the following content for a user with these preferences:
            Preferences: {json.dumps(preferences)}

            Content: "{content}"

            Provide personalized content that matches their interests and learning level.
            """}
        ]

        response = self.agent.chat_completion(messages)

        if "error" in response:
            return content  # Return original content if personalization fails

        return response["choices"][0]["message"]["content"]

class BetterAuth:
    def __init__(self, agent):
        self.agent = agent
        self.users = {}

    def signup(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """
        User signup with validation
        """
        # In a real implementation, you would hash the password
        if username in self.users:
            return {"success": False, "message": "Username already exists"}

        self.users[username] = {
            "email": email,
            "password": password,  # In production, hash this!
            "created_at": "2025-01-01"
        }

        return {"success": True, "message": "User registered successfully", "user_id": username}

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        User login authentication
        """
        if username not in self.users:
            return {"success": False, "message": "Invalid credentials"}

        if self.users[username]["password"] == password:  # In production, compare hashes
            return {"success": True, "message": "Login successful", "user_id": username}
        else:
            return {"success": False, "message": "Invalid credentials"}

class RAGChatbot:
    def __init__(self, agent):
        self.agent = agent
        # Simulated knowledge base (in production, this would be Qdrant)
        self.documents = []

    def add_document(self, content: str, metadata: Dict = None):
        """
        Add document to knowledge base
        """
        self.documents.append({
            "content": content,
            "metadata": metadata or {}
        })

    def search_documents(self, query: str, top_k: int = 3) -> List[str]:
        """
        Simple document search (in production, use Qdrant vector search)
        """
        # For demo purposes, return all documents (in reality, use semantic search)
        return [doc["content"] for doc in self.documents[:top_k]]

    def get_rag_response(self, query: str) -> str:
        """
        Get RAG response using retrieved documents
        """
        # Retrieve relevant documents
        docs = self.search_documents(query)

        if not docs:
            return "I don't have enough information to answer that question."

        # Create context from retrieved documents
        context = "\n".join([f"- {doc}" for doc in docs])

        messages = [
            {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
            {"role": "user", "content": f"""
            Based on the following context, answer the question: "{query}"

            Context:
            {context}

            Answer:
            """}
        ]

        response = self.agent.chat_completion(messages)

        if "error" in response:
            return "Sorry, I encountered an error while processing your request."

        return response["choices"][0]["message"]["content"]

# Usage Examples
if __name__ == "__main__":
    print("=== OPENAI AGENTS SDK WITH GEMINI API ===")

    # Initialize the agent
    agent = OpenAI_Agents_Gemini()

    print("Agent initialized with Gemini API key")

    # Test basic functionality
    messages = [
        {"role": "user", "content": "What is artificial intelligence?"}
    ]

    response = agent.chat_completion(messages)
    if "error" not in response:
        print(f"\nBasic AI Response: {response['choices'][0]['message']['content']}")
    else:
        print(f"\nError: {response['error']}")

    print("\n=== URDU TRANSLATION BUTTON ===")
    translator = UrduTranslationButton(agent)
    english_text = "Hello, welcome to our AI course"
    urdu_text = translator.translate_selected_text(english_text)
    print(f"English: {english_text}")
    print(f"Urdu: {urdu_text}")

    print("\n=== PERSONALIZATION BUTTON ===")
    personalizer = PersonalizationButton(agent)
    user_id = "student_001"
    preferences = {
        "interests": ["robotics", "machine learning"],
        "level": "intermediate",
        "language": "english"
    }

    profile_result = personalizer.create_profile(user_id, preferences)
    print(f"Profile created: {profile_result}")

    content = "Learn about neural networks and deep learning"
    personalized_content = personalizer.personalize_content(user_id, content)
    print(f"Personalized content: {personalized_content}")

    print("\n=== BETTER AUTH ===")
    auth = BetterAuth(agent)
    signup_result = auth.signup("alice_student", "alice@example.com", "secure_password")
    print(f"Signup result: {signup_result}")

    login_result = auth.login("alice_student", "secure_password")
    print(f"Login result: {login_result}")

    print("\n=== RAG CHATBOT ===")
    rag_bot = RAGChatbot(agent)
    rag_bot.add_document("Artificial Intelligence is the simulation of human intelligence by machines.")
    rag_bot.add_document("Machine Learning is a subset of AI that enables computers to learn from data.")
    rag_bot.add_document("Neural Networks are computing systems inspired by the human brain.")

    query = "What is machine learning?"
    rag_response = rag_bot.get_rag_response(query)
    print(f"Query: {query}")
    print(f"RAG Response: {rag_response}")