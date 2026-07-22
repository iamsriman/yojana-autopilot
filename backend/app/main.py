"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routers import chat, eligibility, health, offices, portals, services
from app.utils.json_loader import load_offices, load_portals, load_schemes, load_services
from app.utils.logger import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Warm data and try to prepare the vector index at startup."""

    settings = get_settings()
    logger.info("Starting %s %s", settings.app_name, settings.app_version)
    logger.info(
        "Loaded JSON data: schemes=%s services=%s districts=%s portals=%s",
        len(load_schemes()),
        len(load_services()),
        len(load_offices().get("districts", {})),
        len(load_portals()),
    )
    logger.info("Vector embeddings are lazy-loaded on the first RAG request")
    yield
    logger.info("Shutting down %s", settings.app_name)


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered Government Services and Welfare Assistant for Andhra Pradesh.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Keep unexpected errors logged and returned in a predictable shape."""

    logger.exception("Unhandled error while serving %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(eligibility.router, prefix=settings.api_prefix)
app.include_router(chat.router, prefix=settings.api_prefix)
app.include_router(services.router, prefix=settings.api_prefix)
app.include_router(offices.router, prefix=settings.api_prefix)
app.include_router(portals.router, prefix=settings.api_prefix)


@app.get("/", tags=["root"], summary="API root")
async def root() -> dict[str, str]:
    """Return API metadata and documentation links."""

    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }
