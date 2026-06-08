from fastapi import APIRouter

from app.api.routes.applicants import router as applicants_router
from app.api.routes.gmail import router as gmail_router
from app.api.routes.health import router as health_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.resumes import router as resumes_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(jobs_router, tags=["Jobs"])
api_router.include_router(applicants_router, tags=["Applicants"])
api_router.include_router(gmail_router, tags=["Gmail"])
api_router.include_router(resumes_router, tags=["Resumes"])
