import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.chat_service import RAGChatService
from models.database import SessionLocal

def test_rag_service():
    """Test the RAG service initialization and basic functionality"""
    print("Testing RAG Chat Service...")

    # Initialize the service
    try:
        rag_service = RAGChatService()
        print("✅ RAGChatService initialized successfully")

        if rag_service.vector_store:
            print("✅ Vector store is available")
        else:
            print("⚠️  Vector store is not available (this is expected if Qdrant is not running)")

        # Test embedding model
        if rag_service.embeddings:
            print("✅ Embedding model is available")

        # Test LLM
        if rag_service.llm:
            print("✅ LLM is available")

        return True

    except Exception as e:
        print(f"❌ Error initializing RAGChatService: {e}")
        return False

if __name__ == "__main__":
    test_rag_service()