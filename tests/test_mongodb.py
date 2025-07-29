#!/usr/bin/env python3
"""
Test MongoDB connection
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import Config

async def test_mongodb_connection():
    """Test MongoDB connection"""
    try:
        print("Testing MongoDB connection...")
        print(f"Connection URI: {Config.MONGODB_URI}")
        
        # Create client
        client = AsyncIOMotorClient(Config.MONGODB_URI)
        
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Test database access
        db = client.Apex_db
        collections = await db.list_collection_names()
        print(f"✅ Database 'Apex_db' accessible")
        print(f"Collections: {collections}")
        
        # Test users collection (verified users)
        users_count = await db.users.count_documents({})
        print(f"✅ Users collection (verified): {users_count} users")
        
        # Test pending_users collection (unverified users)
        pending_users_count = await db.pending_users.count_documents({})
        print(f"✅ Pending users collection (unverified): {pending_users_count} users")
        
        # Test images collection
        images_count = await db.images.count_documents({})
        print(f"✅ Images collection accessible. Count: {images_count}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure MongoDB is running")
        print("2. Check if MongoDB is installed")
        print("3. Verify the connection string")
        print("4. Try using MongoDB Atlas (cloud)")
        return False

if __name__ == "__main__":
    asyncio.run(test_mongodb_connection()) 