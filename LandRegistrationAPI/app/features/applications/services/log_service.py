from datetime import datetime, timezone

from app.database.mongo import db
from app.shared.crud import create

logs_collection = db["performance_logs"]


def create_log(application_id, action, details=None):

    log = {
        "application_id": application_id,
        "action": action,
        "details": details,
        "created_at": datetime.now(timezone.utc),
    }

    return create(
        logs_collection,
        log,
    )
