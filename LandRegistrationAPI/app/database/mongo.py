from pymongo import MongoClient

from app.core.config import settings

mongo_client = MongoClient(settings.MONGODB_URL)

db = mongo_client[settings.DATABASE_NAME]
