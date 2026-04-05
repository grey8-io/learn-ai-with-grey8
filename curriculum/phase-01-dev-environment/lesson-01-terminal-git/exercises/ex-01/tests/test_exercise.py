"""Tests for Exercise 1 — Your First Git Repository."""

import os
import subprocess
import tempfile
import shutil
import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SOLUTION_DIR = os.path.join(os.path.dirname(__file__), "..", "solution")
STARTER_DIR = os.path.join(os.path.dirname(__file__), "..", "starter")


def _find_bash() -> str:
    """Return a working bash executable path.

    On Windows, the bare ``bash`` command may resolve to WSL's ``/bin/bash``
    which fails outside WSL.  Prefer Git-for-Windows bash when available.
    """
    import shutil as _sh

    # Fast path — works on Linux/macOS and Windows when Git Bash is on PATH
    found = _sh.which("bash")

    if os.name == "nt":
        # On Windows, try Git-for-Windows bash first to avoid WSL
        git_bash = _sh.which("bash", path=os.environ.get("ProgramFiles", "") + "\\Git\\bin")
        if git_bash:
            return git_bash
        git_bash_x86 = _sh.which("bash", path=os.environ.get("ProgramFiles(x86)", "") + "\\Git\\bin")
        if git_bash_x86:
            return git_bash_x86
        # Fallback: Git Bash commonly at this path
        for candidate in [
            os.path.join(os.environ.get("ProgramFiles", ""), "Git", "bin", "bash.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Git", "bin", "bash.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Git", "bin", "bash.exe"),
        ]:
            if os.path.isfile(candidate):
                return candidate

    if found:
        return found
    return "bash"  # last resort


def _run_script(script_dir: str) -> str:
    """Run main.sh inside a temporary copy of *script_dir* and return the
    path to the resulting 'my-project' directory."""
    tmp = tempfile.mkdtemp()
    work = os.path.join(tmp, "work")
    shutil.copytree(script_dir, work)
    script = os.path.join(work, "main.sh")
    bash = _find_bash()
    subprocess.run([bash, script], cwd=work, check=True, capture_output=True)
    return os.path.join(work, "my-project"), tmp


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def project_dir():
    """Run the solution script once and return the path to my-project."""
    proj, tmp = _run_script(SOLUTION_DIR)
    yield proj
    shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_directory_exists(project_dir):
    """The 'my-project' directory should exist."""
    assert os.path.isdir(project_dir), "my-project directory was not created"


def test_git_initialized(project_dir):
    """A .git directory should exist inside my-project."""
    git_dir = os.path.join(project_dir, ".git")
    assert os.path.isdir(git_dir), "Git repository was not initialized (.git missing)"


def test_hello_file_exists(project_dir):
    """hello.txt should exist in my-project."""
    hello = os.path.join(project_dir, "hello.txt")
    assert os.path.isfile(hello), "hello.txt was not created"


def test_hello_file_content(project_dir):
    """hello.txt should contain the expected greeting."""
    hello = os.path.join(project_dir, "hello.txt")
    content = open(hello).read().strip()
    assert content == "Hello, AI world!", f"Expected 'Hello, AI world!' but got '{content}'"


def test_at_least_one_commit(project_dir):
    """There should be at least one Git commit in the repository."""
    result = subprocess.run(
        ["git", "log", "--oneline"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "git log failed — no commits found"
    commits = result.stdout.strip().splitlines()
    assert len(commits) >= 1, "Expected at least one commit"
