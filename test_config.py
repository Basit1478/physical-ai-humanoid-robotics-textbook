from backend.rag-chatbot.config.settings import settings

print("Configuration loaded:")
print(f"GEMINI_MODEL: {settings.GEMINI_MODEL}")
print(f"QDRANT_URL: {settings.QDRANT_URL}")
print(f"QDRANT_COLLECTION_NAME: {settings.QDRANT_COLLECTION_NAME}")
print(f"RETRIEVAL_TOP_K: {settings.RETRIEVAL_TOP_K}")
print(f"TEMPERATURE: {settings.TEMPERATURE}")