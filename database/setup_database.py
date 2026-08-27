"""Create MongoDB collections, validators, and indexes for LRMIS.

Run from the repository root with::

    python database/setup_database.py

The script is idempotent and never inserts application or demonstration data.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pymongo import ASCENDING, DESCENDING, GEOSPHERE, MongoClient
from pymongo.database import Database
from pymongo.errors import PyMongoError


ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT_DIR / "LandRegistrationAPI" / ".env"

APPLICATION_TYPES = [
    "first_registration",
    "ownership_transfer",
    "parcel_subdivision",
    "parcel_merge",
    "boundary_correction",
    "certificate_request",
]

APPLICATION_STATUSES = [
    "submitted",
    "pre_checked",
    "survey_required",
    "surveyed",
    "legal_review",
    "approved",
    "certificate_issued",
    "closed",
    "rejected",
    "on_hold",
    "missing_documents",
    "under_objection",
]

SURVEY_STATUSES = [
    "assigned",
    "visit_scheduled",
    "arrived_on_site",
    "survey_started",
    "survey_completed",
    "report_uploaded",
    "registrar_reviewed",
]

ID_TYPES = ["objectId", "string"]


def object_schema(required: list[str], properties: dict[str, Any]) -> dict[str, Any]:
    return {
        "bsonType": "object",
        "required": required,
        "properties": properties,
    }


COLLECTION_SCHEMAS: dict[str, dict[str, Any]] = {
    "land_applications": object_schema(
        [
            "application_id",
            "application_type",
            "status",
            "applicant_ref",
            "parcel_ref",
            "workflow",
            "required_documents",
            "timestamps",
        ],
        {
            "application_id": {"bsonType": "string"},
            "application_type": {"enum": APPLICATION_TYPES},
            "status": {"enum": APPLICATION_STATUSES},
            "priority": {"enum": ["low", "normal", "high", "urgent"]},
            "applicant_ref": object_schema(
                ["applicant_id"],
                {
                    "applicant_id": {"bsonType": ID_TYPES},
                    "applicant_type": {"bsonType": "string"},
                    "submitted_by_representative": {"bsonType": "bool"},
                },
            ),
            "parcel_ref": object_schema(
                ["parcel_id"],
                {
                    "parcel_id": {"bsonType": ID_TYPES},
                    "parcel_number": {"bsonType": "string"},
                    "block_number": {"bsonType": "string"},
                    "basin_number": {"bsonType": "string"},
                    "zone_id": {"bsonType": "string"},
                },
            ),
            "workflow": object_schema(
                ["current_state", "allowed_next", "transition_rules_version"],
                {
                    "current_state": {"enum": APPLICATION_STATUSES},
                    "allowed_next": {
                        "bsonType": "array",
                        "items": {"enum": APPLICATION_STATUSES},
                    },
                    "transition_rules_version": {"bsonType": "string"},
                },
            ),
            "required_documents": {"bsonType": "array"},
            "timestamps": object_schema(
                ["submitted_at", "updated_at"],
                {
                    "submitted_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": "date"},
                },
            ),
            "assignment": {"bsonType": "object"},
            "objection": {"bsonType": "object"},
            "internal": {"bsonType": "object"},
            "registrar_review": {"bsonType": "object"},
        },
    ),
    "parcels": object_schema(
        [
            "parcel_code",
            "parcel_number",
            "block_number",
            "basin_number",
            "zone_id",
            "geometry",
        ],
        {
            "parcel_code": {"bsonType": "string"},
            "parcel_number": {"bsonType": "string"},
            "block_number": {"bsonType": "string"},
            "basin_number": {"bsonType": "string"},
            "zone_id": {"bsonType": "string"},
            "current_owner_refs": {"bsonType": "array"},
            "area_sqm": {"bsonType": ["double", "int", "long", "decimal"]},
            "geometry": object_schema(
                ["type", "coordinates"],
                {
                    "type": {"enum": ["Point", "Polygon", "MultiPolygon"]},
                    "coordinates": {"bsonType": "array"},
                },
            ),
            "dispute_state": {"bsonType": "string"},
        },
    ),
    "applicants": object_schema(
        ["full_name", "applicant_type", "identity", "contacts", "address"],
        {
            "full_name": {"bsonType": "string"},
            "applicant_type": {
                "enum": [
                    "citizen",
                    "lawyer",
                    "company",
                    "surveyor",
                    "authorized_representative",
                ]
            },
            "identity": object_schema(
                ["national_id", "verified"],
                {
                    "national_id": {"bsonType": "string"},
                    "verified": {"bsonType": "bool"},
                    "verification_method": {"bsonType": ["string", "null"]},
                    "verified_at": {"bsonType": ["date", "null"]},
                },
            ),
            "contacts": object_schema(
                ["email", "phone"],
                {"email": {"bsonType": "string"}, "phone": {"bsonType": "string"}},
            ),
            "address": {"bsonType": "object"},
            "preferences": {"bsonType": "object"},
            "stats": {"bsonType": "object"},
            "verification_state": {
                "enum": ["unverified", "verified", "suspended"]
            },
            "created_at": {"bsonType": "date"},
        },
    ),
    "staff_members": object_schema(
        [
            "staff_code",
            "name",
            "role",
            "department",
            "skills",
            "contacts",
            "coverage",
            "workload",
            "active",
        ],
        {
            "staff_code": {"bsonType": "string"},
            "name": {"bsonType": "string"},
            "role": {"enum": ["surveyor", "registrar", "officer", "manager"]},
            "skills": {"bsonType": "array"},
            "coverage": {"bsonType": "object"},
            "schedule": {"bsonType": "object"},
            "workload": {"bsonType": "object"},
            "contacts": {"bsonType": "object"},
            "active": {"bsonType": "bool"},
            "created_at": {"bsonType": "date"},
        },
    ),
    "survey_tasks": object_schema(
        [
            "task_id",
            "application_id",
            "assigned_surveyor_id",
            "status",
            "milestones",
            "report_uploaded",
            "created_at",
        ],
        {
            "task_id": {"bsonType": "string"},
            "application_id": {"bsonType": "string"},
            "parcel_id": {"bsonType": ID_TYPES},
            "assigned_surveyor_id": {"bsonType": ID_TYPES},
            "status": {"enum": SURVEY_STATUSES},
            "milestones": {"bsonType": "array"},
            "field_notes": {"bsonType": "array"},
            "report_uploaded": {"bsonType": "bool"},
            "created_at": {"bsonType": "date"},
        },
    ),
    "survey_reports": object_schema(
        [
            "report_id",
            "application_id",
            "task_id",
            "uploaded_by",
            "report_title",
            "summary",
            "file_name",
            "file_path",
            "created_at",
        ],
        {
            "report_id": {"bsonType": "string"},
            "application_id": {"bsonType": "string"},
            "task_id": {"bsonType": "string"},
            "uploaded_by": {"bsonType": "string"},
            "report_title": {"bsonType": "string"},
            "summary": {"bsonType": "string"},
            "file_name": {"bsonType": "string"},
            "file_path": {"bsonType": "string"},
            "created_at": {"bsonType": "date"},
        },
    ),
    "performance_logs": object_schema(
        ["application_id"],
        {
            "application_id": {"bsonType": "string"},
            "action": {"bsonType": "string"},
            "details": {"bsonType": ["object", "null"]},
            "created_at": {"bsonType": "date"},
            "event_stream": {"bsonType": "array"},
            "computed_kpis": {"bsonType": "object"},
        },
    ),
    "certificates": object_schema(
        ["certificate_id", "application_id", "issued_at"],
        {
            "certificate_id": {"bsonType": "string"},
            "application_id": {"bsonType": "string"},
            "parcel_id": {"bsonType": ID_TYPES},
            "certificate_type": {"bsonType": "string"},
            "status": {"bsonType": "string"},
            "issued_to": {"bsonType": "object"},
            "issued_at": {"bsonType": "date"},
            "issued_by": {"bsonType": "string"},
            "verification": {"bsonType": "object"},
        },
    ),
    "application_documents": object_schema(
        ["document_id", "application_id", "document_type", "status", "uploaded_at"],
        {
            "document_id": {"bsonType": "string"},
            "application_id": {"bsonType": "string"},
            "document_type": {"bsonType": "string"},
            "required": {"bsonType": "bool"},
            "status": {"enum": ["missing", "pending_review", "verified", "rejected"]},
            "uploaded_by_applicant_id": {"bsonType": ID_TYPES},
            "uploaded_at": {"bsonType": "date"},
        },
    ),
    "objections": object_schema(
        ["objection_id", "application_id", "reason", "status", "submitted_at"],
        {
            "objection_id": {"bsonType": "string"},
            "application_id": {"bsonType": "string"},
            "submitted_by_applicant_id": {"bsonType": ID_TYPES},
            "reason": {"bsonType": "string"},
            "status": {"enum": ["submitted", "under_review", "accepted", "rejected", "resolved"]},
            "supporting_document_ids": {"bsonType": "array"},
            "submitted_at": {"bsonType": "date"},
        },
    ),
}


INDEXES: dict[str, list[tuple[list[tuple[str, Any]], dict[str, Any]]]] = {
    "land_applications": [
        ([("application_id", ASCENDING)], {"name": "application_id_unique", "unique": True}),
        ([("status", ASCENDING)], {"name": "status_idx"}),
        ([("application_type", ASCENDING)], {"name": "application_type_idx"}),
        ([("parcel_ref.parcel_number", ASCENDING)], {"name": "parcel_number_idx"}),
        ([("parcel_ref.zone_id", ASCENDING)], {"name": "application_zone_idx"}),
        ([("timestamps.submitted_at", DESCENDING)], {"name": "submitted_at_idx"}),
        ([("applicant_ref.applicant_id", ASCENDING)], {"name": "applicant_ref_idx"}),
        ([("status", ASCENDING), ("timestamps.updated_at", DESCENDING)], {"name": "status_updated_idx"}),
    ],
    "parcels": [
        ([("parcel_code", ASCENDING)], {"name": "parcel_code_unique", "unique": True}),
        ([("geometry", GEOSPHERE)], {"name": "geometry_2dsphere"}),
        ([("zone_id", ASCENDING)], {"name": "parcel_zone_idx"}),
        ([("parcel_number", ASCENDING), ("block_number", ASCENDING), ("basin_number", ASCENDING)], {"name": "parcel_identity_idx"}),
        ([("dispute_state", ASCENDING)], {"name": "dispute_state_idx"}),
    ],
    "applicants": [
        ([("identity.national_id", ASCENDING)], {"name": "national_id_unique", "unique": True}),
        ([("applicant_type", ASCENDING)], {"name": "applicant_type_idx"}),
        ([("address.city", ASCENDING)], {"name": "applicant_city_idx"}),
    ],
    "staff_members": [
        ([("staff_code", ASCENDING)], {"name": "staff_code_unique", "unique": True}),
        ([("role", ASCENDING), ("active", ASCENDING)], {"name": "role_active_idx"}),
        ([("coverage.zone_ids", ASCENDING)], {"name": "coverage_zone_idx"}),
        ([("coverage.geo_fence", GEOSPHERE)], {"name": "coverage_geo_fence_2dsphere"}),
    ],
    "survey_tasks": [
        ([("task_id", ASCENDING)], {"name": "task_id_unique", "unique": True}),
        ([("application_id", ASCENDING)], {"name": "survey_application_idx"}),
        ([("assigned_surveyor_id", ASCENDING), ("status", ASCENDING)], {"name": "surveyor_status_idx"}),
    ],
    "survey_reports": [
        ([("report_id", ASCENDING)], {"name": "report_id_unique", "unique": True}),
        ([("application_id", ASCENDING)], {"name": "report_application_idx"}),
        ([("task_id", ASCENDING)], {"name": "report_task_idx"}),
    ],
    "performance_logs": [
        ([("application_id", ASCENDING)], {"name": "log_application_idx"}),
        ([("created_at", DESCENDING)], {"name": "log_created_at_idx"}),
        ([("event_stream.at", DESCENDING)], {"name": "event_time_idx"}),
    ],
    "certificates": [
        ([("certificate_id", ASCENDING)], {"name": "certificate_id_unique", "unique": True}),
        ([("application_id", ASCENDING)], {"name": "certificate_application_idx"}),
        ([("issued_at", DESCENDING)], {"name": "certificate_issued_at_idx"}),
    ],
    "application_documents": [
        ([("document_id", ASCENDING)], {"name": "document_id_unique", "unique": True}),
        ([("application_id", ASCENDING), ("status", ASCENDING)], {"name": "document_application_status_idx"}),
        ([("uploaded_by_applicant_id", ASCENDING)], {"name": "document_uploader_idx"}),
    ],
    "objections": [
        ([("objection_id", ASCENDING)], {"name": "objection_id_unique", "unique": True}),
        ([("application_id", ASCENDING), ("status", ASCENDING)], {"name": "objection_application_status_idx"}),
        ([("submitted_by_applicant_id", ASCENDING)], {"name": "objection_submitter_idx"}),
    ],
}


def load_database_config() -> tuple[str, str, int]:
    load_dotenv(ENV_FILE)
    uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URL")
    database_name = os.getenv("MONGO_DB_NAME") or os.getenv("DATABASE_NAME")
    timeout_ms = int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS", "5000"))

    if not uri:
        raise RuntimeError(
            f"MONGO_URI is not configured. Copy {ENV_FILE.name}.example to {ENV_FILE.name}."
        )
    if not database_name:
        raise RuntimeError("MONGO_DB_NAME is not configured.")

    return uri, database_name, timeout_ms


def get_database() -> tuple[MongoClient, Database]:
    uri, database_name, timeout_ms = load_database_config()
    client = MongoClient(uri, serverSelectionTimeoutMS=timeout_ms)
    client.admin.command("ping")
    return client, client[database_name]


def configure_database(database: Database) -> None:
    existing = set(database.list_collection_names())

    for collection_name, schema in COLLECTION_SCHEMAS.items():
        validator = {"$jsonSchema": schema}
        if collection_name not in existing:
            database.create_collection(
                collection_name,
                validator=validator,
                validationLevel="moderate",
                validationAction="error",
            )
            print(f"Created collection: {collection_name}")
        else:
            database.command(
                "collMod",
                collection_name,
                validator=validator,
                validationLevel="moderate",
                validationAction="error",
            )
            print(f"Updated validator: {collection_name}")

        collection = database[collection_name]
        for keys, options in INDEXES[collection_name]:
            index_name = collection.create_index(keys, **options)
            print(f"  ensured index: {index_name}")


def main() -> None:
    client = None
    try:
        client, database = get_database()
        print(f"Connected to MongoDB database: {database.name}")
        configure_database(database)
        print("Database setup completed. No sample data was inserted.")
    except PyMongoError:
        raise SystemExit(
            "Database setup failed: MongoDB is unavailable. Verify MONGO_URI, "
            "start the local server, or check Atlas network access."
        ) from None
    except (RuntimeError, ValueError) as exc:
        raise SystemExit(f"Database setup failed: {exc}") from exc
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    main()
