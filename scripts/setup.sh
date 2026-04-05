#!/usr/bin/env bash
# =============================================================================
# setup.sh — One-time setup for Learn AI With Grey8
# =============================================================================
# This script prepares your entire development environment in one go:
#
#   1. Checks prerequisites (Python 3.11+, Node.js 20+, Ollama, Git)
#   2. Creates a Python virtual environment
#   3. Installs the Tutor Engine (FastAPI backend for AI chat, grading, hints)
#   4. Installs the ACE Framework (CLI that manages curriculum content)
#   5. Installs the Web Platform (Next.js frontend you learn through)
#   6. Installs Git hooks (auto-syncs curriculum manifest on commits)
#   7. Creates your .env config file from the template
#   8. Pulls the Ollama LLM model (selected for your hardware)
#
# Usage:
#   bash scripts/setup.sh
#
# Works on macOS, Linux, and Git Bash on Windows.
# =============================================================================

# Guard: this script requires bash, not sh
if [ -z "${BASH_VERSION:-}" ]; then
    echo "ERROR: This script must be run with bash, not sh."
    echo ""
    echo "  Run it like this:  bash scripts/setup.sh"
    echo ""
    exit 1
fi

set -euo pipefail

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

info()    { echo -e "${GREEN}[✓]${NC} $*"; }
warn()    { echo -e "${YELLOW}[!]${NC} $*"; }
error()   { echo -e "${RED}[✗]${NC} $*"; }
section() { echo -e "\n${BLUE}${BOLD}── $* ──${NC}"; }

# Ensure we run from the project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo ""
echo "============================================="
echo "  Learn AI With Grey8 — Setup"
echo "============================================="
echo ""

# ---------------------------------------------------------------------------
# Step 1: Check prerequisites
# ---------------------------------------------------------------------------
section "Step 1/8: Checking prerequisites"

ERRORS=0

# Detect OS (Windows Git Bash needs special handling)
IS_WINDOWS=false
case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*) IS_WINDOWS=true ;;
esac

# Python
# On Windows, check 'python' first — 'python3' can trigger the Microsoft Store alias and hang.
PYTHON_CMD=""
if [[ "$IS_WINDOWS" == true ]]; then
    if command -v python &>/dev/null && python --version &>/dev/null 2>&1; then
        PYTHON_CMD="python"
    fi
else
    if command -v python3 &>/dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &>/dev/null; then
        PYTHON_CMD="python"
    fi
fi

if [[ -n "$PYTHON_CMD" ]]; then
    PY_VERSION=$($PYTHON_CMD --version 2>&1)
    PY_VERSION="${PY_VERSION#Python }"           # strip "Python " prefix
    PY_MAJOR="${PY_VERSION%%.*}"                  # e.g. "3"
    PY_REST="${PY_VERSION#*.}"                    # e.g. "11.9"
    PY_MINOR="${PY_REST%%.*}"                     # e.g. "11"
    if [[ "$PY_MAJOR" -ge 3 ]] 2>/dev/null && [[ "$PY_MINOR" -ge 11 ]] 2>/dev/null; then
        info "Python $PY_VERSION ($PYTHON_CMD)"
    else
        error "Python $PY_VERSION found, but 3.11+ is required"
        ERRORS=$((ERRORS + 1))
    fi
else
    error "Python not found. Install Python 3.11+ and add it to PATH."
    ERRORS=$((ERRORS + 1))
fi

# Node.js
if command -v node &>/dev/null; then
    NODE_RAW=$(node --version 2>&1)
    NODE_VERSION="${NODE_RAW#v}"                   # strip leading "v"
    NODE_MAJOR="${NODE_VERSION%%.*}"               # e.g. "20"
    if [[ "$NODE_MAJOR" -ge 20 ]] 2>/dev/null; then
        info "Node.js v$NODE_VERSION"
    else
        error "Node.js v$NODE_VERSION found, but v20+ is required"
        ERRORS=$((ERRORS + 1))
    fi
else
    error "Node.js not found. Install Node.js 20+ (https://nodejs.org)"
    ERRORS=$((ERRORS + 1))
fi

# Git
if command -v git &>/dev/null; then
    GIT_RAW=$(git --version 2>&1)
    GIT_VERSION="${GIT_RAW##* }"                   # last word, e.g. "2.43.0" or "2.43.0.windows.1"
    info "Git $GIT_VERSION"
else
    error "Git not found."
    ERRORS=$((ERRORS + 1))
fi

# Ollama
if command -v ollama &>/dev/null; then
    info "Ollama installed"
else
    error "Ollama not found. Install from https://ollama.com/download"
    ERRORS=$((ERRORS + 1))
fi

if [[ $ERRORS -gt 0 ]]; then
    echo ""
    error "Missing $ERRORS prerequisite(s). Install them and re-run this script."
    echo "  See docs/getting-started.md for installation instructions."
    exit 1
fi

info "All prerequisites found."

# ---------------------------------------------------------------------------
# Step 2: Create Python virtual environment
# ---------------------------------------------------------------------------
section "Step 2/8: Creating Python virtual environment"

if [[ -d ".venv" ]]; then
    info "Virtual environment already exists (.venv/)"
else
    $PYTHON_CMD -m venv .venv
    info "Created virtual environment (.venv/)"
fi

# Activate the virtual environment
# shellcheck disable=SC1091
if [[ -f ".venv/Scripts/activate" ]]; then
    source .venv/Scripts/activate
elif [[ -f ".venv/bin/activate" ]]; then
    source .venv/bin/activate
else
    error "Could not find venv activation script."
    exit 1
fi
info "Virtual environment activated"

# ---------------------------------------------------------------------------
# Step 3: Install the Tutor Engine
# ---------------------------------------------------------------------------
section "Step 3/8: Installing Tutor Engine (FastAPI backend — powers AI chat, grading, hints)"

cd "$PROJECT_ROOT/tutor"
pip install -e ".[dev]" --quiet
info "Tutor engine installed"
cd "$PROJECT_ROOT"

# ---------------------------------------------------------------------------
# Step 4: Install the ACE Framework
# ---------------------------------------------------------------------------
section "Step 4/8: Installing ACE Framework (CLI that manages curriculum content)"

cd "$PROJECT_ROOT/ace"
pip install -e ".[dev]" --quiet
info "ACE framework installed"
cd "$PROJECT_ROOT"

# ---------------------------------------------------------------------------
# Step 5: Install the Web Platform
# ---------------------------------------------------------------------------
section "Step 5/8: Installing Web Platform (Next.js frontend — the UI you learn through)"

cd "$PROJECT_ROOT/platform/web"
npm install --silent 2>/dev/null || npm install
info "Web platform installed"
cd "$PROJECT_ROOT"

# ---------------------------------------------------------------------------
# Step 6: Install Git hooks
# ---------------------------------------------------------------------------
section "Step 6/8: Installing Git hooks (auto-syncs curriculum manifest on commits)"

bash scripts/setup-hooks.sh
info "Git hooks installed"

# ---------------------------------------------------------------------------
# Step 7: Create .env file
# ---------------------------------------------------------------------------
section "Step 7/8: Configuring environment"

if [[ -f ".env" ]]; then
    info ".env already exists (not overwritten)"
else
    cp .env.example .env
    info "Created .env from template (defaults work for local development)"
fi

# ---------------------------------------------------------------------------
# Step 8: Pull Ollama model
# ---------------------------------------------------------------------------
section "Step 8/8: Setting up Ollama model"

SELECTED_MODEL=""

# Check if Ollama is running
if curl -sf http://localhost:11434/api/tags &>/dev/null; then
    info "Ollama server is running"

    # Run the hardware-aware setup script (detects GPU/VRAM, pulls the right model)
    info "Detecting hardware and selecting best model..."
    bash "$PROJECT_ROOT/local-dev/scripts/setup-ollama.sh"

    # Read the model that setup-ollama.sh selected
    if [[ -f "$PROJECT_ROOT/.ollama_model" ]]; then
        SELECTED_MODEL=$(cat "$PROJECT_ROOT/.ollama_model" | tr -d '[:space:]')
        info "Hardware-selected model: $SELECTED_MODEL"
    fi
else
    warn "Ollama server is not running."
    echo "      Start Ollama first, then re-run this script:"
    echo ""
    echo "        ollama serve          # In a separate terminal (skip on Windows if in system tray)"
    echo "        bash scripts/setup.sh"
    echo ""
fi

# Update .env with the selected model so the tutor engine uses the right one
# The tutor reads TUTOR_OLLAMA_MODEL (pydantic-settings uses TUTOR_ prefix)
if [[ -n "$SELECTED_MODEL" && -f ".env" ]]; then
    CURRENT_MODEL=$(grep '^TUTOR_OLLAMA_MODEL=' .env | cut -d= -f2)
    if [[ "$CURRENT_MODEL" != "$SELECTED_MODEL" ]]; then
        # Use temp file for sed (portable across macOS/Linux/Windows Git Bash)
        sed "s|^TUTOR_OLLAMA_MODEL=.*|TUTOR_OLLAMA_MODEL=$SELECTED_MODEL|" .env > .env.tmp && mv .env.tmp .env
        info "Updated .env: TUTOR_OLLAMA_MODEL=$SELECTED_MODEL (was ${CURRENT_MODEL:-not set})"
    else
        info ".env already has TUTOR_OLLAMA_MODEL=$SELECTED_MODEL"
    fi
fi

# ---------------------------------------------------------------------------
# Step 9: Generate curriculum index for AI tutor context
# ---------------------------------------------------------------------------
section "Step 9: Generating curriculum index for AI tutor"

cd "$PROJECT_ROOT"
python scripts/generate_curriculum_index.py
info "Curriculum index generated — tutor will have cross-lesson awareness"

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
echo "============================================="
echo -e "  ${GREEN}${BOLD}Setup Complete!${NC}"
echo "============================================="
echo ""
echo "  To start learning, run:"
echo ""
echo "    bash scripts/start.sh"
echo ""
echo "  Then open http://localhost:3000 in your browser."
echo ""
echo "============================================="
echo ""
