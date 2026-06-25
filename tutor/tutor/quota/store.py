"""Usage counters backing the hosted quota service.

The default store is in-memory: correct for local testing and a single Cloud
Run instance. Because Cloud Run scales to multiple instances, a *globally*
accurate spend circuit-breaker eventually needs a shared store (the central
Supabase/Postgres) — the ``UsageStore`` protocol below is the seam for that.
Until then the in-memory store enforces per-instance limits, which is honest and
safe at launch scale. Swapping in a DB-backed store won't touch any caller.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol


def utc_day() -> str:
    """Current UTC date as an ISO string — the daily reset key."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


class UsageStore(Protocol):
    """Day-keyed counters for per-account and global metered usage."""

    def account_count(self, account_id: str, day: str, kind: str) -> int: ...

    def global_count(self, day: str) -> int: ...

    def incr(self, account_id: str, day: str, kind: str) -> None: ...


class InMemoryUsageStore:
    """Process-local counters keyed by day.

    Counts reset as the day key rolls over; stale prior-day buckets are pruned
    on the next write so memory stays bounded to ~one day of accounts.
    """

    def __init__(self) -> None:
        # day -> account_id -> kind -> count
        self._accounts: dict[str, dict[str, dict[str, int]]] = {}
        # day -> total metered count (drives the global circuit-breaker)
        self._global: dict[str, int] = {}

    def _prune(self, keep_day: str) -> None:
        for d in [d for d in self._accounts if d != keep_day]:
            del self._accounts[d]
        for d in [d for d in self._global if d != keep_day]:
            del self._global[d]

    def account_count(self, account_id: str, day: str, kind: str) -> int:
        return self._accounts.get(day, {}).get(account_id, {}).get(kind, 0)

    def global_count(self, day: str) -> int:
        return self._global.get(day, 0)

    def incr(self, account_id: str, day: str, kind: str) -> None:
        self._prune(day)
        acct = self._accounts.setdefault(day, {}).setdefault(account_id, {})
        acct[kind] = acct.get(kind, 0) + 1
        self._global[day] = self._global.get(day, 0) + 1
