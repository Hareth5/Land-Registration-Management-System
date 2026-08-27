from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo.errors import ConfigurationError, ConnectionFailure

from app.core.config import settings
from app.features.applicants.router import router as applicants_router
from app.features.applications.router import router as applications_router
from app.features.assignments.router import router as assignments_router
from app.features.survey_assignments.router import router as survey_assignments_router
from app.shared.crud import DatabaseUnavailableError

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(DatabaseUnavailableError)
@app.exception_handler(ConnectionFailure)
@app.exception_handler(ConfigurationError)
async def database_unavailable_handler(
    _request: Request,
    _error: DatabaseUnavailableError | ConfigurationError | ConnectionFailure,
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={
            "detail": (
                "MongoDB is unavailable or misconfigured. Verify MONGO_URI "
                "and the Atlas database user and IP access list."
            )
        },
    )


app.include_router(applications_router)
app.include_router(survey_assignments_router)
app.include_router(assignments_router)
app.include_router(applicants_router)
