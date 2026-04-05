#!/usr/bin/env bash
# =============================================================================
# verify-setup.sh — Pre-flight checks for the Learn AI With Grey8 dev environment
# =============================================================================
# Checks all prerequisites and prints a pass/fail checklist.
#
# Usage:
#   chmod +x local-dev/scripts/verify-setup.sh
#   ./local-dev/scripts/verify-setup.sh
# =============================================================================

set -uo pipefail

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
PASS='\033[0;32m[PASS]\033[0m'
FAIL='\033[0;31m[FAIL]\033[0m'
WARN='\033[1;33m[WARN]\033[0m'
NC='\033[0m'

TOTAL=0
PASSED=0
FAILED=0

check() {
    local label="$1"
    local result="$2"  # 0 = pass, 1 = fail, 2 = warn
    local detail="${3:-}"

    TOTAL=$((TOTAL + 1))
    if [[ "$result" -eq 0 ]]; then
        PASSED=$((PASSED + 1))
        echo -e "  $PASS  $label  $detail"
    elif [[ "$result" -eq 2 ]]; then
        echo -e "  $WARN  $label  $detail"
    else
        FAILED=$((FAILED + 1))
        echo -e "  $FAIL  $label  $detail"
    fi
}

# Require minimum version: returns 0 if $1 >= $2 (numeric comparison)
version_gte() {
    local have="$1"
    local need="$2"
    # Compare major version numbers
    local have_major="${have%%.*}"
    local need_major="${need%%.*}"
    [[ "$have_major" -ge "$need_major" ]]
}

echo ""
echo "============================================="
echo "  Learn AI With Grey8 — Setup Verification"
echo "============================================="
echo ""

# ---------------------------------------------------------------------------
# 1. Python 3.11+
# ---------------------------------------------------------------------------
if command -v python3 &>/dev/null; then
    PY_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
    PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
    if [[ "$PY_MAJOR" -ge 3 && "$PY_MINOR" -ge 11 ]]; then
        check "Python 3.11+" 0 "(found $PY_VERSION)"
    else
        check "Python 3.11+" 1 "(found $PY_VERSION, need >= 3.11)"
    fi
elif command -v python &>/dev/null; then
    PY_VERSION=$(python --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
    PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
    if [[ "$PY_MAJOR" -ge 3 && "$PY_MINOR" -ge 11 ]]; then
        check "Python 3.11+" 0 "(found $PY_VERSION via 'python')"
    else
        check "Python 3.11+" 1 "(found $PY_VERSION, need >= 3.11)"
    fi
else
    check "Python 3.11+" 1 "(not found)"
fi

# ---------------------------------------------------------------------------
# 2. Node.js 20+
# ---------------------------------------------------------------------------
if command -v node &>/dev/null; then
    NODE_VERSION=$(node --version 2>&1 | sed 's/^v//' | cut -d. -f1)
    if [[ "$NODE_VERSION" -ge 20 ]]; then
        check "Node.js 20+" 0 "(found v$NODE_VERSION)"
    else
        check "Node.js 20+" 1 "(found v$NODE_VERSION, need >= 20)"
    fi
else
    check "Node.js 20+" 1 "(not found)"
fi

# ---------------------------------------------------------------------------
# 3. Docker installed and running
# ---------------------------------------------------------------------------
if command -v docker &>/dev/null; then
    DOCKER_VERSION=$(docker --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
    if docker info &>/dev/null; then
        check "Docker (installed & running)" 0 "(v$DOCKER_VERSION)"
    else
        check "Docker (installed & running)" 1 "(installed v$DOCKER_VERSION but daemon not running)"
    fi
else
    check "Docker (installed & running)" 1 "(not found)"
fi

# ---------------------------------------------------------------------------
# 4. Docker Compose
# ---------------------------------------------------------------------------
if docker compose version &>/dev/null 2>&1; then
    COMPOSE_VERSION=$(docker compose version --short 2>/dev/null || echo "unknown")
    check "Docker Compose" 0 "(v$COMPOSE_VERSION)"
elif command -v docker-compose &>/dev/null; then
    COMPOSE_VERSION=$(docker-compose --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
    check "Docker Compose" 0 "(legacy v$COMPOSE_VERSION)"
else
    check "Docker Compose" 1 "(not found)"
fi

# ---------------------------------------------------------------------------
# 5. Ollama installed
# ---------------------------------------------------------------------------
if command -v ollama &>/dev/null; then
    OLLAMA_VERSION=$(ollama --version 2>/dev/null || echo "unknown")
    check "Ollama installed" 0 "($OLLAMA_VERSION)"
else
    check "Ollama installed" 1 "(not found — see local-dev/scripts/setup-ollama.sh)"
fi

# ---------------------------------------------------------------------------
# 6. Ollama server running and model pulled
# ---------------------------------------------------------------------------
if curl -sf http://localhost:11434/api/tags &>/dev/null; then
    MODEL_COUNT=$(curl -sf http://localhost:11434/api/tags | grep -o '"name"' | wc -l)
    if [[ "$MODEL_COUNT" -gt 0 ]]; then
        check "Ollama model(s) pulled" 0 "($MODEL_COUNT model(s) available)"
    else
        check "Ollama model(s) pulled" 1 "(server running but no models pulled)"
    fi
else
    check "Ollama model(s) pulled" 1 "(server not reachable at localhost:11434)"
fi

# ---------------------------------------------------------------------------
# 7. Supabase CLI (optional)
# ---------------------------------------------------------------------------
if command -v supabase &>/dev/null; then
    SB_VERSION=$(supabase --version 2>/dev/null || echo "unknown")
    check "Supabase CLI (optional)" 0 "($SB_VERSION)"
else
    check "Supabase CLI (optional)" 2 "(not installed — optional, Docker handles it)"
fi

# ---------------------------------------------------------------------------
# 8. Git
# ---------------------------------------------------------------------------
if command -v git &>/dev/null; then
    GIT_VERSION=$(git --version 2>&1 | grep -oP '\d+\.\d+\.\d+' | head -1)
    check "Git" 0 "(v$GIT_VERSION)"
else
    check "Git" 1 "(not found)"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "============================================="
echo "  Results: $PASSED/$TOTAL passed, $FAILED failed"
echo "============================================="
echo ""

if [[ $FAILED -gt 0 ]]; then
    echo "Some checks failed. Please install the missing prerequisites."
    echo "See docs/getting-started.md for detailed instructions."
    exit 1
else
    echo "All checks passed. You are ready to start developing."
    echo ""
    echo "Next steps:"
    echo "  1. bash scripts/setup.sh    (one-time setup)"
    echo "  2. bash scripts/start.sh    (start all services)"
    echo "  3. Open http://localhost:3000"
    echo ""
fi
