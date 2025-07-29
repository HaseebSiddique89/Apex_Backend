#!/usr/bin/env python3
"""
Test PIAPI configuration and connectivity
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_piapi_config():
    print("🧪 Testing PIAPI Configuration...")
    
    # Check if API key exists
    api_key = os.getenv("PIAPI_API_KEY")
    if not api_key:
        print("❌ PIAPI_API_KEY not found in environment variables")
        print("Please add PIAPI_API_KEY to your .env file")
        return False
    
    print(f"✅ PIAPI_API_KEY found: {api_key[:10]}...")
    
    # Check if the key looks valid (basic check)
    if len(api_key) < 10:
        print("❌ API key seems too short")
        return False
    
    print("✅ API key format looks valid")
    
    # Test basic connectivity
    try:
        import requests
        response = requests.get("https://api.piapi.ai/api/v1/task", 
                              headers={"x-api-key": api_key}, 
                              timeout=10)
        print(f"✅ PIAPI connectivity test: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ PIAPI connectivity test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_piapi_config()
    if success:
        print("\n🎉 PIAPI configuration looks good!")
        print("You can now test the upload-complete endpoint")
    else:
        print("\n❌ PIAPI configuration needs fixing")
        print("Please check your .env file and API key") 