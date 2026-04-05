"""Application settings loaded from environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings

# Resolve .env from the project root (one level above tutor/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_num_ctx: int = 0      # 0 = auto-detect from .ollama_hw_profile or use model default
    ollama_num_batch: int = 0    # 0 = use Ollama default (512)
    ollama_num_gpu: int = -1     # -1 = auto-detect, 0 = CPU-only
    tutor_host: str = "127.0.0.1"
    tutor_port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    curriculum_path: str = str(_PROJECT_ROOT / "curriculum")

    model_config = {"env_prefix": "TUTOR_", "env_file": str(_ENV_FILE), "extra": "ignore"}


settings = Settings()


def _load_hw_profile() -> dict[str, int]:
    """Load hardware profile from .ollama_hw_profile (written by setup-ollama.sh).

    Returns a dict with num_ctx, num_batch, num_gpu values, or empty dict
    if the file doesn't exist or can't be parsed.
    """
    hw_file = _PROJECT_ROOT / ".ollama_hw_profile"
    if not hw_file.exists():
        return {}
    result = {}
    try:
        for line in hw_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            if key == "NUM_CTX":
                result["num_ctx"] = int(val)
            elif key == "NUM_BATCH":
                result["num_batch"] = int(val)
            elif key == "NUM_GPU":
                result["num_gpu"] = int(val)
    except (ValueError, OSError):
        pass
    return result


def get_ollama_options() -> dict[str, int]:
    """Return Ollama inference options based on settings and hardware profile.

    Priority: env vars (TUTOR_OLLAMA_NUM_CTX etc.) > .ollama_hw_profile > defaults.
    Returns only non-default options (empty dict means use Ollama's own defaults).
    """
    hw = _load_hw_profile()
    options: dict[str, int] = {}

    # num_ctx: env > hw_profile > skip (let Ollama use model default)
    num_ctx = settings.ollama_num_ctx
    if num_ctx > 0:
        options["num_ctx"] = num_ctx
    elif hw.get("num_ctx", 0) > 0:
        options["num_ctx"] = hw["num_ctx"]

    # num_batch: env > hw_profile > skip
    num_batch = settings.ollama_num_batch
    if num_batch > 0:
        options["num_batch"] = num_batch
    elif hw.get("num_batch", 0) > 0:
        options["num_batch"] = hw["num_batch"]

    # num_gpu: env > hw_profile > skip (-1 means auto, don't send)
    num_gpu = settings.ollama_num_gpu
    if num_gpu >= 0:
        options["num_gpu"] = num_gpu
    elif hw.get("num_gpu", -1) >= 0:
        options["num_gpu"] = hw["num_gpu"]

    return options


def resolve_curriculum_path() -> Path:
    """Resolve the curriculum path, handling both relative and absolute paths.

    Falls back to project_root/curriculum if the configured path doesn't exist.
    This function is CWD-independent — it always finds the curriculum.
    """
    configured = Path(settings.curriculum_path)
    if configured.is_absolute() and configured.exists():
        return configured
    # Try relative from CWD
    if configured.exists():
        return configured.resolve()
    # Fallback: project root / curriculum (always works regardless of CWD)
    fallback = _PROJECT_ROOT / "curriculum"
    if fallback.exists():
        return fallback
    # Last resort: walk up from this file
    candidate = Path(__file__).resolve().parent.parent.parent / "curriculum"
    if candidate.exists():
        return candidate
    return configured.resolve()
