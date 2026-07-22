"""Portal registry endpoints."""

from fastapi import APIRouter, Depends

from app.dependencies import get_portal_service
from app.models.schemas import PortalResponse
from app.services.portal_service import PortalService

router = APIRouter(prefix="/portal", tags=["portals"])


@router.get(
    "/{portal_id}",
    response_model=PortalResponse,
    summary="Get official portal details",
    description="Looks up one official portal entry from local JSON and returns application URL, status URL, helpline, owner, and verification flag.",
    responses={
        200: {
            "description": "Portal details",
            "content": {
                "application/json": {
                    "example": {
                        "portal_id": "uidai",
                        "name": "UIDAI / myAadhaar",
                        "portal_url": "https://uidai.gov.in",
                        "status_url": "https://myaadhaar.uidai.gov.in/CheckAadhaarStatus",
                        "helpline": "1947",
                        "description": "Enrolment and biometric updates require an in-person visit.",
                        "owner": "Unique Identification Authority of India",
                        "verify_before_use": False,
                    }
                }
            },
        },
        404: {"description": "Portal not found"},
    },
)
async def get_portal(
    portal_id: str,
    service: PortalService = Depends(get_portal_service),
) -> PortalResponse:
    """Return portal URL, status URL, helpline, and description."""

    return service.get_portal(portal_id)
