"""
Configuration settings for the retrieval validation service
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Qdrant settings
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "textbook_content")

# Cohere settings
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
COHERE_MODEL = os.getenv("COHERE_MODEL", "embed-multilingual-v2.0")

# Retrieval settings
TOP_K = int(os.getenv("TOP_K", "5"))
COSINE_THRESHOLD = float(os.getenv("COSINE_THRESHOLD", "0.3"))
MAX_QUERY_LENGTH = int(os.getenv("MAX_QUERY_LENGTH", "2000"))

# Validation settings
RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "0.7"))
TEST_QUERY_FILE = os.getenv("TEST_QUERY_FILE", "test_queries.txt")

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Performance settings
RETRIEVAL_TIMEOUT = int(os.getenv("RETRIEVAL_TIMEOUT", "30"))