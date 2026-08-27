"""Insert interconnected fictional demonstration data for LRMIS.

Run ``python database/setup_database.py`` before running this script. Re-running
this script replaces only documents tagged as this project's sample dataset.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from bson import ObjectId
from pymongo.database import Database
from pymongo.errors import PyMongoError

from setup_database import COLLECTION_SCHEMAS, get_database


SEED_TAG = "lrmis-fictional-sample-v1"
BASE_TIME = datetime(2026, 3, 2, 8, 0, tzinfo=timezone.utc)

APPLICANT_IDS = [ObjectId(f"6751000000000000000001{i:02d}") for i in range(1, 5)]
PARCEL_IDS = [ObjectId(f"6751000000000000000002{i:02d}") for i in range(1, 7)]
STAFF_IDS = [ObjectId(f"6751000000000000000003{i:02d}") for i in range(1, 4)]
TASK_IDS = [ObjectId(f"6751000000000000000004{i:02d}") for i in range(1, 4)]
REPORT_IDS = [ObjectId(f"6751000000000000000005{i:02d}") for i in range(1, 3)]
CERTIFICATE_IDS = [ObjectId(f"6751000000000000000006{i:02d}") for i in range(1, 3)]

APPLICATION_TYPES = [
    "first_registration",
    "ownership_transfer",
    "parcel_subdivision",
    "parcel_merge",
    "boundary_correction",
    "certificate_request",
]

ALLOWED_NEXT = {
    "submitted": ["pre_checked"],
    "pre_checked": ["survey_required", "legal_review"],
    "survey_required": ["surveyed"],
    "surveyed": ["legal_review"],
    "legal_review": ["approved", "rejected"],
    "approved": ["certificate_issued"],
    "certificate_issued": ["closed"],
}

WORKFLOW_ORDER = [
    "submitted",
    "pre_checked",
    "survey_required",
    "surveyed",
    "legal_review",
    "approved",
    "certificate_issued",
    "closed",
]


def sample_applicants() -> list[dict[str, Any]]:
    profiles = [
        ("Lina Haddad", "citizen", "SAMPLE-NID-1001", "lina.haddad@example.test", "+970-555-0101", "Ramallah", True),
        ("Omar Saleh", "lawyer", "SAMPLE-NID-1002", "omar.saleh@example.test", "+970-555-0102", "Al-Bireh", True),
        ("Green Horizon Holdings", "company", "SAMPLE-REG-2001", "registry@example.test", "+970-555-0103", "Ramallah", True),
        ("Maya Darwish", "authorized_representative", "SAMPLE-NID-1004", "maya.darwish@example.test", "+970-555-0104", "Birzeit", False),
    ]

    documents = []
    for index, (name, applicant_type, identity_number, email, phone, city, verified) in enumerate(profiles):
        linked = [f"LRMIS-2026-{number:04d}" for number in range(index + 1, 13, 4)]
        documents.append(
            {
                "_id": APPLICANT_IDS[index],
                "full_name": name,
                "applicant_type": applicant_type,
                "identity": {
                    "national_id": identity_number,
                    "verified": verified,
                    "verification_method": "email_otp_stub" if verified else None,
                    "verified_at": BASE_TIME - timedelta(days=30) if verified else None,
                },
                "verification_state": "verified" if verified else "unverified",
                "contacts": {"email": email, "phone": phone},
                "address": {
                    "city": city,
                    "street": "Fictional Civic Street",
                    "neighborhood": "Central District",
                    "zone_id": "ZONE-RM-01" if index != 3 else "ZONE-RM-02",
                },
                "preferences": {
                    "preferred_contact": "email",
                    "language": "ar" if index % 2 == 0 else "en",
                    "notifications": {
                        "on_status_change": True,
                        "on_missing_documents": True,
                        "on_certificate_ready": True,
                    },
                },
                "privacy_settings": {
                    "show_phone_to_staff_only": True,
                    "allow_service_notifications": True,
                },
                "linked_application_ids": linked,
                "stats": {
                    "total_applications": len(linked),
                    "approved_applications": sum(number in {6, 7, 8} for number in range(index + 1, 13, 4)),
                    "pending_applications": sum(number in {1, 2, 3, 4, 5, 9, 10, 12} for number in range(index + 1, 13, 4)),
                },
                "created_at": BASE_TIME - timedelta(days=45 - index),
                "seed_tag": SEED_TAG,
            }
        )
    return documents


def polygon(longitude: float, latitude: float) -> dict[str, Any]:
    offset = 0.0012
    return {
        "type": "Polygon",
        "coordinates": [
            [
                [longitude, latitude],
                [longitude + offset, latitude],
                [longitude + offset, latitude + offset],
                [longitude, latitude + offset],
                [longitude, latitude],
            ]
        ],
    }


def sample_parcels() -> list[dict[str, Any]]:
    parcel_specs = [
        ("RM-Z01-B12-P145", "145", "12", "3", "ZONE-RM-01", 35.2001, 31.9021, 850.5, "residential", "registered", "none"),
        ("RM-Z01-B12-P146", "146", "12", "3", "ZONE-RM-01", 35.2030, 31.9024, 620.0, "commercial", "registered", "none"),
        ("RM-Z02-B08-P077", "77", "8", "5", "ZONE-RM-02", 35.1904, 31.9150, 1120.75, "agricultural", "provisional", "none"),
        ("RM-Z02-B08-P078", "78", "8", "5", "ZONE-RM-02", 35.1930, 31.9168, 940.25, "residential", "registered", "under_objection"),
        ("RM-Z03-B21-P009", "9", "21", "2", "ZONE-RM-03", 35.2140, 31.8890, 480.0, "residential", "registered", "none"),
        ("RM-Z03-B21-P010", "10", "21", "2", "ZONE-RM-03", 35.2160, 31.8910, 505.4, "mixed_use", "registered", "none"),
    ]

    return [
        {
            "_id": PARCEL_IDS[index],
            "parcel_code": code,
            "parcel_number": parcel_number,
            "block_number": block_number,
            "basin_number": basin_number,
            "zone_id": zone_id,
            "current_owner_refs": [
                {"applicant_id": APPLICANT_IDS[index % len(APPLICANT_IDS)], "share": "1/1"}
            ],
            "area_sqm": area,
            "land_use": land_use,
            "registration_status": registration_status,
            "geometry": polygon(longitude, latitude),
            "address_hint": f"Fictional parcel in {zone_id}",
            "dispute_state": dispute_state,
            "created_at": BASE_TIME - timedelta(days=90 - index),
            "updated_at": BASE_TIME - timedelta(days=index),
            "seed_tag": SEED_TAG,
        }
        for index, (
            code,
            parcel_number,
            block_number,
            basin_number,
            zone_id,
            longitude,
            latitude,
            area,
            land_use,
            registration_status,
            dispute_state,
        ) in enumerate(parcel_specs)
    ]


def sample_staff() -> list[dict[str, Any]]:
    staff_specs = [
        ("SURV-RM-01", "North Survey Team", "surveyor", ["boundary_survey", "gps_mapping"], ["ZONE-RM-01", "ZONE-RM-02"], 2),
        ("SURV-RM-02", "South Survey Team", "surveyor", ["parcel_subdivision", "parcel_merge", "gps_mapping"], ["ZONE-RM-02", "ZONE-RM-03"], 1),
        ("REG-RM-01", "Registrar Review Desk", "registrar", ["legal_review", "ownership_transfer"], ["ZONE-RM-01", "ZONE-RM-02", "ZONE-RM-03"], 2),
    ]

    documents = []
    for index, (staff_code, name, role, skills, zones, active_tasks) in enumerate(staff_specs):
        coverage = {"zone_ids": zones}
        if role == "surveyor":
            coverage["geo_fence"] = polygon(35.185 + index * 0.015, 31.885)
        documents.append(
            {
                "_id": STAFF_IDS[index],
                "staff_code": staff_code,
                "name": name,
                "role": role,
                "department": "Cadastral Survey" if role == "surveyor" else "Land Registration",
                "skills": skills,
                "coverage": coverage,
                "schedule": {
                    "timezone": "Asia/Jerusalem",
                    "shifts": [
                        {"day": day, "start": "08:00", "end": "16:00"}
                        for day in ["Mon", "Tue", "Wed", "Thu"]
                    ],
                    "on_call": False,
                },
                "workload": {"active_tasks": active_tasks, "max_tasks": 8},
                "contacts": {
                    "phone": f"+970-555-02{index + 1:02d}",
                    "email": f"{staff_code.lower()}@example.test",
                },
                "active": True,
                "created_at": BASE_TIME - timedelta(days=60 - index),
                "seed_tag": SEED_TAG,
            }
        )
    return documents


def workflow_timestamps(status: str, submitted_at: datetime) -> dict[str, Any]:
    timestamps: dict[str, Any] = {
        "submitted_at": submitted_at,
        "updated_at": submitted_at + timedelta(days=1),
    }
    if status in WORKFLOW_ORDER:
        current_index = WORKFLOW_ORDER.index(status)
        for index, state in enumerate(WORKFLOW_ORDER[1 : current_index + 1], start=1):
            timestamps[f"{state}_at"] = submitted_at + timedelta(hours=index * 6)
        timestamps["updated_at"] = submitted_at + timedelta(hours=max(current_index, 1) * 6)
    return timestamps


def application_document(
    application_number: int,
    document_number: int,
    applicant_id: ObjectId,
    status: str,
    submitted_at: datetime,
) -> dict[str, Any]:
    document_types = ["ownership_deed", "id_copy", "sale_contract"]
    document_type = document_types[document_number]
    document_id = f"DOC-2026-{application_number:04d}-{document_number + 1}"
    document = {
        "document_id": document_id,
        "document_type": document_type,
        "required": True,
        "status": status,
        "file_name": f"{document_type}-{application_number:04d}.pdf" if status != "missing" else None,
        "file_url": f"sample://documents/{document_id}" if status != "missing" else None,
        "mime_type": "application/pdf" if status != "missing" else None,
        "file_size": 120000 + application_number * 100 if status != "missing" else None,
        "uploaded_by_applicant_id": str(applicant_id) if status != "missing" else None,
        "notes": "Fictional demonstration document.",
    }
    if status != "missing":
        document["uploaded_at"] = submitted_at + timedelta(hours=document_number + 1)
    return document


def sample_applications(parcels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    statuses = [
        "submitted",
        "pre_checked",
        "survey_required",
        "surveyed",
        "legal_review",
        "approved",
        "certificate_issued",
        "closed",
        "under_objection",
        "missing_documents",
        "rejected",
        "on_hold",
    ]
    applicant_types = ["citizen", "lawyer", "company", "authorized_representative"]
    documents = []

    for index, status in enumerate(statuses, start=1):
        applicant_index = (index - 1) % len(APPLICANT_IDS)
        parcel = parcels[(index - 1) % len(parcels)]
        submitted_at = BASE_TIME - timedelta(days=26 - index)
        document_status = "missing" if status == "missing_documents" else (
            "pending_review" if status in {"submitted", "pre_checked"} else "verified"
        )
        required_documents = [
            application_document(index, 0, APPLICANT_IDS[applicant_index], document_status, submitted_at),
            application_document(index, 1, APPLICANT_IDS[applicant_index], "verified", submitted_at),
        ]
        application_id = f"LRMIS-2026-{index:04d}"
        application = {
            "_id": ObjectId(f"6751000000000000000000{index:02d}"),
            "application_id": application_id,
            "application_type": APPLICATION_TYPES[(index - 1) % len(APPLICATION_TYPES)],
            "status": status,
            "priority": "high" if status in {"under_objection", "on_hold"} else "normal",
            "applicant_ref": {
                "applicant_id": APPLICANT_IDS[applicant_index],
                "applicant_type": applicant_types[applicant_index],
                "submitted_by_representative": applicant_types[applicant_index] == "authorized_representative",
            },
            "parcel_ref": {
                "parcel_id": parcel["_id"],
                "parcel_number": parcel["parcel_number"],
                "block_number": parcel["block_number"],
                "basin_number": parcel["basin_number"],
                "zone_id": parcel["zone_id"],
            },
            "description": f"Fictional {APPLICATION_TYPES[(index - 1) % len(APPLICATION_TYPES)].replace('_', ' ')} case.",
            "tags": [APPLICATION_TYPES[(index - 1) % len(APPLICATION_TYPES)], "sample_data"],
            "workflow": {
                "current_state": status,
                "allowed_next": ALLOWED_NEXT.get(status, []),
                "transition_rules_version": "1.0",
            },
            "required_documents": required_documents,
            "timestamps": workflow_timestamps(status, submitted_at),
            "assignment": {
                "assigned_surveyor_id": None,
                "assigned_registrar_id": STAFF_IDS[2],
                "assignment_policy": "zone+availability+workload",
            },
            "objection": {"has_objection": False, "objection_ids": []},
            "internal": {
                "notes": [
                    {
                        "note": f"Sample case prepared in {status} state.",
                        "created_at": submitted_at + timedelta(minutes=30),
                    }
                ],
                "visibility": "staff_only",
            },
            "seed_tag": SEED_TAG,
        }

        if index in {3, 4, 5}:
            application["assignment"]["assigned_surveyor_id"] = STAFF_IDS[(index - 3) % 2]
        if status == "under_objection":
            objection_id = "OBJ-2026-0001"
            application["objection"] = {"has_objection": True, "objection_ids": [objection_id]}
            application["objection_reason"] = "A fictional boundary clarification is pending review."
        if status == "missing_documents":
            application["missing_documents"] = ["ownership_deed"]
        if status == "rejected":
            application["rejection_reason"] = "Fictional application did not satisfy ownership evidence requirements."
        if status == "on_hold":
            application["hold_reason"] = "Awaiting a fictional cadastral correction."
        if status in {"certificate_issued", "closed"}:
            application["certificate_id"] = f"CERT-LRMIS-2026-{index:04d}"

        documents.append(application)

    return documents


def sample_tasks() -> list[dict[str, Any]]:
    specs = [
        (3, "assigned", STAFF_IDS[0], False, ["assigned"]),
        (4, "report_uploaded", STAFF_IDS[1], True, ["assigned", "visit_scheduled", "arrived_on_site", "survey_started", "survey_completed", "report_uploaded"]),
        (5, "report_uploaded", STAFF_IDS[0], True, ["assigned", "visit_scheduled", "arrived_on_site", "survey_started", "survey_completed", "report_uploaded"]),
    ]
    tasks = []
    for index, (application_number, status, surveyor_id, report_uploaded, milestones) in enumerate(specs):
        created_at = BASE_TIME - timedelta(days=12 - index)
        tasks.append(
            {
                "_id": TASK_IDS[index],
                "task_id": f"SURV-2026-{index + 1:04d}",
                "application_id": f"LRMIS-2026-{application_number:04d}",
                "parcel_id": PARCEL_IDS[(application_number - 1) % len(PARCEL_IDS)],
                "assigned_surveyor_id": surveyor_id,
                "status": status,
                "milestones": [
                    {
                        "type": milestone,
                        "at": created_at + timedelta(hours=step * 4),
                        "by": "system" if milestone == "assigned" else "surveyor",
                        "meta": {"note": "Fictional sample milestone"},
                    }
                    for step, milestone in enumerate(milestones)
                ],
                "field_notes": ["Boundary markers inspected; sample record only."],
                "report_uploaded": report_uploaded,
                "created_at": created_at,
                "seed_tag": SEED_TAG,
            }
        )
    return tasks


def sample_reports() -> list[dict[str, Any]]:
    return [
        {
            "_id": REPORT_IDS[index],
            "report_id": f"REP-2026-{index + 1:04d}",
            "application_id": f"LRMIS-2026-{application_number:04d}",
            "task_id": f"SURV-2026-{index + 2:04d}",
            "uploaded_by": str(STAFF_IDS[index % 2]),
            "report_title": "Fictional cadastral field survey",
            "summary": "Sample survey confirms the recorded parcel boundary for demonstration purposes.",
            "file_name": f"sample-survey-{index + 1}.pdf",
            "file_path": f"sample://survey-reports/sample-survey-{index + 1}.pdf",
            "created_at": BASE_TIME - timedelta(days=7 - index),
            "seed_tag": SEED_TAG,
        }
        for index, application_number in enumerate([4, 5])
    ]


def sample_certificates() -> list[dict[str, Any]]:
    return [
        {
            "_id": CERTIFICATE_IDS[index],
            "certificate_id": f"CERT-LRMIS-2026-{application_number:04d}",
            "application_id": f"LRMIS-2026-{application_number:04d}",
            "parcel_id": PARCEL_IDS[(application_number - 1) % len(PARCEL_IDS)],
            "certificate_type": "ownership_certificate",
            "status": "issued",
            "issued_to": {
                "applicant_id": APPLICANT_IDS[(application_number - 1) % len(APPLICANT_IDS)],
                "full_name": "Fictional certificate holder",
            },
            "issued_at": BASE_TIME - timedelta(days=3 - index),
            "issued_by": str(STAFF_IDS[2]),
            "verification": {
                "qr_code_url": f"/certificates/CERT-LRMIS-2026-{application_number:04d}/verify",
                "digital_signature_stub": f"sample-signature-{application_number:04d}",
            },
            "seed_tag": SEED_TAG,
        }
        for index, application_number in enumerate([7, 8])
    ]


def standalone_documents(applications: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for application in applications:
        for document in application["required_documents"]:
            if "uploaded_at" not in document:
                continue
            records.append(
                {
                    "document_id": document["document_id"],
                    "application_id": application["application_id"],
                    "document_type": document["document_type"],
                    "required": document["required"],
                    "status": document["status"],
                    "file_name": document["file_name"],
                    "file_url": document["file_url"],
                    "mime_type": document["mime_type"],
                    "file_size": document["file_size"],
                    "uploaded_by_applicant_id": ObjectId(document["uploaded_by_applicant_id"]),
                    "notes": document["notes"],
                    "uploaded_at": document["uploaded_at"],
                    "seed_tag": SEED_TAG,
                }
            )
    return records


def sample_objections() -> list[dict[str, Any]]:
    return [
        {
            "objection_id": "OBJ-2026-0001",
            "application_id": "LRMIS-2026-0009",
            "submitted_by_applicant_id": APPLICANT_IDS[0],
            "reason": "Fictional request to verify a shared boundary before registration continues.",
            "status": "under_review",
            "supporting_document_ids": ["DOC-2026-0009-1"],
            "registrar_notes": "Sample objection queued for cadastral review.",
            "submitted_at": BASE_TIME - timedelta(days=5),
            "seed_tag": SEED_TAG,
        }
    ]


def sample_logs(applications: list[dict[str, Any]]) -> list[dict[str, Any]]:
    logs = []
    for index, application in enumerate(applications):
        submitted_at = application["timestamps"]["submitted_at"]
        logs.append(
            {
                "application_id": application["application_id"],
                "event_stream": [
                    {
                        "type": "submitted",
                        "by": {
                            "actor_type": "applicant",
                            "actor_id": str(application["applicant_ref"]["applicant_id"]),
                        },
                        "at": submitted_at,
                        "meta": {"channel": "sample_web"},
                    },
                    {
                        "type": application["status"],
                        "by": {"actor_type": "system", "actor_id": "sample_seed"},
                        "at": application["timestamps"]["updated_at"],
                        "meta": {"sample": True},
                    },
                ],
                "computed_kpis": {
                    "processing_days": max((BASE_TIME - submitted_at).days, 0),
                    "precheck_minutes": 60 if index > 0 else None,
                    "survey_delay_days": 2 if index in {3, 4} else None,
                    "certificate_issued": application["status"] in {"certificate_issued", "closed"},
                },
                "seed_tag": SEED_TAG,
            }
        )

    logs.append(
        {
            "application_id": "LRMIS-2026-0001",
            "action": "application_created",
            "details": {"source": "sample_data"},
            "created_at": applications[0]["timestamps"]["submitted_at"],
            "seed_tag": SEED_TAG,
        }
    )
    return logs


def build_sample_data() -> dict[str, list[dict[str, Any]]]:
    parcels = sample_parcels()
    applications = sample_applications(parcels)
    return {
        "applicants": sample_applicants(),
        "parcels": parcels,
        "staff_members": sample_staff(),
        "land_applications": applications,
        "application_documents": standalone_documents(applications),
        "objections": sample_objections(),
        "survey_tasks": sample_tasks(),
        "survey_reports": sample_reports(),
        "certificates": sample_certificates(),
        "performance_logs": sample_logs(applications),
    }


def insert_sample_data(database: Database) -> dict[str, int]:
    missing_collections = set(COLLECTION_SCHEMAS) - set(database.list_collection_names())
    if missing_collections:
        missing = ", ".join(sorted(missing_collections))
        raise RuntimeError(
            f"Database setup is incomplete ({missing}). Run database/setup_database.py first."
        )

    sample_data = build_sample_data()
    counts = {}
    for collection_name, documents in sample_data.items():
        collection = database[collection_name]
        collection.delete_many({"seed_tag": SEED_TAG})
        if documents:
            collection.insert_many(documents, ordered=True)
        counts[collection_name] = len(documents)
    return counts


def main() -> None:
    client = None
    try:
        client, database = get_database()
        counts = insert_sample_data(database)
        print(f"Sample data loaded into database: {database.name}")
        for collection_name, count in counts.items():
            print(f"  {collection_name}: {count}")
    except PyMongoError:
        raise SystemExit(
            "Sample data load failed: MongoDB is unavailable. Verify MONGO_URI, "
            "start the local server, or check Atlas network access."
        ) from None
    except (RuntimeError, ValueError) as exc:
        raise SystemExit(f"Sample data load failed: {exc}") from exc
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    main()
