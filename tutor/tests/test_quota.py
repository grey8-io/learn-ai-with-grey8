"""Tests for the hosted-course quota service, store, and middleware.

All of this is dormant in local mode — the local-mode tests assert exactly that.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from tutor.config import settings
from tutor.main import app
from tutor.quota.service import KIND_TUTOR, QuotaService
from tutor.quota.store import InMemoryUsageStore


def test_store_counts_and_resets_per_day():
    store = InMemoryUsageStore()
    assert store.account_count("u1", "2026-06-04", KIND_TUTOR) == 0

    store.incr("u1", "2026-06-04", KIND_TUTOR)
    store.incr("u1", "2026-06-04", KIND_TUTOR)
    assert store.account_count("u1", "2026-06-04", KIND_TUTOR) == 2
    assert store.global_count("2026-06-04") == 2

    # A new day prunes the prior day's buckets (counts reset).
    store.incr("u1", "2026-06-05", KIND_TUTOR)
    assert store.account_count("u1", "2026-06-04", KIND_TUTOR) == 0
    assert store.global_count("2026-06-05") == 1


def test_per_account_daily_limit(monkeypatch):
    monkeypatch.setattr(settings, "free_tutor_msgs_per_day", 2)
    monkeypatch.setattr(settings, "global_daily_metered_cap", 0)
    svc = QuotaService(InMemoryUsageStore())

    assert svc.consume("u1", KIND_TUTOR).allowed
    assert svc.consume("u1", KIND_TUTOR).allowed
    denied = svc.consume("u1", KIND_TUTOR)
    assert not denied.allowed and denied.status == 429
    # A different account has its own bucket.
    assert svc.consume("u2", KIND_TUTOR).allowed


def test_paid_tier_bypasses_per_account_limit(monkeypatch):
    monkeypatch.setattr(settings, "free_tutor_msgs_per_day", 1)
    monkeypatch.setattr(settings, "global_daily_metered_cap", 0)
    svc = QuotaService(InMemoryUsageStore())

    assert svc.consume("p1", KIND_TUTOR, tier="paid").allowed
    assert svc.consume("p1", KIND_TUTOR, tier="paid").allowed  # still allowed


def test_global_circuit_breaker(monkeypatch):
    monkeypatch.setattr(settings, "free_tutor_msgs_per_day", 100)
    monkeypatch.setattr(settings, "global_daily_metered_cap", 2)
    svc = QuotaService(InMemoryUsageStore())

    assert svc.consume("u1", KIND_TUTOR).allowed
    assert svc.consume("u2", KIND_TUTOR).allowed
    tripped = svc.consume("u3", KIND_TUTOR)
    assert not tripped.allowed and tripped.status == 503
    # The breaker caps total spend, so even a paid account is stopped.
    assert not svc.consume("vip", KIND_TUTOR, tier="paid").allowed


@pytest.mark.asyncio
async def test_local_mode_never_requires_auth(monkeypatch):
    """In local mode a metered endpoint is reachable with no account header."""
    monkeypatch.setattr(settings, "deployment_mode", "local")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://t") as client:
        resp = await client.post(
            "/hint",
            json={"exercise_id": "nope", "code": "", "hint_level": 1},
        )
    assert resp.status_code != 401


@pytest.mark.asyncio
async def test_hosted_mode_requires_account(monkeypatch):
    """In hosted mode a metered endpoint without an account header is 401."""
    monkeypatch.setattr(settings, "deployment_mode", "hosted")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://t") as client:
        resp = await client.post(
            "/hint",
            json={"exercise_id": "nope", "code": "", "hint_level": 1},
        )
    assert resp.status_code == 401
    assert "error" in resp.json()


@pytest.mark.asyncio
async def test_hosted_mode_allows_with_account_header(monkeypatch):
    """A valid account header passes the auth gate (hint falls back to a generic
    tip when the LLM is unreachable, so we just assert it is not blocked)."""
    monkeypatch.setattr(settings, "deployment_mode", "hosted")
    monkeypatch.setattr(settings, "free_hints_per_day", 5)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://t") as client:
        resp = await client.post(
            "/hint",
            json={"exercise_id": "nope", "code": "", "hint_level": 1},
            headers={"X-Account-Id": "test-user", "X-Account-Tier": "free"},
        )
    assert resp.status_code not in (401, 429, 503)
