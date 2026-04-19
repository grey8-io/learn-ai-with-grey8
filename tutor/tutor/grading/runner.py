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
            return _failure_result(
                "Test execution timed out after 30 seconds.",
                "Your code may have an infinite loop or a very slow operation. "
                "Check for unbounded `while` loops or expensive recursion.",
            )
        except FileNotFoundError:
            return _failure_result(
                "pytest not found. Ensure it is installed.",
                "This is a server-side configuration problem, not a problem with your code.",
            )
        except Exception as exc:  # noqa: BLE001 — surface unexpected errors to the student
            return _failure_result(
                f"Test runner crashed: {type(exc).__name__}: {exc}",
                "This is unexpected. Try resubmitting; if it persists, report it.",
            )

        output = stdout_bytes.decode(errors="replace")
        stderr_output = stderr_bytes.decode(errors="replace")
        items = _parse_pytest_output(output)
        passed_count = sum(1 for i in items if i.passed)
        failed_count = sum(1 for i in items if not i.passed)
        total = len(items)

        # When pytest emitted no per-test status lines we can parse, surface the
        # raw error so the student isn't stuck staring at "0/0 Tests Passed".
        # This handles collection failures, bad pytest output, exotic errors, etc.
        if total == 0:
            extracted = _extract_pytest_error(output, stderr_output)
            return _failure_result(extracted, raw_output=output or stderr_output)

        return TestResult(
            passed=failed_count == 0 and total > 0,
            total=total,
            passed_count=passed_count,
            failed_count=failed_count,
            items=items,
            raw_output=output,
        )


def _failure_result(message: str, hint: str = "", raw_output: str = "") -> "TestResult":
    """Build a TestResult with a single synthetic failure item.

    Used when pytest can't run or produces no parseable output, so the student
    sees a real explanation instead of an empty "0/0 Tests Passed" panel.
    """
    translated = _humanize_error(message)
    full_message = f"{translated}\n\n{hint}".strip() if hint else translated
    return TestResult(
        passed=False,
        total=1,
        passed_count=0,
        failed_count=1,
        items=[
            TestResultItem(
                name="Test setup",
                passed=False,
                message=full_message,
            )
        ],
        raw_output=raw_output or message,
    )


# ---------------------------------------------------------------------------
# Beginner-friendly error translation
# ---------------------------------------------------------------------------
# Maps common Python error patterns to clearer, instructive messages.
# Order matters: the first matching pattern wins, so list specific patterns
# (like the dunder typos) BEFORE their generic counterparts.
_TRANSLATIONS: list[tuple[str, str]] = [
    # Dunder typos — the exact case that prompted this layer
    (
        r"NameError: name '_name_' is not defined",
        "'_name_' is not defined. You probably meant '__name__' (Python's special variables use TWO underscores on each side, not one).",
    ),
    (
        r"NameError: name '_main_' is not defined",
        "'_main_' is not defined. You probably meant '__main__' (double underscores on each side).",
    ),
    (
        r"NameError: name '_init_' is not defined",
        "'_init_' is not defined. You probably meant '__init__' (double underscores on each side).",
    ),
    # Generic NameError — captures the variable name
    (
        r"NameError: name '(\w+)' is not defined",
        "'{0}' is not defined. Check the spelling, or make sure you defined this variable/function before using it.",
    ),
    # SyntaxError variants
    (
        r"SyntaxError: expected ':'",
        "Missing colon. Lines starting with 'if', 'for', 'while', 'def', or 'class' must end with ':'.",
    ),
    (
        r"SyntaxError: '(\w+)' was never closed",
        "Unclosed '{0}'. Every opening bracket / paren / quote needs a matching close.",
    ),
    (
        r"SyntaxError: unterminated string literal",
        "A string is missing its closing quote. Check that every opening ' or \" has a matching close on the same line.",
    ),
    (
        r"SyntaxError: invalid syntax",
        "Python can't parse this line. Common causes: missing colon, mismatched parentheses/brackets, unclosed strings, missing comma between items.",
    ),
    # IndentationError variants
    (
        r"IndentationError: expected an indented block",
        "Python expects code inside if/for/while/def/class blocks to be indented (4 spaces is standard).",
    ),
    (
        r"IndentationError: unexpected indent",
        "There's an unexpected indent here. Indentation should only increase after a line ending in ':'.",
    ),
    (
        r"IndentationError: unindent does not match",
        "Indentation doesn't line up with the surrounding code. This usually means tabs and spaces are mixed — pick one (4 spaces is standard).",
    ),
    (
        r"TabError",
        "Tabs and spaces are mixed in this file. Pick one (4 spaces is the Python convention) and use it everywhere.",
    ),
    # ModuleNotFoundError / ImportError
    (
        r"ModuleNotFoundError: No module named '([^']+)'",
        "Module '{0}' isn't installed. Check the spelling, or install it: `pip install {0}`",
    ),
    (
        r"ImportError: cannot import name '(\w+)' from",
        "'{0}' isn't available from that module. Check the spelling — Python is case-sensitive — or look at what the module actually exports.",
    ),
    # TypeError — common beginner forms
    (
        r"TypeError: '(\w+)' object is not callable",
        "Tried to call a '{0}' as if it were a function. You're using parentheses on something that isn't a function — check the variable name.",
    ),
    (
        r"TypeError: (\w+)\(\) missing (\d+) required positional argument",
        "Function '{0}' needs {1} more argument(s). Check the function signature.",
    ),
    (
        r"TypeError: (\w+)\(\) takes (\d+) positional arguments? but (\d+) were given",
        "Function '{0}' expects {1} argument(s) but you passed {2}. Check the parameter count.",
    ),
    (
        r"TypeError: unsupported operand type\(s\) for ([+\-*/%]+): '(\w+)' and '(\w+)'",
        "Can't use '{0}' between a {1} and a {2}. You may need to convert one — e.g. int(my_string) or str(my_number).",
    ),
    # AttributeError
    (
        r"AttributeError: '(\w+)' object has no attribute '(\w+)'",
        "'{1}' isn't a valid method or attribute of a {0}. Check spelling, or look up what {0} supports.",
    ),
    # Common runtime errors
    (
        r"ZeroDivisionError",
        "Tried to divide by zero. Add a check (e.g. `if denom != 0:`) before the division.",
    ),
    (
        r"IndexError: list index out of range",
        "Tried to access an item past the end of the list. Use len(my_list) to check the size first, or remember that indexing is 0-based.",
    ),
    (
        r"KeyError: '?(\w+)'?",
        "The key '{0}' doesn't exist in the dictionary. Use `my_dict.get('{0}')` for safer lookup, or check `if '{0}' in my_dict:` first.",
    ),
    (
        r"ValueError: invalid literal for int\(\) with base 10: '([^']*)'",
        "Couldn't convert '{0}' to an integer. The string must contain only digits (and an optional leading minus sign).",
    ),
]

_COMPILED_TRANSLATIONS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(pattern), template) for pattern, template in _TRANSLATIONS
]


def _humanize_error(message: str) -> str:
    """Translate common Python error patterns into beginner-friendly messages.

    Returns the original message if no translation matches. Safe to call on
    any string — non-error text passes through unchanged.
    """
    if not message:
        return message
    for pattern, template in _COMPILED_TRANSLATIONS:
        match = pattern.search(message)
        if match:
            try:
                return template.format(*match.groups())
            except (IndexError, KeyError):
                return template
    return message


def _extract_pytest_error(stdout: str, stderr: str) -> str:
    """Pull the most useful error line from pytest output for an unparseable run.

    Priority: E-lines (assertion / exception details) > short summary > last
    non-empty stderr line > generic fallback.
    """
    e_lines = [
        line.strip()[2:].strip()
        for line in stdout.splitlines()
        if line.strip().startswith("E ")
    ]
    if e_lines:
        return " | ".join(e_lines[:3])

    # Pytest short summary lines (FAILED / ERROR / collection errors)
    for line in stdout.splitlines():
        s = line.strip()
        if s.startswith(("FAILED", "ERROR", "INTERNALERROR")):
            return s

    stderr_tail = [line for line in stderr.splitlines() if line.strip()]
    if stderr_tail:
        return stderr_tail[-1].strip()

    return "Tests did not run. The submission may have a syntax error or pytest produced unexpected output."


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
            # Translate common Python errors into beginner-friendly hints
            message = _humanize_error(message)
            # Truncate very long messages
            if len(message) > 240:
                message = message[:237] + "..."

        items.append(
            TestResultItem(
                name=full_name,
                passed=status == "PASSED",
                message=message,
            )
        )

    return items
