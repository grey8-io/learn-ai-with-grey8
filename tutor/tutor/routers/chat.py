"""Chat router: Socratic tutoring via streaming SSE."""

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from tutor.engine.context import build_context
from tutor.engine.ollama_client import ollama_client
from tutor.models.schemas import ChatRequest

router = APIRouter(tags=["chat"])


@router.post("/chat")
async def chat(req: ChatRequest) -> StreamingResponse:
    """Socratic chat endpoint. Streams the assistant's response as SSE.

    Context is assembled in tiers based on the active model's context window:
    - Always: system prompt + student profile + roadmap + current lesson
    - Medium+ models (8K+): adds curriculum index for cross-lesson awareness
    - Exercise mode: adds TODO comments, test names, submission context
    """
    # Detect model context window at runtime
    context_length = await ollama_client.get_context_length()

    # Build tiered context
    system_prompt, trimmed_history = await build_context(
        lesson_id=req.lesson_id,
        student_code="",
        history=[{"role": m.role, "content": m.content} for m in req.history],
        student_profile=req.student_profile,
        model_context_length=context_length,
    )

    # Assemble messages for the chat API
    messages = list(trimmed_history)
    messages.append({"role": "user", "content": req.message})

    async def event_stream():
        try:
            stream = await ollama_client.chat(
                messages=messages,
                system=system_prompt,
                stream=True,
            )
            async for chunk in stream:
                payload = json.dumps({"content": chunk})
                yield f"data: {payload}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as exc:
            error_payload = json.dumps({"error": str(exc)})
            yield f"data: {error_payload}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
