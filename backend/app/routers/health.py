"""Health endpoint."""

from fastapi import APIRouter, Depends

from app.config import Settings
from app.dependencies import get_embedding_service, settings_dependency
from app.models.schemas import HealthResponse
from app.services.embedding_service import EmbeddingService
from app.utils.json_loader import load_offices, load_portals, load_schemes, load_services

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "",
    response_model=HealthResponse,
    summary="Check API and data health",
    description="Reports API status, JSON data counts, and whether a ChromaDB vector collection is already present.",
    responses={
        200: {
            "description": "Health response",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ok",
                        "app_name": "Yojana Autopilot API",
                        "version": "1.0.0",
                        "data_files_loaded": {"schemes": 10, "services": 40, "districts": 5, "portals": 35},
                        "vector_store_ready": True,
                    }
                }
            },
        }
    },
)
async def health_check(
    settings: Settings = Depends(settings_dependency),
    embedding_service: EmbeddingService = Depends(get_embedding_service),
) -> HealthResponse:
    """Return API status and basic data availability."""

    offices = load_offices().get("districts", {})
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
        data_files_loaded={
            "schemes": len(load_schemes()),
            "services": len(load_services()),
            "districts": len(offices),
            "portals": len(load_portals()),
        },
        vector_store_ready=embedding_service.ready,
    )
