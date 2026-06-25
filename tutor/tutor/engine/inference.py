"""Inference backend abstraction.

The tutor talks to one of two backends, selected by ``TUTOR_INFERENCE_BACKEND``:

- ``ollama``        — local Ollama server (default; the local-first dev path).
- ``openai_compat`` — any OpenAI-compatible ``/chat/completions`` endpoint:
                      DeepInfra/Together/Groq for the hosted course, or even
                      Ollama's own ``/v1`` route for a free end-to-end test.

Both backends expose the same surface, so routers never care which is active.
Keeping the seam here is what lets the public repo ship ONE codebase that runs
unchanged locally and on GCP Cloud Run — only env vars differ. See
``deployment_mode`` in config.py.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any, Protocol, runtime_checkable

import httpx

from tutor.config import settings
from tutor.engine.ollama_client import ollama_client


@runtime_checkable
class InferenceBackend(Protocol):
    """The surface every router relies on. ``OllamaClient`` already satisfies it."""

    async def check_health(self) -> bool: ...

    async def get_context_length(self) -> int: ...

    async def generate(
        self, prompt: str, system: str = "", stream: bool = False
    ) -> str | AsyncIterator[str]: ...

    async def chat(
        self,
        messages: list[dict[str, str]],
        system: str = "",
        stream: bool = False,
    ) -> str | AsyncIterator[str]: ...

    async def close(self) -> None: ...


class OpenAICompatBackend:
    """Client for an OpenAI-compatible chat-completions API.

    Works with DeepInfra/Together/Groq (the hosted-course inference providers)
    and with Ollama's own ``/v1`` route — which lets us exercise this exact code
    path locally for free before pointing it at a paid provider.
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.base_url = (base_url or settings.inference_base_url).rstrip("/")
        self.api_key = api_key or settings.inference_api_key
        self.model = model or settings.inference_model
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            headers: dict[str, str] = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                # Generous read timeout: a cold serverless cold-start or a long
                # generation must not abort mid-stream. Matches the Ollama client.
                timeout=httpx.Timeout(connect=5.0, read=300.0, write=10.0, pool=10.0),
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def check_health(self) -> bool:
        """Return True if the provider responds to a models list."""
        if not self.base_url:
            return False
        try:
            client = await self._get_client()
            resp = await client.get("/models")
            return resp.status_code == 200
        except (httpx.ConnectError, httpx.TimeoutException):
            return False

    async def get_context_length(self) -> int:
        """OpenAI-compatible APIs expose no per-model context probe (unlike
        Ollama's ``/api/show``), so we trust the configured value. chat.py still
        clamps with ``min(this, effective_num_ctx)`` to keep prompts small."""
        return settings.inference_context_length

    def _payload(
        self, messages: list[dict[str, str]], stream: bool
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
        }
        if settings.inference_max_tokens > 0:
            payload["max_tokens"] = settings.inference_max_tokens
        return payload

    async def generate(
        self, prompt: str, system: str = "", stream: bool = False
    ) -> str | AsyncIterator[str]:
        """Single-turn generation, mapped onto chat-completions (no /generate)."""
        messages: list[dict[str, str]] = [{"role": "user", "content": prompt}]
        return await self.chat(messages=messages, system=system, stream=stream)

    async def chat(
        self,
        messages: list[dict[str, str]],
        system: str = "",
        stream: bool = False,
    ) -> str | AsyncIterator[str]:
        all_messages: list[dict[str, str]] = []
        if system:
            all_messages.append({"role": "system", "content": system})
        all_messages.extend(messages)
        payload = self._payload(all_messages, stream)

        if stream:
            return self._stream_chat(payload)

        client = await self._get_client()
        resp = await client.post("/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()
        choices = data.get("choices") or []
        if not choices:
            return ""
        return (choices[0].get("message") or {}).get("content") or ""

    async def _stream_chat(
        self, payload: dict[str, Any]
    ) -> AsyncIterator[str]:
        client = await self._get_client()
        async with client.stream("POST", "/chat/completions", json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                data = line[len("data:") :].strip()
                if data == "[DONE]":
                    break
                try:
                    obj = json.loads(data)
                except json.JSONDecodeError:
                    continue
                choices = obj.get("choices") or []
                if not choices:
                    continue
                chunk = (choices[0].get("delta") or {}).get("content", "")
                if chunk:
                    yield chunk


def get_inference_backend() -> InferenceBackend:
    """Select the active backend from settings. Reads at call time so tests can
    flip ``inference_backend`` without re-importing."""
    if settings.inference_backend == "openai_compat":
        return OpenAICompatBackend()
    return ollama_client


# Shared singleton — chosen once at import from the environment.
inference_backend: InferenceBackend = get_inference_backend()
