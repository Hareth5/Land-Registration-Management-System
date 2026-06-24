from enum import Enum
from typing import Any
from pydantic import BaseModel

class SurveyMilestoneType(str, Enum):
    ASSIGNED = "assigned"
    VISIT_SCHEDULED = "visit_scheduled"
    ARRIVED_ON_SITE = "arrived_on_site"
    SURVEY_STARTED = "survey_started"
    SURVEY_COMPLETED = "survey_completed"
    REPORT_UPLOADED = "report_uploaded"
    REGISTRAR_REVIEWED = "registrar_reviewed"

class MilestoneActor(str, Enum):
    SYSTEM = "system"
    SURVEYOR = "surveyor"
    REGISTRAR = "registrar"

class SurveyMilestoneRequest(BaseModel):
    milestone_type: SurveyMilestoneType
    by: MilestoneActor
    meta: dict[str, Any] = {}

class SurveyReportRequest(BaseModel):
    uploaded_by: str
    report_title: str
    summary: str
    file_name: str
    file_path: str

class RegistrarDecision(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_CORRECTION = "needs_correction"

class RegistrarReviewRequest(BaseModel):
    reviewed_by: str
    decision: RegistrarDecision
    notes: str