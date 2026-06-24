from pydantic import BaseModel, EmailStr, Field
from typing import Any, List, Optional
from datetime import datetime
from enum import Enum


##this schema for (POST /applicants)
class ApplicantType(str, Enum):
    citizen = "citizen"
    lawyer = "lawyer"
    company = "company"
    surveyor = "surveyor"
    authorized_representative = "authorized_representative"


class Identity(BaseModel):
    national_id: str
    verified: bool = False
    verification_method: Optional[str] = None
    verified_at: Optional[datetime] = None


class Contacts(BaseModel):
    email: EmailStr
    phone: str


class preferredContact(str, Enum):
    email = "email"
    phone = "phone"


class Address(BaseModel):
    city: str
    street: Optional[str] = None


class Notifications(BaseModel):
    on_status_change: bool = True
    on_missing_documents: bool = True
    on_certificate_ready: bool = True


class Preferences(BaseModel):
    prefereed_contact: preferredContact = preferredContact.email
    language: str = "ar"
    notifications: Notifications = Field(default_factory=Notifications)


class Stats(BaseModel):
    total_applications: int = 0
    approved_applications: int = 0
    pending_appliations: int = 0


# request body :
class ApplicantCreate(BaseModel):
    full_name: str
    applicant_type: ApplicantType
    identity: Identity
    contacts: Contacts
    address: Address
    preferances: Preferences


##this for end point : GET /applicants/{applicant_id}
# response body , same request body + id , stats , created_at
class ApplicantResponse(BaseModel):
    id: str
    full_name: str
    applicant_type: ApplicantType
    identity: Identity
    contacts: Contacts
    address: Address
    preferances: Preferences
    stats: Stats
    created_at: datetime


# this part for end point : GET /applicants/{applicant_id}/applications
# must exists in parcels schemas (more reusable)
class ApplicantParcelResponse(BaseModel):
    parcel_number: Optional[str] = None
    block_number: Optional[str] = None
    basin_number: Optional[str] = None
    zone_id: Optional[str] = None


# must exeists in application schemas
class ApplicantApplicationResponse(BaseModel):
    id: str
    application_id: str
    application_type: str
    status: str
    priority: Optional[str] = None
    parcel_ref: Optional[ApplicantParcelResponse] = None
    submitted_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# represent the list of applications linked to specific applicant
class ApplicantApplicationsListResponse(BaseModel):
    applicant_id: str
    total: int
    applications: List[ApplicantApplicationResponse]


# this schamea for add documents endpoint :POST /applications/{application_id}/documents
class DocumentType(str, Enum):
    ownership_deed = "ownership_deed"
    id_copy = "id_copy"
    sale_contract = "sale_contract"
    power_of_attorney = "power_of_attorney"
    survey_report = "survey_report"
    other = "other"


class DocumentStatus(str, Enum):
    missing = "missing"
    pending_review = "pending_review"
    verified = "verified"
    rejected = "rejected"


class ApplicationDocumentCreate(BaseModel):
    document_type: DocumentType
    file_name: str
    file_url: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    uploaded_by_applicant_id: Optional[str] = None
    notes: Optional[str] = None


class ApplicationDocumentResponse(BaseModel):
    document_id: str
    application_id: str
    document_type: DocumentType
    required: bool
    status: DocumentStatus
    file_name: Optional[str] = None
    file_url: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    uploaded_by_applicant_id: Optional[str] = None
    notes: Optional[str] = None
    uploaded_at: datetime


# this schema for this end point :POST /applications/{application_id}/comments
class InternalVisibility(str, Enum):
    staff_only = "staff_only"
    applicant_visible = "applicant_visible"


class ApplicationCommentCreate(BaseModel):
    comment: str = Field(..., min_length=1, max_length=2000)


class ApplicationCommentResponse(BaseModel):
    application_id: str
    note: str
    visibility: InternalVisibility
    created_at: datetime


# this schema for this endpoint :POST /applications/{application_id}/objection
class ApplicationObjectionCreate(BaseModel):
    reason: str = Field(..., min_length=1, max_length=2000)
    submitted_by_applicant_id: Optional[str] = None


class ApplicationObjectionResponse(BaseModel):
    application_id: str
    has_objection: bool
    objection_ids: List[str]
    new_objection_id: str
    reason: str
    submitted_by_applicant_id: Optional[str] = None
    submitted_at: datetime


# this schema for this end point :
class TimelineEventType(str, Enum):
    status_change = "status_change"
    document = "document"
    objection = "objection"
    note = "note"


class TimelineEventResponse(BaseModel):
    type: TimelineEventType
    title: str
    description: Optional[str] = None
    at: Optional[datetime] = None
    meta: Optional[dict[str, Any]] = None


class ApplicationTimelineResponse(BaseModel):
    application_id: str
    current_status: str
    current_workflow_state: Optional[str] = None
    total_events: int
    timeline: List[TimelineEventResponse]
