"""Grading router: run tests and LLM rubric scoring."""

from fastapi import APIRouter

from tutor.engine.context import get_tests_dir, load_exercise_metadata
from tutor.engine.ollama_client import ollama_client
from tutor.grading.rubric import score_with_rubric
from tutor.grading.runner import run_tests
from tutor.models.schemas import GradeRequest, GradeResponse

router = APIRouter(tags=["grade"])


@router.post("/grade", response_model=GradeResponse)
async def grade(req: GradeRequest) -> GradeResponse:
    """Grade student code using tests (60%) and LLM rubric (40%)."""
    test_score = 0
    test_items = []
    tests_ran = False

    # Run pytest tests if available
    tests_dir = get_tests_dir(req.exercise_id)
    if tests_dir is not None:
        result = await run_tests(req.code, tests_dir)
        test_score = result.score
        test_items = result.items
        tests_ran = True

    # Build a concise test summary for the LLM rubric grader
    test_summary_lines = []
    for t in test_items:
        status = "PASS" if t.passed else "FAIL"
        line = f"  {status}: {t.name}"
        if not t.passed and t.message:
            line += f" — {t.message}"
        test_summary_lines.append(line)
    test_summary = (
        f"{sum(1 for t in test_items if t.passed)}/{len(test_items)} tests passed.\n"
        + "\n".join(test_summary_lines)
        if test_items
        else "No tests were run."
    )

    # Run LLM rubric grading
    meta = load_exercise_metadata(req.exercise_id)
    rubric_text = meta.get("rubric", "")
    rubric_score = 0
    feedback = ""

    if rubric_text:
        rubric_result = await score_with_rubric(
            code=req.code,
            rubric=rubric_text,
            exercise_id=req.exercise_id,
            client=ollama_client,
            test_summary=test_summary,
        )
        rubric_score = rubric_result.score
        feedback = rubric_result.feedback
    else:
        # No rubric: use LLM for general feedback only
        rubric_score = test_score  # mirror test score when no rubric
        feedback = "No rubric defined for this exercise."

    # Combined score: 60% tests + 40% rubric (if both available)
    if tests_ran and rubric_text:
        combined = int(test_score * 0.6 + rubric_score * 0.4)
    elif tests_ran:
        combined = test_score
    elif rubric_text:
        combined = rubric_score
    else:
        combined = 0
        feedback = "No tests or rubric available for this exercise."

    return GradeResponse(
        passed=combined >= 70,
        score=combined,
        test_results=test_items,
        feedback=feedback,
    )
