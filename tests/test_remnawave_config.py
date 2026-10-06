import pytest

from src.remnawave.config import ConfigurationError, RemnawaveConfig


def test_default_secondary_mapping() -> None:
    config = RemnawaveConfig(base_url="https://panel.example", api_token="secret")
    assert config.secondary_username("alice") == "alice_addsub"


def test_mapping_is_independent_per_user() -> None:
    config = RemnawaveConfig(base_url="https://panel.example", api_token="secret")
    assert config.secondary_username("alice") != config.secondary_username("bob")


def test_empty_username_rejected() -> None:
    config = RemnawaveConfig(base_url="https://panel.example", api_token="secret")
    with pytest.raises(ValueError):
        config.secondary_username(" ")


def test_environment_requires_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REMNAWAVE_API_URL", "https://panel.example/")
    monkeypatch.delenv("REMNAWAVE_API_TOKEN", raising=False)
    with pytest.raises(ConfigurationError):
        RemnawaveConfig.from_env()


def test_secondary_username_rejects_already_secondary_name() -> None:
    config = RemnawaveConfig(base_url="https://panel.example", api_token="secret")
    with pytest.raises(ValueError, match="secondary suffix"):
        config.secondary_username("alice_addsub")
