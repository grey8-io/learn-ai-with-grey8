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

# NOTE: deliberately NO `-e`. Hardware detection is best-effort across an
# unknowable range of OS/hardware; a missing or renamed probe (e.g. `wmic` is
# gone on modern Windows 11) must degrade to a safe-bet model, never abort
# before the model is pulled. The few truly critical failures exit explicitly.
set -uo pipefail

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
# Step 3: Detect GPU and available VRAM (best-effort — never fatal)
# ---------------------------------------------------------------------------
VRAM_GB=0
GPU_NAME="none"

if command -v nvidia-smi &>/dev/null; then
    # Parse total VRAM from nvidia-smi (in MiB), convert to GB. Tolerant of
    # any unexpected output: stays at 0 (-> RAM-based selection) on failure.
    VRAM_MIB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null \
        | head -1 | tr -cd '0-9' || true)
    if [[ -n "$VRAM_MIB" && "$VRAM_MIB" =~ ^[0-9]+$ ]]; then
        VRAM_GB=$((VRAM_MIB / 1024))
        GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1 || true)
        info "NVIDIA GPU detected: ${GPU_NAME:-unknown} ($VRAM_GB GB VRAM)"
    fi
else
    warn "nvidia-smi not found. Assuming CPU-only or non-NVIDIA GPU."
    warn "If you have an NVIDIA GPU, install the NVIDIA drivers first."
fi

# ---------------------------------------------------------------------------
# Step 3b: Detect system RAM (best-effort — never fatal)
# ---------------------------------------------------------------------------
# Every probe is forced to exit 0 (|| true) so a missing/renamed tool degrades
# to the safe-bet failover below instead of aborting setup. RAM_DETECTED stays
# false when we genuinely cannot tell — we then refuse to guess "8 GB" (which
# would wrongly pick a heavy model on a tiny machine).
RAM_GB=0
RAM_DETECTED=false
RAM_RAW=""

case "$OS" in
    linux)
        RAM_RAW=$(grep -i MemTotal /proc/meminfo 2>/dev/null | awk '{print $2}' || true)   # kB
        if [[ -n "$RAM_RAW" && "$RAM_RAW" =~ ^[0-9]+$ ]]; then
            RAM_GB=$((RAM_RAW / 1024 / 1024))
        else
            # Containers/minimal images may lack /proc/meminfo — try `free`.
            RAM_RAW=$(free -k 2>/dev/null | awk '/^Mem:/ {print $2}' || true)              # kB
            [[ -n "$RAM_RAW" && "$RAM_RAW" =~ ^[0-9]+$ ]] && RAM_GB=$((RAM_RAW / 1024 / 1024))
        fi
        ;;
    macos)
        RAM_RAW=$(sysctl -n hw.memsize 2>/dev/null | tr -cd '0-9' || true)                 # bytes
        [[ -n "$RAM_RAW" && "$RAM_RAW" =~ ^[0-9]+$ ]] && RAM_GB=$((RAM_RAW / 1024 / 1024 / 1024))
        ;;
    windows)
        # wmic is deprecated and absent on modern Windows 11 builds — prefer
        # PowerShell CIM (present since Windows 8 / PS 3.0), fall back to wmic.
        RAM_RAW=$(powershell.exe -NoProfile -Command \
            "(Get-CimInstance -ClassName Win32_ComputerSystem).TotalPhysicalMemory" \
            2>/dev/null | tr -cd '0-9' || true)                                            # bytes
        if [[ -z "$RAM_RAW" ]]; then
            RAM_RAW=$(wmic ComputerSystem get TotalPhysicalMemory 2>/dev/null \
                | grep -Eo '[0-9]+' | head -1 || true)                                     # bytes
        fi
        [[ -n "$RAM_RAW" && "$RAM_RAW" =~ ^[0-9]+$ ]] && RAM_GB=$((RAM_RAW / 1024 / 1024 / 1024))
        ;;
esac

if [[ "$RAM_GB" -gt 0 ]]; then
    RAM_DETECTED=true
    info "System RAM detected: ${RAM_GB} GB"
else
    warn "Could not detect system RAM on this '$OS' environment."
fi

# ---------------------------------------------------------------------------
# Step 3c: Hardware profile (RAM-based Ollama tuning). Unknown hardware ->
# conservative 'low' profile so we never over-allocate context on a small box.
# These values land in .ollama_hw_profile and drive tutor request options.
# ---------------------------------------------------------------------------
if [[ "$RAM_DETECTED" != true ]]; then
    HW_TIER="low"; OPT_NUM_CTX=1024; OPT_NUM_BATCH=128; OPT_NUM_GPU=0
    warn "Using conservative tuning (tier=LOW) until hardware is known."
elif [[ $RAM_GB -le 4 ]]; then
    HW_TIER="low"; OPT_NUM_CTX=1024; OPT_NUM_BATCH=128; OPT_NUM_GPU=0
    info "Hardware tier: LOW (${RAM_GB}GB RAM) — num_ctx=$OPT_NUM_CTX, num_batch=$OPT_NUM_BATCH, num_gpu=$OPT_NUM_GPU"
elif [[ $RAM_GB -le 8 ]]; then
    HW_TIER="medium"; OPT_NUM_CTX=2048; OPT_NUM_BATCH=256; OPT_NUM_GPU=0
    info "Hardware tier: MEDIUM (${RAM_GB}GB RAM) — num_ctx=$OPT_NUM_CTX, num_batch=$OPT_NUM_BATCH"
elif [[ $RAM_GB -le 16 ]]; then
    HW_TIER="high"; OPT_NUM_CTX=4096; OPT_NUM_BATCH=512; OPT_NUM_GPU=-1
    info "Hardware tier: HIGH (${RAM_GB}GB RAM) — num_ctx=$OPT_NUM_CTX, num_batch=$OPT_NUM_BATCH"
else
    HW_TIER="ultra"; OPT_NUM_CTX=8192; OPT_NUM_BATCH=512; OPT_NUM_GPU=-1
    info "Hardware tier: ULTRA (${RAM_GB}GB RAM) — num_ctx=$OPT_NUM_CTX, num_batch=$OPT_NUM_BATCH"
fi

# CPU-only machines: a large num_ctx makes prompt prefill painfully slow on
# CPU (the dominant latency cost — far more than model size). Cap context and
# batch and force CPU regardless of the RAM tier so the tutor stays usable.
# GPU machines keep the bigger window since GPU prefill is cheap.
if [[ "$VRAM_GB" -eq 0 ]]; then
    OPT_NUM_GPU=0
    [[ $OPT_NUM_CTX -gt 2048 ]] && OPT_NUM_CTX=2048
    [[ $OPT_NUM_BATCH -gt 256 ]] && OPT_NUM_BATCH=256
    info "CPU-only — capping num_ctx=$OPT_NUM_CTX, num_batch=$OPT_NUM_BATCH for responsiveness"
fi

# ---------------------------------------------------------------------------
# Step 4: Select model — GPU VRAM first, then system RAM, then a universal
# safe bet. The safe bet (llama3.2:1b) runs CPU-only on ~4 GB and is the
# "learner is never blocked" guarantee.
# ---------------------------------------------------------------------------
SAFE_MODEL="llama3.2:1b"
DETECTION_FAILED=false

if [[ $VRAM_GB -ge 12 ]]; then
    MODEL="llama3.1:8b"; info "${VRAM_GB} GB VRAM detected — selecting $MODEL"
elif [[ $VRAM_GB -ge 8 ]]; then
    MODEL="llama3.2:3b"; info "${VRAM_GB} GB VRAM detected — selecting $MODEL"
elif [[ $VRAM_GB -gt 0 ]]; then
    MODEL="$SAFE_MODEL";  info "${VRAM_GB} GB VRAM detected — selecting $MODEL"
elif [[ "$RAM_DETECTED" == true ]]; then
    # No usable GPU. 3b is too slow on CPU even on 16 GB / i7 boxes (real
    # learner feedback), so CPU-only always uses the lightweight model.
    # 3b is reserved for machines with a capable GPU (VRAM >= 8 GB).
    MODEL="$SAFE_MODEL"
    info "No usable GPU, ${RAM_GB} GB RAM — selecting $MODEL (CPU mode; 3b is too slow on CPU)"
else
    # Nothing detected anywhere — guarantee a working tutor with the safe bet.
    MODEL="$SAFE_MODEL"
    DETECTION_FAILED=true
    warn "Hardware could not be detected — using the safe-bet model: $MODEL"
    warn "On a machine with >=6 GB RAM you can later run:  ollama pull llama3.2:3b"
    warn "then set TUTOR_OLLAMA_MODEL=llama3.2:3b in your .env"
fi

# ---------------------------------------------------------------------------
# Step 5: Pull the model — retry once, then last-resort to the safe bet so a
# learner is never left with no model at all.
# ---------------------------------------------------------------------------
pull_model() {
    local m="$1"
    info "Pulling model: $m (first run can take several minutes)..."
    if ollama pull "$m"; then return 0; fi
    warn "First attempt to pull '$m' failed — retrying once..."
    ollama pull "$m"
}

PULLED=""
if pull_model "$MODEL"; then
    PULLED="$MODEL"
elif [[ "$MODEL" != "$SAFE_MODEL" ]]; then
    warn "Could not pull '$MODEL'. Falling back to the safe-bet model: $SAFE_MODEL"
    if pull_model "$SAFE_MODEL"; then
        PULLED="$SAFE_MODEL"
        MODEL="$SAFE_MODEL"
        # We downshifted the model — pin conservative tuning to match it.
        HW_TIER="low"; OPT_NUM_CTX=1024; OPT_NUM_BATCH=128; OPT_NUM_GPU=0
    fi
fi

if [[ -z "$PULLED" ]]; then
    error "Could not download any model (likely a network or disk-space issue)."
    echo ""
    echo "  Fix it manually, then re-run this script or 'bash scripts/start.sh':"
    echo ""
    echo "    ollama pull llama3.2:3b      # or llama3.2:1b on a 4 GB machine"
    echo ""
    exit 1
fi

info "Model $PULLED is ready."

# ---------------------------------------------------------------------------
# Step 6: Verify with a test prompt (informational — never fatal)
# ---------------------------------------------------------------------------
info "Verifying model with a test prompt..."
RESPONSE=$(ollama run "$MODEL" "Say 'hello' in one word." 2>/dev/null | head -5 || true)

if [[ -n "$RESPONSE" ]]; then
    info "Model responded successfully."
    echo ""
    echo "  Test response: $RESPONSE"
    echo ""
else
    warn "Model did not return a test response yet (it may still be loading)."
    warn "Try running:  ollama run $MODEL \"Hello\""
fi

# ---------------------------------------------------------------------------
# Done — record what ACTUALLY happened so .env / tutor stay in sync.
# ---------------------------------------------------------------------------
echo ""
echo "============================================="
echo "  Ollama Setup Complete"
echo "============================================="
echo "  OS:     $OS"
if [[ "$RAM_DETECTED" == true ]]; then
    echo "  RAM:    ${RAM_GB} GB"
else
    echo "  RAM:    unknown (conservative defaults)"
fi
echo "  GPU:    $GPU_NAME"
echo "  VRAM:   ${VRAM_GB} GB"
echo "  Tier:   $HW_TIER"
echo "  Model:  $MODEL"
echo "  Tuning: num_ctx=$OPT_NUM_CTX  num_batch=$OPT_NUM_BATCH  num_gpu=$OPT_NUM_GPU"
echo "  API:    http://localhost:11434"
echo "============================================="
echo ""

# Write the model that was actually pulled so setup.sh / start.sh can sync .env
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

if [[ "$DETECTION_FAILED" == true ]]; then
    warn "Hardware detection failed; '$MODEL' is a conservative safe bet."
    warn "On a stronger machine, pull a bigger model and update TUTOR_OLLAMA_MODEL in .env."
fi

info "You can now start the tutor with:  bash scripts/start.sh"
