from fastapi import APIRouter, status

from .schemas import (
    ApplicantApplicationsListResponse,
    ApplicantCreate,
    ApplicantResponse,
)
from .service import (
    create_applicant_service,
    get_applicant_applications_service,
    get_applicant_by_id_service,
)

router = APIRouter(
    prefix="/applicants",
    tags=["Applicants"],
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_applicant(applicant: ApplicantCreate):
    return create_applicant_service(applicant)


@router.get("/{applicant_id}", response_model=ApplicantResponse)
def get_applicant_by_id(applicant_id: str):
    return get_applicant_by_id_service(applicant_id)


@router.get(
    "/{applicant_id}/applications", response_model=ApplicantApplicationsListResponse
)
def get_applicant_applications(applicant_id: str):
    return get_applicant_applications_service(applicant_id)
