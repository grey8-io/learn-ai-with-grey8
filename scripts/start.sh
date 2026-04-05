#!/usr/bin/env bash
# =============================================================================
# start.sh — Start all Learn AI With Grey8 services
# =============================================================================
# Launches three services needed to run the platform:
#
#   1. Ollama    — Local LLM runtime (serves the AI model)
#   2. Tutor API — FastAPI backend (chat, grading, hints via Ollama)
#   3. Web UI    — Next.js frontend (the browser app you learn through)
#
# Press Ctrl+C to stop everything cleanly.
# Re-running this script always starts fresh (kills old processes first).
#
# Usage:
#   bash scripts/start.sh
#
# Works on macOS, Linux, and Git Bash on Windows.
# =============================================================================

# Guard: this script requires bash, not sh
if [ -z "${BASH_VERSION:-}" ]; then
    echo "ERROR: This script must be run with bash, not sh."
    echo ""
    echo "  Run it like this:  bash scripts/start.sh"
    echo ""
    exit 1
fi

set -uo pipefail

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

# Ensure we run from the project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# PID file to track processes we start
PID_FILE="$PROJECT_ROOT/.running_pids"
LOG_DIR="$PROJECT_ROOT/.logs"
mkdir -p "$LOG_DIR"

# Detect OS
IS_WINDOWS=false
case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*) IS_WINDOWS=true ;;
esac

# ---------------------------------------------------------------------------
# Port management: kill any process on a given port
# ---------------------------------------------------------------------------
kill_port() {
    local port=$1
    local label=${2:-"process"}

    if [[ "$IS_WINDOWS" == true ]]; then
        # Windows: use netstat + taskkill
        local pid
        pid=$(netstat -ano 2>/dev/null | grep ":${port} " | grep 'LISTENING' | awk '{print $NF}' | head -1 | tr -d '[:space:]')
        if [[ -n "$pid" && "$pid" != "0" ]]; then
            taskkill //PID "$pid" //F &>/dev/null 2>&1 || true
            return 0
        fi
    else
        # macOS/Linux: use lsof
        if command -v lsof &>/dev/null; then
            local pids
            pids=$(lsof -ti:"$port" 2>/dev/null || true)
            if [[ -n "$pids" ]]; then
                echo "$pids" | xargs kill 2>/dev/null || true
                return 0
            fi
        fi
    fi
    return 1
}

# ---------------------------------------------------------------------------
# Cleanup: stop all services on Ctrl+C or exit
# ---------------------------------------------------------------------------
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"

    # Kill processes by PID file
    if [[ -f "$PID_FILE" ]]; then
        while read -r pid; do
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid" 2>/dev/null || true
            fi
        done < "$PID_FILE"
        rm -f "$PID_FILE"
    fi

    # Also kill by port as a safety net
    kill_port 8000 "Tutor API" 2>/dev/null || true
    kill_port 3000 "Web UI" 2>/dev/null || true

    sleep 1
    echo -e "${GREEN}All services stopped.${NC}"
    exit 0
}

trap cleanup INT TERM EXIT

# ---------------------------------------------------------------------------
# Clean slate: kill any stale processes from a previous run
# ---------------------------------------------------------------------------
echo ""
echo "============================================="
echo "  Learn AI With Grey8 — Starting Services"
echo "============================================="

# Kill leftover processes from previous runs
STALE=false
if curl -sf http://localhost:8000/health &>/dev/null; then
    kill_port 8000 "Tutor API" && STALE=true
fi
if curl -sf -o /dev/null http://localhost:3000 2>/dev/null; then
    kill_port 3000 "Web UI" && STALE=true
fi
if [[ "$STALE" == true ]]; then
    echo ""
    warn "Stopped stale services from a previous session."
    sleep 2  # give ports time to free up
fi

# Clean old PID file
rm -f "$PID_FILE"

# ---------------------------------------------------------------------------
# Activate virtual environment
# ---------------------------------------------------------------------------
if [[ -d ".venv" ]]; then
    # shellcheck disable=SC1091
    if [[ -f ".venv/Scripts/activate" ]]; then
        source .venv/Scripts/activate
    elif [[ -f ".venv/bin/activate" ]]; then
        source .venv/bin/activate
    fi
else
    error "Virtual environment not found. Run setup first: bash scripts/setup.sh"
    exit 1
fi

# ---------------------------------------------------------------------------
# Service 1: Ollama
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}${BOLD}[1/3] Ollama (LLM runtime on port 11434)${NC}"

if curl -sf http://localhost:11434/api/tags &>/dev/null; then
    info "Ollama is already running"
else
    if command -v ollama &>/dev/null; then
        warn "Ollama is not running. Attempting to start..."
        ollama serve &>/dev/null &
        OLLAMA_PID=$!
        echo "$OLLAMA_PID" >> "$PID_FILE"

        # Wait up to 10 seconds for Ollama
        for i in {1..10}; do
            if curl -sf http://localhost:11434/api/tags &>/dev/null; then
                info "Ollama started"
                break
            fi
            if [[ $i -eq 10 ]]; then
                warn "Could not start Ollama automatically."
                if [[ "$IS_WINDOWS" == true ]]; then
                    echo "      Check that Ollama is running in the system tray."
                else
                    echo "      Run 'ollama serve' in a separate terminal."
                fi
            fi
            sleep 1
        done
    else
        error "Ollama is not installed. Install from https://ollama.com/download"
    fi
fi

# Verify model is available
if curl -sf http://localhost:11434/api/tags &>/dev/null; then
    MODEL_COUNT=$(curl -sf http://localhost:11434/api/tags | grep -o '"name"' | wc -l | tr -d ' ')
    if [[ "$MODEL_COUNT" -eq 0 ]]; then
        warn "No models found. Run: bash scripts/setup.sh"
    else
        info "$MODEL_COUNT model(s) available"
    fi
fi

# ---------------------------------------------------------------------------
# Service 2: Tutor API
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}${BOLD}[2/3] Tutor API (FastAPI on port 8000)${NC}"

cd "$PROJECT_ROOT/tutor"
uvicorn tutor.main:app --reload --host 0.0.0.0 --port 8000 > "$LOG_DIR/tutor.log" 2>&1 &
TUTOR_PID=$!
echo "$TUTOR_PID" >> "$PID_FILE"
cd "$PROJECT_ROOT"

for i in {1..15}; do
    if curl -sf http://localhost:8000/health &>/dev/null; then
        # Show which model the tutor is using
        TUTOR_MODEL=$(curl -sf http://localhost:8000/health | grep -o '"model":"[^"]*"' | cut -d'"' -f4)
        info "Tutor API started (model: ${TUTOR_MODEL:-unknown})"
        break
    fi
    # Check if the process crashed
    if ! kill -0 "$TUTOR_PID" 2>/dev/null; then
        error "Tutor API crashed on startup. Last 20 lines of log:"
        echo ""
        tail -20 "$LOG_DIR/tutor.log" 2>/dev/null
        echo ""
        break
    fi
    if [[ $i -eq 15 ]]; then
        warn "Tutor API is taking longer than expected to start."
        echo "      Check logs: cat .logs/tutor.log"
    fi
    sleep 1
done

# ---------------------------------------------------------------------------
# Service 3: Web UI
# ---------------------------------------------------------------------------
echo ""
echo -e "${BLUE}${BOLD}[3/3] Web UI (Next.js on port 3000)${NC}"

cd "$PROJECT_ROOT/platform/web"
npm run dev > "$LOG_DIR/web.log" 2>&1 &
WEB_PID=$!
echo "$WEB_PID" >> "$PID_FILE"
cd "$PROJECT_ROOT"

for i in {1..30}; do
    if curl -sf -o /dev/null http://localhost:3000 2>/dev/null; then
        info "Web UI started"
        break
    fi
    # Check if the process crashed
    if ! kill -0 "$WEB_PID" 2>/dev/null; then
        error "Web UI crashed on startup. Last 20 lines of log:"
        echo ""
        tail -20 "$LOG_DIR/web.log" 2>/dev/null
        echo ""
        break
    fi
    if [[ $i -eq 30 ]]; then
        warn "Web UI is taking longer than expected to start."
        echo "      Check logs: cat .logs/web.log"
    fi
    sleep 1
done

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "============================================="
echo -e "  ${GREEN}${BOLD}All services are running!${NC}"
echo "============================================="
echo ""
echo "  Open in your browser:"
echo ""
echo "    http://localhost:3000        Web UI (start learning here)"
echo "    http://localhost:8000/health  Tutor API health check"
echo ""
echo "  Press Ctrl+C to stop all services."
echo "============================================="
echo ""

# Keep the script alive, waiting for Ctrl+C
wait
