from fastapi import APIRouter
from app.features.survey_assignments import service
from app.features.survey_assignments.schemas import StaffCreate

router = APIRouter(tags=["Survey Assignments"])

@router.post("/staff/")
def create_staff(staff: StaffCreate):
    return service.create_staff(staff)

@router.get("/staff/{staff_id}")
def get_staff_by_id(staff_id: str):
    return service.get_staff_by_id(staff_id)
