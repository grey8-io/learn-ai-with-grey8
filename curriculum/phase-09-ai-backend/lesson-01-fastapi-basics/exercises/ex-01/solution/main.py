"""
Exercise: FastAPI AI Backend — Solution
=========================================
"""

from fastapi import FastAPI
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

class PredictRequest(BaseModel):
    text: str
    model: str = "default"


class PredictResponse(BaseModel):
    result: str
    confidence: float
    model: str


class BatchRequest(BaseModel):
    texts: list[str]


class BatchResponse(BaseModel):
    results: list[str]
    count: int


# ---------------------------------------------------------------------------
# Available models (used by /models and /predict)
# ---------------------------------------------------------------------------
AVAILABLE_MODELS = ["default", "fast", "accurate"]


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app() -> FastAPI:
    """Create and return a FastAPI application with AI endpoints."""
    app = FastAPI()

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/predict")
    def predict(request: PredictRequest):
        confidence = min(len(request.text) / 100, 1.0)
        return PredictResponse(
            result=f"predicted: {request.text[:50]}",
            confidence=confidence,
            model=request.model,
        )

    @app.get("/models")
    def list_models():
        return AVAILABLE_MODELS

    @app.post("/batch")
    def batch(request: BatchRequest):
        results = [f"predicted: {text[:50]}" for text in request.texts]
        return BatchResponse(results=results, count=len(results))

    return app


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
