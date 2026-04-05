"""Basic tests for the tutor engine API."""

import pytest
from httpx import ASGITransport, AsyncClient

from tutor.main import app


@pytest.mark.asyncio
async def test_health_returns_200():
    """The /health endpoint should return 200 even if Ollama is unreachable."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")

    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("ok", "degraded")
    assert "ollama_connected" in data
    assert "model" in data


@pytest.mark.asyncio
async def test_health_response_model():
    """The /health response should include the configured model name."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")

    data = resp.json()
    assert isinstance(data["model"], str)
    assert len(data["model"]) > 0
