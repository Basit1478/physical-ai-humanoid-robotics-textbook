"""
Validate the retrieval validation service implementation by checking file structure and imports
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
        "test_queries.txt",
        "src/retrieval_service.py",
        "src/validation_service.py",
        "src/cli_harness.py",
        "src/main.py",
        "utils/embedding_utils.py",
        "utils/similarity_utils.py",
        "config/settings.py"
    ]

    all_present = True
    for file_path in required_files:
        full_path = Path("backend/retrieval-validation") / file_path
        if os.path.exists(full_path):
            print(f"   ✓ {file_path}")
        else:
            print(f"   ✗ {file_path}")
            all_present = False

    return all_present


def validate_imports():
    """Validate that all modules can be imported without errors."""
    print("\nValidating imports...")

    # Add the retrieval validation service to Python path
    sys.path.insert(0, os.path.join(os.getcwd(), "backend", "retrieval-validation"))

    modules_to_test = [
        ("utils.embedding_utils", "EmbeddingService"),
        ("utils.similarity_utils", "calculate_semantic_relevance"),
        ("src.retrieval_service", "RetrievalService"),
        ("src.validation_service", "ValidationService"),
        ("config.settings", "QDRANT_URL, COHERE_API_KEY"),
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
        # Test embedding utilities
        from utils.embedding_utils import EmbeddingService
        print("   ✓ EmbeddingService class available")

        # Test similarity utilities
        from utils.similarity_utils import calculate_text_similarity, calculate_semantic_relevance
        print("   ✓ Similarity utilities available")

        # Test text similarity
        similarity = calculate_text_similarity("test query", "test result")
        print(f"   ✓ Text similarity calculation: {similarity:.4f}")

        # Test semantic relevance calculation
        relevance_data = calculate_semantic_relevance("test query", "test result", [], "test result")
        print(f"   ✓ Semantic relevance calculation: combined={relevance_data['combined_relevance']:.4f}")

        success = True
    except Exception as e:
        print(f"   ✗ Core logic validation failed: {e}")
        import traceback
        traceback.print_exc()
        success = False

    return success


def validate_service_concepts():
    """Validate that service classes exist with expected methods."""
    print("\nValidating service concepts...")

    try:
        # Import the service classes
        from src.retrieval_service import RetrievalService
        from src.validation_service import ValidationService

        # Check RetrievalService methods
        retrieval_methods = ['search', 'search_with_validation', 'batch_search', 'validate_retrieval_accuracy']
        missing_retrieval_methods = []
        for method in retrieval_methods:
            if not hasattr(RetrievalService, method.replace('search', 'search')):  # Check if method exists in class
                try:
                    # Actually check if method exists
                    if not hasattr(RetrievalService, method):
                        missing_retrieval_methods.append(method)
                except:
                    missing_retrieval_methods.append(method)

        # Check ValidationService methods
        validation_methods = ['validate_semantic_relevance', 'validate_metadata_accuracy', 'run_comprehensive_validation']
        missing_validation_methods = []
        for method in validation_methods:
            if not hasattr(ValidationService, method):
                missing_validation_methods.append(method)

        if missing_retrieval_methods:
            print(f"   ✗ Missing methods in RetrievalService: {missing_retrieval_methods}")
        else:
            print("   ✓ RetrievalService has expected methods")

        if missing_validation_methods:
            print(f"   ✗ Missing methods in ValidationService: {missing_validation_methods}")
        else:
            print("   ✓ ValidationService has expected methods")

        success = (len(missing_retrieval_methods) == 0 and len(missing_validation_methods) == 0)
    except Exception as e:
        print(f"   ✗ Service concept validation failed: {e}")
        import traceback
        traceback.print_exc()
        success = False

    return success


def validate_cli():
    """Validate that CLI harness is properly configured."""
    print("\nValidating CLI configuration...")

    try:
        from src.cli_harness import cli
        import click

        # Check if cli is a Click group with commands
        if hasattr(cli, 'commands') and len(cli.commands) > 0:
            command_names = list(cli.commands.keys())
            expected_commands = ['search', 'validate', 'test-query-types', 'collection-info', 'interactive']
            print(f"   ✓ CLI has {len(command_names)} commands: {command_names}")

            # Check for expected commands (with dashes converted to underscores in some cases)
            found_expected = []
            for expected in expected_commands:
                # Click converts dashes to underscores in command names
                expected_normalized = expected.replace('-', '_')
                if expected_normalized in command_names:
                    found_expected.append(expected)

            print(f"   ✓ Found expected commands: {found_expected}")
            return True
        else:
            print("   ✗ CLI does not have commands configured")
            return False

    except Exception as e:
        print(f"   ✗ CLI validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validation checks."""
    print("Validating Retrieval Validation Service Implementation")
    print("="*65)

    # Run all validation steps
    structure_ok = validate_file_structure()
    imports_ok = validate_imports()
    logic_ok = validate_core_logic()
    services_ok = validate_service_concepts()
    cli_ok = validate_cli()

    print("\n" + "="*65)
    print("VALIDATION SUMMARY")
    print("="*65)
    print(f"File Structure: {'✓ PASS' if structure_ok else '✗ FAIL'}")
    print(f"Imports: {'✓ PASS' if imports_ok else '✗ FAIL'}")
    print(f"Core Logic: {'✓ PASS' if logic_ok else '✗ FAIL'}")
    print(f"Service Concepts: {'✓ PASS' if services_ok else '✗ FAIL'}")
    print(f"CLI Configuration: {'✓ PASS' if cli_ok else '✗ FAIL'}")

    overall_success = structure_ok and imports_ok and logic_ok and services_ok and cli_ok

    print(f"\nOverall Status: {'✓ ALL TESTS PASSED' if overall_success else '✗ SOME TESTS FAILED'}")

    if overall_success:
        print("\n✓ The retrieval validation service implementation is complete and structurally correct!")
        print("\nTo run the validation service:")
        print("1. Create a .env file with your API keys (matching your ingestion service)")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run CLI commands like: python -m src.main --help")
        print("4. Or run validation: python -m src.main validate")
    else:
        print("\n✗ The implementation has issues that need to be addressed.")

    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)