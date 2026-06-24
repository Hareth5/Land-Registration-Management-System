from fastapi import APIRouter
from app.features.assignments import service
from app.features.assignments.schemas import SurveyMilestoneRequest, SurveyReportRequest, RegistrarReviewRequest

router = APIRouter(tags=["Assignments"])

@router.post("/applications/{application_id}/auto-assign-surveyor")
def auto_assign_surveyor(application_id: str):
    return service.auto_assign_surveyor(application_id)

@router.patch("/applications/{application_id}/survey-milestone")
def add_survey_milestone(
    application_id: str, milestone: SurveyMilestoneRequest):
    return service.add_survey_milestone(application_id, milestone)

@router.post("/applications/{application_id}/survey-report")
def add_survey_report(application_id: str, report: SurveyReportRequest):
    return service.add_survey_report(application_id, report)

@router.patch("/applications/{application_id}/registrar-review")
def registrar_review(application_id: str, review: RegistrarReviewRequest):
    return service.registrar_review(application_id, review)