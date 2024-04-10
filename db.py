from motor.motor_asyncio import AsyncIOMotorClient
import os

mongodb_url = os.environ.get("MONGODB_URL")
client = AsyncIOMotorClient(mongodb_url)
db = client["quaxly"]
