#!/usr/bin/env python3
"""
Simple API test script to check if the API is responding
"""

import requests
import time
import sys

def test_api():
    base_url = "http://localhost:8000"
    
    print("🔍 Testing EEG Authentication API...")
    print(f"Base URL: {base_url}")
    
    # Test 1: Health check
    try:
        print("\n1️⃣ Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health Status: {response.status_code}")
        print(f"✅ Health Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: API is not running or not accessible")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: API is not responding")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Check docs endpoint
    try:
        print("\n2️⃣ Testing docs endpoint...")
        response = requests.get(f"{base_url}/docs", timeout=5)
        print(f"✅ Docs Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Docs Error: {e}")
    
    # Test 3: Check available endpoints
    try:
        print("\n3️⃣ Testing OpenAPI spec...")
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        if response.status_code == 200:
            openapi = response.json()
            endpoints = list(openapi.get('paths', {}).keys())
            print(f"✅ Available endpoints: {endpoints}")
        else:
            print(f"❌ OpenAPI Status: {response.status_code}")
    except Exception as e:
        print(f"❌ OpenAPI Error: {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting API connectivity test...")
    
    # Wait a moment for API to be ready
    print("⏳ Waiting 2 seconds for API to be ready...")
    time.sleep(2)
    
    success = test_api()
    
    if success:
        print("\n✅ API is running and accessible!")
        print("\n🌐 You can also test in browser:")
        print("   - Health: http://localhost:8000/health")
        print("   - Docs:   http://localhost:8000/docs")
    else:
        print("\n❌ API is not accessible!")
        print("\n🔧 Troubleshooting:")
        print("   1. Check if API is running in another terminal")
        print("   2. Check if port 8000 is available")
        print("   3. Try restarting the API")
    
    sys.exit(0 if success else 1)
