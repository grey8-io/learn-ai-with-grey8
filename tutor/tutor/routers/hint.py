"""Hints router: progressive hints from templates or LLM."""

from fastapi import APIRouter

from tutor.engine.context import load_exercise_metadata
from tutor.engine.ollama_client import ollama_client
from tutor.engine.prompts import HINT_PROMPTS
from tutor.models.schemas import HintRequest, HintResponse

router = APIRouter(tags=["hint"])


@router.post("/hint", response_model=HintResponse)
async def hint(req: HintRequest) -> HintResponse:
    """Return a progressive hint (level 1-3) for an exercise.

    Prefers static hint templates from exercise metadata when available,
    falling back to LLM-generated hints with guardrails.
    """
    meta = load_exercise_metadata(req.exercise_id)
    hints_list = meta.get("hints", [])

    # hints.json is an array: index 0 = level 1, index 1 = level 2, etc.
    hint_index = req.hint_level - 1

    # Use static hint from exercise metadata if available
    if 0 <= hint_index < len(hints_list):
        return HintResponse(hint=hints_list[hint_index], level=req.hint_level)

    # Fall back to LLM-generated hint
    prompt_template = HINT_PROMPTS.get(req.hint_level, HINT_PROMPTS[1])
    prompt = prompt_template.format(
        exercise_id=req.exercise_id,
        code=req.code or "(no code yet)",
    )

    system = (
        "You are a helpful but careful tutor. NEVER give complete solutions. "
        "Follow the hint level instructions exactly."
    )

    try:
        response = await ollama_client.generate(
            prompt=prompt,
            system=system,
            stream=False,
        )
        assert isinstance(response, str)
        hint_text = response.strip()
    except Exception:
        hint_text = _fallback_hint(req.hint_level)

    return HintResponse(hint=hint_text, level=req.hint_level)


def _fallback_hint(level: int) -> str:
    """Provide a generic fallback hint when the LLM is unavailable."""
    fallbacks = {
        1: "Re-read the exercise description carefully. What is the key input and expected output?",
        2: "Break the problem into smaller steps. What needs to happen first?",
        3: "Try writing pseudocode first, then translate each line to Python.",
    }
    return fallbacks.get(level, fallbacks[1])
