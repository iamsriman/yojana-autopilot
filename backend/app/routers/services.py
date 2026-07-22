"""Government service search endpoints."""

from fastapi import APIRouter, Depends

from app.dependencies import get_catalog_search_service
from app.models.schemas import SearchRequest, ServiceSearchResult
from app.services.services import CatalogSearchService

router = APIRouter(prefix="/services", tags=["services"])


@router.post(
    "/search",
    response_model=list[ServiceSearchResult],
    summary="Search government services",
    description="Fuzzy search over service JSON by keywords, category, Telugu aliases, abbreviations, and document names.",
    responses={
        200: {
            "description": "Ranked service matches",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "income_certificate",
                            "name": "Income Certificate",
                            "category": "certificates",
                            "description": "Certificate proving household income.",
                            "documents": ["Aadhaar card", "Ration card"],
                            "portal": "meeseva_ap",
                            "offices": ["meeseva", "sachivalayam"],
                            "processing_time": "7-15 days",
                            "score": 1.25,
                        }
                    ]
                }
            },
        }
    },
)
async def search_services(
    request: SearchRequest,
    service: CatalogSearchService = Depends(get_catalog_search_service),
) -> list[ServiceSearchResult]:
    """Search services by keywords, category, and required documents."""

    return service.search_services(request)
