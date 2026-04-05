"""Async client for the Ollama API."""

from collections.abc import AsyncIterator
from typing import Any

import httpx

from tutor.config import get_ollama_options, settings


class OllamaClient:
    """Async wrapper around the Ollama HTTP API."""

    def __init__(
        self,
        host: str | None = None,
        model: str | None = None,
    ) -> None:
        self.host = (host or settings.ollama_host).rstrip("/")
        self.model = model or settings.ollama_model
        self._client: httpx.AsyncClient | None = None
        # Load hardware-aware options once at init (from env/hw_profile)
        self._options: dict[str, int] = get_ollama_options()

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.host,
                timeout=httpx.Timeout(connect=5.0, read=120.0, write=10.0, pool=10.0),
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def check_health(self) -> bool:
        """Return True if Ollama is reachable."""
        try:
            client = await self._get_client()
            resp = await client.get("/api/tags")
            return resp.status_code == 200
        except (httpx.ConnectError, httpx.TimeoutException):
            return False

    async def get_context_length(self) -> int:
        """Detect the active model's context window size at runtime.

        Queries Ollama /api/show for model metadata. Falls back to 2048
        if the model info is unavailable.
        """
        try:
            client = await self._get_client()
            resp = await client.post(
                "/api/show", json={"model": self.model}
            )
            if resp.status_code == 200:
                data = resp.json()
                # Ollama returns model_info with context_length or
                # parameters with num_ctx
                model_info = data.get("model_info", {})
                for key, val in model_info.items():
                    if "context_length" in key:
                        return int(val)
                # Fallback: check parameters string
                params = data.get("parameters", "")
                for line in params.split("\n"):
                    if "num_ctx" in line:
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            return int(parts[-1])
            return 2048  # safe default for small models
        except (httpx.ConnectError, httpx.TimeoutException, ValueError):
            return 2048

    async def generate(
        self,
        prompt: str,
        system: str = "",
        stream: bool = False,
    ) -> str | AsyncIterator[str]:
        """Generate a completion. Returns full text or an async iterator of chunks."""
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
        }
        if system:
            payload["system"] = system
        if self._options:
            payload["options"] = {**self._options}

        if stream:
            return self._stream_generate(payload)

        client = await self._get_client()
        resp = await client.post("/api/generate", json=payload)
        resp.raise_for_status()
        return resp.json().get("response", "")

    async def _stream_generate(
        self, payload: dict[str, Any]
    ) -> AsyncIterator[str]:
        client = await self._get_client()
        async with client.stream("POST", "/api/generate", json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                import json as _json

                data = _json.loads(line)
                chunk = data.get("response", "")
                if chunk:
                    yield chunk

    async def chat(
        self,
        messages: list[dict[str, str]],
        system: str = "",
        stream: bool = False,
    ) -> str | AsyncIterator[str]:
        """Send a chat completion request."""
        all_messages: list[dict[str, str]] = []
        if system:
            all_messages.append({"role": "system", "content": system})
        all_messages.extend(messages)

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": all_messages,
            "stream": stream,
        }
        if self._options:
            payload["options"] = {**self._options}

        if stream:
            return self._stream_chat(payload)

        client = await self._get_client()
        resp = await client.post("/api/chat", json=payload)
        resp.raise_for_status()
        return resp.json().get("message", {}).get("content", "")

    async def _stream_chat(
        self, payload: dict[str, Any]
    ) -> AsyncIterator[str]:
        client = await self._get_client()
        async with client.stream("POST", "/api/chat", json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                import json as _json

                data = _json.loads(line)
                chunk = data.get("message", {}).get("content", "")
                if chunk:
                    yield chunk


# Shared singleton instance
ollama_client = OllamaClient()
