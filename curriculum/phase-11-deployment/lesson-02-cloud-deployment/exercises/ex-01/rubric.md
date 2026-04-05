# Rubric — Deployment Configuration Utilities

| Criterion | Points | Description |
|---|---|---|
| generate_nginx_config produces valid config | 20 | Includes server block, domain, proxy_pass, headers; SSL variant works |
| generate_systemd_service has correct sections | 15 | [Unit], [Service], [Install] with proper fields |
| generate_env_file handles secrets | 15 | Outputs KEY=value lines, marks secrets with comments |
| generate_health_check_script is functional | 15 | Bash script with shebang, curl commands, status reporting |
| estimate_server_requirements returns sensible values | 20 | Correct formulas, minimum values enforced, cost range included |
| DeploymentConfig stores attributes correctly | 5 | __init__ handles defaults properly |
| Code quality | 10 | Clean methods with type hints and readable logic |

**Total: 100 points**

## Passing threshold

- **80+ points**: Pass
- **Below 80**: Review the lesson content and try again -- you've got this!
