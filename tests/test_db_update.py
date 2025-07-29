#!/usr/bin/env python3
"""
Test script to verify database update functionality
"""

import asyncio
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.db.mongo import get_db
from backend.config import Config

async def test_db_update():
    """Test database update functionality"""
    
    print("🧪 Testing database update functionality...")
    
    # Connect to database
    db = await get_db()
    
    # Test task_id (from your console output)
    test_task_id = "9b0e45b1-110e-4bde-80e3-bc18b0eff06b"
    
    # Check if record exists
    existing_record = await db.models3d.find_one({'task_id': test_task_id})
    
    if existing_record:
        print(f"✅ Found existing record for task_id: {test_task_id}")
        print(f"📊 Current status: {existing_record.get('status')}")
        print(f"📊 Current local_files: {existing_record.get('local_files')}")
        
        # Test update
        test_files = {
            'glb': '3d_models/test_file.glb',
            'no_background_image': 'no_background_image/test_file.png'
        }
        
        update_result = await db.models3d.update_one(
            {'task_id': test_task_id},
            {'$set': {
                'status': 'completed', 
                'local_files': test_files,
                'completed_at': datetime.utcnow()
            }}
        )
        
        if update_result.modified_count > 0:
            print(f"✅ Database update successful! Modified {update_result.modified_count} record(s)")
            
            # Verify the update
            updated_record = await db.models3d.find_one({'task_id': test_task_id})
            print(f"📊 Updated status: {updated_record.get('status')}")
            print(f"📊 Updated local_files: {updated_record.get('local_files')}")
        else:
            print("❌ Database update failed - no records modified")
    else:
        print(f"❌ No record found for task_id: {test_task_id}")
    
    print("\n🎉 Database update test completed!")

if __name__ == "__main__":
    asyncio.run(test_db_update()) 