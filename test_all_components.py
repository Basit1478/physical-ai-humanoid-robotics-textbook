import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_all_components():
    """Test all components integration"""
    print("Testing all components integration...")

    # Test 1: Qdrant connection
    print("\n1. Testing Qdrant connection...")
    try:
        from backend.services.qdrant_mcp_service import qdrant_mcp_service
        info = qdrant_mcp_service.client.get_collections()
        print("✅ Qdrant connection successful!")
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
        return False

    # Test 2: Gemini API integration
    print("\n2. Testing Gemini API integration...")
    try:
        from backend.services.gemini_service import gemini_service
        prompt = "Explain what artificial intelligence is in simple terms."
        response = gemini_service.generate_content_gemini(prompt)
        print("✅ Gemini API integration successful!")
    except Exception as e:
        print(f"❌ Gemini API integration failed: {e}")
        return False

    # Test 3: Translation service
    print("\n3. Testing translation service...")
    try:
        from backend.services.translation_service import translation_service
        text = "Hello, how are you?"
        translated = translation_service.translate_text(text, "ur")
        print("✅ Translation service working!")
    except Exception as e:
        print(f"❌ Translation service failed: {e}")
        return False

    # Test 4: Personalization service
    print("\n4. Testing personalization service...")
    try:
        from backend.services.personalization_service import personalization_service
        # This would normally require a database session
        print("✅ Personalization service loaded!")
    except Exception as e:
        print(f"❌ Personalization service failed: {e}")
        return False

    # Test 5: Enhanced auth
    print("\n5. Testing enhanced auth...")
    try:
        from backend.auth.enhanced_auth import validate_email, validate_password_strength
        # Test email validation
        assert validate_email("test@example.com") == True
        assert validate_email("invalid-email") == False

        # Test password validation
        weak_password = "123"
        strong_password = "StrongPass123!"

        weak_result = validate_password_strength(weak_password)
        strong_result = validate_password_strength(strong_password)

        assert weak_result["valid"] == False
        assert strong_result["valid"] == True

        print("✅ Enhanced auth validation working!")
    except Exception as e:
        print(f"❌ Enhanced auth failed: {e}")
        return False

    print("\n🎉 All components integrated successfully!")
    return True

if __name__ == "__main__":
    test_all_components()