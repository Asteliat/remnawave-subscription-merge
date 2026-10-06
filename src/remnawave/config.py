"""Configuration for the Remnawave upstream client."""

from dataclasses import dataclass
import os


class ConfigurationError(ValueError):
    """Raised when required Remnawave configuration is missing or invalid."""


@dataclass(frozen=True, slots=True)
class RemnawaveConfig:
    base_url: str
    api_token: str
    timeout_seconds: float = 10.0
    secondary_suffix: str = "_addsub"

    @classmethod
    def from_env(cls) -> "RemnawaveConfig":
        base_url = os.getenv("REMNAWAVE_API_URL", "").strip().rstrip("/")
        token = os.getenv("REMNAWAVE_API_TOKEN", "").strip()
        if not base_url:
            raise ConfigurationError("REMNAWAVE_API_URL is required")
        if not token:
            raise ConfigurationError("REMNAWAVE_API_TOKEN is required")
        try:
            timeout = float(os.getenv("REMNAWAVE_TIMEOUT_SECONDS", "10"))
        except ValueError as exc:
            raise ConfigurationError("REMNAWAVE_TIMEOUT_SECONDS must be numeric") from exc
        if timeout <= 0:
            raise ConfigurationError("REMNAWAVE_TIMEOUT_SECONDS must be positive")
        suffix = os.getenv("REMNAWAVE_SECONDARY_SUFFIX", "_addsub")
        return cls(base_url=base_url, api_token=token, timeout_seconds=timeout, secondary_suffix=suffix)

    def secondary_username(self, main_username: str) -> str:
        username = main_username.strip()
        if not username:
            raise ValueError("main username must not be empty")
        return f"{username}{self.secondary_suffix}"
