import re
from motor.motor_asyncio import AsyncIOMotorClient
import os

import redis.asyncio
import redis

mongodb_url = os.environ.get("MONGODB_URL")

mongodb_url = mongodb_url or "mongodb://localhost:27017"

client = AsyncIOMotorClient(mongodb_url)
db = client["quaxly"]

redis_url = os.environ.get("REDIS_URL")

redis_url = redis_url or "localhost"

r = redis.asyncio.Redis(host=redis_url, port=6379, socket_keepalive=True)
rs = redis.Redis(host=redis_url, port=6379)
