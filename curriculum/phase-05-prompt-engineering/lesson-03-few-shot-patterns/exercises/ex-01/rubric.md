# Rubric — Advanced Prompt Patterns

| Criterion | Points | Description |
|---|---|---|
| build_chain_of_thought_prompt formats correctly | 20 | Includes question and step-by-step instruction, handles optional hint |
| build_few_shot_prompt formats examples | 20 | Correctly formats task, input/output pairs, and query |
| extract_final_answer finds markers | 25 | Detects common answer markers and extracts the answer text |
| extract_final_answer fallback works | 10 | Falls back to last non-empty line when no marker found |
| build_self_consistency_prompts generates variations | 15 | Returns n unique prompts with different prefixes |
| Code quality | 10 | Clean functions with type hints and readable logic |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Review the lesson content and try again -- you've got this!
