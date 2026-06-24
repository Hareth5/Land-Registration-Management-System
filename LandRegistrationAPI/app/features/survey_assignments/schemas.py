from pydantic import BaseModel, EmailStr

class ContactInfo(BaseModel):
    phone: str
    email: EmailStr

class Coverage(BaseModel):
    zone_ids: list[str]

class Workload(BaseModel):
    active_tasks: int = 0
    max_tasks: int = 10

class StaffCreate(BaseModel):
    staff_code: str
    name: str
    role: str
    department: str
    skills: list[str]
    contacts: ContactInfo
    coverage: Coverage
    workload: Workload
    active: bool = True