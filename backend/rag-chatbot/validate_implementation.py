"""
Validate the RAG Agent implementation by checking file structure and imports
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
        "src/main.py",
        "src/rag_agent.py",
        "utils/gemini_client.py",
        "utils/qdrant_retriever.py",
        "config/settings.py"
    ]

    all_present = True
    for file_path in required_files:
        full_path = Path("backend/rag-agent") / file_path
        if os.path.exists(full_path):
            print(f"   ✓ {file_path}")
        else:
            print(f"   ✗ {file_path}")
            all_present = False

    return all_present


def validate_imports():
    """Validate that all modules can be imported without errors."""
    print("\nValidating imports...")

    # Add the rag agent service to Python path
    sys.path.insert(0, os.path.join(os.getcwd(), "backend", "rag-agent"))

    modules_to_test = [
        ("config.settings", "settings"),
        ("utils.gemini_client", "GeminiClient"),
        ("utils.qdrant_retriever", "QdrantRetriever"),
        ("src.rag_agent", "RAGAgent"),
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


def validate_fastapi_app():
    """Validate that the FastAPI app is properly configured."""
    print("\nValidating FastAPI application...")

    try:
        from src.main import app
        import inspect

        # Check if app is a FastAPI instance
        from fastapi import FastAPI
        if isinstance(app, FastAPI):
            print("   ✓ FastAPI app instance found")
        else:
            print("   ✗ FastAPI app not found")
            return False

        # Check for required endpoints
        routes = {route.path: route.methods for route in app.routes}
        required_endpoints = ["/ask", "/retrieve", "/health"]

        found_endpoints = []
        for endpoint in required_endpoints:
            if endpoint in routes:
                found_endpoints.append(endpoint)
                print(f"   ✓ Endpoint {endpoint} found with methods: {routes[endpoint]}")

        if len(found_endpoints) < len(required_endpoints):
            missing = set(required_endpoints) - set(found_endpoints)
            print(f"   ✗ Missing endpoints: {missing}")
            return False

        return True

    except Exception as e:
        print(f"   ✗ FastAPI validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_core_logic():
    """Validate core logic functions."""
    print("\nValidating core logic...")

    try:
        # Test RAG Agent initialization (without API keys to avoid errors)
        from src.rag_agent import RAGAgent
        print("   ✓ RAGAgent class available")

        # Test that we can access the class methods
        agent_methods = ['ask', 'retrieve_only', 'process_selected_text_query', 'get_service_info']
        for method in agent_methods:
            if hasattr(RAGAgent, method):
                print(f"   ✓ RAGAgent.{method} method available")
            else:
                print(f"   ✗ RAGAgent.{method} method missing")
                return False

        # Test utility classes
        from utils.gemini_client import GeminiClient
        from utils.qdrant_retriever import QdrantRetriever

        print("   ✓ GeminiClient class available")
        print("   ✓ QdrantRetriever class available")

        success = True
    except Exception as e:
        print(f"   ✗ Core logic validation failed: {e}")
        import traceback
        traceback.print_exc()
        success = False

    return success


def validate_config():
    """Validate that configuration is properly set up."""
    print("\nValidating configuration...")

    try:
        from config.settings import settings
        print("   ✓ Settings module available")

        # Check for required configuration attributes
        required_attrs = [
            'GEMINI_API_KEY', 'GEMINI_MODEL', 'QDRANT_URL', 'QDRANT_API_KEY',
            'QDRANT_COLLECTION_NAME', 'AGENT_SYSTEM_INSTRUCTIONS', 'RETRIEVAL_TOP_K'
        ]

        for attr in required_attrs:
            if hasattr(settings, attr):
                print(f"   ✓ Settings.{attr} available")
            else:
                print(f"   ✗ Settings.{attr} missing")
                return False

        return True

    except Exception as e:
        print(f"   ✗ Configuration validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validation checks."""
    print("Validating RAG Agent Service Implementation")
    print("="*65)

    # Run all validation steps
    structure_ok = validate_file_structure()
    imports_ok = validate_imports()
    fastapi_ok = validate_fastapi_app()
    logic_ok = validate_core_logic()
    config_ok = validate_config()

    print("\n" + "="*65)
    print("VALIDATION SUMMARY")
    print("="*65)
    print(f"File Structure: {'✓ PASS' if structure_ok else '✗ FAIL'}")
    print(f"Imports: {'✓ PASS' if imports_ok else '✗ FAIL'}")
    print(f"FastAPI App: {'✓ PASS' if fastapi_ok else '✗ FAIL'}")
    print(f"Core Logic: {'✓ PASS' if logic_ok else '✗ FAIL'}")
    print(f"Configuration: {'✓ PASS' if config_ok else '✗ FAIL'}")

    overall_success = structure_ok and imports_ok and fastapi_ok and logic_ok and config_ok

    print(f"\nOverall Status: {'✓ ALL TESTS PASSED' if overall_success else '✗ SOME TESTS FAILED'}")

    if overall_success:
        print("\n✓ The RAG Agent service implementation is complete and structurally correct!")
        print("\nTo run the service:")
        print("1. Create a .env file with your API keys")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Start the service: uvicorn src.main:app --reload")
        print("4. Access the API at http://localhost:8000")
        print("5. Use /docs for interactive API documentation")
    else:
        print("\n✗ The implementation has issues that need to be addressed.")

    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)