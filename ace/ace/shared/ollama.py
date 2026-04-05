"""Synchronous Ollama client for the ACE CLI."""

from __future__ import annotations

import httpx

from ace.shared.config import get_settings


class OllamaError(Exception):
    """Raised when an Ollama API call fails."""


def generate(prompt: str, system: str = "") -> str:
    """Send a prompt to the local Ollama instance and return the response text.

    Parameters
    ----------
    prompt:
        The user / instruction prompt.
    system:
        An optional system prompt that steers the model's behaviour.

    Returns
    -------
    str
        The generated text from the model.
    """
    settings = get_settings()

    payload: dict = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
    }
    if system:
        payload["system"] = system

    try:
        response = httpx.post(
            f"{settings.ollama_host}/api/generate",
            json=payload,
            timeout=120.0,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
    except httpx.ConnectError as exc:
        raise OllamaError(
            f"Cannot connect to Ollama at {settings.ollama_host}. "
            "Is Ollama running?"
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise OllamaError(
            f"Ollama returned HTTP {exc.response.status_code}: "
            f"{exc.response.text}"
        ) from exc
    except Exception as exc:
        raise OllamaError(f"Ollama request failed: {exc}") from exc
