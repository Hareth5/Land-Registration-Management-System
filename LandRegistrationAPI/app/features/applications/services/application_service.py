from datetime import datetime

from app.database.mongo import db

from app.shared.crud import (
    create,
    get_one,
    get_many,
    update_one,
)
from .log_service import create_log

from ..enums import (
    ApplicationStatus,
)

from .workflow_service import (
    validate_transition,
)

applications_collection = db["land_applications"]

certificates_collection = db["certificates"]


def serialize_document(document):

    document["_id"] = str(document["_id"])

    return document


def generate_application_id():

    total = applications_collection.count_documents({})

    return f"LRMIS-2026-{total + 1:04d}"


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
            "submitted_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        },
        "internal": {
            "notes": [],
        },
    }

    inserted_id = create(
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

        application["_id"] = str(application["_id"])

    return application


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

    for application in applications:

        application["_id"] = str(application["_id"])

    return applications


def transition_application(
    application_id,
    new_status,
):
    application = get_one(applications_collection, {"application_id": application_id})
    if not application:
        raise Exception("Application not found")

    validate_transition(
        application,
        new_status,
    )

    application = update_one(
        applications_collection,
        {"application_id": application_id},
        {
            "status": new_status,
            "workflow.current_state": new_status,
            "timestamps.updated_at": datetime.utcnow(),
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

        raise Exception("Application not found")

    application = update_one(
        applications_collection,
        {"application_id": application_id},
        {
            "status": ApplicationStatus.ON_HOLD,
            "workflow.current_state": ApplicationStatus.ON_HOLD,
            "hold_reason": reason,
            "timestamps.updated_at": datetime.utcnow(),
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

        raise Exception("Rejection reason is required")

    application = get_one(applications_collection, {"application_id": application_id})

    if not application:

        raise Exception("Application not found")

    application = update_one(
        applications_collection,
        {"application_id": application_id},
        {
            "status": ApplicationStatus.REJECTED,
            "workflow.current_state": ApplicationStatus.REJECTED,
            "rejection_reason": reason,
            "timestamps.updated_at": datetime.utcnow(),
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

        raise Exception("Application not found")

    if application["status"] != ApplicationStatus.APPROVED:

        raise Exception("Application must be approved before issuing a certificate")

    certificate = {
        "certificate_id": f"CERT-{application_id}",
        "application_id": application_id,
        "issued_at": datetime.utcnow(),
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
            "certificate_id": certificate["certificate_id"],
            "timestamps.updated_at": datetime.utcnow(),
        },
    )
    create_log(
        application_id,
        "certificate_issued",
        {
            "certificate_id": certificate["certificate_id"],
        },
    )

    return certificate


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

        raise Exception("Application not found")

    application["internal"]["notes"].append(
        {
            "note": note,
            "created_at": datetime.utcnow(),
        }
    )

    application = update_one(
        applications_collection,
        {
            "application_id": application_id,
        },
        {
            "internal.notes": application["internal"]["notes"],
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

        raise Exception("Application not found")

    application = update_one(
        applications_collection,
        {
            "application_id": application_id,
        },
        {
            "status": ApplicationStatus.MISSING_DOCUMENTS,
            "workflow.current_state": ApplicationStatus.MISSING_DOCUMENTS,
            "missing_documents": documents,
            "timestamps.updated_at": datetime.utcnow(),
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

        raise Exception("Application not found")

    application = update_one(
        applications_collection,
        {
            "application_id": application_id,
        },
        {
            "status": ApplicationStatus.UNDER_OBJECTION,
            "workflow.current_state": ApplicationStatus.UNDER_OBJECTION,
            "objection_reason": reason,
            "timestamps.updated_at": datetime.utcnow(),
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
