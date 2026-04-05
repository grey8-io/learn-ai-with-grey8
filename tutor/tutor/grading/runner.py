"""Sandboxed test runner: executes student code against pytest test suites."""

import asyncio
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from tutor.models.schemas import TestResultItem


class TestResult:
    """Result of running tests against student code."""

    def __init__(
        self,
        passed: bool,
        total: int,
        passed_count: int,
        failed_count: int,
        items: list[TestResultItem],
        raw_output: str = "",
    ) -> None:
        self.passed = passed
        self.total = total
        self.passed_count = passed_count
        self.failed_count = failed_count
        self.items = items
        self.raw_output = raw_output

    @property
    def score(self) -> int:
        if self.total == 0:
            return 0
        return int((self.passed_count / self.total) * 100)


async def run_tests(code: str, test_dir: Path) -> TestResult:
    """Write student code to a temp file and run pytest against it.

    Args:
        code: The student's Python code as a string.
        test_dir: Path to the directory containing pytest test files.

    Returns:
        A TestResult with pass/fail counts and per-test details.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # Detect shell exercises: if the starter directory has main.sh, write
        # student code as main.sh inside a solution_dir/ subdirectory so the
        # bash test harness can find it.
        starter_dir = test_dir.parent / "starter"
        if (starter_dir / "main.sh").exists():
            sol_dir = tmp_path / "solution_dir"
            sol_dir.mkdir()
            (sol_dir / "main.sh").write_text(code, encoding="utf-8")
        else:
            # Write student code as solution.py so tests can import it
            (tmp_path / "solution.py").write_text(code, encoding="utf-8")

        # Copy test files into the temp directory, rewriting hardcoded paths
        # so tests load the student's code instead of the curriculum solution.
        for test_file in test_dir.glob("test_*.py"):
            content = test_file.read_text(encoding="utf-8")
            # Rewrite SOLUTION_PATH to load solution.py from the temp dir.
            # The original pattern spans multiple lines:
            #   SOLUTION_PATH = os.path.join(
            #       os.path.dirname(__file__), "..", "solution", "main.py"
            #   )
            # Match from "SOLUTION_PATH =" through the closing ")" on its own line.
            content = re.sub(
                r"SOLUTION_PATH\s*=\s*os\.path\.join\([\s\S]*?\n\)",
                'SOLUTION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "solution.py")',
                content,
            )
            # Rewrite SOLUTION_DIR for bash exercises (single-line pattern)
            content = re.sub(
                r"SOLUTION_DIR\s*=\s*os\.path\.join\(.*\)",
                'SOLUTION_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "solution_dir")',
                content,
            )
            dest = tmp_path / test_file.name
            dest.write_text(content, encoding="utf-8")

        try:
            def _run_pytest():
                return subprocess.run(
                    [sys.executable, "-m", "pytest", str(tmp_path), "-v", "--tb=short", "--no-header"],
                    capture_output=True,
                    cwd=str(tmp_path),
                    timeout=30,
                )

            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=1) as pool:
                proc_result = await loop.run_in_executor(pool, _run_pytest)

            stdout_bytes = proc_result.stdout
            stderr_bytes = proc_result.stderr
        except subprocess.TimeoutExpired:
            return TestResult(
                passed=False,
                total=0,
                passed_count=0,
                failed_count=0,
                items=[],
                raw_output="Test execution timed out after 30 seconds.",
            )
        except FileNotFoundError:
            return TestResult(
                passed=False,
                total=0,
                passed_count=0,
                failed_count=0,
                items=[],
                raw_output="pytest not found. Ensure it is installed.",
            )

        output = stdout_bytes.decode(errors="replace")
        items = _parse_pytest_output(output)
        passed_count = sum(1 for i in items if i.passed)
        failed_count = sum(1 for i in items if not i.passed)
        total = len(items)

        return TestResult(
            passed=failed_count == 0 and total > 0,
            total=total,
            passed_count=passed_count,
            failed_count=failed_count,
            items=items,
            raw_output=output,
        )


def _parse_pytest_output(output: str) -> list[TestResultItem]:
    """Parse pytest -v output into structured test results with failure details."""
    items: list[TestResultItem] = []

    # Step 1: Collect pass/fail status from verbose lines
    # Matches lines like: "test_exercise.py::test_something PASSED" (status at end of line)
    # Excludes summary lines like: "FAILED test_exercise.py::test_foo - ErrorType: ..."
    status_pattern = re.compile(
        r"^(\S+?::test_\w+)\s+(PASSED|FAILED|ERROR)\s*(?:\[.*\])?\s*$", re.MULTILINE
    )
    test_statuses: dict[str, str] = {}
    for match in status_pattern.finditer(output):
        name = match.group(1).strip()
        status = match.group(2)
        # Normalize name — remove file prefix, keep test function name
        short_name = name.split("::")[-1] if "::" in name else name
        test_statuses[short_name] = status

    # Step 2: Extract failure/error details from short summary lines
    # Pattern: "FAILED test_file::test_name - ErrorType: message"
    # or:      "ERROR test_file::test_name - ErrorType: message"
    failure_details: dict[str, str] = {}
    fail_detail_pattern = re.compile(
        r"(?:FAILED|ERROR)\s+\S+?::(test_\w+)\s*[-–—]\s*(.+?)$", re.MULTILINE
    )
    for match in fail_detail_pattern.finditer(output):
        test_name = match.group(1)
        detail = match.group(2).strip()
        failure_details[test_name] = detail

    # Step 3: Extract E-lines from tracebacks (assertion details, TypeErrors, etc.)
    # Track which test section we're in by matching traceback headers.
    e_lines: dict[str, list[str]] = {}
    current_test = ""
    for line in output.split("\n"):
        # Match traceback section headers (multiple formats):
        #   "_ ERROR at setup of test_foo _"
        #   "_ FAILED test_file::test_foo _"
        #   "_____ test_welcome_message _____"  (plain failure)
        tb_header = re.search(r"_{3,}\s*(?:ERROR at setup of |FAILED\s+\S*::)?(test_\w+)\s*_{3,}", line)
        if tb_header:
            current_test = tb_header.group(1)
            e_lines.setdefault(current_test, [])
            continue
        # Section boundary — reset when we hit a major separator
        if line.startswith("=") and len(line) > 3:
            current_test = ""
            continue
        # Capture E-lines (pytest assertion/error details)
        if current_test and line.strip().startswith("E "):
            detail = line.strip()[2:].strip()
            if detail and current_test in e_lines:
                e_lines[current_test].append(detail)

    # Step 4: Build test result items with meaningful messages
    for full_name, status in test_statuses.items():
        short = full_name.split("::")[-1] if "::" in full_name else full_name

        if status == "PASSED":
            message = ""
        else:
            # Priority: E-lines > failure detail > generic
            if short in e_lines and e_lines[short]:
                message = " | ".join(e_lines[short][:3])
            elif short in failure_details:
                message = failure_details[short]
            else:
                message = f"Test {status}"

            # Clean up common noise
            message = message.replace("AssertionError: ", "").replace("AssertError: ", "")
            # Truncate very long messages
            if len(message) > 200:
                message = message[:197] + "..."

        items.append(
            TestResultItem(
                name=full_name,
                passed=status == "PASSED",
                message=message,
            )
        )

    return items
