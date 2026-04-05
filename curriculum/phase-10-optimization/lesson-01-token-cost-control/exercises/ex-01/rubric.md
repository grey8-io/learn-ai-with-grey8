# Rubric — Token & Cost Management

| Criterion | Points | Description |
|---|---|---|
| estimate_tokens returns correct approximation | 10 | len(text) // 4 |
| CostTracker.track records usage correctly | 20 | Calculates tokens and cost, appends record with all fields |
| CostTracker.get_usage_report aggregates correctly | 20 | Totals, averages, handles empty tracker |
| CostTracker.get_model_breakdown groups by model | 15 | Correct per-model aggregation |
| optimize_prompt cleans and truncates | 20 | Collapses whitespace, removes fillers, respects token budget |
| select_model picks correct model per complexity | 10 | Low=speed, high=quality, medium=balanced |
| Code quality | 5 | Clean functions, proper type hints, readable logic |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Review the lesson content and try again -- you've got this!
