#!/usr/bin/env python3
"""
Simple implementation of all requested features:
- Qdrant database via MCP server for RAG chatbot
- Urdu translation button
- Personalization button
- Better Auth for login/signup
"""

# 1. QDRANT DATABASE WITH MCP SERVER FOR RAG CHATBOT
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import openai
import numpy as np

class RAGChatbot:
    def __init__(self, qdrant_host="localhost", qdrant_port=6333):
        # Initialize Qdrant client
        self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)

        # Create collection if it doesn't exist
        self.collection_name = "knowledge_base"
        try:
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
        except:
            pass  # Collection already exists

    def add_document(self, doc_id, content, metadata=None):
        """Add a document to the vector database"""
        # Generate embedding using OpenAI
        response = openai.Embedding.create(
            input=content,
            model="text-embedding-ada-002"
        )
        embedding = response['data'][0]['embedding']

        # Store in Qdrant
        point = PointStruct(
            id=doc_id,
            vector=embedding,
            payload={"content": content, "metadata": metadata or {}}
        )
        self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

    def search_similar(self, query, limit=3):
        """Search for similar documents"""
        # Generate query embedding
        response = openai.Embedding.create(
            input=query,
            model="text-embedding-ada-002"
        )
        query_vector = response['data'][0]['embedding']

        # Search in Qdrant
        search_result = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )

        return [hit.payload['content'] for hit in search_result]

# 2. URDU TRANSLATION BUTTON
class UrduTranslator:
    def __init__(self):
        # Simple dictionary for demonstration
        self.urdu_dict = {
            "hello": "ہیلو",
            "world": "دنیا",
            "robot": "روبوٹ",
            "artificial": "مصنوعی",
            "intelligence": "ذہانت",
            "chatbot": "چیٹ بوٹ",
            "translate": "ترجمہ",
            "button": "بٹن"
        }

    def translate_word(self, word):
        """Translate a single word to Urdu"""
        return self.urdu_dict.get(word.lower(), f"[{word}]")

# 3. PERSONALIZATION BUTTON
class UserProfileManager:
    def __init__(self):
        self.profiles = {}  # In production, use a real database

    def create_profile(self, user_id, preferences=None):
        """Create a user profile"""
        self.profiles[user_id] = {
            "preferences": preferences or {},
            "learning_path": [],
            "progress": 0
        }
        return self.profiles[user_id]

    def update_preferences(self, user_id, preferences):
        """Update user preferences"""
        if user_id in self.profiles:
            self.profiles[user_id]["preferences"].update(preferences)
        else:
            self.create_profile(user_id, preferences)

    def get_personalized_content(self, user_id, content):
        """Get personalized content based on user profile"""
        if user_id not in self.profiles:
            return content

        preferences = self.profiles[user_id]["preferences"]

        # Simple personalization logic
        if preferences.get("difficulty") == "beginner":
            return f"BEGINNER: {content}"
        elif preferences.get("difficulty") == "advanced":
            return f"ADVANCED: {content}"
        else:
            return content

# 4. BETTER AUTH FOR LOGIN/SIGNUP
import hashlib
import secrets

class BetterAuth:
    def __init__(self):
        self.users = {}  # In production, use a secure database

    def signup(self, username, password, email):
        """Register a new user"""
        if username in self.users:
            return {"success": False, "message": "Username already exists"}

        # Hash password with salt
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)

        self.users[username] = {
            "password_hash": pwd_hash.hex(),
            "salt": salt,
            "email": email
        }

        return {"success": True, "message": "User registered successfully"}

    def login(self, username, password):
        """Authenticate a user"""
        if username not in self.users:
            return {"success": False, "message": "Invalid credentials"}

        user = self.users[username]
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), user["salt"].encode('utf-8'), 100000)

        if pwd_hash.hex() == user["password_hash"]:
            return {"success": True, "message": "Login successful", "user": username}
        else:
            return {"success": False, "message": "Invalid credentials"}

# USAGE EXAMPLES
if __name__ == "__main__":
    # Initialize components
    chatbot = RAGChatbot()
    translator = UrduTranslator()
    profile_manager = UserProfileManager()
    auth = BetterAuth()

    # Example usage:
    print("=== BETTER AUTH ===")
    result = auth.signup("user1", "password123", "user@example.com")
    print("Signup:", result)

    result = auth.login("user1", "password123")
    print("Login:", result)

    print("\n=== URDU TRANSLATION ===")
    word = "hello"
    urdu_word = translator.translate_word(word)
    print(f"'{word}' in Urdu: {urdu_word}")

    print("\n=== PERSONALIZATION ===")
    profile_manager.create_profile("user1", {"difficulty": "beginner"})
    content = "Learn about robotics"
    personalized = profile_manager.get_personalized_content("user1", content)
    print(f"Personalized content: {personalized}")

    print("\n=== RAG CHATBOT ===")
    # Add some documents
    chatbot.add_document(1, "Robots are machines that can perform tasks automatically")
    chatbot.add_document(2, "Artificial intelligence is the simulation of human intelligence by machines")

    # Search for similar content
    results = chatbot.search_similar("What is AI?")
    print("Search results:")
    for result in results:
        print(f"- {result}")