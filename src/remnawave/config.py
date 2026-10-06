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
    max_subscription_bytes: int = 8 * 1024 * 1024
    secondary_label: str = ""

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
        suffix = os.getenv("REMNAWAVE_SECONDARY_SUFFIX", "_addsub").strip()
        if not suffix:
            raise ConfigurationError("REMNAWAVE_SECONDARY_SUFFIX must not be empty")
        try:
            max_subscription_bytes = int(
                os.getenv("REMNAWAVE_MAX_SUBSCRIPTION_BYTES", str(8 * 1024 * 1024))
            )
        except ValueError as exc:
            raise ConfigurationError("REMNAWAVE_MAX_SUBSCRIPTION_BYTES must be an integer") from exc
        if max_subscription_bytes <= 0:
            raise ConfigurationError("REMNAWAVE_MAX_SUBSCRIPTION_BYTES must be positive")
        return cls(
            base_url=base_url,
            api_token=token,
            timeout_seconds=timeout,
            secondary_suffix=suffix,
            max_subscription_bytes=max_subscription_bytes,
            secondary_label=os.getenv("REMNAWAVE_SECONDARY_LABEL", "").strip(),
        )

    def secondary_username(self, main_username: str) -> str:
        username = main_username.strip()
        if not username:
            raise ValueError("main username must not be empty")
        if username.endswith(self.secondary_suffix):
            raise ValueError("main username already uses the secondary suffix")
        return f"{username}{self.secondary_suffix}"
