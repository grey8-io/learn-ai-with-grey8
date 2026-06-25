"""Resolve the calling account from a request.

In hosted mode the tutor runs as an INTERNAL Cloud Run service reachable only by
the Next.js BFF, which has already verified the Supabase session. The BFF passes
a trusted identity downstream via headers. Keeping verification in the BFF means
the tutor needs no JWT secret and no extra dependency, and there is one auth
boundary — consistent with "frontend calls backend only".

Hosted deployments MUST therefore keep the tutor ingress internal-only and have
the web proxy inject these headers after verifying the signed-in user.
"""

from starlette.requests import Request

HEADER_ACCOUNT_ID = "X-Account-Id"
HEADER_ACCOUNT_TIER = "X-Account-Tier"


def resolve_account(request: Request) -> tuple[str | None, str]:
    """Return (account_id, tier). account_id is None when unauthenticated."""
    account_id = request.headers.get(HEADER_ACCOUNT_ID)
    tier = (request.headers.get(HEADER_ACCOUNT_TIER) or "free").lower()
    if tier not in ("free", "paid"):
        tier = "free"
    return (account_id or None), tier
