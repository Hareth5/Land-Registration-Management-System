from enum import Enum


class ApplicationType(str, Enum):
    FIRST_REGISTRATION = "first_registration"
    OWNERSHIP_TRANSFER = "ownership_transfer"
    PARCEL_SUBDIVISION = "parcel_subdivision"
    PARCEL_MERGE = "parcel_merge"
    BOUNDARY_CORRECTION = "boundary_correction"
    CERTIFICATE_REQUEST = "certificate_request"


class ApplicationStatus(str, Enum):
    SUBMITTED = "submitted"
    PRE_CHECKED = "pre_checked"
    SURVEY_REQUIRED = "survey_required"
    SURVEYED = "surveyed"
    LEGAL_REVIEW = "legal_review"
    APPROVED = "approved"
    CERTIFICATE_ISSUED = "certificate_issued"
    CLOSED = "closed"

    REJECTED = "rejected"
    ON_HOLD = "on_hold"
    MISSING_DOCUMENTS = "missing_documents"
    UNDER_OBJECTION = "under_objection"
