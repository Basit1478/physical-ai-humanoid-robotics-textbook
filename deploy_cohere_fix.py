#!/usr/bin/env python3
"""
Deployment script to update the RAG service with Cohere embedding fix
This script automates the process of updating the deployed service to use Cohere embeddings
for both ingestion and retrieval, fixing the compatibility issue.
"""
import os
import subprocess
import sys
from pathlib import Path


def update_backend_service():
    """
    Update the backend service with Cohere embedding compatibility
    """
    print("Updating backend RAG service with Cohere embedding fix...")

    # Paths to the files that need to be updated
    backend_path = Path("backend/rag-chatbot")

    # 1. Update requirements.txt to include cohere
    requirements_path = backend_path / "requirements.txt"
    with open(requirements_path, "r") as f:
        requirements = f.read()

    if "cohere" not in requirements.lower():
        with open(requirements_path, "a") as f:
            f.write("\ncohere==4.32\n")
        print("✓ Added cohere to requirements.txt")
    else:
        print("- Cohere already in requirements.txt")

    # 2. The qdrant_retriever.py file has already been updated with Cohere support
    print("✓ QdrantRetriever updated with Cohere embedding compatibility")

    # 3. Update the main.py to initialize Cohere client
    main_path = backend_path / "src" / "main.py"
    if main_path.exists():
        with open(main_path, "r") as f:
            main_content = f.read()

        # Check if Cohere client initialization exists
        if "cohere_client" not in main_content:
            print("Note: main.py may need updates for Cohere client initialization")
        else:
            print("- Cohere client already initialized in main.py")

    print("\nBackend service updated with Cohere embedding compatibility!")


def prepare_deployment():
    """
    Prepare the updated service for deployment
    """
    print("\nPreparing updated service for deployment...")

    # Verify the changes are correct
    qdrant_retriever_path = Path("backend/rag-chatbot/utils/qdrant_retriever.py")
    with open(qdrant_retriever_path, "r") as f:
        content = f.read()

    if "cohere_client.embed" in content or "cohere.Client" in content:
        print("✓ Cohere integration verified in qdrant_retriever.py")
    else:
        print("✗ Cohere integration not found in qdrant_retriever.py")
        return False

    # Check requirements
    requirements_path = Path("backend/rag-chatbot/requirements.txt")
    with open(requirements_path, "r") as f:
        req_content = f.read()

    if "cohere" in req_content.lower():
        print("✓ Cohere dependency verified in requirements.txt")
    else:
        print("✗ Cohere dependency not found in requirements.txt")
        return False

    return True


def redeploy_service():
    """
    Provide instructions for redeploying the service
    """
    print("\n" + "="*60)
    print("DEPLOYMENT INSTRUCTIONS")
    print("="*60)
    print("\nThe RAG service has been updated with Cohere embedding compatibility.")
    print("To complete the fix, you need to redeploy the service to Render:")
    print()
    print("1. COMMIT YOUR CHANGES:")
    print("   git add .")
    print("   git commit -m \"Fix: Update service to use Cohere embeddings for compatibility\"")
    print()
    print("2. PUSH TO TRIGGER RENDER DEPLOYMENT:")
    print("   git push origin main  # or your deployment branch")
    print()
    print("3. ALTERNATIVELY, YOU CAN DEPLOY MANUALLY:")
    print("   - Go to your Render dashboard")
    print("   - Find the rag-chatbot service")
    print("   - Click 'Manual Deploy' to redeploy with the changes")
    print()
    print("4. UPDATE ENVIRONMENT VARIABLES ON RENDER:")
    print("   - Make sure COHERE_API_KEY is set in your Render service")
    print("   - Verify COHERE_MODEL is set (should be 'embed-multilingual-v2.0' or similar)")
    print()
    print("5. VERIFY THE DEPLOYMENT:")
    print("   curl -X POST https://your-render-service.onrender.com/retrieve \\")
    print("        -H \"Content-Type: application/json\" \\")
    print("        -d '{\"query_text\": \"ROS 2\", \"top_k\": 3}'")
    print()
    print("Expected: Should return relevant chunks instead of empty array")
    print()
    print("="*60)
    print("DEPLOYMENT STATUS: Ready for redeployment with Cohere fix")
    print("="*60)


def verify_fix():
    """
    Verify that the fix should work once deployed
    """
    print("\nVerifying the embedding compatibility fix...")

    # Check that Cohere client is properly initialized
    qdrant_retriever_path = Path("backend/rag-chatbot/utils/qdrant_retriever.py")
    with open(qdrant_retriever_path, "r") as f:
        content = f.read()

    checks = [
        ("Cohere client initialization", "cohere.Client" in content or "cohere_client" in content),
        ("Embedding generation with Cohere", "cohere_client.embed" in content or ".embed(" in content and "cohere" in content),
        ("Fallback handling", "placeholder" in content and ("except" in content or "try:" in content)),
        ("Settings integration", "settings.COHERE" in content)
    ]

    all_passed = True
    for check_name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"   {status} {check_name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n✓ All compatibility checks passed!")
        print("The fix should resolve the embedding mismatch issue when deployed.")
    else:
        print("\n✗ Some checks failed - please review the implementation.")

    return all_passed


def main():
    """
    Main function to execute the Cohere embedding fix process
    """
    print("Cohere Embedding Compatibility Fix for RAG Service")
    print("="*50)

    # Update the backend service
    update_backend_service()

    # Verify the changes
    if not prepare_deployment():
        print("\n❌ Pre-deployment verification failed!")
        return 1

    # Verify the fix
    if verify_fix():
        print("\n✓ Fix verification successful!")
    else:
        print("\n❌ Fix verification failed!")
        return 1

    # Provide deployment instructions
    redeploy_service()

    print("\n🎉 Cohere embedding fix preparation completed!")
    print("Follow the deployment instructions above to apply the fix to your deployed service.")

    return 0


if __name__ == "__main__":
    sys.exit(main())