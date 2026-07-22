"""Chat orchestration over RAG, DuckDuckGo, and Groq."""

from typing import Any

import httpx
from fastapi import HTTPException, status

from app.config import Settings
from app.models.schemas import ChatResponse, RetrievedSource
from app.prompts import SYSTEM_PROMPT, build_user_prompt
from app.services.rag_engine import RAGEngine
from app.utils.logger import get_logger
from app.utils.text_cleaner import normalize_text

logger = get_logger(__name__)


class ChatService:
    """Generate grounded answers using local JSON context and optional web search."""

    def __init__(self, settings: Settings, rag_engine: RAGEngine) -> None:
        self.settings = settings
        self.rag_engine = rag_engine

    async def answer(self, question: str, top_k: int | None = None) -> ChatResponse:
        logger.info("Chat request received top_k=%s", top_k or self.settings.rag_top_k)
        json_sources, confidence = self.rag_engine.retrieve(question, top_k=top_k)
        used_web = False
        sources = list(json_sources)

        if confidence < self.settings.rag_min_confidence:
            web_sources = await self._duckduckgo_search(question, max_results=self.settings.web_search_max_results)
            sources.extend(web_sources)
            used_web = bool(web_sources)

        if not self.settings.groq_api_key:
            fallback = self._fallback_answer(question, sources, confidence, used_web)
            return ChatResponse(answer=fallback, confidence=confidence, sources=sources, used_web_search=used_web)

        context = self.rag_engine.format_context(sources)
        answer = await self._call_groq(question, context)
        return ChatResponse(answer=answer, confidence=confidence, sources=sources, used_web_search=used_web)

    async def _call_groq(self, question: str, context: str) -> str:
        url = f"{self.settings.groq_base_url.rstrip('/')}/chat/completions"
        payload: dict[str, Any] = {
            "model": self.settings.groq_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(question, context)},
            ],
            "temperature": 0.1,
            "max_tokens": self.settings.groq_max_tokens,
        }
        headers = {"Authorization": f"Bearer {self.settings.groq_api_key}"}
        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.exception("Groq request failed")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Groq API request failed.",
            ) from exc
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()

    async def _duckduckgo_search(self, query: str, max_results: int) -> list[RetrievedSource]:
        try:
            from duckduckgo_search import DDGS
        except Exception:
            logger.warning("duckduckgo-search package is not installed; web fallback skipped")
            return []

        def run_search() -> list[dict[str, Any]]:
            with DDGS() as ddgs:
                return list(ddgs.text(query, region="in-en", safesearch="moderate", max_results=max_results))

        try:
            import asyncio

            results = await asyncio.to_thread(run_search)
        except Exception:
            logger.exception("DuckDuckGo search failed")
            return []

        sources = []
        for result in results:
            sources.append(
                RetrievedSource(
                    source_type="Web",
                    title=result.get("title") or result.get("href") or "Web result",
                    content=normalize_text(result.get("body")),
                    score=None,
                    url=result.get("href"),
                    metadata={"source": "duckduckgo"},
                )
            )
        return sources

    def _fallback_answer(
        self,
        question: str,
        sources: list[RetrievedSource],
        confidence: float,
        used_web: bool,
    ) -> str:
        if not sources:
            return (
                "Overview\n"
                "I couldn't verify this from the available government sources.\n\n"
                "Tips\n"
                "Please verify with the relevant official portal or nearest Sachivalayam/MeeSeva office.\n\n"
                "Source\n"
                "No reliable source found."
            )
        local = [source for source in sources if source.source_type == "JSON"]
        web = [source for source in sources if source.source_type == "Web"]
        primary = sources[0]
        source_line = "Local Knowledge Base"
        if used_web and web:
            source_line = "Local Knowledge Base; Web Search" if local else "Web Search"
        official_hint = self._metadata_value(primary, "portal") or primary.url or "Check the official portal listed for this service or scheme."
        helpline = self._extract_label(primary.content, "helpline") or "Contact the relevant department helpline or local office."
        return (
            f"{primary.title}\n\n"
            "Overview\n"
            f"{self._short_summary(primary.content)}\n\n"
            "Eligibility\n"
            "Use the eligibility endpoint for scheme-specific decisions. Final approval depends on official verification.\n\n"
            "Required Documents\n"
            f"{self._extract_label(primary.content, 'documents') or 'I could not verify a complete document list from the available government sources.'}\n\n"
            "Application Process\n"
            "Use the official portal where available. Visit MeeSeva, Sachivalayam, or the relevant department office when biometrics, document verification, or assisted filing is needed.\n\n"
            "Fees\n"
            f"{self._extract_label(primary.content, 'fees') or 'I could not verify the fee from the available government sources.'}\n\n"
            "Processing Time\n"
            f"{self._extract_label(primary.content, 'processing_time') or 'I could not verify the processing time from the available government sources.'}\n\n"
            "Tips\n"
            f"Confidence from local retrieval: {confidence}. Prefer official AP Government or Government of India portals before acting.\n\n"
            "Official Portal\n"
            f"{official_hint}\n\n"
            "Helpline\n"
            f"{helpline}\n\n"
            "Source\n"
            f"{source_line}"
        )

    def _short_summary(self, text: str) -> str:
        text = normalize_text(text)
        if len(text) <= 650:
            return text
        return text[:650].rsplit(" ", 1)[0] + "."

    def _metadata_value(self, source: RetrievedSource, key: str) -> str | None:
        value = source.metadata.get(key)
        return str(value) if value else None

    def _extract_label(self, text: str, label: str) -> str | None:
        normalized = normalize_text(text)
        lower = normalized.lower()
        index = lower.find(label.lower())
        if index == -1:
            return None
        snippet = normalized[index : index + 450]
        return snippet.rsplit(" ", 1)[0]
