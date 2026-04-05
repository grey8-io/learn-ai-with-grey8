"""
Project 12: Image Description Service (Starter)
Use a multimodal LLM (LLaVA) to describe uploaded images via FastAPI.
"""

import base64

import requests
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
import uvicorn

# Ollama API configuration
# Note: We use LLaVA here — a multimodal model that understands images
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llava"

app = FastAPI(title="Image Description Service")


def chat(prompt: str, image_b64: str) -> str:
    """Send an image and prompt to the LLaVA model via Ollama.

    Args:
        prompt: Text prompt describing what to do with the image.
        image_b64: Base64-encoded image string.

    Returns:
        The model's description of the image.
    """
    # TODO: Send a POST request to OLLAMA_URL with:
    #   - "model": MODEL
    #   - "messages": a list with one user message containing:
    #       - "role": "user"
    #       - "content": the prompt text
    #       - "images": a list with the base64 image string
    #   - "stream": False
    #
    # The Ollama multimodal API expects images as a list of base64 strings
    # inside the message object.
    #
    # Return the assistant's message content from the response.
    # Hint: response.json()["message"]["content"]
    pass


def describe_image(image_bytes: bytes, prompt: str) -> str:
    """Encode an image and get a description from the LLM.

    Args:
        image_bytes: Raw bytes of the uploaded image.
        prompt: What to describe about the image.

    Returns:
        The model's description.
    """
    # TODO: Step 1 — Convert image_bytes to a base64-encoded string
    # Use base64.b64encode() and decode to a UTF-8 string
    #
    # TODO: Step 2 — Call chat() with the prompt and base64 string
    #
    # TODO: Step 3 — Return the result
    pass


@app.post("/describe")
async def describe_endpoint(
    file: UploadFile = File(...),
    prompt: str = Form(default="Describe this image in detail."),
):
    """Upload an image and get an AI-generated description.

    Args:
        file: The uploaded image file (JPEG, PNG, etc.)
        prompt: Optional custom prompt for the description.

    Returns:
        JSON with filename, prompt used, and description.
    """
    # TODO: Step 1 — Read the uploaded file bytes with `await file.read()`
    #
    # TODO: Step 2 — Validate it's an image (check file.content_type starts with "image/")
    #   If not an image, return JSONResponse with status_code=400 and an error message
    #
    # TODO: Step 3 — Call describe_image() with the bytes and prompt
    #
    # TODO: Step 4 — Return a JSON response with:
    #   - "filename": file.filename
    #   - "prompt": prompt
    #   - "description": the model's response
    pass


@app.get("/")
async def root():
    """Health check and usage info."""
    return {
        "service": "Image Description Service",
        "usage": "POST an image to /describe",
        "docs": "/docs",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
