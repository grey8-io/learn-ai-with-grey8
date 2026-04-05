"""
Exercise: FastAPI AI Backend
==============================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build a simple AI-ready API with FastAPI.
"""

from fastapi import FastAPI
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

# TODO: Define PredictRequest with:
#   - text: str
#   - model: str = "default"


# TODO: Define PredictResponse with:
#   - result: str
#   - confidence: float
#   - model: str


# TODO: Define BatchRequest with:
#   - texts: list[str]


# TODO: Define BatchResponse with:
#   - results: list[str]
#   - count: int


# ---------------------------------------------------------------------------
# Available models (used by /models and /predict)
# ---------------------------------------------------------------------------
AVAILABLE_MODELS = ["default", "fast", "accurate"]


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app() -> FastAPI:
    """Create and return a FastAPI application with AI endpoints.

    Endpoints:
        GET  /health  -> {"status": "ok"}
        POST /predict -> accepts PredictRequest, returns PredictResponse
        GET  /models  -> returns list of available model names
        POST /batch   -> accepts BatchRequest, returns BatchResponse

    Predict logic (placeholder):
        - result: "predicted: {text[:50]}"
        - confidence: min(len(text) / 100, 1.0)
        - model: the model from the request

    Batch logic:
        - results: list of "predicted: {text[:50]}" for each text
        - count: number of texts processed
    """
    # TODO: Create a FastAPI app instance.

    # TODO: Add GET /health endpoint that returns {"status": "ok"}.

    # TODO: Add POST /predict endpoint that:
    #   1. Accepts a PredictRequest body
    #   2. Calculates confidence as min(len(request.text) / 100, 1.0)
    #   3. Returns PredictResponse with result, confidence, and model

    # TODO: Add GET /models endpoint that returns AVAILABLE_MODELS.

    # TODO: Add POST /batch endpoint that:
    #   1. Accepts a BatchRequest body
    #   2. Processes each text into "predicted: {text[:50]}"
    #   3. Returns BatchResponse with results and count

    # TODO: Return the app.
    pass


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
