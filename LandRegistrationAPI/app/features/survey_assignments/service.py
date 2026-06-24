from fastapi import HTTPException
from datetime import datetime, timezone
from bson import ObjectId
from app.database.mongo import db
from app.features.survey_assignments.schemas import StaffCreate
from app.shared import crud

staff_members = db["staff_members"]

def create_staff(staff: StaffCreate):
    staff_data = staff.model_dump()
    existing_staff = crud.get_one(staff_members, {"staff_code": staff_data["staff_code"]})

    if existing_staff:
        raise HTTPException(status_code = 400, detail = "Staff code already exists")

    staff_data["created_at"] = datetime.now(timezone.utc)
    inserted_id = crud.create(staff_members, staff_data)

    return {
        "message": "Staff member created successfully",
        "staff_id": str(inserted_id)
    }

def get_staff_by_id(staff_id: str):
    if not ObjectId.is_valid(staff_id):
        raise HTTPException(status_code = 400, detail = "Invalid Staff ID format")
    
    found = crud.get_one(staff_members, {"_id" : ObjectId(staff_id)})
    sta

    if not found:
        raise HTTPException( status_code = 404,  detail = "Staff not found")
    
    found["_id"] = str(found["_id"])
    return found