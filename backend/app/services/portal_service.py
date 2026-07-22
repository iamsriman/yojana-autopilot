"""Portal lookup service."""

from typing import Any

from fastapi import HTTPException, status

from app.models.schemas import PortalResponse
from app.utils.json_loader import load_portals
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PortalService:
    """Read portal metadata from local JSON."""

    def get_portal(self, portal_id: str) -> PortalResponse:
        portals = load_portals()
        portal = portals.get(portal_id)
        if portal is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Portal '{portal_id}' was not found.",
            )
        logger.info("Portal lookup portal_id=%s", portal_id)
        return self._to_response(portal_id, portal)

    def _to_response(self, portal_id: str, portal: dict[str, Any]) -> PortalResponse:
        return PortalResponse(
            portal_id=portal_id,
            name=portal.get("name", portal_id),
            portal_url=portal.get("portal") or portal.get("citizen_portal") or portal.get("self_service"),
            status_url=portal.get("status_check"),
            helpline=portal.get("helpline"),
            description=portal.get("notes"),
            owner=portal.get("owner"),
            verify_before_use=bool(portal.get("verify_flag", False)),
        )
