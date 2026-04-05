# Rubric — Monitoring & Observability System

| Criterion | Points | Description |
|---|---|---|
| AIMetrics records and retrieves requests | 15 | record_request stores all fields with timestamp |
| get_summary calculates correct metrics | 20 | Accurate avg latency, p95, error rate, token count, RPM |
| get_model_metrics filters by model | 10 | Returns per-model breakdown with correct counts |
| get_alerts checks rules correctly | 15 | Supports > and < operators, returns triggered alerts with values |
| StructuredLogger produces valid JSON | 15 | log, log_request, and log_llm_call output parseable JSON |
| create_dashboard_data aggregates correctly | 15 | Returns charts and top endpoints sorted by count |
| Code quality | 10 | Clean classes with type hints and readable logic |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Review the lesson content and try again -- you've got this!
