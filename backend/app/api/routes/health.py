from fastapi import APIRouter

from app.schemas.health import HealthData, HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    return HealthResponse(
        success=True,
        message="TalentFlow AI API is healthy.",
        data=HealthData(status="healthy", version="0.1.0"),
    )
