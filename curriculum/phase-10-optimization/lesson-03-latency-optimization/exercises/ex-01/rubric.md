# Rubric — Latency Optimization

| Criterion | Points | Description |
|---|---|---|
| LatencyTracker start/end records durations correctly | 15 | Stores timestamps, calculates ms, handles missing starts |
| LatencyTracker get_stats with percentiles | 20 | min, max, avg, p50, p95, p99, count all correct |
| LatencyTracker get_slow_operations filters and sorts | 10 | Finds operations above threshold, sorted descending by avg_ms |
| measure decorator records time and preserves name | 15 | Sets last_duration_ms, uses functools.wraps |
| StreamBuffer accumulates and emits correctly | 20 | Buffers until min_chars, emits, flush returns remainder |
| estimate_time computes correctly | 10 | output_tokens = input_length // 4, divides by speed |
| Code quality | 10 | Clean classes, proper type hints, readable logic |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Review the lesson content and try again -- you've got this!
