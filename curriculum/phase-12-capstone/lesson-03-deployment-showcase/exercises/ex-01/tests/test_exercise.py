"""Tests for Exercise 1 — Showcase & Deployment Utilities."""

import importlib.util
import os
import pytest

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


@pytest.fixture
def showcase(mod):
    return mod.ProjectShowcase(
        "Test Project",
        "A test project description",
        ["python", "fastapi", "docker"],
        github_url="https://github.com/user/test",
    )


# ---------------------------------------------------------------------------
# Tests — ProjectShowcase.__init__
# ---------------------------------------------------------------------------

def test_showcase_stores_attributes(mod):
    """ProjectShowcase should store all attributes."""
    s = mod.ProjectShowcase("My App", "Does things", ["python"])
    assert s.project_name == "My App"
    assert s.description == "Does things"
    assert s.tech_stack == ["python"]
    assert s.github_url is None


# ---------------------------------------------------------------------------
# Tests — generate_demo_script
# ---------------------------------------------------------------------------

def test_demo_script_contains_title(showcase):
    """Demo script should contain the project name."""
    result = showcase.generate_demo_script([
        {"step": "Start", "command_or_action": "python main.py", "expected_output": "Running"},
    ])
    assert "Test Project" in result


def test_demo_script_contains_steps(showcase):
    """Demo script should contain all steps."""
    steps = [
        {"step": "Start", "command_or_action": "python main.py", "expected_output": "Running"},
        {"step": "Test", "command_or_action": "curl localhost:8000", "expected_output": "OK"},
    ]
    result = showcase.generate_demo_script(steps)
    assert "Step 1" in result
    assert "Step 2" in result
    assert "python main.py" in result
    assert "curl localhost:8000" in result


# ---------------------------------------------------------------------------
# Tests — generate_architecture_diagram
# ---------------------------------------------------------------------------

def test_architecture_contains_components(showcase):
    """Architecture diagram should list all components."""
    components = [
        {"name": "API", "type": "backend", "connects_to": ["DB"]},
        {"name": "DB", "type": "database", "connects_to": []},
    ]
    result = showcase.generate_architecture_diagram(components)
    assert "API" in result
    assert "DB" in result
    assert "backend" in result


def test_architecture_contains_connections(showcase):
    """Architecture diagram should show connections."""
    components = [
        {"name": "API", "type": "backend", "connects_to": ["DB"]},
        {"name": "DB", "type": "database", "connects_to": []},
    ]
    result = showcase.generate_architecture_diagram(components)
    assert "API --> DB" in result


# ---------------------------------------------------------------------------
# Tests — generate_portfolio_entry
# ---------------------------------------------------------------------------

def test_portfolio_contains_name(showcase):
    """Portfolio entry should contain the project name."""
    result = showcase.generate_portfolio_entry()
    assert "## Test Project" in result


def test_portfolio_contains_tech_stack(showcase):
    """Portfolio entry should list tech stack."""
    result = showcase.generate_portfolio_entry()
    assert "python" in result
    assert "fastapi" in result


def test_portfolio_contains_github_url(showcase):
    """Portfolio entry should include GitHub URL when provided."""
    result = showcase.generate_portfolio_entry()
    assert "https://github.com/user/test" in result


# ---------------------------------------------------------------------------
# Tests — generate_deployment_checklist
# ---------------------------------------------------------------------------

def test_checklist_has_base_items(showcase):
    """Checklist should always have base items."""
    result = showcase.generate_deployment_checklist()
    assert "All tests pass" in result
    assert "README is up to date" in result


def test_checklist_docker_items(showcase):
    """Docker projects should have Docker-specific items."""
    result = showcase.generate_deployment_checklist()
    assert "Docker image builds successfully" in result


def test_checklist_fastapi_items(showcase):
    """FastAPI projects should have web-specific items."""
    result = showcase.generate_deployment_checklist()
    assert "Health check endpoint works" in result


# ---------------------------------------------------------------------------
# Tests — generate_license
# ---------------------------------------------------------------------------

def test_license_mit(mod):
    """MIT license should contain key phrases."""
    result = mod.generate_license("MIT", "Test Author", 2025)
    assert "MIT License" in result
    assert "Test Author" in result
    assert "2025" in result
    assert "Permission is hereby granted" in result


def test_license_apache(mod):
    """Apache license should contain key phrases."""
    result = mod.generate_license("Apache-2.0", "Test Author", 2025)
    assert "Apache License" in result
    assert "Test Author" in result


def test_license_invalid_raises(mod):
    """Invalid license type should raise ValueError."""
    with pytest.raises(ValueError):
        mod.generate_license("GPL")


# ---------------------------------------------------------------------------
# Tests — create_changelog
# ---------------------------------------------------------------------------

def test_changelog_has_title(mod):
    """Changelog should start with a title."""
    result = mod.create_changelog([
        {"version": "1.0.0", "date": "2025-01-01", "changes": ["Initial release"]},
    ])
    assert "# Changelog" in result


def test_changelog_has_entries(mod):
    """Changelog should contain all entries."""
    result = mod.create_changelog([
        {"version": "1.0.0", "date": "2025-01-01", "changes": ["Initial release"]},
        {"version": "1.1.0", "date": "2025-02-01", "changes": ["New feature", "Bug fix"]},
    ])
    assert "v1.0.0" in result
    assert "v1.1.0" in result
    assert "Initial release" in result
    assert "New feature" in result
    assert "Bug fix" in result
