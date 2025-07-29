#!/usr/bin/env python3
"""
Quick Backend Test Script
"""
import asyncio
import aiohttp
import json
import os

BASE_URL = "http://localhost:5000"

async def test_backend():
    """Test the backend API endpoints"""
    print("🧪 Testing Apex Backend API...")
    print(f"Base URL: {BASE_URL}")
    print("-" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Check if server is running
        print("1. Testing server connection...")
        try:
            async with session.get(f"{BASE_URL}/") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Server is running: {data}")
                else:
                    print(f"❌ Server error: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            print("Make sure your backend is running with: python -m backend.app")
            return False
        
        # Test 2: Test signup endpoint
        print("\n2. Testing signup endpoint...")
        signup_data = {
            "username": "testuser_postman",
            "email": "test_postman@example.com",
            "password": "password123"
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/auth/signup",
                json=signup_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                data = await response.json()
                print(f"✅ Signup response: {data}")
                if response.status == 201:
                    print("✅ Signup endpoint working correctly")
                else:
                    print(f"❌ Signup failed: {response.status}")
        except Exception as e:
            print(f"❌ Signup test failed: {e}")
        
        # Test 3: Test login endpoint
        print("\n3. Testing login endpoint...")
        login_data = {
            "username_or_email": "testuser_postman",
            "password": "password123"
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                data = await response.json()
                if response.status == 200 and "token" in data:
                    token = data["token"]
                    print("✅ Login successful, token obtained")
                    print(f"Token: {token[:50]}...")
                    
                    # Test 4: Test authenticated endpoint
                    print("\n4. Testing authenticated endpoint...")
                    headers = {
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }
                    
                    try:
                        async with session.get(
                            f"{BASE_URL}/image/user/images",
                            headers=headers
                        ) as response:
                            data = await response.json()
                            if response.status == 200:
                                print("✅ Authenticated endpoint working")
                                print(f"User has {len(data.get('data', []))} images")
                            else:
                                print(f"❌ Authenticated endpoint failed: {response.status}")
                    except Exception as e:
                        print(f"❌ Authenticated test failed: {e}")
                        
                else:
                    print(f"❌ Login failed: {data}")
        except Exception as e:
            print(f"❌ Login test failed: {e}")
        
        # Test 5: Test file upload (if you have a test image)
        print("\n5. Testing file upload...")
        test_image_path = "heart.jpg"  # Use your existing test image
        
        if os.path.exists(test_image_path):
            try:
                # Create form data
                form_data = aiohttp.FormData()
                form_data.add_field('file', 
                                  open(test_image_path, 'rb'),
                                  filename='test_image.jpg',
                                  content_type='image/jpeg')
                
                headers = {"Authorization": f"Bearer {token}"}
                
                async with session.post(
                    f"{BASE_URL}/image/upload",
                    data=form_data,
                    headers=headers
                ) as response:
                    data = await response.json()
                    if response.status == 201 and data.get("success"):
                        print("✅ File upload successful!")
                        print(f"Image ID: {data['data']['image_id']}")
                        print(f"3D Task ID: {data['data']['model3d_task_id']}")
                        
                        # Test 6: Check 3D model status
                        print("\n6. Testing 3D model status...")
                        status_data = {
                            "task_id": data['data']['model3d_task_id'],
                            "model3d_id": data['data']['model3d_id']
                        }
                        
                        try:
                            async with session.post(
                                f"{BASE_URL}/image/3d/status",
                                json=status_data,
                                headers=headers
                            ) as response:
                                status_result = await response.json()
                                if response.status == 200:
                                    print("✅ 3D status endpoint working")
                                    print(f"Status: {status_result['data']['status']}")
                                else:
                                    print(f"❌ 3D status failed: {response.status}")
                        except Exception as e:
                            print(f"❌ 3D status test failed: {e}")
                            
                    else:
                        print(f"❌ File upload failed: {data}")
            except Exception as e:
                print(f"❌ File upload test failed: {e}")
        else:
            print(f"⚠️  Test image not found: {test_image_path}")
            print("Skipping file upload test")
    
    print("\n" + "=" * 50)
    print("🎉 Backend testing completed!")
    print("Your API is ready for Postman testing!")
    print("\nNext steps:")
    print("1. Open Postman")
    print("2. Follow the POSTMAN_TESTING_GUIDE.md")
    print("3. Test all endpoints manually")
    print("4. Integrate with React Native")

if __name__ == "__main__":
    asyncio.run(test_backend()) 