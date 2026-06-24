from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .enums import (
    ApplicationStatus,
    ApplicationType,
)


class CreateApplicationRequest(BaseModel):

    application_type: ApplicationType

    applicant_id: str

    parcel_id: str


class TransitionRequest(BaseModel):

    new_status: ApplicationStatus


class HoldRequest(BaseModel):

    reason: str


class RejectRequest(BaseModel):

    reason: str


class ApplicantRef(BaseModel):

    applicant_id: str

    applicant_type: str

    submitted_by_representative: bool = False


class ParcelRef(BaseModel):

    parcel_id: str

    parcel_number: str

    block_number: str

    basin_number: str

    zone_id: str


class WorkflowInfo(BaseModel):

    current_state: ApplicationStatus

    allowed_next: list[str]

    transition_rules_version: str


class RequiredDocument(BaseModel):

    document_type: str

    required: bool

    status: str


class Timestamps(BaseModel):

    submitted_at: datetime

    updated_at: datetime


class Application(BaseModel):

    application_id: str

    application_type: ApplicationType

    status: ApplicationStatus

    priority: str

    applicant_ref: ApplicantRef

    parcel_ref: ParcelRef

    workflow: WorkflowInfo

    required_documents: list[RequiredDocument]

    timestamps: Timestamps


class NoteRequest(BaseModel):

    note: str


class MissingDocumentsRequest(BaseModel):

    documents: list[str]


class ObjectionRequest(BaseModel):

    reason: str
