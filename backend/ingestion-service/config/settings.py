"""
Configuration settings for the ingestion service
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Crawler settings
DOCUSAURUS_BASE_URL = os.getenv("DOCUSAURUS_BASE_URL", "https://your-docusaurus-site.com")
CRAWLER_DELAY = float(os.getenv("CRAWLER_DELAY", "1.0"))  # Delay between requests in seconds
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

# Content extraction settings
MAIN_CONTENT_SELECTORS = [
    "main div[class*='docItem']",
    "article",
    ".markdown",
    "[class*='docContent']",
    "[class*='theme']",
    "main",
    "[role='main']"
]

# Chunking settings
CHUNK_SIZE_MIN = int(os.getenv("CHUNK_SIZE_MIN", "500"))
CHUNK_SIZE_MAX = int(os.getenv("CHUNK_SIZE_MAX", "1200"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# Cohere settings
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
COHERE_MODEL = os.getenv("COHERE_MODEL", "embed-multilingual-v2.0")

# Google Gemini settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Qdrant settings
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "textbook_content")

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Processing settings
RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "3"))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", "1.0"))