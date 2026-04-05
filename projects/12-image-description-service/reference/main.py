"""
Project 12: Image Description Service (Reference)
Use a multimodal LLM (LLaVA) to describe uploaded images via FastAPI.
"""

import base64

import requests
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
import uvicorn

# Ollama API configuration — LLaVA is multimodal (text + image)
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llava"

app = FastAPI(title="Image Description Service")


def chat(prompt: str, image_b64: str) -> str:
    """Send an image and prompt to the LLaVA model via Ollama."""
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_b64],
                }
            ],
            "stream": False,
        },
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def describe_image(image_bytes: bytes, prompt: str) -> str:
    """Encode an image to base64 and get a description from the LLM."""
    # Convert raw bytes to base64 string for the Ollama API
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    return chat(prompt, image_b64)


@app.post("/describe")
async def describe_endpoint(
    file: UploadFile = File(...),
    prompt: str = Form(default="Describe this image in detail."),
):
    """Upload an image and get an AI-generated description."""
    # Read uploaded file
    image_bytes = await file.read()

    # Validate content type
    if not file.content_type or not file.content_type.startswith("image/"):
        return JSONResponse(
            status_code=400,
            content={"error": f"Expected an image file, got {file.content_type}"},
        )

    # Generate description
    try:
        description = describe_image(image_bytes, prompt)
    except requests.RequestException as e:
        return JSONResponse(
            status_code=502,
            content={"error": f"Ollama API error: {str(e)}"},
        )

    return {
        "filename": file.filename,
        "prompt": prompt,
        "description": description,
    }


@app.get("/")
async def root():
    """Health check and usage info."""
    return {
        "service": "Image Description Service",
        "model": MODEL,
        "usage": "POST an image to /describe",
        "docs": "/docs",
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
