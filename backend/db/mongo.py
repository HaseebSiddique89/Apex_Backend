from motor.motor_asyncio import AsyncIOMotorClient
from quart import current_app, g

async def get_db():
    if 'db' not in g:
        mongo_uri = current_app.config['MONGODB_URI']
        client = AsyncIOMotorClient(mongo_uri)
        g.db = client.get_default_database()
    return g.db 