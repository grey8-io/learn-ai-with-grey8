"""
Project 07: AI-Powered API (Reference)

A FastAPI REST API with /summarize, /classify, and /generate endpoints,
all powered by a local Ollama LLM.
"""

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:3b"

app = FastAPI(title="AI-Powered API", version="1.0.0")


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


# --- Request/Response Models ---

class SummarizeRequest(BaseModel):
    text: str


class ClassifyRequest(BaseModel):
    text: str
    categories: list[str]


class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 200


class AIResponse(BaseModel):
    result: str


# --- Endpoints ---

@app.post("/summarize", response_model=AIResponse)
def summarize(req: SummarizeRequest):
    """Summarize the provided text into a concise paragraph."""
    system_prompt = (
        "You are a summarization assistant. Condense the user's text into a clear, "
        "concise summary. Keep the most important points. Respond with only the summary."
    )
    result = chat(system_prompt, req.text)
    return AIResponse(result=result)


@app.post("/classify", response_model=AIResponse)
def classify(req: ClassifyRequest):
    """Classify the provided text into one of the given categories."""
    categories_str = ", ".join(req.categories)
    system_prompt = (
        f"You are a text classifier. Classify the user's text into exactly one of "
        f"these categories: {categories_str}. Respond with ONLY the category name, "
        f"nothing else."
    )
    result = chat(system_prompt, req.text)
    return AIResponse(result=result.strip())


@app.post("/generate", response_model=AIResponse)
def generate(req: GenerateRequest):
    """Generate text based on the provided prompt."""
    system_prompt = (
        "You are a creative text generator. Follow the user's instructions to produce "
        "the requested content. Be creative, clear, and concise."
    )
    result = chat(system_prompt, req.prompt)
    return AIResponse(result=result)


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "model": MODEL}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
