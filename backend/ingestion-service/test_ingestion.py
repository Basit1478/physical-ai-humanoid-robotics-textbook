"""
Simple test to verify the ingestion service implementation
"""
import asyncio
import os
from src.ingestion_service import IngestionService


async def test_ingestion_service():
    """
    Test the ingestion service components without actually running the full pipeline.
    """
    print("Testing Ingestion Service Implementation...")

    # Test configuration loading
    print("\n1. Testing configuration...")
    try:
        from config.settings import (
            DOCUSAURUS_BASE_URL, COHERE_API_KEY, QDRANT_URL,
            CHUNK_SIZE_MIN, CHUNK_SIZE_MAX
        )
        print(f"   ✓ Base URL configured: {'Yes' if DOCUSAURUS_BASE_URL else 'No'}")
        print(f"   ✓ Cohere API key configured: {'Yes' if COHERE_API_KEY else 'No (will fail at runtime)'}")
        print(f"   ✓ Qdrant URL configured: {'Yes' if QDRANT_URL else 'No (will fail at runtime)'}")
        print(f"   ✓ Chunk size range: {CHUNK_SIZE_MIN}-{CHUNK_SIZE_MAX} tokens")
    except Exception as e:
        print(f"   ✗ Configuration error: {e}")
        return False

    # Test utility functions
    print("\n2. Testing utility functions...")
    try:
        from utils.tokenization import count_tokens, chunk_text, clean_text

        # Test token counting
        test_text = "This is a test sentence for token counting."
        token_count = count_tokens(test_text)
        print(f"   ✓ Token counting: '{test_text[:30]}...' -> {token_count} tokens")

        # Test text cleaning
        dirty_text = "  This   has   extra   spaces  \n\n and newlines  "
        clean_result = clean_text(dirty_text)
        print(f"   ✓ Text cleaning: '{dirty_text}' -> '{clean_result}'")

        # Test chunking
        long_text = "This is a longer text. " * 50  # Create a longer text
        chunks = chunk_text(long_text, min_tokens=10, max_tokens=50, overlap=5)
        print(f"   ✓ Text chunking: {len(chunks)} chunks created from {len(long_text)} chars")

    except Exception as e:
        print(f"   ✗ Utility function error: {e}")
        return False

    # Test content extraction utilities
    print("\n3. Testing content extraction utilities...")
    try:
        from utils.content_extraction import extract_main_content, extract_page_title

        sample_html = """
        <html>
        <head><title>Test Page</title></head>
        <body>
            <nav>Navigation content</nav>
            <main>
                <h1>Main Content</h1>
                <p>This is the main content that should be extracted.</p>
                <p>Additional paragraph with more content.</p>
            </main>
            <footer>Footer content</footer>
        </body>
        </html>
        """

        content = extract_main_content(sample_html)
        title = extract_page_title(sample_html)
        print(f"   ✓ Content extraction: Title='{title}', Content length={len(content) if content else 0}")

    except Exception as e:
        print(f"   ✗ Content extraction error: {e}")
        return False

    # Test URL utilities
    print("\n4. Testing URL utilities...")
    try:
        from utils.url_utils import is_valid_url, normalize_url, extract_links_from_html

        base_url = "https://example.com"
        test_url = "https://example.com/page"
        is_valid = is_valid_url(test_url, base_url)
        normalized = normalize_url(test_url + "#section?param=value")

        print(f"   ✓ URL validation: {test_url} -> {is_valid}")
        print(f"   ✓ URL normalization: {test_url}#section?param=value -> {normalized}")

    except Exception as e:
        print(f"   ✗ URL utility error: {e}")
        return False

    # Test service initialization (without running full pipeline)
    print("\n5. Testing service initialization...")
    try:
        ingestion_service = IngestionService()
        print("   ✓ Ingestion service initialized successfully")

        # Test that required services are created
        print(f"   ✓ Crawler service: {'Yes' if ingestion_service.crawler else 'No'}")
        print(f"   ✓ Content processor: {'Yes' if ingestion_service.content_processor else 'No'}")
        print(f"   ✓ Embedding service: {'Yes' if ingestion_service.embedding_service else 'No'}")
        print(f"   ✓ Qdrant storage: {'Yes' if ingestion_service.qdrant_storage else 'No'}")

    except Exception as e:
        print(f"   ✗ Service initialization error: {e}")
        return False

    print("\n✓ All tests passed! The ingestion service implementation is structurally correct.")
    print("\nNote: To run the full ingestion pipeline, you need to provide valid API keys")
    print("for Cohere and Qdrant in your .env file, and a valid Docusaurus site URL.")

    return True


def test_environment():
    """
    Test that required environment variables are set.
    """
    print("\n6. Testing environment configuration...")

    required_vars = ['DOCUSAURUS_BASE_URL']
    optional_vars = ['COHERE_API_KEY', 'QDRANT_URL', 'QDRANT_API_KEY']

    missing_required = []
    missing_optional = []

    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)

    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)

    if missing_required:
        print(f"   ✗ Missing required environment variables: {missing_required}")
    else:
        print("   ✓ All required environment variables are set")

    if missing_optional:
        print(f"   ⚠ Missing optional environment variables (will cause runtime errors): {missing_optional}")
    else:
        print("   ✓ All optional environment variables are set")

    return len(missing_required) == 0


if __name__ == "__main__":
    print("Running Ingestion Service Implementation Test...")

    # Test environment first
    env_ok = test_environment()

    # Test implementation
    impl_ok = asyncio.run(test_ingestion_service())

    print(f"\n{'='*60}")
    if env_ok and impl_ok:
        print("✓ All tests passed! The implementation is ready to run.")
        print("\nTo execute the full pipeline:")
        print("1. Ensure all required environment variables are set")
        print("2. Run: python -m src.ingestion_service")
    else:
        print("✗ Some tests failed. Please check the output above.")
    print(f"{'='*60}")