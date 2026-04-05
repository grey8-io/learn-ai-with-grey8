# Rubric — Docker Configuration Generators

| Criterion | Points | Description |
|---|---|---|
| generate_dockerfile produces valid Dockerfiles | 25 | Correct FROM, WORKDIR, COPY, RUN, EXPOSE, and CMD for both app types |
| generate_compose produces valid YAML | 25 | Correctly distinguishes build vs image, includes ports, env, depends_on, volumes |
| generate_dockerignore includes standard patterns | 15 | All standard patterns present, extras appended when provided |
| validate_dockerfile catches common issues | 20 | Detects missing FROM, EXPOSE, CMD/ENTRYPOINT, and empty content |
| Error handling | 5 | ValueError raised for invalid app_type |
| Code quality | 10 | Clean functions with type hints and readable logic |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Review the lesson content and try again -- you've got this!
