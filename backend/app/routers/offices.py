"""Office directory endpoints."""

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_office_service
from app.models.schemas import OfficesResponse
from app.services.office_service import OfficeService

router = APIRouter(prefix="/offices", tags=["offices"])


@router.get(
    "/{district}",
    response_model=OfficesResponse,
    summary="Get nearby offices for a district",
    description="Returns office addresses, phone numbers, opening hours, coordinates, ratings, notes, and office type for a district.",
    responses={
        200: {
            "description": "District office directory",
            "content": {
                "application/json": {
                    "example": {
                        "district": "Guntur",
                        "offices": [
                            {
                                "name": "V.R. MeeSeva Centre, Arundelpet",
                                "address": "4th Lane, Arundelpet, Guntur 522002",
                                "phone": "+91 90004 52658",
                                "hours": "Daily 10:00 AM - 9:00 PM",
                                "latitude": 16.3023506,
                                "longitude": 80.4396699,
                                "office_type": "meeseva",
                                "rating": 4.2,
                                "notes": "Handles Aadhaar, EC, driving licence applications and labour licences.",
                            }
                        ],
                        "available_office_types": ["collectorate", "meeseva", "rto"],
                    }
                }
            },
        },
        404: {"description": "District not found"},
    },
)
async def get_district_offices(
    district: str,
    office_type: str | None = Query(default=None, description="Optional office type such as meeseva, rto, psk."),
    service: OfficeService = Depends(get_office_service),
) -> OfficesResponse:
    """Return office address, phone, hours, coordinates, and type."""

    return service.get_offices(district, office_type=office_type)
