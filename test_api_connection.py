#!/usr/bin/env python3
"""
Test API connection and endpoints
"""

import requests
import json

def test_api_connection():
    """Test if API is running and accessible"""
    api_url = "http://localhost:8000"
    
    print("🔌 Testing API Connection...")
    print("=" * 40)
    
    # Test health endpoint
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Health Check: PASSED")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ API Health Check: FAILED (Status: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API Connection: FAILED")
        print(f"   Error: {e}")
        print(f"   Make sure API is running: python run.py")
        return False
    
    # Test CORS headers
    try:
        response = requests.options(f"{api_url}/register", 
                                  headers={'Origin': 'http://localhost:5173'}, 
                                  timeout=5)
        if 'access-control-allow-origin' in response.headers:
            print("✅ CORS Configuration: PASSED")
        else:
            print("⚠️  CORS Configuration: May have issues")
    except Exception as e:
        print(f"⚠️  CORS Test: {e}")
    
    # Test register endpoint exists
    try:
        # This should return 422 (validation error) not 404
        response = requests.post(f"{api_url}/register", timeout=5)
        if response.status_code == 422:
            print("✅ Register Endpoint: EXISTS (validation error expected)")
        elif response.status_code == 404:
            print("❌ Register Endpoint: NOT FOUND")
            return False
        else:
            print(f"✅ Register Endpoint: EXISTS (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Register Endpoint Test: {e}")
        return False
    
    print("\n🎯 API Connection Test Results:")
    print("   ✅ API is running and accessible")
    print("   ✅ Register endpoint exists")
    print("   ✅ Ready for frontend enrollment")
    
    return True

if __name__ == '__main__':
    test_api_connection()
