"""ACE configuration via Pydantic settings."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class AceSettings(BaseSettings):
    """Configuration for the ACE framework.

    Values are loaded from environment variables or a .env file in the
    project root.  Environment variable names are prefixed with ``ACE_``
    (e.g. ``ACE_OLLAMA_HOST``).
    """

    model_config = SettingsConfigDict(
        env_prefix="ACE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    curriculum_path: Path = Path("curriculum")
    output_path: Path = Path("output")


def get_settings() -> AceSettings:
    """Return a cached settings instance."""
    return AceSettings()
