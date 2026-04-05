"""
Exercise: Docker Configuration Generators — Solution
=====================================================
"""

import yaml


def generate_dockerfile(app_type: str, python_version: str = "3.11", port: int = 8000) -> str:
    """Generate a Dockerfile string for a Python AI application.

    Args:
        app_type: Either "fastapi" or "streamlit".
        python_version: Python version for the base image (default "3.11").
        port: Port to expose (default 8000).

    Returns:
        A valid Dockerfile as a string.

    Raises:
        ValueError: If app_type is not "fastapi" or "streamlit".
    """
    if app_type not in ("fastapi", "streamlit"):
        raise ValueError(f"Unsupported app_type: {app_type}. Must be 'fastapi' or 'streamlit'.")

    lines = [
        f"FROM python:{python_version}-slim",
        "WORKDIR /app",
        "COPY requirements.txt .",
        "RUN pip install --no-cache-dir -r requirements.txt",
        "COPY . .",
        f"EXPOSE {port}",
    ]

    if app_type == "fastapi":
        lines.append(f'CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{port}"]')
    else:
        lines.append(f'CMD ["streamlit", "run", "main.py", "--server.port", "{port}", "--server.address", "0.0.0.0"]')

    return "\n".join(lines)


def generate_compose(services: list[dict]) -> str:
    """Generate a docker-compose.yml string from a list of service definitions.

    Args:
        services: List of dicts with name, image_or_build, port, env, depends_on, volumes.

    Returns:
        A docker-compose.yml string (valid YAML).
    """
    compose = {"version": "3.8", "services": {}}

    for svc in services:
        service_def = {}

        if svc["image_or_build"].startswith(".") or svc["image_or_build"].startswith("/"):
            service_def["build"] = svc["image_or_build"]
        else:
            service_def["image"] = svc["image_or_build"]

        if svc.get("port"):
            service_def["ports"] = [f"{svc['port']}:{svc['port']}"]

        if svc.get("env"):
            service_def["environment"] = svc["env"]

        if svc.get("depends_on"):
            service_def["depends_on"] = svc["depends_on"]

        if svc.get("volumes"):
            service_def["volumes"] = svc["volumes"]

        compose["services"][svc["name"]] = service_def

    return yaml.dump(compose, default_flow_style=False, sort_keys=False)


def generate_dockerignore(extra_patterns: list[str] | None = None) -> str:
    """Generate a .dockerignore file content.

    Args:
        extra_patterns: Optional list of additional patterns to include.

    Returns:
        A .dockerignore string with standard patterns plus any extras.
    """
    patterns = [
        "__pycache__",
        "*.pyc",
        ".venv",
        ".git",
        ".env",
        "node_modules",
        "*.egg-info",
        ".pytest_cache",
    ]

    if extra_patterns:
        patterns.extend(extra_patterns)

    return "\n".join(patterns)


def validate_dockerfile(content: str) -> dict:
    """Validate a Dockerfile string for common issues.

    Args:
        content: A Dockerfile string to validate.

    Returns:
        A dict with valid (bool) and issues (list[str]).
    """
    issues = []

    if not content.strip():
        issues.append("Dockerfile is empty")
        return {"valid": False, "issues": issues}

    upper_content = content.upper()

    if "FROM " not in upper_content:
        issues.append("Missing FROM instruction")

    if "EXPOSE " not in upper_content:
        issues.append("Missing EXPOSE instruction")

    if "CMD " not in upper_content and "ENTRYPOINT " not in upper_content:
        issues.append("Missing CMD or ENTRYPOINT instruction")

    return {"valid": len(issues) == 0, "issues": issues}


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== Dockerfile (FastAPI) ===")
    print(generate_dockerfile("fastapi"))
    print()

    print("=== Dockerfile (Streamlit) ===")
    print(generate_dockerfile("streamlit", port=8501))
    print()

    print("=== Docker Compose ===")
    services = [
        {"name": "api", "image_or_build": "./backend", "port": 8000, "env": {"OLLAMA_HOST": "http://ollama:11434"}, "depends_on": ["ollama"], "volumes": None},
        {"name": "ollama", "image_or_build": "ollama/ollama", "port": 11434, "env": None, "depends_on": None, "volumes": ["ollama_data:/root/.ollama"]},
    ]
    print(generate_compose(services))
    print()

    print("=== .dockerignore ===")
    print(generate_dockerignore(extra_patterns=["*.log", "data/"]))
    print()

    print("=== Validate Dockerfile ===")
    print(validate_dockerfile(generate_dockerfile("fastapi")))
