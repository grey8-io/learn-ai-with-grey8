"""FastAPI application entry point for the Learn AI Tutor Engine."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from tutor.config import settings
from tutor.engine.ollama_client import ollama_client
from tutor.models.schemas import HealthResponse
from tutor.routers import chat, grade, hint


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifecycle: startup and shutdown."""
    yield
    await ollama_client.close()


app = FastAPI(
    title="Learn AI Tutor Engine",
    description="AI-powered Socratic tutor for Learn AI With Grey8",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(grade.router)
app.include_router(hint.router)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint. Also verifies Ollama connectivity."""
    connected = await ollama_client.check_health()
    return HealthResponse(
        status="ok" if connected else "degraded",
        ollama_connected=connected,
        model=settings.ollama_model,
    )


def cli() -> None:
    """CLI entry point: run the tutor server with uvicorn."""
    import uvicorn

    uvicorn.run(
        "tutor.main:app",
        host=settings.tutor_host,
        port=settings.tutor_port,
        reload=True,
    )


if __name__ == "__main__":
    cli()
