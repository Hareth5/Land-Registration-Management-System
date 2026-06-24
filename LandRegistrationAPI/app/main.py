from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.features.survey_assignments.router import router as survey_assignments_router
from app.features.assignments.router import router as assignments_router
# from app.features.categories.router import router as categories_router


app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(survey_assignments_router)
app.include_router(assignments_router)
# app.include_router(categories_router)