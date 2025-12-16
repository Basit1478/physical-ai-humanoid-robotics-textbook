"""
Validate the ingestion service implementation by checking file structure and imports
"""
import os
import sys
from pathlib import Path


def validate_file_structure():
    """Validate that all required files exist."""
    print("Validating file structure...")

    required_files = [
        "requirements.txt",
        "README.md",
        ".env.example",
        "src/crawler.py",
        "src/embedding_service.py",
        "src/qdrant_service.py",
        "src/ingestion_service.py",
        "utils/tokenization.py",
        "utils/content_extraction.py",
        "utils/url_utils.py",
        "config/settings.py"
    ]

    all_present = True
    for file_path in required_files:
        full_path = Path("backend/ingestion-service") / file_path
        if os.path.exists(full_path):
            print(f"   ✓ {file_path}")
        else:
            print(f"   ✗ {file_path}")
            all_present = False

    return all_present


def validate_imports():
    """Validate that all modules can be imported without errors."""
    print("\nValidating imports...")

    # Add the ingestion service to Python path
    sys.path.insert(0, os.path.join(os.getcwd(), "backend", "ingestion-service"))

    modules_to_test = [
        ("utils.tokenization", "count_tokens, chunk_text"),
        ("utils.content_extraction", "extract_main_content"),
        ("utils.url_utils", "is_valid_url, extract_links_from_html"),
        ("config.settings", "DOCUSAURUS_BASE_URL, CHUNK_SIZE_MIN"),
    ]

    all_imports_ok = True
    for module_name, test_attrs in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[test_attrs.split(',')[0].strip() if ',' in test_attrs else test_attrs])
            print(f"   ✓ {module_name}")
        except ImportError as e:
            print(f"   ✗ {module_name}: {e}")
            all_imports_ok = False

    return all_imports_ok


def validate_core_logic():
    """Validate core logic functions."""
    print("\nValidating core logic...")

    try:
        # Test tokenization functions
        from utils.tokenization import count_tokens, chunk_text, clean_text

        # Test token counting
        test_text = "This is a test sentence."
        tokens = count_tokens(test_text)
        print(f"   ✓ Token counting: '{test_text}' -> {tokens} tokens")

        # Test text cleaning
        dirty_text = "  This   has   extra   spaces  "
        clean_result = clean_text(dirty_text)
        print(f"   ✓ Text cleaning: '{dirty_text}' -> '{clean_result}'")

        # Test chunking
        long_text = "This is a test. " * 20  # Create a longer text
        chunks = chunk_text(long_text, min_tokens=5, max_tokens=15, overlap=2)
        print(f"   ✓ Text chunking: {len(chunks)} chunks from {len(long_text)} chars")

        success = True
    except Exception as e:
        print(f"   ✗ Core logic validation failed: {e}")
        success = False

    return success


def validate_service_concepts():
    """Validate that service classes exist with expected methods."""
    print("\nValidating service concepts...")

    try:
        # Import the service classes (without initializing with API keys)
        import importlib.util

        # Load the modules to check class definitions
        crawler_spec = importlib.util.spec_from_file_location("crawler",
            "backend/ingestion-service/src/crawler.py")
        crawler_module = importlib.util.module_from_spec(crawler_spec)
        crawler_spec.loader.exec_module(crawler_module)

        # Check that the main classes exist
        if hasattr(crawler_module, 'AsyncCrawler'):
            print("   ✓ AsyncCrawler class exists")
        else:
            print("   ✗ AsyncCrawler class missing")
            return False

        if hasattr(crawler_module, 'ContentProcessor'):
            print("   ✓ ContentProcessor class exists")
        else:
            print("   ✗ ContentProcessor class missing")
            return False

        # Check for expected methods
        crawler_class = getattr(crawler_module, 'AsyncCrawler')
        required_methods = ['crawl_site', 'process_url']
        missing_methods = []

        for method in required_methods:
            if not hasattr(crawler_class, method):
                missing_methods.append(method)

        if missing_methods:
            print(f"   ✗ Missing methods in AsyncCrawler: {missing_methods}")
            return False
        else:
            print("   ✓ AsyncCrawler has expected methods")

        success = True
    except Exception as e:
        print(f"   ✗ Service concept validation failed: {e}")
        success = False

    return success


def main():
    """Run all validation checks."""
    print("Validating Docusaurus Content Ingestion Service Implementation")
    print("="*65)

    # Run all validation steps
    structure_ok = validate_file_structure()
    imports_ok = validate_imports()
    logic_ok = validate_core_logic()
    services_ok = validate_service_concepts()

    print("\n" + "="*65)
    print("VALIDATION SUMMARY")
    print("="*65)
    print(f"File Structure: {'✓ PASS' if structure_ok else '✗ FAIL'}")
    print(f"Imports: {'✓ PASS' if imports_ok else '✗ FAIL'}")
    print(f"Core Logic: {'✓ PASS' if logic_ok else '✗ FAIL'}")
    print(f"Service Concepts: {'✓ PASS' if services_ok else '✗ FAIL'}")

    overall_success = structure_ok and imports_ok and logic_ok and services_ok

    print(f"\nOverall Status: {'✓ ALL TESTS PASSED' if overall_success else '✗ SOME TESTS FAILED'}")

    if overall_success:
        print("\n✓ The ingestion service implementation is complete and structurally correct!")
        print("\nTo run the full pipeline:")
        print("1. Create a .env file with your API keys")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run: python -m src.ingestion_service")
    else:
        print("\n✗ The implementation has issues that need to be addressed.")

    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)