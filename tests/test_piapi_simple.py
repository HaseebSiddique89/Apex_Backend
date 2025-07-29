#!/usr/bin/env python3
"""
Simple PIAPI test to check connectivity and API key
"""
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_piapi_simple():
    print("🧪 Testing PIAPI Simple Connection...")
    
    # Check if API key exists
    api_key = os.getenv("PIAPI_API_KEY")
    if not api_key:
        print("❌ PIAPI_API_KEY not found in environment variables")
        print("Please add PIAPI_API_KEY to your .env file")
        return False
    
    print(f"✅ PIAPI_API_KEY found: {api_key[:10]}...")
    
    # Test basic connectivity
    try:
        print("🔄 Testing PIAPI connectivity...")
        response = requests.get("https://api.piapi.ai/api/v1/task", 
                              headers={"x-api-key": api_key}, 
                              timeout=10)
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ PIAPI connectivity successful!")
            return True
        elif response.status_code == 401:
            print("❌ PIAPI authentication failed - check your API key")
            return False
        else:
            print(f"❌ PIAPI returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ PIAPI connectivity test failed: {e}")
        return False

def test_piapi_task_creation():
    print("\n🧪 Testing PIAPI Task Creation...")
    
    api_key = os.getenv("PIAPI_API_KEY")
    if not api_key:
        return False
    
    # Create a simple test payload
    test_payload = {
        "model": "Qubico/trellis",
        "task_type": "image-to-3d",
        "input": {
            "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",  # 1x1 pixel
            "ss_sampling_steps": 10,
            "slat_sampling_steps": 10,
            "ss_guidance_strength": 7.5,
            "slat_guidance_strength": 3,
            "seed": 0
        }
    }
    
    try:
        print("🔄 Creating test task...")
        response = requests.post(
            "https://api.piapi.ai/api/v1/task",
            headers={
                "x-api-key": api_key,
                "Content-Type": "application/json"
            },
            data=json.dumps(test_payload),
            timeout=30
        )
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📊 Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get('task_id')
            if task_id:
                print(f"✅ Task created successfully: {task_id}")
                return True
            else:
                print(f"❌ No task_id in response: {result}")
                return False
        else:
            print(f"❌ Task creation failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Task creation test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("PIAPI CONFIGURATION TEST")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    connectivity_ok = test_piapi_simple()
    
    if connectivity_ok:
        # Test 2: Task creation
        task_creation_ok = test_piapi_task_creation()
        
        if task_creation_ok:
            print("\n🎉 PIAPI is working correctly!")
            print("You can now test the upload-complete endpoint")
        else:
            print("\n❌ PIAPI task creation failed")
            print("Check your API key and account status")
    else:
        print("\n❌ PIAPI connectivity failed")
        print("Check your internet connection and API key")
    
    print("\n" + "=" * 50) 