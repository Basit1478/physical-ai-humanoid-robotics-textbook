import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "backend-api"}

def test_auth_signup():
    # Test signup endpoint
    signup_data = {
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User",
        "software_background": "beginner",
        "hardware_background": "intermediate"
    }
    response = client.post("/auth/signup", json=signup_data)
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "token" in data

def test_rag_health():
    response = client.get("/rag/health")
    assert response.status_code == 200

def test_translate_health():
    response = client.get("/translate/health")
    assert response.status_code == 200

def test_personalize_health():
    response = client.get("/personalize/health")
    assert response.status_code == 200

if __name__ == "__main__":
    print("Running backend tests...")
    test_health_endpoint()
    print("✓ Health endpoint test passed")

    test_auth_signup()
    print("✓ Auth signup test passed")

    test_rag_health()
    print("✓ RAG health test passed")

    test_translate_health()
    print("✓ Translate health test passed")

    test_personalize_health()
    print("✓ Personalize health test passed")

    print("\nAll tests passed! Backend is working correctly.")