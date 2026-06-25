"""Hosted quota + spend circuit-breaker logic.

Local mode never reaches this (the middleware short-circuits). In hosted mode it
keeps free-tier accounts within generous daily limits and protects against a
runaway global bill — the only real hosted cost being LLM tokens.

Metered kinds (each has a per-account daily free limit):
- ``tutor``  — one /chat message
- ``hint``   — one LLM-generated hint (generous limit)
- ``rubric`` — one LLM rubric grading; tests-only grading stays free, so the
               LLM rubric is the metered perk
"""

from __future__ import annotations

from dataclasses import dataclass

from tutor.config import settings
from tutor.quota.store import InMemoryUsageStore, UsageStore, utc_day

KIND_TUTOR = "tutor"
KIND_HINT = "hint"
KIND_RUBRIC = "rubric"


@dataclass
class QuotaResult:
    allowed: bool
    status: int  # 200 ok | 429 per-account limit | 503 global breaker
    message: str  # human-readable reason when denied ("" when allowed)


class QuotaService:
    def __init__(self, store: UsageStore | None = None) -> None:
        self._store = store or InMemoryUsageStore()

    def _free_limit(self, kind: str) -> int:
        return {
            KIND_TUTOR: settings.free_tutor_msgs_per_day,
            KIND_HINT: settings.free_hints_per_day,
            KIND_RUBRIC: settings.free_rubric_gradings_per_day,
        }.get(kind, 0)

    def consume(
        self, account_id: str, kind: str, *, tier: str = "free"
    ) -> QuotaResult:
        """Check limits and, if allowed, record one unit of usage.

        The global circuit-breaker is checked for every tier (it caps total
        spend); per-account daily limits apply to free accounts only.
        """
        day = utc_day()

        cap = settings.global_daily_metered_cap
        if cap > 0 and self._store.global_count(day) >= cap:
            return QuotaResult(
                False,
                503,
                "The tutor has reached today's global capacity. "
                "Please try again tomorrow.",
            )

        if tier != "paid":
            limit = self._free_limit(kind)
            if limit > 0 and self._store.account_count(account_id, day, kind) >= limit:
                return QuotaResult(
                    False,
                    429,
                    f"You've hit today's free limit for this feature ({limit}/day). "
                    "It resets tomorrow — upgrade for more.",
                )

        self._store.incr(account_id, day, kind)
        return QuotaResult(True, 200, "")


# Shared singleton (in-memory). A Supabase-backed store can replace the default
# without touching callers — see store.py.
quota_service = QuotaService()
