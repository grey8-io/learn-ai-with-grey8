# Rubric — Production Patterns for AI Backends

| Criterion | Points | Description |
|---|---|---|
| RateLimiter tracks and enforces limits per client | 25 | Sliding window, allows under limit, blocks over limit, separate clients |
| RateLimiter get_wait_time works correctly | 10 | Returns 0 when allowed, positive seconds when rate limited |
| ResponseCache stores, retrieves, and expires entries | 20 | Set/get works, TTL expiry, eviction when full |
| ResponseCache make_key is deterministic | 5 | Same inputs produce same hash, different inputs produce different hash |
| sanitize_input handles all edge cases | 20 | Control chars removed, length enforced, non-strings handled, whitespace stripped |
| create_error_response returns correct structure | 10 | Contains message, type, status_code with proper defaults |
| Code quality | 10 | Clean classes, proper type hints, readable logic |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Review the lesson content and try again -- you've got this!
