from pymongo import MongoClient

from app.core.config import settings

mongo_client = MongoClient(
    settings.MONGO_URI,
    connect=False,
    serverSelectionTimeoutMS=settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
)

db = mongo_client[settings.MONGO_DB_NAME]
