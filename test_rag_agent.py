import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'rag-chatbot'))

from config.settings import settings
from src.rag_agent import RAGAgent

print("Testing fresh RAGAgent instance...")

# Create a new RAGAgent instance
rag_agent = RAGAgent()

# Get service info
service_info = rag_agent.get_service_info()

print("Settings loaded in RAGAgent:")
print(f"  Model: {settings.GEMINI_MODEL}")
print(f"  Collection: {settings.QDRANT_COLLECTION_NAME}")

print("\nService info from RAGAgent:")
print(f"  Model: {service_info.get('model')}")
print(f"  Collection: {service_info.get('collection_info', {}).get('collection_name')}")
print(f"  Vector count: {service_info.get('collection_info', {}).get('vector_count')}")