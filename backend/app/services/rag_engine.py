"""Retrieval augmented generation helpers."""

from app.config import Settings
from app.models.schemas import RetrievedSource
from app.services.embedding_service import EmbeddingService
from app.utils.logger import get_logger
from app.utils.text_cleaner import normalize_text

logger = get_logger(__name__)


class RAGEngine:
    """Coordinates local vector retrieval and confidence calculation."""

    def __init__(self, settings: Settings, embedding_service: EmbeddingService) -> None:
        self.settings = settings
        self.embedding_service = embedding_service

    def retrieve(self, question: str, top_k: int | None = None) -> tuple[list[RetrievedSource], float]:
        k = top_k or self.settings.rag_top_k
        sources = self.embedding_service.retrieve(question, top_k=k)
        confidence = self.confidence(sources)
        logger.info("RAG retrieval complete top_k=%s sources=%s confidence=%s", k, len(sources), confidence)
        return sources, confidence

    def confidence(self, sources: list[RetrievedSource]) -> float:
        if not sources:
            return 0.0
        scores = [source.score or 0.0 for source in sources]
        return round(max(scores), 4)

    def format_context(self, sources: list[RetrievedSource]) -> str:
        blocks = []
        for index, source in enumerate(sources, start=1):
            blocks.append(
                f"[{index}] SourceType={source.source_type}; Title={source.title}; "
                f"Score={source.score}; Metadata={source.metadata}\n{normalize_text(source.content)}"
            )
        return "\n\n".join(blocks)
