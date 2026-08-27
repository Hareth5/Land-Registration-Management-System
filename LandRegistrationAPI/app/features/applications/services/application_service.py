from datetime import datetime, timezone

from fastapi import HTTPException

from app.database.mongo import db
from app.shared.crud import (
    create,
    get_many,
    get_one,
    update_one,
)
from app.shared.serialization import serialize_mongo

from ..enums import (
    ApplicationStatus,
)
from .log_service import create_log
from .workflow_service import (
    ALLOWED_TRANSITIONS,
    validate_transition,
)

applications_collection = db["land_applications"]

certificates_collection = db["certificates"]


def serialize_document(document):
    return serialize_mongo(document)


def generate_application_id():

    total = applications_collection.count_documents({})

    year = datetime.now(timezone.utc).year

    return f"LRMIS-{year}-{total + 1:04d}"


def create_application(data):

    application = {
        "application_id": generate_application_id(),
        "application_type": data.application_type,
        "status": ApplicationStatus.SUBMITTED,
        "priority": "normal",
        "applicant_ref": {
            "applicant_id": data.applicant_id,
        },
        "parcel_ref": {
            "parcel_id": data.parcel_id,
        },
        "workflow": {
            "current_state": ApplicationStatus.SUBMITTED,
            "allowed_next": [
                ApplicationStatus.PRE_CHECKED,
            ],
            "transition_rules_version": "1.0",
        },
        "required_documents": [],
        "timestamps": {
            "submitted_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        },
        "internal": {
            "notes": [],
        },
    }

    create(
        applications_collection,
        application,
    )
    create_log(
        application["application_id"],
        "application_created",
    )

    return {"application_id": application["application_id"]}


def get_application(application_id):

    application = get_one(
        applications_collection,
        {"application_id": application_id},
    )

    if application:
        application = serialize_document(application)
        return application

    raise HTTPException(status_code=404, detail="Application not found")


def get_applications(
    filters=None,
    skip=0,
    limit=100,
    sort_field=None,
    sort_order=1,
):

    applications = get_many(
        applications_collection,
        filters,
        skip,
        limit,
        sort_field,
        sort_order,
    )

    return [serialize_document(application) for application in applications]


def transition_application(
    application_id,
    new_status,
):
    application = get_one(applications_collection, {"application_id": application_id})
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    try:
        validate_transition(application, new_status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    application = update_one(
        applications_collection,
        {"application_id": application_id},
        {
            "status": new_status,
            "workflow.current_state": new_status,
            "workflow.allowed_next": ALLOWED_TRANSITIONS.get(new_status, []),
            "timestamps.updated_at": datetime.now(timezone.utc),
        },
    )

    create_log(
        application_id,
        "status_changed",
        {
            "new_status": str(new_status),
        },
    )
    application = serialize_document(application)
    return application


def hold_application(
    application_id,
    reason,
):

    application = get_one(applications_collection, {"application_id": application_id})

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application = update_one(
        applications_collection,
        {"application_id": application_id},
        {
            "status": ApplicationStatus.ON_HOLD,
            "workflow.current_state": ApplicationStatus.ON_HOLD,
            "workflow.allowed_next": [],
            "hold_reason": reason,
            "timestamps.updated_at": datetime.now(timezone.utc),
        },
    )
    create_log(
        application_id,
        "application_on_hold",
        {
            "reason": reason,
        },
    )
    application = serialize_document(application)
    return application


def reject_application(
    application_id,
    reason,
):

    if not reason:
        raise HTTPException(status_code=400, detail="Rejection reason is required")

    application = get_one(applications_collection, {"application_id": application_id})

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application = update_one(
        applications_collection,
        {"application_id": application_id},
        {
            "status": ApplicationStatus.REJECTED,
            "workflow.current_state": ApplicationStatus.REJECTED,
            "workflow.allowed_next": [],
            "rejection_reason": reason,
            "timestamps.updated_at": datetime.now(timezone.utc),
        },
    )
    create_log(
        application_id,
        "application_rejected",
        {
            "reason": reason,
        },
    )
    application = serialize_document(application)
    return application


def generate_certificate(
    application_id,
):

    application = get_one(
        applications_collection,
        {
            "application_id": application_id,
        },
    )

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if application["status"] != ApplicationStatus.APPROVED:
        raise HTTPException(
            status_code=400,
            detail="Application must be approved before issuing a certificate",
        )

    certificate = {
        "certificate_id": f"CERT-{application_id}",
        "application_id": application_id,
        "issued_at": datetime.now(timezone.utc),
    }

    create(
        certificates_collection,
        certificate,
    )

    update_one(
        applications_collection,
        {
            "application_id": application_id,
        },
        {
            "status": ApplicationStatus.CERTIFICATE_ISSUED,
            "workflow.current_state": ApplicationStatus.CERTIFICATE_ISSUED,
            "workflow.allowed_next": ALLOWED_TRANSITIONS.get(
                ApplicationStatus.CERTIFICATE_ISSUED, []
            ),
            "certificate_id": certificate["certificate_id"],
            "timestamps.updated_at": datetime.now(timezone.utc),
        },
    )
    create_log(
        application_id,
        "certificate_issued",
        {
            "certificate_id": certificate["certificate_id"],
        },
    )

    return serialize_document(certificate)


def add_note(
    application_id,
    note,
):

    application = get_one(
        applications_collection,
        {
            "application_id": application_id,
        },
    )

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    notes = application.get("internal", {}).get("notes", [])
    notes.append(
        {
            "note": note,
            "created_at": datetime.now(timezone.utc),
        }
    )

    application = update_one(
        applications_collection,
        {
            "application_id": application_id,
        },
        {
            "internal.notes": notes,
        },
    )

    application = serialize_document(application)

    create_log(
        application_id,
        "note_added",
        {
            "note": note,
        },
    )

    return application


def mark_missing_documents(
    application_id,
    documents,
):

    application = get_one(
        applications_collection,
        {
            "application_id": application_id,
        },
    )

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application = update_one(
        applications_collection,
        {
            "application_id": application_id,
        },
        {
            "status": ApplicationStatus.MISSING_DOCUMENTS,
            "workflow.current_state": ApplicationStatus.MISSING_DOCUMENTS,
            "workflow.allowed_next": [],
            "missing_documents": documents,
            "timestamps.updated_at": datetime.now(timezone.utc),
        },
    )

    application = serialize_document(application)

    create_log(
        application_id,
        "missing_documents_marked",
        {
            "documents": documents,
        },
    )

    return application


def mark_under_objection(
    application_id,
    reason,
):

    application = get_one(
        applications_collection,
        {
            "application_id": application_id,
        },
    )

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    application = update_one(
        applications_collection,
        {
            "application_id": application_id,
        },
        {
            "status": ApplicationStatus.UNDER_OBJECTION,
            "workflow.current_state": ApplicationStatus.UNDER_OBJECTION,
            "workflow.allowed_next": [],
            "objection_reason": reason,
            "timestamps.updated_at": datetime.now(timezone.utc),
        },
    )

    application = serialize_document(application)

    create_log(
        application_id,
        "application_under_objection",
        {
            "reason": reason,
        },
    )

    return application
