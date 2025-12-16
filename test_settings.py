import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'rag-chatbot'))

from config.settings import settings

print("Current settings values:")
print(f"GEMINI_API_KEY: {'SET' if settings.GEMINI_API_KEY else 'NOT SET'}")
print(f"GEMINI_MODEL: {settings.GEMINI_MODEL}")
print(f"QDRANT_URL: {settings.QDRANT_URL}")
print(f"QDRANT_COLLECTION_NAME: {settings.QDRANT_COLLECTION_NAME}")
print(f"RETRIEVAL_TOP_K: {settings.RETRIEVAL_TOP_K}")
print(f"TEMPERATURE: {settings.TEMPERATURE}")