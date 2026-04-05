"""Tests for Exercise 1 — Project Planning Utilities."""

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
def plan(mod):
    p = mod.ProjectPlan("Test Project", "A test project", ["python", "fastapi"])
    p.add_requirement("User login", "high")
    p.add_requirement("Chat interface", "medium")
    p.add_milestone("MVP", ["Basic chat", "LLM integration"])
    return p


# ---------------------------------------------------------------------------
# Tests — ProjectPlan.__init__
# ---------------------------------------------------------------------------

def test_plan_stores_attributes(mod):
    """ProjectPlan should store name, description, and tech_stack."""
    p = mod.ProjectPlan("My App", "Does things", ["python"])
    assert p.name == "My App"
    assert p.description == "Does things"
    assert p.tech_stack == ["python"]


def test_plan_default_tech_stack(mod):
    """tech_stack should default to empty list."""
    p = mod.ProjectPlan("My App", "Does things")
    assert p.tech_stack == []


# ---------------------------------------------------------------------------
# Tests — add_requirement / add_milestone
# ---------------------------------------------------------------------------

def test_add_requirement(mod):
    """add_requirement should store requirement with priority."""
    p = mod.ProjectPlan("Test", "Test")
    p.add_requirement("Feature X", "high")
    assert len(p.requirements) == 1
    assert p.requirements[0]["requirement"] == "Feature X"
    assert p.requirements[0]["priority"] == "high"


def test_add_milestone(mod):
    """add_milestone should store milestone with tasks."""
    p = mod.ProjectPlan("Test", "Test")
    p.add_milestone("MVP", ["Task 1", "Task 2"], deadline="2025-06-01")
    assert len(p.milestones) == 1
    assert p.milestones[0]["name"] == "MVP"
    assert len(p.milestones[0]["tasks"]) == 2


# ---------------------------------------------------------------------------
# Tests — generate_readme
# ---------------------------------------------------------------------------

def test_readme_contains_name(plan):
    """README should contain the project name as a heading."""
    readme = plan.generate_readme()
    assert "# Test Project" in readme


def test_readme_contains_description(plan):
    """README should contain the description."""
    readme = plan.generate_readme()
    assert "A test project" in readme


def test_readme_contains_tech_stack(plan):
    """README should list the tech stack."""
    readme = plan.generate_readme()
    assert "python" in readme
    assert "fastapi" in readme


# ---------------------------------------------------------------------------
# Tests — generate_structure
# ---------------------------------------------------------------------------

def test_structure_has_core_dirs(plan):
    """Structure should always have src and tests."""
    structure = plan.generate_structure()
    assert "src" in structure
    assert "tests" in structure
    assert "requirements.txt" in structure


def test_structure_fastapi_has_app(plan):
    """FastAPI projects should have app.py in src."""
    structure = plan.generate_structure()
    assert "app.py" in structure["src"]


def test_structure_docker(mod):
    """Docker projects should have Dockerfile."""
    p = mod.ProjectPlan("Test", "Test", ["python", "docker"])
    structure = p.generate_structure()
    assert "Dockerfile" in structure


# ---------------------------------------------------------------------------
# Tests — estimate_complexity
# ---------------------------------------------------------------------------

def test_complexity_small(mod):
    """Few requirements and milestones should be small."""
    p = mod.ProjectPlan("Test", "Test")
    p.add_requirement("One thing")
    p.add_milestone("MVP", ["task"])
    assert p.estimate_complexity() == "small"


def test_complexity_large(mod):
    """Many requirements should be large."""
    p = mod.ProjectPlan("Test", "Test")
    for i in range(10):
        p.add_requirement(f"Requirement {i}")
    assert p.estimate_complexity() == "large"


# ---------------------------------------------------------------------------
# Tests — select_project
# ---------------------------------------------------------------------------

def test_select_returns_list(mod):
    """select_project should return a list."""
    result = mod.select_project(["code"], "beginner")
    assert isinstance(result, list)


def test_select_max_three(mod):
    """select_project should return at most 3 projects."""
    result = mod.select_project(["code", "education", "web"], "advanced")
    assert len(result) <= 3


def test_select_beginner_only_beginner(mod):
    """Beginner skill level should only return beginner projects."""
    result = mod.select_project(["code", "education"], "beginner")
    for project in result:
        assert project["level"] == "beginner"


def test_select_has_reason(mod):
    """Each recommendation should include a reason."""
    result = mod.select_project(["code"], "intermediate")
    for project in result:
        assert "reason" in project
        assert len(project["reason"]) > 0
