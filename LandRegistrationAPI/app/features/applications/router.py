from fastapi import APIRouter
from typing import Optional

from .schemas import (
    CreateApplicationRequest,
    TransitionRequest,
    HoldRequest,
    RejectRequest,
    NoteRequest,
    MissingDocumentsRequest,
    ObjectionRequest,
)

from .services.application_service import (
    create_application,
    get_application,
    get_applications,
    transition_application,
    hold_application,
    reject_application,
    generate_certificate,
    add_note,
    mark_missing_documents,
    mark_under_objection,
)

router = APIRouter(
    prefix="/applications",
    tags=["Applications"],
)


@router.post("/")
def create_application_endpoint(
    data: CreateApplicationRequest,
):

    return create_application(data)


@router.get("/{application_id}")
def get_application_endpoint(
    application_id: str,
):

    return get_application(application_id)


@router.get("/")
def get_applications_endpoint(
    status: Optional[str] = None,
    application_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    sort_field: Optional[str] = None,
    sort_order: int = 1,
):

    filters = {}

    if status:

        filters["status"] = status

    if application_type:

        filters["application_type"] = application_type

    return get_applications(
        filters=filters,
        skip=skip,
        limit=limit,
        sort_field=sort_field,
        sort_order=sort_order,
    )


@router.patch("/{application_id}/transition")
def transition_application_endpoint(
    application_id: str,
    data: TransitionRequest,
):

    return transition_application(
        application_id,
        data.new_status,
    )


@router.post("/{application_id}/hold")
def hold_application_endpoint(
    application_id: str,
    data: HoldRequest,
):

    return hold_application(
        application_id,
        data.reason,
    )


@router.post("/{application_id}/reject")
def reject_application_endpoint(
    application_id: str,
    data: RejectRequest,
):

    return reject_application(
        application_id,
        data.reason,
    )


@router.post("/{application_id}/certificate")
def generate_certificate_endpoint(
    application_id: str,
):

    return generate_certificate(
        application_id,
    )


@router.post("/{application_id}/notes")
def add_note_endpoint(
    application_id: str,
    data: NoteRequest,
):

    return add_note(
        application_id,
        data.note,
    )


@router.post("/{application_id}/missing-documents")
def missing_documents_endpoint(
    application_id: str,
    data: MissingDocumentsRequest,
):

    return mark_missing_documents(
        application_id,
        data.documents,
    )


@router.post("/{application_id}/objection")
def objection_endpoint(
    application_id: str,
    data: ObjectionRequest,
):

    return mark_under_objection(
        application_id,
        data.reason,
    )
