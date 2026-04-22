# Contributing

Thanks for your interest in Learn AI With Grey8! Here is how to get involved.

---

## Dev Environment Setup

Follow the **[Getting Started](getting-started.md)** guide to install all prerequisites, then:

```bash
bash scripts/setup.sh    # One-time setup
bash scripts/start.sh    # Start all services
```

---

## Monorepo Structure

| Directory | Language | Purpose |
|-----------|----------|---------|
| `curriculum/` | Markdown, JSON, Python | Lesson content, exercises, quizzes |
| `tutor/` | Python (FastAPI) | AI tutor engine (chat, grading, hints) |
| `platform/web/` | TypeScript (Next.js 14) | Web frontend |
| `platform/supabase/` | SQL | Database migrations |
| `ace/` | Python (Click CLI) | Autonomous Curriculum Engine |
| `docker/` | YAML, Dockerfile | Docker Compose and container configs |
| `projects/` | Python | 15 capstone project starters |
| `docs/` | Markdown | Documentation |

---

## Code Style

### Python (tutor/, ace/)

- **Linting:** [Ruff](https://docs.astral.sh/ruff/) -- `ruff check .`
- **Formatting:** [Black](https://black.readthedocs.io/) -- `black .`
- **Testing:** pytest (use `pytest-asyncio` for async tests in tutor)
- **Dependencies:** Defined in `pyproject.toml` (never create `requirements.txt`)
- **Install:** `pip install -e ".[dev]"` in each package directory

### TypeScript (platform/web/)

- **Linting:** ESLint with `eslint-config-next`
- **Testing:** Jest
- **Styling:** Tailwind CSS, dark-mode by default
- **Components:** `"use client"` directive required for stateful components

Run all checks:

```bash
# Lint
cd tutor && ruff check .
cd ace && ruff check .
cd platform/web && npm run lint

# Test
cd tutor && pytest
cd platform/web && npm test
cd ace && pytest
```

> **Tip:** If you have `make` installed, you can use `make lint` and `make test` as shortcuts.

---

## Adding Curriculum Content

### Lesson Structure

Every lesson lives under `curriculum/phase-NN-slug/lesson-NN-slug/` and requires these files:

```
lesson-NN-slug/
  content.md                          # Lesson text (~800-1000 words)
  quiz.json                           # 5 multiple-choice questions
  exercises/
    ex-01/
      starter/main.py                 # Starter code with TODOs
      solution/main.py                # Complete working solution
      tests/test_exercise.py          # pytest tests
      rubric.md                       # Grading criteria for AI evaluation
      hints.json                      # Array of exactly 3 progressive hints
```

### Content Guidelines

| File | Format | Key Rules |
|------|--------|-----------|
| `content.md` | Markdown | ~800-1000 words, clear examples, no jargon without explanation |
| `quiz.json` | JSON | 5 questions, 4 options each, zero-indexed correct answer |
| `starter/main.py` | Python | Clear TODO comments marking where students write code |
| `solution/main.py` | Python | Complete, working, well-commented solution |
| `tests/test_exercise.py` | pytest | Covers all TODO items, clear assertion messages |
| `rubric.md` | Markdown | Specific grading criteria for the AI evaluator |
| `hints.json` | JSON array | Exactly 3 strings: nudge, approach, near-solution |

### Workflow

1. Identify the correct phase directory under `curriculum/`
2. Create a new lesson folder following the naming convention: `lesson-NN-slug/`
3. Create all required files conforming to `curriculum/schema.json`
4. Run `ace sync` to update `manifest.json` (never edit it manually)
5. Validate your content: `ace curate --path curriculum/phase-NN-slug/`
6. Run tests: `cd tutor && pytest` (and `cd platform/web && npm test`)
7. Commit and open a PR

### Using ACE to Generate Content

The ACE framework can scaffold lessons from YAML specs:

```bash
# Create a spec file (see ace/specs/ for existing examples)
ace generate --spec specs/phase-NN.yml    # Generate draft content
ace curate --path curriculum/phase-NN/    # Validate and review quality
ace reflect --output reports/             # Analyze curriculum coverage
ace sync                                  # Update manifest.json
```

### Writing Exercise Tests

Exercise tests run through the tutor's grading sandbox. The sandbox writes the student's submission to `solution.py` in a temp dir and rewrites `SOLUTION_PATH` in the test file so tests import the student's code. Two conventions the sandbox requires — violating either causes every test in the file to fail:

**1. `SOLUTION_PATH` must be a multi-line `os.path.join(...)` ending with `)` on its own line.** The runner's regex rewriter only matches this shape:

```python
# Correct — closing paren on its own line
SOLUTION_PATH = os.path.join(
    os.path.dirname(__file__), "..", "solution", "main.py"
)

# WRONG — regex can't rewrite this, tests load the curriculum solution
# instead of the student's code
SOLUTION_PATH = os.path.join(os.path.dirname(__file__), "..", "solution", "main.py")
```

**2. Patch at the module level, not via `student_main.*`.** The helper loads the solution with `importlib.util.spec_from_file_location("student_main", ...)`, which does NOT register the module in `sys.modules`. Any patch referencing `student_main.X` will fail with `ModuleNotFoundError: No module named 'student_main'` and every test will fail. Patch the library directly instead:

```python
# Correct — patches the library globally, affects the student's imports too
with patch("httpx.post") as mock_post:
    ...

# WRONG — student_main isn't registered in sys.modules
with patch("student_main.httpx.post") as mock_post:
    ...
```

When the student uses `from X import Y` style (e.g. `from PyPDF2 import PdfReader`), `patch("X.Y")` won't reach the local binding. Either change the solution to use attribute-style access (`import PyPDF2; PyPDF2.PdfReader(...)`) or use `patch.object(mod, "Y")` inside the test.

**3. Match starter imports to what the tests patch.** If tests patch `httpx.post`, the starter must import `httpx` (not `requests`). The student fills in the TODOs; they shouldn't have to rewrite imports to make tests pass.

---

## Adding Platform Features

| What | Where | Notes |
|------|-------|-------|
| Pages | `platform/web/app/` | Next.js App Router conventions |
| Shared components | `platform/web/components/` | `"use client"` for stateful components |
| API proxy routes | `platform/web/app/api/` | Proxy to tutor engine, never call Ollama directly |
| Progress persistence | `platform/web/lib/progress/` | Use `useProgress()` hook, never access Supabase directly from pages |
| Database changes | `platform/supabase/migrations/` | Sequential numbered SQL files |
| Frontend env vars | `.env` | Must be prefixed with `NEXT_PUBLIC_` |

### Progress System

The platform has a dual-layer progress persistence system:

- **`lib/progress/types.ts`** -- defines the `ProgressBackend` interface
- **`lib/progress/local-backend.ts`** -- localStorage implementation (anonymous users)
- **`lib/progress/supabase-backend.ts`** -- Supabase implementation (signed-in users)
- **`components/ProgressProvider.tsx`** -- React context that auto-selects the right backend

**When adding pages that interact with progress:**

1. Import `useProgress` from `@/components/ProgressProvider`
2. Call `const { backend, refreshStats } = useProgress()`
3. Use `backend` methods to read/write progress data
4. Call `refreshStats()` after any write to update the dashboard
5. Never import Supabase directly -- the backend abstraction handles both storage modes

---

## Adding Tutor Features

1. Create a new router in `tutor/tutor/routers/`
2. Include the router in `tutor/tutor/main.py` via `app.include_router()`
3. Define request/response models in `tutor/tutor/models/schemas.py`
4. Add a corresponding proxy route in `platform/web/app/api/` if the frontend needs access
5. Write async tests with `pytest-asyncio`

---

## Pull Request Process

1. **Fork** the repository and create a feature branch: `git checkout -b feat/my-change`
2. Make your changes and add tests where applicable
3. Run the full test suite: `cd tutor && pytest` and `cd platform/web && npm test` and `cd ace && pytest`
4. Run linters: `cd tutor && ruff check .` and `cd platform/web && npm run lint`
5. Run `ace sync` if you changed curriculum files
6. Push your branch and open a **Pull Request** against `main`
7. Fill in the PR template -- describe what changed and why
8. A maintainer will review and merge

---

## Do NOT

- **Don't manually edit `curriculum/manifest.json`** -- run `ace sync` instead
- **Don't call Ollama from the Next.js frontend** -- proxy through `app/api/` routes
- **Don't hardcode lesson data in React components** -- load from the content API
- **Don't use `pip install -r requirements.txt`** -- use `pip install -e ".[dev]"`
- **Don't put secrets in `.env.example`** -- it is committed to git
- **Don't create `requirements.txt` files** -- dependencies are in `pyproject.toml`
- **Don't skip tests before committing** -- run tests and linters (see [Code Style](#code-style) section)
- **Don't access Supabase directly from page components** -- use the `useProgress()` hook
- **Don't require auth for `/learn/*` routes** -- anonymous users must be able to learn freely
- **Don't hardcode progress values** -- always read from the progress backend via `useProgress()`

---

## Reporting Issues

Open a GitHub Issue with:

- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots or logs (if applicable)
- OS and tool versions

---

## Code of Conduct

Be kind, be constructive, and help others learn. We are building this for learners worldwide.
