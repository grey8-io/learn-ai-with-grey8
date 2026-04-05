"""
Project 09: AI Content Moderator (Reference)

Classify text as safe/warning/unsafe using an LLM with structured JSON output.
"""

import json
import re
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
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "stream": False,
            },
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Ollama unavailable: {e}")


def extract_json(text: str) -> dict:
    """Extract a JSON object from LLM output, handling markdown code blocks."""
    # Strip markdown code fences if present
    cleaned = re.sub(r"```(?:json)?\s*", "", text).strip()
    cleaned = cleaned.rstrip("`").strip()

    return json.loads(cleaned)


MODERATION_PROMPT = """You are a content moderation system. Analyze the provided text and classify it.

Respond with ONLY a JSON object (no extra text) in this exact format:
{"category": "<safe|warning|unsafe>", "severity": <1-5>, "explanation": "<brief reason>"}

Rules:
- "safe" (severity 1-2): Normal, appropriate content
- "warning" (severity 2-3): Mildly negative, frustration, or borderline content
- "unsafe" (severity 4-5): Harmful, hateful, threatening, or clearly inappropriate content

Always respond with valid JSON only."""


def moderate(text: str) -> ModerationResult:
    """Classify a piece of text using the LLM."""
    raw = chat(MODERATION_PROMPT, text)

    try:
        data = extract_json(raw)
        # Validate and normalize the category
        category = data.get("category", "safe").lower().strip()
        if category not in ("safe", "warning", "unsafe"):
            category = "warning"

        severity = int(data.get("severity", 1))
        severity = max(1, min(5, severity))  # Clamp to 1-5

        explanation = data.get("explanation", "No explanation provided.")

        return ModerationResult(
            category=category,
            severity=severity,
            explanation=explanation,
        )
    except (json.JSONDecodeError, KeyError, ValueError):
        # Fallback if LLM returns invalid JSON
        return ModerationResult(
            category="warning",
            severity=3,
            explanation=f"Could not parse moderation result. Raw: {raw[:200]}",
        )


# --- Endpoints ---

@app.post("/moderate", response_model=ModerationResponse)
def moderate_text(req: ModerateRequest):
    """Moderate a single piece of text."""
    result = moderate(req.text)
    return ModerationResponse(text=req.text, result=result)


@app.post("/moderate/batch", response_model=list[ModerationResponse])
def moderate_batch(req: BatchModerateRequest):
    """Moderate multiple texts at once."""
    results = []
    for text in req.texts:
        result = moderate(text)
        results.append(ModerationResponse(text=text, result=result))
    return results


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
