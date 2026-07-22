"""Embedding and ChromaDB integration."""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.config import Settings
from app.models.schemas import RetrievedSource
from app.utils.json_loader import load_offices, load_portals, load_schemes, load_services
from app.utils.logger import get_logger
from app.utils.text_cleaner import normalize_text

logger = get_logger(__name__)
INDEX_SCHEMA_VERSION = "2026-07-22-v2"


@dataclass(frozen=True)
class DocumentChunk:
    id: str
    text: str
    metadata: dict[str, Any]


class EmbeddingService:
    """Build and query a persistent ChromaDB vector store."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._model: Any | None = None
        self._client: Any | None = None
        self._collection: Any | None = None
        self._index_checked = False

    @property
    def ready(self) -> bool:
        try:
            return bool(self.collection.count())
        except Exception:
            return False

    @property
    def model(self) -> Any:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.settings.embedding_model)
        return self._model

    @property
    def collection(self) -> Any:
        if self._collection is None:
            import chromadb

            self.settings.vector_db_dir.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(path=str(self.settings.vector_db_dir))
            self._collection = self._client.get_or_create_collection(
                name=self.settings.chroma_collection,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def build_index(self, force: bool = False) -> int:
        """Create embeddings for all local JSON records and upsert them into ChromaDB."""

        if self._index_checked and not force:
            return 0

        chunks = self._dedupe_chunks(self._build_chunks())
        if not chunks:
            return 0
        collection = self.collection
        existing_payload = collection.get(include=["metadatas"])
        if self._needs_metadata_refresh(existing_payload.get("metadatas", [])):
            stale_ids = existing_payload.get("ids", [])
            if stale_ids:
                logger.info("Refreshing vector index metadata schema for %s existing chunks", len(stale_ids))
                collection.delete(ids=stale_ids)
                existing_payload = {"ids": []}
        if force:
            ids = existing_payload.get("ids", collection.get(include=[])["ids"])
            if ids:
                collection.delete(ids=ids)

        existing = set(collection.get(include=[])["ids"])
        pending = [chunk for chunk in chunks if force or chunk.id not in existing]
        if not pending:
            self._index_checked = True
            return 0

        logger.info("Building embeddings for %s new JSON chunks", len(pending))
        embeddings = self.model.encode([chunk.text for chunk in pending], normalize_embeddings=True)
        collection.upsert(
            ids=[chunk.id for chunk in pending],
            documents=[chunk.text for chunk in pending],
            metadatas=[chunk.metadata for chunk in pending],
            embeddings=embeddings.tolist(),
        )
        self._index_checked = True
        logger.info("Indexed %s JSON chunks into ChromaDB", len(pending))
        return len(pending)

    def retrieve(self, query: str, top_k: int) -> list[RetrievedSource]:
        """Retrieve top matching chunks."""

        self.build_index(force=False)
        embedding = self.model.encode([query], normalize_embeddings=True)[0].tolist()
        result = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        sources: list[RetrievedSource] = []
        docs = result.get("documents", [[]])[0]
        metadata = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        for document, meta, distance in zip(docs, metadata, distances, strict=False):
            score = max(0.0, 1.0 - float(distance))
            sources.append(
                RetrievedSource(
                    source_type="JSON",
                    title=meta.get("title", meta.get("id", "JSON document")),
                    content=document,
                    score=round(score, 4),
                    metadata=meta,
                )
            )
        return sources

    def _build_chunks(self) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        for scheme_id, scheme in load_schemes().items():
            chunks.extend(self._scheme_chunks(scheme_id, scheme))
        for service in load_services():
            chunks.append(
                self._chunk(
                    "service",
                    service.get("id", ""),
                    service.get("name", ""),
                    service,
                    category=service.get("category"),
                    portal=service.get("portal"),
                    service_id=service.get("id"),
                    keywords=service.get("keywords", []),
                    office=service.get("office", []),
                )
            )
        for district, district_data in load_offices().get("districts", {}).items():
            for office_type, offices in district_data.items():
                if isinstance(offices, list):
                    for idx, office in enumerate(offices):
                        record = {"district": district, "office_type": office_type, **office}
                        chunks.append(
                            self._chunk(
                                "office",
                                f"{district}-{office_type}-{idx}",
                                office.get("name", ""),
                                record,
                                office=office_type,
                                category=district,
                            )
                        )
        for portal_id, portal in load_portals().items():
            chunks.append(
                self._chunk(
                    "portal",
                    portal_id,
                    portal.get("name", portal_id),
                    portal,
                    portal=portal.get("portal"),
                )
            )
        return chunks

    def _scheme_chunks(self, scheme_id: str, scheme: dict[str, Any]) -> list[DocumentChunk]:
        base = {
            "id": scheme_id,
            "name": scheme.get("name"),
            "category": scheme.get("category"),
            "benefit": scheme.get("benefit"),
            "description": scheme.get("description"),
            "eligibility_rules": scheme.get("eligibility_rules"),
        }
        detail = {
            "documents": scheme.get("documents"),
            "application_process": scheme.get("application_process"),
            "fees": scheme.get("fees"),
            "processing_time": scheme.get("processing_time"),
            "portal": scheme.get("portal"),
            "helpline": scheme.get("helpline"),
            "notes": scheme.get("notes"),
        }
        return [
            self._chunk(
                "scheme",
                f"{scheme_id}-overview",
                scheme.get("name", scheme_id),
                base,
                scheme_id=scheme_id,
                category=scheme.get("category"),
                portal=scheme.get("portal"),
            ),
            self._chunk(
                "scheme",
                f"{scheme_id}-details",
                scheme.get("name", scheme_id),
                detail,
                scheme_id=scheme_id,
                category=scheme.get("category"),
                portal=scheme.get("portal"),
            ),
        ]

    def _chunk(self, source: str, item_id: str, title: str, record: dict[str, Any], **metadata: Any) -> DocumentChunk:
        text = normalize_text(record)
        digest = hashlib.sha1(f"{source}:{item_id}:{text}".encode("utf-8")).hexdigest()[:16]
        clean_metadata = {
            "source": source,
            "id": str(item_id),
            "title": str(title or item_id),
            "schema_version": INDEX_SCHEMA_VERSION,
        }
        clean_metadata.update(self._metadata_value(key, value) for key, value in metadata.items() if value is not None)
        return DocumentChunk(id=f"{source}-{item_id}-{digest}", text=text, metadata=clean_metadata)

    def _dedupe_chunks(self, chunks: list[DocumentChunk]) -> list[DocumentChunk]:
        seen: set[str] = set()
        deduped: list[DocumentChunk] = []
        for chunk in chunks:
            fingerprint = hashlib.sha1(chunk.text.encode("utf-8")).hexdigest()
            if fingerprint in seen:
                continue
            seen.add(fingerprint)
            deduped.append(chunk)
        return deduped

    def _metadata_value(self, key: str, value: Any) -> tuple[str, str | int | float | bool]:
        if isinstance(value, str | int | float | bool):
            return key, value
        return key, json.dumps(value, ensure_ascii=False)

    def _needs_metadata_refresh(self, metadatas: list[dict[str, Any] | None]) -> bool:
        return any((metadata or {}).get("schema_version") != INDEX_SCHEMA_VERSION for metadata in metadatas)

    def export_chunks_preview(self, path: Path) -> None:
        """Debug helper for inspecting generated chunks."""

        path.write_text(
            json.dumps([chunk.__dict__ for chunk in self._build_chunks()], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
