#!/usr/bin/env bash
# =============================================================================
# setup-ollama.sh — Install and configure Ollama for Learn AI With Grey8
# =============================================================================
# Works on Linux, macOS, and Git Bash on Windows.
#
# Usage:
#   chmod +x local-dev/scripts/setup-ollama.sh
#   ./local-dev/scripts/setup-ollama.sh
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; }

# ---------------------------------------------------------------------------
# Detect OS
# ---------------------------------------------------------------------------
detect_os() {
    case "$(uname -s)" in
        Linux*)   OS="linux" ;;
        Darwin*)  OS="macos" ;;
        MINGW*|MSYS*|CYGWIN*) OS="windows" ;;
        *)        OS="unknown" ;;
    esac
    echo "$OS"
}

OS=$(detect_os)
info "Detected OS: $OS"

# ---------------------------------------------------------------------------
# Step 1: Check if Ollama is installed
# ---------------------------------------------------------------------------
if ! command -v ollama &>/dev/null; then
    error "Ollama is not installed."
    echo ""
    echo "Install Ollama for your platform:"
    echo ""
    case "$OS" in
        linux)
            echo "  curl -fsSL https://ollama.com/install.sh | sh"
            ;;
        macos)
            echo "  brew install ollama"
            echo "  # or download from https://ollama.com/download"
            ;;
        windows)
            echo "  Download the installer from https://ollama.com/download/windows"
            echo "  After installing, restart your terminal."
            ;;
        *)
            echo "  Visit https://ollama.com/download for installation instructions."
            ;;
    esac
    echo ""
    exit 1
fi

info "Ollama is installed: $(ollama --version 2>/dev/null || echo 'version unknown')"

# ---------------------------------------------------------------------------
# Step 2: Ensure Ollama is running
# ---------------------------------------------------------------------------
if ! curl -sf http://localhost:11434/api/tags &>/dev/null; then
    warn "Ollama server is not running. Attempting to start it..."
    case "$OS" in
        linux|macos)
            ollama serve &>/dev/null &
            sleep 3
            ;;
        windows)
            warn "On Windows, please start Ollama from the system tray or run 'ollama serve' in another terminal."
            echo "Waiting 10 seconds for you to start it..."
            sleep 10
            ;;
    esac

    if ! curl -sf http://localhost:11434/api/tags &>/dev/null; then
        error "Could not connect to Ollama at http://localhost:11434"
        error "Please start Ollama manually and re-run this script."
        exit 1
    fi
fi

info "Ollama server is running."

# ---------------------------------------------------------------------------
# Step 3: Detect GPU and available VRAM
# ---------------------------------------------------------------------------
VRAM_GB=0
GPU_NAME="none"

if command -v nvidia-smi &>/dev/null; then
    # Parse total VRAM from nvidia-smi (in MiB), convert to GB
    VRAM_MIB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
    if [[ -n "$VRAM_MIB" && "$VRAM_MIB" =~ ^[0-9]+$ ]]; then
        VRAM_GB=$((VRAM_MIB / 1024))
        GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
        info "NVIDIA GPU detected: $GPU_NAME ($VRAM_GB GB VRAM)"
    fi
else
    warn "nvidia-smi not found. Assuming CPU-only or non-NVIDIA GPU."
    warn "If you have an NVIDIA GPU, install the NVIDIA drivers first."
fi

# ---------------------------------------------------------------------------
# Step 3b: Detect system RAM
# ---------------------------------------------------------------------------
RAM_GB=0

case "$OS" in
    linux)
        RAM_KB=$(grep MemTotal /proc/meminfo 2>/dev/null | awk '{print $2}')
        if [[ -n "$RAM_KB" && "$RAM_KB" =~ ^[0-9]+$ ]]; then
            RAM_GB=$((RAM_KB / 1024 / 1024))
        fi
        ;;
    macos)
        RAM_BYTES=$(sysctl -n hw.memsize 2>/dev/null)
        if [[ -n "$RAM_BYTES" && "$RAM_BYTES" =~ ^[0-9]+$ ]]; then
            RAM_GB=$((RAM_BYTES / 1024 / 1024 / 1024))
        fi
        ;;
    windows)
        # Git Bash / MSYS: parse from systeminfo or wmic
        RAM_KB=$(wmic ComputerSystem get TotalPhysicalMemory 2>/dev/null | grep -o '[0-9]*')
        if [[ -n "$RAM_KB" && "$RAM_KB" =~ ^[0-9]+$ ]]; then
            RAM_GB=$((RAM_KB / 1024 / 1024 / 1024))
        fi
        ;;
esac

if [[ $RAM_GB -gt 0 ]]; then
    info "System RAM detected: ${RAM_GB} GB"
else
    warn "Could not detect system RAM. Assuming 8 GB."
    RAM_GB=8
fi

# ---------------------------------------------------------------------------
# Step 3c: Determine hardware profile (RAM-based Ollama tuning)
# ---------------------------------------------------------------------------
# These values are written to .ollama_hw_profile so the tutor engine
# can send optimal options (num_ctx, num_batch, num_gpu) with each request.

if [[ $RAM_GB -le 4 ]]; then
    HW_TIER="low"
    OPT_NUM_CTX=1024
    OPT_NUM_BATCH=128
    OPT_NUM_GPU=0
    info "Hardware tier: LOW (${RAM_GB}GB RAM) — num_ctx=$OPT_NUM_CTX, num_batch=$OPT_NUM_BATCH, num_gpu=$OPT_NUM_GPU"
elif [[ $RAM_GB -le 8 ]]; then
    HW_TIER="medium"
    OPT_NUM_CTX=2048
    OPT_NUM_BATCH=256
    OPT_NUM_GPU=0   # safe default; GPU users with 4GB+ VRAM can override
    info "Hardware tier: MEDIUM (${RAM_GB}GB RAM) — num_ctx=$OPT_NUM_CTX, num_batch=$OPT_NUM_BATCH"
elif [[ $RAM_GB -le 16 ]]; then
    HW_TIER="high"
    OPT_NUM_CTX=4096
    OPT_NUM_BATCH=512
    OPT_NUM_GPU=-1   # auto-detect (let Ollama decide)
    info "Hardware tier: HIGH (${RAM_GB}GB RAM) — num_ctx=$OPT_NUM_CTX, num_batch=$OPT_NUM_BATCH"
else
    HW_TIER="ultra"
    OPT_NUM_CTX=8192
    OPT_NUM_BATCH=512
    OPT_NUM_GPU=-1
    info "Hardware tier: ULTRA (${RAM_GB}GB RAM) — num_ctx=$OPT_NUM_CTX, num_batch=$OPT_NUM_BATCH"
fi

# ---------------------------------------------------------------------------
# Step 4: Select model based on VRAM and system RAM
# ---------------------------------------------------------------------------
# GPU-capable machines use VRAM for selection; CPU-only machines use RAM.
if [[ $VRAM_GB -ge 16 ]]; then
    MODEL="llama3.1:8b"
    info "16+ GB VRAM detected — selecting $MODEL"
elif [[ $VRAM_GB -ge 12 ]]; then
    MODEL="llama3.1:8b"
    info "12-16 GB VRAM detected — selecting $MODEL"
elif [[ $VRAM_GB -ge 8 ]]; then
    MODEL="llama3.2:3b"
    info "8-12 GB VRAM detected — selecting $MODEL"
elif [[ $VRAM_GB -gt 0 ]]; then
    MODEL="llama3.2:1b"
    info "<8 GB VRAM detected — selecting $MODEL"
else
    # CPU-only: use system RAM to pick the model
    if [[ $RAM_GB -ge 16 ]]; then
        MODEL="llama3.2:3b"
        info "No GPU, 16+ GB RAM — selecting $MODEL (CPU mode)"
    elif [[ $RAM_GB -ge 8 ]]; then
        MODEL="llama3.2:3b"
        info "No GPU, 8+ GB RAM — selecting $MODEL (CPU mode)"
    elif [[ $RAM_GB -ge 6 ]]; then
        MODEL="llama3.2:3b"
        info "No GPU, 6+ GB RAM — selecting $MODEL (CPU mode, may be tight)"
    else
        MODEL="llama3.2:1b"
        info "No GPU, <6 GB RAM — selecting $MODEL (CPU mode, lightweight)"
    fi
fi

# ---------------------------------------------------------------------------
# Step 5: Pull the model
# ---------------------------------------------------------------------------
info "Pulling model: $MODEL (this may take a few minutes on first run)..."
ollama pull "$MODEL"

info "Model $MODEL is ready."

# ---------------------------------------------------------------------------
# Step 6: Verify with a test prompt
# ---------------------------------------------------------------------------
info "Verifying model with a test prompt..."
RESPONSE=$(ollama run "$MODEL" "Say 'hello' in one word." 2>/dev/null | head -5)

if [[ -n "$RESPONSE" ]]; then
    info "Model responded successfully."
    echo ""
    echo "  Test response: $RESPONSE"
    echo ""
else
    warn "Model did not return a response. It may still be loading."
    warn "Try running:  ollama run $MODEL \"Hello\""
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
echo "============================================="
echo "  Ollama Setup Complete"
echo "============================================="
echo "  OS:     $OS"
echo "  RAM:    ${RAM_GB} GB"
echo "  GPU:    $GPU_NAME"
echo "  VRAM:   ${VRAM_GB} GB"
echo "  Tier:   $HW_TIER"
echo "  Model:  $MODEL"
echo "  Tuning: num_ctx=$OPT_NUM_CTX  num_batch=$OPT_NUM_BATCH  num_gpu=$OPT_NUM_GPU"
echo "  API:    http://localhost:11434"
echo "============================================="
echo ""
# Write selected model to a file so setup.sh can read it
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
echo "$MODEL" > "$REPO_ROOT/.ollama_model"

# Write hardware profile so the tutor engine can send optimal Ollama options
cat > "$REPO_ROOT/.ollama_hw_profile" <<HWEOF
# Auto-generated by setup-ollama.sh — do not edit manually.
# These values are read by the tutor engine to optimize Ollama requests.
HW_TIER=$HW_TIER
RAM_GB=$RAM_GB
VRAM_GB=$VRAM_GB
NUM_CTX=$OPT_NUM_CTX
NUM_BATCH=$OPT_NUM_BATCH
NUM_GPU=$OPT_NUM_GPU
HWEOF
info "Hardware profile written to .ollama_hw_profile (tier=$HW_TIER)"

info "You can now start the tutor with:  docker compose -f docker/docker-compose.yml up"
