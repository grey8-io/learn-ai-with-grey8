"""Rubric-based grading using the LLM."""

import re

from tutor.engine.ollama_client import OllamaClient
from tutor.engine.prompts import GRADING_RUBRIC_PROMPT


class RubricResult:
    """Result of LLM rubric-based grading."""

    def __init__(self, score: int, feedback: str) -> None:
        self.score = score
        self.feedback = feedback


async def score_with_rubric(
    code: str,
    rubric: str,
    exercise_id: str,
    client: OllamaClient,
    test_summary: str = "",
) -> RubricResult:
    """Send student code + rubric to the LLM and parse the score/feedback.

    Args:
        code: The student's code.
        rubric: The grading rubric text.
        exercise_id: The exercise identifier.
        client: An OllamaClient instance.
        test_summary: Human-readable summary of test results.

    Returns:
        A RubricResult with score (0-100) and feedback string.
    """
    prompt = GRADING_RUBRIC_PROMPT.format(
        exercise_id=exercise_id,
        rubric=rubric,
        code=code,
        test_summary=test_summary or "No test results available.",
    )

    try:
        response = await client.generate(prompt=prompt, stream=False)
        assert isinstance(response, str)
        return _parse_rubric_response(response)
    except Exception:
        return RubricResult(score=0, feedback="Unable to grade with rubric at this time.")


def _parse_rubric_response(text: str) -> RubricResult:
    """Parse SCORE: and FEEDBACK: from the LLM response."""
    score = 50  # default if parsing fails
    feedback = text.strip()

    score_match = re.search(r"SCORE:\s*(\d+)", text)
    if score_match:
        raw = int(score_match.group(1))
        score = max(0, min(100, raw))

    feedback_match = re.search(r"FEEDBACK:\s*(.+)", text, re.DOTALL)
    if feedback_match:
        feedback = feedback_match.group(1).strip()

    return RubricResult(score=score, feedback=feedback)
