"""Grading router: run tests and LLM rubric scoring."""

from fastapi import APIRouter, Request

from tutor.config import settings
from tutor.engine.context import get_tests_dir, load_exercise_metadata
from tutor.engine.inference import inference_backend
from tutor.grading.rubric import score_with_rubric
from tutor.grading.runner import run_tests
from tutor.models.schemas import GradeRequest, GradeResponse
from tutor.quota.service import KIND_RUBRIC, quota_service

router = APIRouter(tags=["grade"])


@router.post("/grade", response_model=GradeResponse)
async def grade(req: GradeRequest, request: Request) -> GradeResponse:
    """Grade student code using tests (60%) and LLM rubric (40%)."""
    test_score = 0
    test_items = []
    tests_ran = False
    load_failed = False

    # Run pytest tests if available
    tests_dir = get_tests_dir(req.exercise_id)
    if tests_dir is not None:
        result = await run_tests(req.code, tests_dir)
        test_score = result.score
        test_items = result.items
        tests_ran = True
        load_failed = result.load_failed

    # File didn't import — nothing ran, so skip the rubric and score 0
    # rather than award partial credit for reading dead code.
    if load_failed:
        return GradeResponse(
            passed=False,
            score=0,
            test_results=test_items,
            feedback=(
                "Your file couldn't be loaded, so no part of it was evaluated. "
                "Fix the error shown above first — once the file parses cleanly, "
                "your code is graded against the tests and rubric."
            ),
        )

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

    # Hosted free tier: the LLM rubric is the metered perk — tests-only grading
    # stays free. When a free account is over its daily rubric limit, fall back
    # to tests-only scoring instead of erroring. Local mode skips this entirely.
    rubric_metered_out = False
    if rubric_text and settings.deployment_mode == "hosted":
        account_id = getattr(request.state, "account_id", None)
        tier = getattr(request.state, "account_tier", "free")
        if account_id:
            decision = quota_service.consume(account_id, KIND_RUBRIC, tier=tier)
            rubric_metered_out = not decision.allowed

    if rubric_text and not rubric_metered_out:
        rubric_result = await score_with_rubric(
            code=req.code,
            rubric=rubric_text,
            exercise_id=req.exercise_id,
            client=inference_backend,
            test_summary=test_summary,
        )
        rubric_score = rubric_result.score
        feedback = rubric_result.feedback
    elif rubric_metered_out:
        feedback = (
            "Your code was graded against the tests above. AI rubric feedback is "
            "today's free-tier limit — it resets tomorrow, or upgrade for "
            "unlimited AI feedback."
        )
    else:
        # No rubric: use LLM for general feedback only
        rubric_score = test_score  # mirror test score when no rubric
        feedback = "No rubric defined for this exercise."

    # Combined score: 60% tests + 40% rubric when both available. When the
    # rubric was metered out, the submission is scored on tests alone.
    if rubric_metered_out:
        combined = test_score
    elif tests_ran and rubric_text:
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
