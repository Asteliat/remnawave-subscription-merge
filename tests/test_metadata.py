import pytest

from src.metadata import merge_userinfo, parse_userinfo


def test_userinfo_adds_usage_and_quota_and_keeps_latest_expiry() -> None:
    result = merge_userinfo("download=10;upload=20;total=100;expire=1000", "download=3;upload=4;total=50;expire=2000")
    assert result == "download=13;upload=24;total=150;expire=2000"


def test_userinfo_rejects_malformed_values() -> None:
    with pytest.raises(ValueError):
        parse_userinfo("download=x;upload=1;total=2;expire=3")


def test_userinfo_rejects_missing_fields() -> None:
    with pytest.raises(ValueError):
        parse_userinfo("download=1;upload=2")
