from bson import ObjectId


def serialize_mongo(value):
    """Recursively convert BSON-only values into JSON-compatible values."""
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, dict):
        return {key: serialize_mongo(item) for key, item in value.items()}
    if isinstance(value, list):
        return [serialize_mongo(item) for item in value]
    if isinstance(value, tuple):
        return [serialize_mongo(item) for item in value]
    return value
