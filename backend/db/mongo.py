from motor.motor_asyncio import AsyncIOMotorClient
from quart import g
from backend.config import Config

async def get_db():
    if 'db' not in g:
        client = AsyncIOMotorClient(Config.MONGODB_URI)
        g.db = client.get_default_database()
    return g.db 