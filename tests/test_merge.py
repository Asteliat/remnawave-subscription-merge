import base64
import json

import pytest
import yaml

from src.merge import merge_payloads
from src.remnawave.subscription import SubscriptionPayloadError, detect_format


def b64(*entries: str) -> str:
    return base64.b64encode(("\n".join(entries) + "\n").encode()).decode()


def test_base64_uri_merge_deduplicates_exact_entries() -> None:
    body, content_type = merge_payloads(b64("vless://one", "vless://two"), b64("vless://two", "vless://three"))
    assert content_type == "text/plain"
    assert base64.b64decode(body).decode().splitlines() == ["vless://one", "vless://two", "vless://three"]


def test_clash_yaml_merge_keeps_main_top_level_and_deduplicates_names() -> None:
    main = yaml.safe_dump({"proxies": [{"name": "one", "server": "a"}], "mode": "rule"}, sort_keys=False)
    secondary = yaml.safe_dump({"proxies": [{"name": "one", "server": "other"}, {"name": "two", "server": "b"}], "mode": "global"}, sort_keys=False)
    body, content_type = merge_payloads(main, secondary)
    result = yaml.safe_load(body)
    assert content_type == "text/yaml"
    assert result["mode"] == "rule"
    assert [p["name"] for p in result["proxies"]] == ["one", "two"]


def test_json_outbounds_merge_by_tag() -> None:
    main = json.dumps({"outbounds": [{"tag": "one", "type": "direct"}], "route": {"final": "one"}})
    secondary = json.dumps({"outbounds": [{"tag": "one", "type": "block"}, {"tag": "two", "type": "direct"}]})
    body, _ = merge_payloads(main, secondary)
    result = json.loads(body)
    assert [x["tag"] for x in result["outbounds"]] == ["one", "two"]
    assert result["route"]["final"] == "one"


def test_mixed_formats_fail_closed() -> None:
    with pytest.raises(SubscriptionPayloadError):
        merge_payloads(b64("vless://one"), json.dumps({"proxies": []}))


def test_unknown_json_fails_closed() -> None:
    with pytest.raises(SubscriptionPayloadError):
        detect_format(json.dumps({"foo": "bar"}))


def test_clash_yaml_is_detected_as_yaml() -> None:
    body = yaml.safe_dump({"proxies": [{"name": "one", "server": "example"}]}, sort_keys=False)
    assert detect_format(body) == "clash_yaml"
