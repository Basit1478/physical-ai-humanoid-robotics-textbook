import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.gemini_service import gemini_service

def test_gemini_integration():
    """Test Gemini API integration"""
    print("Testing Gemini API integration...")

    try:
        # Test 1: List available models
        print("Testing model listing...")
        models = gemini_service.list_gemini_models()
        print(f"✅ Available models: {models}")

        # Test 2: Generate content with Gemini
        print("Testing content generation...")
        prompt = "Explain what artificial intelligence is in simple terms."
        response = gemini_service.generate_content_gemini(prompt)
        print(f"✅ Generated content: {response[:100]}...")

        # Test 3: Embed text
        print("Testing text embedding...")
        text = "This is a sample text for embedding."
        embedding = gemini_service.embed_text_gemini(text)
        print(f"✅ Generated embedding (first 5 dimensions): {embedding[:5]}")

        print("✅ All Gemini integration tests passed!")
        return True

    except Exception as e:
        print(f"❌ Error in Gemini integration: {e}")
        return False

if __name__ == "__main__":
    test_gemini_integration()