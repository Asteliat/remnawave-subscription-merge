import pytest

from src.metadata import merge_userinfo, parse_userinfo


def test_userinfo_adds_usage_and_keeps_latest_expiry() -> None:
    result = merge_userinfo("download=10;upload=20;total=100;expire=1000", "download=3;upload=4;total=50;expire=2000")
    assert result == "upload=24;download=13;total=150;expire=2000"


def test_unlimited_total_stays_unlimited() -> None:
    result = merge_userinfo("download=10;upload=20;total=0;expire=1000", "download=3;upload=4;total=50;expire=2000")
    assert result == "upload=24;download=13;total=0;expire=2000"


def test_both_unlimited_stays_unlimited() -> None:
    result = merge_userinfo("download=0;upload=0;total=0;expire=1000", "download=0;upload=0;total=0;expire=2000")
    assert result == "upload=0;download=0;total=0;expire=2000"


def test_userinfo_rejects_malformed_values() -> None:
    with pytest.raises(ValueError):
        parse_userinfo("download=x;upload=1;total=2;expire=3")


def test_userinfo_rejects_missing_fields() -> None:
    with pytest.raises(ValueError):
        parse_userinfo("download=1;upload=2")
