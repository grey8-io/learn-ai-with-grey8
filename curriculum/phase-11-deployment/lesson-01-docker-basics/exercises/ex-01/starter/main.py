"""
Exercise: Docker Configuration Generators
==========================================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build utility functions that generate Docker configuration files.
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

    The Dockerfile should include:
        - FROM python:{version}-slim
        - WORKDIR /app
        - COPY requirements.txt .
        - RUN pip install --no-cache-dir -r requirements.txt
        - COPY . .
        - EXPOSE {port}
        - CMD appropriate for the app_type:
            - fastapi: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{port}"]
            - streamlit: ["streamlit", "run", "main.py", "--server.port", "{port}", "--server.address", "0.0.0.0"]

    Raises:
        ValueError: If app_type is not "fastapi" or "streamlit".
    """
    # TODO: Implement this function.
    # 1. Validate app_type is "fastapi" or "streamlit".
    # 2. Build the Dockerfile string line by line.
    # 3. Use the correct CMD for each app_type.
    # 4. Return the complete Dockerfile string.
    pass


def generate_compose(services: list[dict]) -> str:
    """Generate a docker-compose.yml string from a list of service definitions.

    Args:
        services: List of dicts, each with keys:
            - name (str): Service name
            - image_or_build (str): Docker image name or build path (starting with "." or "/")
            - port (int or None): Port mapping (same port inside and outside)
            - env (dict or None): Environment variables
            - depends_on (list[str] or None): Service dependencies
            - volumes (list[str] or None): Volume mounts

    Returns:
        A docker-compose.yml string (valid YAML).
    """
    # TODO: Implement this function.
    # 1. Create a compose dict with version "3.8" and empty services dict.
    # 2. Loop through services and build each service definition:
    #    - If image_or_build starts with "." or "/", use "build", otherwise "image".
    #    - If port is provided, add ports as ["{port}:{port}"].
    #    - If env is provided, add environment dict.
    #    - If depends_on is provided, add depends_on list.
    #    - If volumes is provided, add volumes list.
    # 3. Use yaml.dump() to convert to YAML string.
    # 4. Return the YAML string.
    pass


def generate_dockerignore(extra_patterns: list[str] | None = None) -> str:
    """Generate a .dockerignore file content.

    Args:
        extra_patterns: Optional list of additional patterns to include.

    Returns:
        A .dockerignore string with standard patterns plus any extras.

    Standard patterns to always include:
        __pycache__, *.pyc, .venv, .git, .env, node_modules,
        *.egg-info, .pytest_cache
    """
    # TODO: Implement this function.
    # 1. Define a list of standard patterns.
    # 2. If extra_patterns is provided, extend the list.
    # 3. Join with newlines and return.
    pass


def validate_dockerfile(content: str) -> dict:
    """Validate a Dockerfile string for common issues.

    Args:
        content: A Dockerfile string to validate.

    Returns:
        A dict with:
            - valid (bool): True if no issues found.
            - issues (list[str]): List of issue descriptions.

    Checks:
        1. Must contain a FROM instruction -> "Missing FROM instruction"
        2. Should contain an EXPOSE instruction -> "Missing EXPOSE instruction"
        3. Should contain a CMD or ENTRYPOINT instruction -> "Missing CMD or ENTRYPOINT instruction"
        4. Should not be empty -> "Dockerfile is empty"
    """
    # TODO: Implement this function.
    # 1. Initialize issues as an empty list.
    # 2. Check if content is empty or whitespace-only.
    # 3. Check for FROM, EXPOSE, CMD/ENTRYPOINT instructions.
    # 4. Return dict with valid and issues.
    pass


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
