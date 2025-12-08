#!/usr/bin/env python3
"""
Integration test script to verify frontend-backend communication
"""

import requests
import time
import sys

def test_backend_health():
    """Test if backend is healthy and responsive"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Backend health check failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not reachable. Make sure it's running on port 8000")
        return False
    except Exception as e:
        print(f"❌ Backend health check failed with error: {e}")
        return False

def test_backend_root():
    """Test if backend root endpoint is working"""
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "message" in data and "services" in data:
                print("✅ Backend root endpoint is working correctly")
                return True
            else:
                print("❌ Backend root endpoint returned unexpected data structure")
                return False
        else:
            print(f"❌ Backend root endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend root endpoint test failed with error: {e}")
        return False

def test_api_docs():
    """Test if API documentation is accessible"""
    try:
        response = requests.get("http://localhost:8000/api/docs", timeout=10)
        if response.status_code == 200:
            print("✅ API documentation is accessible")
            return True
        else:
            print(f"❌ API documentation not accessible (status {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ API documentation test failed with error: {e}")
        return False

def test_frontend_access():
    """Test if frontend can access backend API"""
    try:
        # Test getting client configuration
        response = requests.get("http://localhost:8000/api/config", timeout=10)
        if response.status_code == 200:
            data = response.json()
            required_fields = ["api_base_url", "auth_enabled", "rag_enabled", "translation_enabled"]
            if all(field in data for field in required_fields):
                print("✅ Frontend can access backend API configuration")
                return True
            else:
                print("❌ Backend API configuration missing required fields")
                return False
        else:
            print(f"❌ Frontend cannot access backend API configuration (status {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Frontend-backend integration test failed with error: {e}")
        return False

def main():
    print("🧪 Starting integration tests between frontend and backend...\n")

    # Wait a moment for services to stabilize
    time.sleep(2)

    tests = [
        test_backend_health,
        test_backend_root,
        test_api_docs,
        test_frontend_access
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests

    print(f"📊 Integration test results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All integration tests passed! Frontend and backend are properly integrated.")
        return 0
    else:
        print("⚠️  Some integration tests failed. Please check the backend deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())