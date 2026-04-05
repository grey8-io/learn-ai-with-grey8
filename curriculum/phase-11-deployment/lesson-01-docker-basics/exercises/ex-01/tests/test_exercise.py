"""Tests for Exercise 1 — Docker Configuration Generators."""

import importlib.util
import os
import pytest
import yaml

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SOLUTION_PATH = os.path.join(
    os.path.dirname(__file__), "..", "solution", "main.py"
)


def _load_module(path: str):
    """Import main.py as a module from the given path."""
    spec = importlib.util.spec_from_file_location("student_main", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def mod():
    return _load_module(SOLUTION_PATH)


# ---------------------------------------------------------------------------
# Tests — generate_dockerfile
# ---------------------------------------------------------------------------

def test_dockerfile_fastapi_has_from(mod):
    """FastAPI Dockerfile should start with FROM."""
    result = mod.generate_dockerfile("fastapi")
    assert result.startswith("FROM python:3.11-slim")


def test_dockerfile_fastapi_has_uvicorn_cmd(mod):
    """FastAPI Dockerfile should use uvicorn in CMD."""
    result = mod.generate_dockerfile("fastapi")
    assert "uvicorn" in result
    assert "EXPOSE 8000" in result


def test_dockerfile_streamlit_has_streamlit_cmd(mod):
    """Streamlit Dockerfile should use streamlit in CMD."""
    result = mod.generate_dockerfile("streamlit", port=8501)
    assert "streamlit" in result
    assert "EXPOSE 8501" in result


def test_dockerfile_custom_python_version(mod):
    """Dockerfile should use the specified Python version."""
    result = mod.generate_dockerfile("fastapi", python_version="3.12")
    assert "python:3.12-slim" in result


def test_dockerfile_invalid_app_type_raises(mod):
    """Invalid app_type should raise ValueError."""
    with pytest.raises(ValueError):
        mod.generate_dockerfile("flask")


# ---------------------------------------------------------------------------
# Tests — generate_compose
# ---------------------------------------------------------------------------

def test_compose_valid_yaml(mod):
    """Generated compose should be valid YAML."""
    services = [
        {"name": "api", "image_or_build": "./backend", "port": 8000, "env": None, "depends_on": None, "volumes": None},
    ]
    result = mod.generate_compose(services)
    parsed = yaml.safe_load(result)
    assert "services" in parsed
    assert "api" in parsed["services"]


def test_compose_build_vs_image(mod):
    """Services with paths should use 'build', others should use 'image'."""
    services = [
        {"name": "app", "image_or_build": "./src", "port": 8000, "env": None, "depends_on": None, "volumes": None},
        {"name": "db", "image_or_build": "postgres:15", "port": 5432, "env": None, "depends_on": None, "volumes": None},
    ]
    result = mod.generate_compose(services)
    parsed = yaml.safe_load(result)
    assert "build" in parsed["services"]["app"]
    assert "image" in parsed["services"]["db"]


def test_compose_includes_env_and_depends(mod):
    """Compose should include environment and depends_on when provided."""
    services = [
        {"name": "api", "image_or_build": "./app", "port": 8000, "env": {"KEY": "value"}, "depends_on": ["db"], "volumes": None},
    ]
    result = mod.generate_compose(services)
    parsed = yaml.safe_load(result)
    assert parsed["services"]["api"]["environment"]["KEY"] == "value"
    assert "db" in parsed["services"]["api"]["depends_on"]


# ---------------------------------------------------------------------------
# Tests — generate_dockerignore
# ---------------------------------------------------------------------------

def test_dockerignore_has_standard_patterns(mod):
    """Dockerignore should include standard patterns."""
    result = mod.generate_dockerignore()
    assert "__pycache__" in result
    assert ".venv" in result
    assert ".git" in result
    assert ".env" in result


def test_dockerignore_includes_extras(mod):
    """Dockerignore should include extra patterns when provided."""
    result = mod.generate_dockerignore(extra_patterns=["*.log", "data/"])
    assert "*.log" in result
    assert "data/" in result


# ---------------------------------------------------------------------------
# Tests — validate_dockerfile
# ---------------------------------------------------------------------------

def test_validate_valid_dockerfile(mod):
    """A well-formed Dockerfile should be valid."""
    dockerfile = mod.generate_dockerfile("fastapi")
    result = mod.validate_dockerfile(dockerfile)
    assert result["valid"] is True
    assert result["issues"] == []


def test_validate_empty_dockerfile(mod):
    """An empty Dockerfile should be invalid."""
    result = mod.validate_dockerfile("")
    assert result["valid"] is False
    assert any("empty" in issue.lower() for issue in result["issues"])


def test_validate_missing_from(mod):
    """A Dockerfile without FROM should report the issue."""
    result = mod.validate_dockerfile("COPY . .\nCMD ['python', 'main.py']")
    assert result["valid"] is False
    assert any("FROM" in issue for issue in result["issues"])
