from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

from app.features.applications.router import router as applications_router
from app.features.survey_assignments.router import router as survey_assignments_router
from app.features.assignments.router import router as assignments_router
from app.features.applicatns.router import router as applicants_router

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(applications_router)
app.include_router(survey_assignments_router)
app.include_router(assignments_router)
app.include_router(applicants_router)
