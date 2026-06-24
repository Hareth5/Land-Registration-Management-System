from fastapi import HTTPException, status
from bson import ObjectId
from datetime import datetime, timezone

from app.shared.crud import (
    create,
    get_many,
    get_one,
)

from app.database.mongo import db

from .schemas import (
    ApplicantCreate,
    ApplicationDocumentCreate,
    ApplicationCommentCreate,
    ApplicationObjectionCreate,
)

applicants_collection = db["applicants"]

land_applications_collection = db["land_applications"]

performance_logs_collection = db["performance_logs"]


# this methode to convert to json to best represent
def serialize_applicant(applicant: dict) -> dict:
    return {
        "id": str(applicant["_id"]),
        "full_name": applicant["full_name"],
        "applicant_type": applicant["applicant_type"],
        "identity": applicant["identity"],
        "contacts": applicant["contacts"],
        "address": applicant["address"],
        "preferences": applicant["preferences"],
        "stats": applicant.get(
            "stats",
            {
                "total_applications": 0,
                "approved_applications": 0,
                "pending_applications": 0,
            },
        ),
        "created_at": applicant.get("created_at"),
    }


# 1 Create applicant (POST /applicants)
def create_applicant_service(applicant: ApplicantCreate):
    # MongoDB can not store pydantic object so must convert to py dictinory
    applicant_dict = applicant.model_dump()

    # we must check if the national id is already exist or not
    national_id = applicant_dict["identity"]["national_id"]
    if get_one(applicants_collection, {"identity.national_id": national_id}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Applicant with this national id is already exists",
        )

    # if not exists we must assigne verefication and stats detailse :
    applicant_dict["identity"]["verified"] = False
    applicant_dict["identity"]["verification_method"] = None
    applicant_dict["identity"]["verified_at"] = None

    applicant_dict["stats"] = {
        "total_applications": 0,
        "approved_applications": 0,
        "pending_applications": 0,
    }
    applicant_dict["created_at"] = datetime.now(timezone.utc)

    inserted_id = create(applicants_collection, applicant_dict)
    created_applicant = get_one(applicants_collection, {"_id": inserted_id})
    # must convert from Objectid to string (json canot understand Objectid)
    created_applicant["_id"] = str(created_applicant["_id"])

    return {
        "message": "Applicant created successfully",
        "applicant": serialize_applicant(created_applicant),
    }


# 2 get applicant by id (GET /applicants/{applicant_id})
def get_applicant_by_id_service(applicant_id: str) -> dict:
    # must check if applicant_id fromat is correct
    if not ObjectId.is_valid(applicant_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid applicant ID format",
        )

    applicant = get_one(applicants_collection, {"_id": ObjectId(applicant_id)})

    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found"
        )

    return serialize_applicant(applicant)


# 3 get applications linked to specific applicant
def serialize_applicant_application(application: dict) -> dict:
    timestamps = application.get("timestamps", {})

    return {
        "id": str(application["_id"]),
        "application_id": application.get("application_id"),
        "application_type": application.get("application_type"),
        "status": application.get("status"),
        "priority": application.get("priority"),
        "parcel_ref": {
            "parcel_number": application.get("parcel_ref", {}).get("parcel_number"),
            "block_number": application.get("parcel_ref", {}).get("block_number"),
            "basin_number": application.get("parcel_ref", {}).get("basin_number"),
            "zone_id": application.get("parcel_ref", {}).get("zone_id"),
        },
        "submitted_at": timestamps.get("submitted_at"),
        "updated_at": timestamps.get("updated_at"),
    }


def get_applicant_applications_service(applicant_id: str) -> dict:
    # check if this object coming we can make it MongoDB ObjectId
    # because if user enter "abc" -> ObjectId("abc") must make exception
    if not ObjectId.is_valid(applicant_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid applicant ID format",
        )

    # convert id entered by user into ObjectId to
    # be able to search in MongoDB (String --> ObjectId)
    applicant_object_id = ObjectId(applicant_id)

    applicant = get_one(applicants_collection, {"_id": applicant_object_id})

    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Applicant not found"
        )

    applications = get_many(
        land_applications_collection,
        {"applicant_ref.applicant_id": applicant_object_id},
        sort_field="timestamps.submitted_at",
        sort_order=-1,
    )

    # applied the serialize_applicant_application
    # function to each application located inside applications
    # and stored the new results inside a list
    #  named serialized_applications.
    serialized_applications = []
    for application in applications:
        serialized_application = serialize_applicant_application(application)
        serialized_applications.append(serialized_application)

    return {
        "applicant_id": applicant_id,
        "total": len(serialized_applications),
        "applications": serialized_applications,
    }


# 4 add documents to specefic application(POST /applications/{application_id}/documents)
def serialize_embedded_application_document(
    application_id: str, document: dict
) -> dict:
    return {
        "document_id": document["document_id"],
        "application_id": application_id,
        "document_type": document["document_type"],
        "required": document["required"],
        "status": document["status"],
        "file_name": document.get("file_name"),
        "file_url": document.get("file_url"),
        "mime_type": document.get("mime_type"),
        "file_size": document.get("file_size"),
        "uploaded_by_applicant_id": document.get("uploaded_by_applicant_id"),
        "notes": document.get("notes"),
        "uploaded_at": document["uploaded_at"],
    }


application = None
document_dict = None


def add_application_document_service(
    application_id: str, document_data: ApplicationDocumentCreate
) -> dict:
    application = get_one(
        land_applications_collection, {"application_id": application_id}
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    # MongoDB can not store pydantic object so must convert to py dictinory
    document_dict = document_data.model_dump()

    now = datetime.now(timezone.utc)

    # 5 create new document
    new_document = {
        "document_id": str(ObjectId()),
        "document_type": document_dict["document_type"],
        "required": False,
        "status": "pending_review",
        "file_name": document_dict["file_name"],
        "file_url": document_dict.get("file_url"),
        "mime_type": document_dict.get("mime_type"),
        "file_size": document_dict.get("file_size"),
        "uploaded_by_applicant_id": document_dict.get("uploaded_by_applicant_id"),
        "notes": document_dict.get("notes"),
        "uploaded_at": now,
    }
    # get existing documents in the application
    existing_documents = application.get("required_documents", [])

    is_exists = any(
        document.get("document_type") == document_dict["document_type"]
        for document in existing_documents
    )

    if is_exists:
        update_result = land_applications_collection.update_one(
            {
                "application_id": application_id,
                "required_documents.document_type": document_dict["document_type"],
            },
            {
                "$set": {
                    "required_documents.$.document_id": new_document["document_id"],
                    "required_documents.$.status": new_document["status"],
                    "required_documents.$.file_name": new_document["file_name"],
                    "required_documents.$.file_url": new_document["file_url"],
                    "required_documents.$.mime_type": new_document["mime_type"],
                    "required_documents.$.file_size": new_document["file_size"],
                    "required_documents.$.uploaded_by_applicant_id": new_document[
                        "uploaded_by_applicant_id"
                    ],
                    "required_documents.$.notes": new_document["notes"],
                    "required_documents.$.uploaded_at": new_document["uploaded_at"],
                    "timestamps.updated_at": now,
                }
            },
        )

        if update_result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document could not be updated",
            )
    else:
        update_result = land_applications_collection.update_one(
            {"application_id": application_id},
            {
                "$push": {"required_documents": new_document},
                "$set": {"timestamps.updated_at": now},
            },
        )

        if update_result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document could not be added",
            )

    return serialize_embedded_application_document(application_id, new_document)


# 6 add comments
def add_application_comment_service(
    application_id: str, comment_data: ApplicationCommentCreate
) -> dict:
    application = get_one(
        land_applications_collection, {"application_id": application_id}
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    now = datetime.now(timezone.utc)

    note_text = comment_data.comment

    update_result = land_applications_collection.update_one(
        {"application_id": application_id},
        {
            "$push": {"internal.notes": note_text},
            "$set": {"internal.visibility": "staff_only", "timestamps.updated_at": now},
        },
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Comment could not be added"
        )

    return {
        "application_id": application_id,
        "note": note_text,
        "visibility": "staff_only",
        "created_at": now,
    }


# 7 add objection
def submit_application_objection_service(
    application_id: str, objection_data: ApplicationObjectionCreate
) -> dict:
    application = get_one(
        land_applications_collection, {"application_id": application_id}
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    if application.get("status") in ["closed", "rejected", "certificate_issued"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot submit objection for a closed, rejected, or certificate-issued application",
        )

    now = datetime.now(timezone.utc)
    new_objection_id = str(ObjectId())

    objection_note = (
        f"Objection submitted. "
        f"Objection ID: {new_objection_id}. "
        f"Reason: {objection_data.reason}"
    )

    if objection_data.submitted_by_applicant_id:
        objection_note += (
            f" Submitted by applicant: " f"{objection_data.submitted_by_applicant_id}."
        )

    update_result = land_applications_collection.update_one(
        {"application_id": application_id},
        {
            "$set": {
                "objection.has_objection": True,
                "status": "under_objection",
                "workflow.current_state": "under_objection",
                "timestamps.updated_at": now,
            },
            "$push": {
                "objection.objection_ids": new_objection_id,
                "internal.notes": objection_note,
            },
        },
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Objection could not be submitted",
        )

    updated_application = get_one(
        land_applications_collection, {"application_id": application_id}
    )

    return {
        "application_id": application_id,
        "has_objection": True,
        "objection_ids": updated_application.get("objection", {}).get(
            "objection_ids", []
        ),
        "new_objection_id": new_objection_id,
        "reason": objection_data.reason,
        "submitted_by_applicant_id": objection_data.submitted_by_applicant_id,
        "submitted_at": now,
    }


# 8 get timeline :


def add_timeline_event(
    timeline: list,
    event_type: str,
    title: str,
    description: str | None = None,
    at=None,
    meta: dict | None = None,
):
    timeline.append(
        {
            "type": event_type,
            "title": title,
            "description": description,
            "at": at,
            "meta": meta,
        }
    )


def get_application_timeline_service(application_id: str) -> dict:
    application = get_one(
        land_applications_collection, {"application_id": application_id}
    )

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    timeline = []

    timestamps = application.get("timestamps", {})

    status_timestamp_map = [
        ("submitted_at", "submitted", "Application submitted"),
        ("pre_checked_at", "pre_checked", "Application pre-checked"),
        ("survey_required_at", "survey_required", "Survey required"),
        ("surveyed_at", "surveyed", "Survey completed"),
        ("legal_review_at", "legal_review", "Legal review started"),
        ("approved_at", "approved", "Application approved"),
        ("certificate_issued_at", "certificate_issued", "Certificate issued"),
        ("closed_at", "closed", "Application closed"),
    ]

    for timestamp_field, status_name, title in status_timestamp_map:
        event_time = timestamps.get(timestamp_field)

        if event_time:
            add_timeline_event(
                timeline=timeline,
                event_type="status_change",
                title=title,
                description=f"Application moved to {status_name} state.",
                at=event_time,
                meta={"status": status_name, "timestamp_field": timestamp_field},
            )

    required_documents = application.get("required_documents", [])

    for document in required_documents:
        uploaded_at = document.get("uploaded_at")

        if uploaded_at:
            add_timeline_event(
                timeline=timeline,
                event_type="document",
                title="Document uploaded",
                description=f"{document.get('document_type')} document was uploaded.",
                at=uploaded_at,
                meta={
                    "document_id": document.get("document_id"),
                    "document_type": document.get("document_type"),
                    "status": document.get("status"),
                    "file_name": document.get("file_name"),
                    "required": document.get("required"),
                },
            )

        else:
            add_timeline_event(
                timeline=timeline,
                event_type="document",
                title="Required document registered",
                description=f"{document.get('document_type')} is required with status {document.get('status')}.",
                at=None,
                meta={
                    "document_type": document.get("document_type"),
                    "status": document.get("status"),
                    "required": document.get("required"),
                },
            )

    objection = application.get("objection", {})

    if objection.get("has_objection"):
        objection_ids = objection.get("objection_ids", [])

        for objection_id in objection_ids:
            add_timeline_event(
                timeline=timeline,
                event_type="objection",
                title="Objection submitted",
                description="An objection was submitted for this application.",
                at=None,
                meta={"objection_id": objection_id},
            )

    internal = application.get("internal", {})
    notes = internal.get("notes", [])

    for note in notes:
        add_timeline_event(
            timeline=timeline,
            event_type="note",
            title="Internal note",
            description=note,
            at=None,
            meta={"visibility": internal.get("visibility", "staff_only")},
        )

    timeline.sort(
        key=lambda event: event["at"] if event["at"] is not None else "", reverse=False
    )

    return {
        "application_id": application_id,
        "current_status": application.get("status"),
        "current_workflow_state": application.get("workflow", {}).get("current_state"),
        "total_events": len(timeline),
        "timeline": timeline,
    }
