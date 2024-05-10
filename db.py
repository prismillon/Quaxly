import re
from motor.motor_asyncio import AsyncIOMotorClient
import os

import redis.asyncio
import redis

mongodb_url = os.environ.get("MONGODB_URL") or "mongodb://localhost:27017"

client = AsyncIOMotorClient(mongodb_url)
db = client["Quaxly"]

redis_url = os.environ.get("REDIS_URL") or "localhost"

r = redis.asyncio.Redis(host=redis_url, port=6379, socket_keepalive=True)
rs = redis.Redis(host=redis_url, port=6379)
