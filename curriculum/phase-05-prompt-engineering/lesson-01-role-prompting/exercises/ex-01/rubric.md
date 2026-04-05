# Rubric — Prompt Engineering Utilities

| Criterion | Points | Description |
|---|---|---|
| create_system_prompt assembles all components | 25 | Returns formatted string with role, expertise, tone, constraints |
| create_few_shot_prompt formats examples | 25 | Correctly formats task, examples as input/output pairs, and query |
| validate_prompt catches empty prompts | 15 | Detects empty and whitespace-only prompts |
| validate_prompt checks token limits | 15 | Estimates tokens as chars/4 and flags when exceeded |
| validate_prompt returns correct dict shape | 10 | Returns dict with valid, issues, and estimated_tokens keys |
| Code quality | 10 | Clean functions with type hints and readable logic |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Review the lesson content and try again -- you've got this!
