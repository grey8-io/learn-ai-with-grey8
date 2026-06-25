"""Request-quota guard for the hosted course.

Local mode: pure pass-through — local learners are NEVER metered (the privacy
guarantee and the "no paywall on learning" rule).

Hosted mode: requires an authenticated account on the metered endpoints,
enforces per-account daily free limits, and trips a global spend circuit-breaker.

Token-costing endpoints:
- /chat  → one tutor message  (metered here; 429 when over)
- /hint  → one LLM hint        (metered here; generous limit)
- /grade → tests are FREE; the LLM rubric is metered INSIDE the grade handler,
           so a student over their rubric limit still gets tests-only grading
           rather than a hard 429.

The resolved (account_id, tier) is stashed on the ASGI scope state so the grade
handler can reuse it for rubric metering.

Implemented as pure ASGI middleware (not BaseHTTPMiddleware) so it never wraps or
buffers the response — the /chat SSE stream passes through untouched.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from tutor.config import settings
from tutor.quota.identity import resolve_account
from tutor.quota.service import KIND_HINT, KIND_TUTOR, quota_service

# Endpoints that require an account in hosted mode.
_AUTH_PATHS = ("/chat", "/grade", "/hint")
# Endpoints metered (and blocked with 429/503) directly by this middleware.
_BLOCKING_KIND = {"/chat": KIND_TUTOR, "/hint": KIND_HINT}


class QuotaMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (
            scope["type"] != "http"
            or settings.deployment_mode != "hosted"
            or scope.get("path") not in _AUTH_PATHS
        ):
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)  # headers only; body is not consumed
        account_id, tier = resolve_account(request)

        if not account_id:
            await self._deny(
                scope, receive, send,
                401, "Sign in to use the AI tutor, grading, and hints.",
            )
            return

        # Make identity available to downstream handlers (grade rubric metering).
        scope.setdefault("state", {})
        scope["state"]["account_id"] = account_id
        scope["state"]["account_tier"] = tier

        kind = _BLOCKING_KIND.get(scope["path"])
        if kind is not None:
            result = quota_service.consume(account_id, kind, tier=tier)
            if not result.allowed:
                await self._deny(scope, receive, send, result.status, result.message)
                return

        await self.app(scope, receive, send)

    @staticmethod
    async def _deny(
        scope: Scope, receive: Receive, send: Send, status: int, message: str
    ) -> None:
        response = JSONResponse({"error": message}, status_code=status)
        await response(scope, receive, send)
