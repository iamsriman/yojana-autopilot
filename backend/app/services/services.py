"""Service and scheme catalog search."""

from typing import Any

from fastapi import HTTPException, status

from app.models.schemas import (
    DocumentChecklistResponse,
    SchemeSearchResult,
    SearchRequest,
    ServiceSearchResult,
)
from app.utils.json_loader import load_schemes, load_services
from app.utils.logger import get_logger
from app.utils.text_cleaner import keyword_score, normalize_text, tokenize

logger = get_logger(__name__)


class CatalogSearchService:
    """Local JSON-backed search for public services and schemes."""

    def search_services(self, request: SearchRequest) -> list[ServiceSearchResult]:
        terms = self._request_terms(request, include_benefits=False)
        results: list[ServiceSearchResult] = []
        for item in load_services():
            if request.category and item.get("category", "").lower() != request.category.lower():
                continue
            score = self._score_service(item, terms, request)
            if score <= 0:
                continue
            results.append(
                ServiceSearchResult(
                    id=item.get("id", ""),
                    name=item.get("name", ""),
                    category=item.get("category"),
                    description=item.get("description"),
                    documents=item.get("documents", []),
                    portal=item.get("portal"),
                    offices=item.get("office", []),
                    processing_time=item.get("processing_time"),
                    score=round(score, 4),
                )
            )
        ranked = sorted(results, key=lambda result: result.score, reverse=True)[: request.top_k]
        logger.info("Service search query=%r category=%r results=%s", request.query or request.keywords, request.category, len(ranked))
        return ranked

    def search_schemes(self, request: SearchRequest) -> list[SchemeSearchResult]:
        terms = self._request_terms(request, include_benefits=True)
        results: list[SchemeSearchResult] = []
        for item in load_schemes().values():
            if request.category and item.get("category", "").lower() != request.category.lower():
                continue
            score = self._score_scheme(item, terms, request)
            if score <= 0:
                continue
            results.append(
                SchemeSearchResult(
                    id=item.get("id", ""),
                    name=item.get("name", ""),
                    category=item.get("category"),
                    benefit=item.get("benefit"),
                    documents=item.get("documents", []),
                    portal=item.get("portal"),
                    processing_time=item.get("processing_time"),
                    score=round(score, 4),
                )
            )
        ranked = sorted(results, key=lambda result: result.score, reverse=True)[: request.top_k]
        logger.info("Scheme search query=%r category=%r results=%s", request.query or request.benefits, request.category, len(ranked))
        return ranked

    def get_document_checklist(self, scheme_id: str) -> DocumentChecklistResponse:
        scheme = load_schemes().get(scheme_id)
        if scheme is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scheme '{scheme_id}' was not found.",
            )

        process = scheme.get("application_process", {})
        modes = [mode for mode, steps in process.items() if steps]
        return DocumentChecklistResponse(
            scheme_id=scheme_id,
            scheme_name=scheme.get("name", scheme_id),
            required_documents=scheme.get("documents", []),
            optional_documents=scheme.get("optional_documents", []),
            fees=scheme.get("fees"),
            timeline=scheme.get("processing_time"),
            application_mode=modes or ["online", "offline"],
        )

    def _request_terms(self, request: SearchRequest, include_benefits: bool) -> set[str]:
        values: list[Any] = [request.query, request.keywords, request.documents]
        if include_benefits:
            values.append(request.benefits)
        return tokenize(values)

    def _score_service(self, item: dict[str, Any], terms: set[str], request: SearchRequest) -> float:
        weighted_text = {
            "name": item.get("name"),
            "name_te": item.get("name_te"),
            "keywords": item.get("keywords", []),
            "description": item.get("description"),
            "documents": item.get("documents", []),
            "category": item.get("category"),
        }
        score = keyword_score(terms, weighted_text)
        score += 0.5 * keyword_score(terms, item.get("name"))
        score += 0.35 * keyword_score(tokenize(request.documents), item.get("documents", []))
        score += 0.25 * keyword_score(tokenize(request.keywords), item.get("keywords", []))
        if request.category and item.get("category", "").lower() == request.category.lower():
            score += 0.2
        return score

    def _score_scheme(self, item: dict[str, Any], terms: set[str], request: SearchRequest) -> float:
        weighted_text = {
            "name": item.get("name"),
            "name_telugu": item.get("name_telugu"),
            "category": item.get("category"),
            "subcategory": item.get("subcategory"),
            "benefit": item.get("benefit"),
            "description": item.get("description"),
            "documents": item.get("documents", []),
        }
        score = keyword_score(terms, weighted_text)
        score += 0.5 * keyword_score(terms, item.get("name"))
        score += 0.4 * keyword_score(tokenize(request.benefits), normalize_text(item.get("benefit")))
        score += 0.25 * keyword_score(tokenize(request.documents), item.get("documents", []))
        if request.category and item.get("category", "").lower() == request.category.lower():
            score += 0.2
        return score
