"""Eligibility endpoints."""

from fastapi import APIRouter, Depends

from app.dependencies import get_catalog_search_service, get_eligibility_engine
from app.models.schemas import (
    DocumentChecklistResponse,
    EligibilityProfile,
    EligibilityResponse,
    SchemeSearchResult,
    SearchRequest,
)
from app.services.eligibility_engine import EligibilityEngine
from app.services.services import CatalogSearchService

router = APIRouter(tags=["schemes"])


@router.post(
    "/eligibility",
    response_model=EligibilityResponse,
    summary="Evaluate scheme eligibility using deterministic JSON rules",
    description=(
        "Classifies schemes into eligible, need_more_information, and not_eligible. "
        "Missing answers generate dynamic next questions and never cause rejection."
    ),
    responses={
        200: {
            "description": "Three-state eligibility result",
            "content": {
                "application/json": {
                    "example": {
                        "eligible": [],
                        "need_more_information": [
                            {
                                "scheme_id": "annadata_sukhibhava",
                                "scheme_name": "Annadata Sukhibhava",
                                "category": "Agriculture",
                                "status": "need_more_information",
                                "eligible": False,
                                "reasons": ["No exclusion matched; more information is needed before confirming eligibility."],
                                "missing_information": ["has digitized land records", "ekyc done"],
                                "missing_questions": [
                                    "Do you have digitized land records such as Webland, Adangal, or 1B?",
                                    "Have you completed eKYC?",
                                ],
                                "next_questions": ["Do you have digitized land records such as Webland, Adangal, or 1B?"],
                                "missing_documents": ["Aadhaar card", "Land records (Webland / Adangal / 1B)"],
                                "benefits": ["Rs.20,000 per year per farmer family"],
                                "application_links": ["https://annadathasukhibhava.ap.gov.in"],
                                "processing_time": "Disbursed in 3 installments per financial year",
                                "confidence": 0.5,
                            }
                        ],
                        "not_eligible": [],
                    }
                }
            },
        }
    },
)
async def evaluate_eligibility(
    profile: EligibilityProfile,
    engine: EligibilityEngine = Depends(get_eligibility_engine),
) -> EligibilityResponse:
    """Compare applicant facts against each scheme's eligibility_rules."""

    return engine.evaluate(profile)


@router.post(
    "/schemes/search",
    response_model=list[SchemeSearchResult],
    summary="Search welfare schemes",
    description="Fuzzy search over local scheme JSON by benefits, category, documents, Telugu terms, and keywords.",
    responses={
        200: {
            "description": "Ranked scheme matches",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "jagananna_vidya_deevena",
                            "name": "Jagananna Vidya Deevena",
                            "category": "Education",
                            "benefit": "Full fee reimbursement + maintenance allowance",
                            "documents": ["Aadhaar card", "Income certificate"],
                            "portal": "https://jnanabhumi.ap.gov.in",
                            "processing_time": "College verification: 15 days",
                            "score": 1.2,
                        }
                    ]
                }
            },
        }
    },
)
async def search_schemes(
    request: SearchRequest,
    service: CatalogSearchService = Depends(get_catalog_search_service),
) -> list[SchemeSearchResult]:
    """Search schemes by benefits, category, documents, and keywords."""

    return service.search_schemes(request)


@router.get(
    "/schemes/{scheme_id}/documents",
    response_model=DocumentChecklistResponse,
    summary="Get document checklist for a scheme",
    description="Returns required documents, fees, timeline, and supported application modes for one scheme.",
    responses={
        200: {
            "description": "Document checklist",
            "content": {
                "application/json": {
                    "example": {
                        "scheme_id": "pm_kisan",
                        "scheme_name": "PM-KISAN",
                        "required_documents": ["Aadhaar card", "Land ownership records"],
                        "optional_documents": [],
                        "fees": {"online": "Free"},
                        "timeline": "Registration: 15-30 days",
                        "application_mode": ["online", "offline"],
                    }
                }
            },
        },
        404: {"description": "Scheme not found"},
    },
)
async def document_checklist(
    scheme_id: str,
    service: CatalogSearchService = Depends(get_catalog_search_service),
) -> DocumentChecklistResponse:
    """Return documents, fees, timeline, and application modes."""

    return service.get_document_checklist(scheme_id)
