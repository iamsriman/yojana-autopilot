"""FastAPI dependency factories."""

from functools import lru_cache

from app.config import Settings, get_settings
from app.services.chat_service import ChatService
from app.services.eligibility_engine import EligibilityEngine
from app.services.embedding_service import EmbeddingService
from app.services.office_service import OfficeService
from app.services.portal_service import PortalService
from app.services.rag_engine import RAGEngine
from app.services.services import CatalogSearchService


@lru_cache
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService(get_settings())


@lru_cache
def get_rag_engine() -> RAGEngine:
    return RAGEngine(get_settings(), get_embedding_service())


@lru_cache
def get_chat_service() -> ChatService:
    return ChatService(get_settings(), get_rag_engine())


@lru_cache
def get_eligibility_engine() -> EligibilityEngine:
    return EligibilityEngine()


@lru_cache
def get_catalog_search_service() -> CatalogSearchService:
    return CatalogSearchService()


@lru_cache
def get_office_service() -> OfficeService:
    return OfficeService()


@lru_cache
def get_portal_service() -> PortalService:
    return PortalService()


def settings_dependency() -> Settings:
    return get_settings()

