"""
Project 07: AI-Powered API (Starter)

A FastAPI REST API with /summarize, /classify, and /generate endpoints,
all powered by a local Ollama LLM.

Your task: implement the chat helper, Pydantic models, and endpoint logic.
"""

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2:3b"

app = FastAPI(title="AI-Powered API", version="1.0.0")


# --- Helper ---

def chat(system_prompt: str, user_message: str) -> str:
    """Send a chat request to Ollama and return the assistant's response.

    Args:
        system_prompt: Instructions for the LLM's behavior.
        user_message: The user's input text.

    Returns:
        The assistant's response text.
    """
    # TODO: Send a POST to OLLAMA_URL/api/chat with model, messages, stream=False.
    # TODO: Return response.json()["message"]["content"].
    # TODO: Wrap in try/except and raise HTTPException(status_code=503) on failure.
    pass


# --- Request/Response Models ---

# TODO: Create a SummarizeRequest model with a single field:
#   - text: str
class SummarizeRequest(BaseModel):
    pass


# TODO: Create a ClassifyRequest model with fields:
#   - text: str
#   - categories: list[str]
class ClassifyRequest(BaseModel):
    pass


# TODO: Create a GenerateRequest model with fields:
#   - prompt: str
#   - max_tokens: int = 200 (with a default)
class GenerateRequest(BaseModel):
    pass


# TODO: Create an AIResponse model with a single field:
#   - result: str
class AIResponse(BaseModel):
    pass


# --- Endpoints ---

@app.post("/summarize", response_model=AIResponse)
def summarize(req: SummarizeRequest):
    """Summarize the provided text into a concise paragraph."""
    # TODO: Call chat() with a system prompt that instructs the LLM to summarize.
    # TODO: Pass req.text as the user message.
    # TODO: Return an AIResponse with the result.
    pass


@app.post("/classify", response_model=AIResponse)
def classify(req: ClassifyRequest):
    """Classify the provided text into one of the given categories."""
    # TODO: Build a system prompt that lists the allowed categories.
    # TODO: Instruct the LLM to respond with ONLY the category name.
    # TODO: Call chat() and return an AIResponse.
    pass


@app.post("/generate", response_model=AIResponse)
def generate(req: GenerateRequest):
    """Generate text based on the provided prompt."""
    # TODO: Call chat() with a creative-writing system prompt.
    # TODO: Pass req.prompt as the user message.
    # TODO: Return an AIResponse with the result.
    pass


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "model": MODEL}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
