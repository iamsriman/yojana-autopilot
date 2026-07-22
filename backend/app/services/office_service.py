"""District office lookup service."""

from typing import Any

from fastapi import HTTPException, status

from app.models.schemas import Office, OfficesResponse
from app.utils.json_loader import load_offices
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OfficeService:
    """Find district-level offices from local JSON."""

    def get_offices(self, district: str, office_type: str | None = None) -> OfficesResponse:
        data = load_offices()
        districts: dict[str, Any] = data.get("districts", {})
        district_key = self._resolve_district_key(district, districts)
        if district_key is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No office data found for district '{district}'.",
            )

        district_data = districts[district_key]
        offices: list[Office] = []
        for key, entries in district_data.items():
            if office_type and key.lower() != office_type.lower():
                continue
            if isinstance(entries, list):
                for entry in entries:
                    offices.append(Office(**entry, office_type=key))

        response = OfficesResponse(
            district=district_key,
            offices=offices,
            available_office_types=sorted(
                key for key, value in district_data.items() if isinstance(value, list)
            ),
        )
        logger.info("Office lookup district=%s office_type=%s results=%s", district_key, office_type, len(offices))
        return response

    def _resolve_district_key(self, district: str, districts: dict[str, Any]) -> str | None:
        wanted = district.strip().lower()
        for key in districts:
            if key.lower() == wanted:
                return key
        return None
