# Getting Started

Go from zero to running the Learn AI With Grey8 platform on your machine in three steps.

---

## Prerequisites

Install the following tools before proceeding. Run the verification command for each to confirm it is installed correctly.

| Requirement | Minimum Version | Purpose | Verification |
|-------------|----------------|---------|--------------|
| **OS** | Windows 10+, macOS 12+, or Ubuntu 20.04+ | Host system | -- |
| **Git** | Any recent version | Clone repo, exercises in Phase 1 | `git --version` |
| **Python** | 3.11+ | Tutor engine, ACE framework, all exercises | `python --version` |
| **Node.js** | 20+ | Next.js web platform | `node --version` |
| **Ollama** | Latest | Local LLM inference for all AI features | `ollama --version` |
| **Docker Desktop** | With Docker Compose | Optional: full-stack workflow with Supabase | `docker compose version` |
| **Disk space** | ~10 GB free | Ollama models (~2 GB) + project dependencies | -- |
| **RAM** | 4 GB minimum (8 GB+ recommended) | Running LLM inference locally | -- |

> **Windows users:** Use **Git Bash** (installed with Git for Windows) or **WSL** for all commands in this guide. Do **not** use `cmd.exe` or PowerShell -- the scripts use Unix shell syntax.

### Installing Python 3.11+

- **Windows:** Download from [python.org](https://www.python.org/downloads/). **Check "Add Python to PATH"** during installation.
- **macOS:** `brew install python@3.11`
- **Linux:** `sudo apt update && sudo apt install python3.11 python3.11-venv`

Verify: `python --version` (should print 3.11 or higher). On some systems, use `python3 --version`.

### Installing Node.js 20+

We recommend [nvm](https://github.com/nvm-sh/nvm) (macOS/Linux) or [nvm-windows](https://github.com/coreybutler/nvm-windows) (Windows):

```bash
nvm install 20
nvm use 20
```

Verify: `node --version` (should print v20 or higher).

### Installing Docker (optional)

Docker is only needed if you want to run the full stack (including Supabase) in containers. You can learn without it.

- **Windows / macOS:** Install [Docker Desktop](https://www.docker.com/products/docker-desktop/). Launch it after installation and wait for it to finish starting.
- **Linux:** Follow the [official install guide](https://docs.docker.com/engine/install/)

Verify: `docker compose version`

### Installing Ollama

Ollama runs large language models locally on your machine.

- **Windows:** Download the installer from [ollama.com/download](https://ollama.com/download). After installing, Ollama runs in the system tray automatically.
- **macOS:** `brew install ollama`
- **Linux:** `curl -fsSL https://ollama.com/install.sh | sh`

Verify: `ollama --version`

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/user/learn-ai-with-grey8.git
cd learn-ai-with-grey8
```

## Step 2: Run the Setup Script

A single script installs everything you need:

```bash
bash scripts/setup.sh
```

**That's it.** The script handles all of the following automatically:

| What it does | Why you need it |
|-------------|-----------------|
| Checks all prerequisites are installed | Catches missing tools upfront with clear error messages |
| Creates a Python virtual environment (`.venv/`) | Keeps project dependencies isolated from your system Python |
| Installs the **Tutor Engine** (`tutor/`) | FastAPI backend that powers AI chat, exercise grading, and progressive hints |
| Installs the **ACE Framework** (`ace/`) | CLI tool that manages curriculum content — generates, validates, and syncs lessons |
| Installs the **Web Platform** (`platform/web/`) | Next.js frontend — the browser UI where you read lessons, write code, and interact with the tutor |
| Installs **Git hooks** | Auto-syncs the curriculum manifest when you commit or switch branches — you never need to update `manifest.json` manually |
| Creates your **`.env` config** from the template | Tells all services how to find each other on localhost (defaults work out of the box) |
| Pulls the **Ollama LLM model** | Downloads the AI model (~2 GB) that powers the tutor, grading, and all AI exercises |

> **Note:** If Ollama is not running when you run setup, the script will skip the model pull and tell you how to do it manually:
> ```bash
> ollama serve          # Start Ollama (skip on Windows if it's in the system tray)
> ollama pull llama3.2:3b
> ```

## Step 3: Start Learning

Launch all services with one command:

```bash
bash scripts/start.sh
```

This starts three services in the background:

| Service | Port | What it does |
|---------|------|-------------|
| **Ollama** | 11434 | Serves the local AI model for all LLM features |
| **Tutor API** | 8000 | FastAPI backend — handles chat, grading, and hints |
| **Web UI** | 3000 | Next.js frontend — the app you learn through |

Once you see "All services are running!", open **http://localhost:3000** in your browser.

Press **Ctrl+C** in the terminal to stop all services when you're done.

> **Docker alternative:** If you prefer running everything in containers (including Supabase), use this instead of `start.sh`:
> ```bash
> docker compose -f docker/docker-compose.yml up
> ```
> If you have an NVIDIA GPU, edit `docker/docker-compose.yml` and uncomment the `deploy` block under the `ollama` service to enable GPU acceleration.

---

## Verify Your Setup

If something doesn't look right, run the verification script:

```bash
bash local-dev/scripts/verify-setup.sh
```

Or check each service manually:

| Service | Health Check | Expected |
|---------|-------------|----------|
| Ollama | `ollama list` | Shows `llama3.2:3b` (or your model) |
| Tutor API | Open http://localhost:8000/health | `{"status": "ok"}` |
| Web UI | Open http://localhost:3000 | Dashboard page loads |

---

## Your Learning Path

1. Open **http://localhost:3000** in your browser
2. Click **Start Learning** or go to **Phases**
3. Open **Phase 1, Lesson 1: Terminal & Git Basics**
4. Read the lesson content
5. Click **Mark as Complete** when you finish reading
6. Click on the exercise
7. Write your solution in the code editor
8. Click **Submit** to get graded -- your submission is saved automatically
9. Use **Hints** if you are stuck (three levels of progressive help)
10. Open the **Tutor chat** for Socratic guidance -- chat history is preserved
11. Take the **Quiz** to test your understanding -- your best score is tracked

The curriculum is fully linear -- follow the lesson order from Phase 1 through Phase 12. Each lesson builds on the previous one. See the [Course Guide](course-guide.md) for the complete list of all 35 lessons and 15 projects.

> **Note:** Project 12 (Image Description Service) requires an additional model. Pull it when you reach that project: `ollama pull llava`

### Progress Tracking

Your progress is saved automatically as you learn:

| What | How it's saved | Persists across |
|------|---------------|-----------------|
| Lesson completion | Marked when you click "Mark as Complete" | Page refreshes, service restarts |
| Exercise submissions | Saved after every grading -- your code and score are kept | Page refreshes, service restarts |
| Quiz results | Best score is recorded | Page refreshes, service restarts |
| Tutor chat | Messages saved per lesson | Page refreshes, service restarts |

**Without an account**, your progress is stored in the browser's local storage. This means it persists across page refreshes and service restarts, but is tied to your browser.

**With an account** (optional, requires extra setup -- see [Enabling Sign-In](#enabling-sign-in-optional) below), your progress is stored in the Supabase database. This enables multi-device access, multi-user tracking (for teams/classrooms), and enterprise reporting. If you've been learning anonymously and then create an account, your existing progress is automatically migrated.

> **Tip:** Sign-in is **off by default**. The free single-user experience is complete without it -- the sign-in/create-account UI only appears once you enable Supabase. Skip the next section unless you actually need multi-device sync or team tracking.

---

## Enabling Sign-In (Optional)

Sign-in is **not required** to use the bootcamp. Anonymous local progress works for one learner on one browser. Enable sign-in only if you need:

- **Multi-device sync** -- continue your progress across laptop, desktop, etc.
- **Team / classroom tracking** -- multiple learners under one deployment
- **Migration of local progress** -- carry your existing anonymous progress into an account

### Steps

1. **Install the Supabase CLI** (one-time):
   - macOS: `brew install supabase/tap/supabase`
   - Windows: `scoop bucket add supabase https://github.com/supabase/scoop-bucket.git && scoop install supabase`
   - Linux: see [supabase.com/docs/guides/cli](https://supabase.com/docs/guides/cli/getting-started)

2. **Start the local Supabase stack** from the project root:
   ```bash
   supabase start
   ```
   First run downloads container images (~1 GB) and may take several minutes. The CLI prints API URL, anon key, and service role key when ready.

3. **Copy the printed values into your `.env`**:
   ```
   NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
   NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon key from supabase start output>
   SUPABASE_URL=http://localhost:54321
   SUPABASE_ANON_KEY=<same anon key>
   SUPABASE_SERVICE_KEY=<service role key from supabase start output>
   ```

4. **Restart the web app** so it picks up the new env vars:
   ```bash
   bash scripts/start.sh
   ```

5. **Open http://localhost:3000** -- the sidebar now shows **Sign in to sync** and **Create account** buttons. The home page shows a "Create an account" prompt for anonymous users.

To stop Supabase later: `supabase stop`. To reset its data: `supabase stop --no-backup && supabase start`.

> **Note:** The `docker/docker-compose.yml` file includes Postgres, GoTrue, and PostgREST containers, but these are a partial setup intended for advanced/CI use -- they don't expose the unified `localhost:54321` API gateway that the app expects. Use the Supabase CLI for local development.

---

## Environment Configuration

The setup script creates a `.env` file with sensible defaults. You only need to edit it if you want to change ports or add Supabase keys.

| Variable | Default | Service |
|----------|---------|---------|
| `TUTOR_OLLAMA_HOST` | `http://localhost:11434` | Tutor |
| `TUTOR_OLLAMA_MODEL` | `llama3.2:3b` (auto-configured by setup) | Tutor |
| `TUTOR_HOST` | `0.0.0.0` | Tutor |
| `TUTOR_PORT` | `8000` | Tutor |
| `TUTOR_CORS_ORIGINS` | `["http://localhost:3000"]` | Tutor |
| `NEXT_PUBLIC_TUTOR_URL` | `http://localhost:8000` | Web |
| `NEXT_PUBLIC_SUPABASE_URL` | `http://localhost:54321` | Web |
| `SUPABASE_URL` | `http://localhost:54321` | Tutor, Web |

> **Note:** All tutor engine variables use the `TUTOR_` prefix (required by pydantic-settings). The setup script auto-configures `TUTOR_OLLAMA_MODEL` to match the model installed on your machine.

---

## Using the Makefile (optional)

If you have `make` installed (standard on macOS/Linux; on Windows: `choco install make`), you can use these shortcuts:

```bash
make help              # List all available targets
make setup             # Same as scripts/setup.sh
make dev               # Start all services via Docker Compose
make dev-local         # Start all services locally
make test              # Run all tests (tutor + web + ace)
make lint              # Run all linters (ruff + eslint)
make docs              # Serve documentation at http://localhost:4000
```

These are convenience shortcuts -- the setup and start scripts work without `make`.

---

## Hardware Guide — Running on Low-End Machines

The setup script automatically detects your hardware and configures the AI model and inference parameters for the best experience. Here's what happens on different machines.

### Hardware Tiers

| RAM | GPU | Model Selected | Context Window | Expected Speed |
|-----|-----|---------------|---------------|---------------|
| **4 GB** | None | `llama3.2:1b` | 1024 tokens | ~20-35 tok/s |
| **6-8 GB** | None | `llama3.2:3b` | 2048 tokens | ~8-15 tok/s |
| **8-16 GB** | None or basic | `llama3.2:3b` | 4096 tokens | ~8-15 tok/s |
| **16+ GB** | None | `llama3.2:3b` | 8192 tokens | ~10-18 tok/s |
| **Any** | 8+ GB VRAM | `llama3.2:3b` | 4096 tokens | ~30-60 tok/s |
| **Any** | 12+ GB VRAM | `llama3.1:8b` | 4096 tokens | ~20-40 tok/s |

Speed depends heavily on CPU generation. Modern CPUs (2020+) with AVX2 support are 30-50% faster than older ones. Apple Silicon (M1/M2/M3) performs exceptionally well — expect 15-25 tok/s on 3B models even with 8GB unified memory.

### 4 GB RAM Survival Guide

Running a local LLM on 4 GB is tight but doable. Follow these tips:

1. **An SSD is required.** The model uses memory-mapped files (mmap) that page in and out. On an HDD, this makes inference unbearably slow.
2. **Close other apps.** A single Chrome tab uses 200-500 MB. Close tabs, VS Code extensions, and background apps before starting.
3. **Use native Ollama, not WSL2.** On Windows, WSL2 reserves half your RAM for its VM. Run Ollama natively on Windows instead.
4. **Ensure your page file is large enough.** Windows: System > Advanced > Performance > Virtual Memory — set to at least 8 GB on your SSD.
5. **The 1B model is your friend.** It's noticeably less capable for nuanced tutoring, but it runs comfortably and responds fast.

### Switching to a Different Model

If the auto-selected model is too slow or you want to try a different one:

```bash
# Pull and switch to the smaller 1B model
ollama pull llama3.2:1b

# Or try a code-specialized model for later phases
ollama pull qwen2.5-coder:3b
```

Then update your `.env` file:

```
TUTOR_OLLAMA_MODEL=llama3.2:1b
```

Restart the tutor service for the change to take effect.

### Alternative Models for Specific Use Cases

| Model | Size | Strength | When to Use |
|-------|------|----------|-------------|
| `llama3.2:3b` | ~2 GB | General tutoring | **Default for 8GB+ RAM** |
| `llama3.2:1b` | ~0.7 GB | Fast, lightweight | **4GB RAM fallback** |
| `qwen2.5-coder:3b` | ~1.9 GB | Better code quality | Phases 6+ if you want stronger code help |
| `phi3.5:3.8b` | ~2.2 GB | Strong reasoning | Alternative for conceptual phases |

### Manual Performance Tuning

The setup script writes optimal parameters to `.ollama_hw_profile`. If you want to override them, add these to your `.env`:

```bash
TUTOR_OLLAMA_NUM_CTX=2048     # Context window (lower = less RAM, shorter conversations)
TUTOR_OLLAMA_NUM_BATCH=256    # Prompt batch size (lower = less peak RAM)
TUTOR_OLLAMA_NUM_GPU=0        # Force CPU-only (set -1 for auto-detect)
```

### What's Coming: TurboQuant

Google's [TurboQuant](https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/) (ICLR 2026) compresses the KV cache to 3 bits with zero accuracy loss — a 6x memory reduction. Once it lands in Ollama (expected after the official llama.cpp integration), low-end machines could run much longer conversations. We'll update the platform to use it as soon as it's officially available.

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|---------|
| `make` command not found | `make` is not installed (common on Windows) | Not needed -- use `bash scripts/setup.sh` and `bash scripts/start.sh` instead |
| Setup script fails at prerequisites | Missing tool | Install the tool listed in the error, then re-run `bash scripts/setup.sh` |
| "Ollama not found" | Ollama not installed or not running | Install from [ollama.com/download](https://ollama.com/download), then run `ollama serve` |
| "Cannot connect to tutor" | Tutor not running on port 8000 | Re-run `bash scripts/start.sh`, or manually: `source .venv/bin/activate && cd tutor && uvicorn tutor.main:app --reload --port 8000` |
| "Model not found" | Model not pulled | Run `ollama pull llama3.2:3b` |
| Port conflicts | Another app on 3000, 8000, or 11434 | Stop the conflicting app, or change ports in `.env` |
| Windows: "bash not found" | Not using Git Bash or WSL | Open **Git Bash** (comes with Git for Windows) instead of cmd.exe or PowerShell |
| Docker won't start | Docker Desktop not running | Start Docker Desktop, wait for it to initialize, then retry |
| "Sign-in is not enabled" notice on /auth/login | Supabase not configured (this is by design) | See [Enabling Sign-In](#enabling-sign-in-optional) above. Anonymous local progress works without sign-in. |
| Supabase auth errors after enabling | Wrong anon key in `.env` | Re-run `supabase status` to print the current anon key, then update `.env` and restart `scripts/start.sh` |
| "CUDA out of memory" | GPU memory insufficient for model | Use CPU-only mode (default) or try a smaller model |
| AI tutor is very slow (<3 tok/s) | Low RAM or slow CPU | Switch to `llama3.2:1b` (see Hardware Guide above). Close other apps. Ensure SSD is used |
| High RAM usage / swapping | Model + context too large for RAM | Lower `TUTOR_OLLAMA_NUM_CTX` in `.env` (try 1024). Or switch to 1B model |
| `npm install` fails | Node version too old | Upgrade to Node.js 20+: `nvm install 20 && nvm use 20` |
| `python` not found | Python not in PATH | Reinstall Python and check "Add to PATH", or use `python3` instead |
