"""
Project 09: AI Content Moderator (Starter)

Classify text as safe/warning/unsafe using an LLM with structured JSON output.

Your task: implement the moderation logic, JSON parsing, and API endpoints.
"""

import json
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:3b"

app = FastAPI(title="AI Content Moderator", version="1.0.0")


# --- Request/Response Models ---

class ModerateRequest(BaseModel):
    text: str


class BatchModerateRequest(BaseModel):
    texts: list[str]


class ModerationResult(BaseModel):
    category: str       # "safe", "warning", or "unsafe"
    severity: int       # 1-5 scale
    explanation: str    # Why this classification was chosen


class ModerationResponse(BaseModel):
    text: str
    result: ModerationResult


# --- Helper ---

def chat(system_prompt: str, user_message: str) -> str:
    """Send a chat request to Ollama and return the assistant's response."""
    # TODO: Send a POST to OLLAMA_URL/api/chat with model, messages, stream=False.
    # TODO: Return the response content string.
    # TODO: Raise HTTPException(503) if Ollama is unavailable.
    pass


def moderate(text: str) -> ModerationResult:
    """Classify a piece of text using the LLM.

    Args:
        text: The text to moderate.

    Returns:
        A ModerationResult with category, severity, and explanation.
    """
    # TODO: Create a system prompt that instructs the LLM to:
    #   1. Analyze the text for harmful, offensive, or inappropriate content
    #   2. Classify it as "safe", "warning", or "unsafe"
    #   3. Assign a severity score from 1 (harmless) to 5 (very harmful)
    #   4. Provide a brief explanation
    #   5. Respond with ONLY a JSON object like:
    #      {"category": "safe", "severity": 1, "explanation": "..."}
    #
    # TODO: Call chat() with the system prompt and the text to moderate.
    #
    # TODO: Parse the JSON response. Handle cases where the LLM returns
    #   invalid JSON by wrapping in try/except and returning a fallback result.
    #
    # Hint: The LLM might wrap JSON in markdown code blocks like ```json...```
    # You may need to strip those before parsing.
    pass


# --- Endpoints ---

@app.post("/moderate", response_model=ModerationResponse)
def moderate_text(req: ModerateRequest):
    """Moderate a single piece of text."""
    # TODO: Call moderate(req.text) and return a ModerationResponse.
    pass


@app.post("/moderate/batch", response_model=list[ModerationResponse])
def moderate_batch(req: BatchModerateRequest):
    """Moderate multiple texts at once."""
    # TODO: Loop over req.texts, call moderate() on each, collect results.
    # TODO: Return a list of ModerationResponse objects.
    pass


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
