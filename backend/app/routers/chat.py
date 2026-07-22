"""Chat endpoint."""

from fastapi import APIRouter, Depends

from app.dependencies import get_chat_service
from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "",
    response_model=ChatResponse,
    summary="Ask the AI government services assistant",
    description=(
        "Retrieves local JSON knowledge from ChromaDB, falls back to DuckDuckGo when confidence is low, "
        "and uses Groq to generate a structured answer with source coverage."
    ),
    responses={
        200: {
            "description": "Structured grounded chat answer",
            "content": {
                "application/json": {
                    "example": {
                        "answer": "Income Certificate\n\nOverview\n...\n\nSource\nLocal Knowledge Base",
                        "confidence": 0.72,
                        "sources": [
                            {
                                "source_type": "JSON",
                                "title": "Income Certificate",
                                "content": "Service summary used by the model",
                                "score": 0.72,
                                "metadata": {"source": "service", "service_id": "income_certificate"},
                                "url": None,
                            }
                        ],
                        "used_web_search": False,
                    }
                }
            },
        },
        502: {"description": "Groq request failed"},
    },
)
async def chat(request: ChatRequest, service: ChatService = Depends(get_chat_service)) -> ChatResponse:
    """Retrieve local context, optionally search the web, and answer through Groq."""

    question = request.question
    if request.district:
        question = f"{question}\nDistrict: {request.district}"
    return await service.answer(question, top_k=request.top_k)
