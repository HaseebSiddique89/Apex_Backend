#!/usr/bin/env python3
"""
Test script for updated PIAPI integration
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from isometric_to_3D import create_trellis_image_to_3d_task, get_trellis_task_status, prepare_image_for_api
from dotenv import load_dotenv

load_dotenv()

async def test_piapi_integration():
    """Test the updated PIAPI integration"""
    
    # Test image path (use an existing isometric image)
    test_image_path = "Isometrics/isometric_20250722_001200_e28f6f.png"
    
    if not os.path.exists(test_image_path):
        print(f"❌ Test image not found: {test_image_path}")
        return
    
    print("🧪 Testing updated PIAPI integration...")
    
    # 1. Prepare image
    print("📸 Preparing image for API...")
    encoded_image = prepare_image_for_api(test_image_path)
    
    if not encoded_image:
        print("❌ Failed to prepare image")
        return
    
    print("✅ Image prepared successfully")
    
    # 2. Create 3D model task
    print("🔄 Creating 3D model task...")
    task_result = create_trellis_image_to_3d_task(encoded_image, prompt="a highly detailed 3D model with realistic textures")
    
    if not task_result or task_result.get("code") != 200:
        print("❌ Failed to create 3D model task")
        print(f"Response: {task_result}")
        return
    
    task_id = task_result.get("data", {}).get("task_id")
    if not task_id:
        print("❌ No task_id in response")
        print(f"Response: {task_result}")
        return
    
    print(f"✅ 3D model task created successfully: {task_id}")
    
    # 3. Check status (just once to verify it works)
    print("🔄 Checking task status...")
    status_result = get_trellis_task_status(task_id)
    
    if not status_result:
        print("❌ Failed to get task status")
        return
    
    status = status_result.get('data', {}).get('status')
    print(f"✅ Task status retrieved: {status}")
    
    print("\n🎉 PIAPI integration test completed successfully!")
    print(f"Task ID: {task_id}")
    print(f"Current Status: {status}")
    print("\nYou can now test the full backend with this working PIAPI integration!")

if __name__ == "__main__":
    asyncio.run(test_piapi_integration()) 