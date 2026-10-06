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


def test_base64_uri_merge_renames_secondary_colliding_fragment() -> None:
    main = b64("vless://main@host:443#rrrrrr", "ss://main@host#other")
    secondary = b64("vless://secondary@host:443#rrrrrr", "ss://secondary@host#other")

    body, content_type = merge_payloads(main, secondary)

    assert content_type == "text/plain"
    assert base64.b64decode(body).decode().splitlines() == [
        "vless://main@host:443#rrrrrr",
        "ss://main@host#other",
        "vless://secondary@host:443#rrrrrr [addsub]",
        "ss://secondary@host#other [addsub]",
    ]


def test_clash_yaml_merge_keeps_main_top_level_and_deduplicates_names() -> None:
    main = yaml.safe_dump({"proxies": [{"name": "one", "server": "a"}], "mode": "rule"}, sort_keys=False)
    secondary = yaml.safe_dump({"proxies": [{"name": "one", "server": "other"}, {"name": "two", "server": "b"}], "mode": "global"}, sort_keys=False)
    body, content_type = merge_payloads(main, secondary)
    result = yaml.safe_load(body)
    assert content_type == "text/yaml"
    assert result["mode"] == "rule"
    assert [p["name"] for p in result["proxies"]] == ["one", "one [addsub]", "two"]


def test_json_outbounds_merge_by_tag() -> None:
    main = json.dumps({"outbounds": [{"tag": "one", "type": "direct"}], "route": {"final": "one"}})
    secondary = json.dumps({"outbounds": [{"tag": "one", "type": "block"}, {"tag": "two", "type": "direct"}]})
    body, _ = merge_payloads(main, secondary)
    result = json.loads(body)
    assert [x["tag"] for x in result["outbounds"]] == ["one", "one [addsub]", "two"]
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


def test_clash_duplicate_proxy_names_are_rejected_within_source() -> None:
    duplicate = yaml.safe_dump({"proxies": [{"name": "proxy"}, {"name": "proxy"}]}, sort_keys=False)
    with pytest.raises(SubscriptionPayloadError, match="duplicate name"):
        merge_payloads(duplicate, yaml.safe_dump({"proxies": [{"name": "other"}]}, sort_keys=False))


def test_clash_duplicate_proxy_names_are_renamed_and_group_is_extended() -> None:
    main = yaml.safe_dump({
        "proxies": [{"name": "rrrrrr", "server": "main"}],
        "proxy-groups": [{"name": "Proxy", "type": "select", "proxies": ["rrrrrr"]}],
    }, sort_keys=False)
    secondary = yaml.safe_dump({
        "proxies": [{"name": "rrrrrr", "server": "secondary"}],
        "proxy-groups": [{"name": "Proxy", "type": "select", "proxies": ["rrrrrr"]}],
    }, sort_keys=False)
    body, _ = merge_payloads(main, secondary)
    result = yaml.safe_load(body)
    names = [item["name"] for item in result["proxies"]]
    assert names == ["rrrrrr", "rrrrrr [addsub]"]
    assert result["proxy-groups"][0]["proxies"] == ["rrrrrr", "rrrrrr [addsub]"]


def test_clash_proxy_collision_does_not_rename_unrelated_group_name() -> None:
    main = yaml.safe_dump({
        "proxies": [{"name": "proxy", "server": "main"}],
        "proxy-groups": [{"name": "main", "type": "select", "proxies": ["proxy"]}],
    }, sort_keys=False)
    secondary = yaml.safe_dump({
        "proxies": [{"name": "proxy", "server": "secondary"}],
        "proxy-groups": [{"name": "proxy", "type": "select", "proxies": ["proxy"]}],
    }, sort_keys=False)

    body, _ = merge_payloads(main, secondary)
    result = yaml.safe_load(body)

    assert [group["name"] for group in result["proxy-groups"]] == ["main", "proxy"]
    assert result["proxy-groups"][1]["proxies"] == ["proxy [addsub]"]


def test_json_duplicate_tags_are_rejected_within_source() -> None:
    duplicate = json.dumps({"outbounds": [{"tag": "proxy", "type": "vless"}, {"tag": "proxy", "type": "vless"}]})
    with pytest.raises(SubscriptionPayloadError, match="duplicate tag"):
        merge_payloads(duplicate, json.dumps({"outbounds": [{"tag": "other", "type": "vless"}]}))


def test_json_duplicate_tags_are_renamed() -> None:
    main = json.dumps({"outbounds": [{"tag": "proxy", "type": "vless"}]})
    secondary = json.dumps({"outbounds": [{"tag": "proxy", "type": "vless"}]})
    body, _ = merge_payloads(main, secondary)
    result = json.loads(body)
    assert [item["tag"] for item in result["outbounds"]] == ["proxy", "proxy [addsub]"]


def test_singbox_merge_preserves_single_selector_and_adds_secondary_vless() -> None:
    main = json.dumps({
        "dns": {"servers": [{"tag": "local", "type": "udp"}]},
        "route": {"rules": [{"outbound": "direct"}]},
        "inbounds": [{"tag": "tun-in"}],
        "outbounds": [
            {"tag": "→ Remnawave", "type": "selector", "outbounds": ["proxy"]},
            {"tag": "direct", "type": "direct"},
            {"tag": "proxy", "type": "vless", "server": "main"},
        ],
    })
    secondary = json.dumps({
        "outbounds": [
            {"tag": "→ Remnawave", "type": "selector", "outbounds": ["proxy"]},
            {"tag": "direct", "type": "direct"},
            {"tag": "proxy", "type": "vless", "server": "secondary"},
        ],
    })
    body, content_type = merge_payloads(main, secondary)
    result = json.loads(body)
    assert content_type == "application/json"
    assert [x["tag"] for x in result["outbounds"]] == ["→ Remnawave", "direct", "proxy", "proxy [addsub]"]
    assert result["outbounds"][0]["outbounds"] == ["proxy", "proxy [addsub]"]


def test_xray_duplicate_tags_are_rejected_within_source() -> None:
    duplicate = json.dumps([{"outbounds": [{"tag": "proxy", "protocol": "vless"}, {"tag": "proxy", "protocol": "vless"}]}])
    with pytest.raises(SubscriptionPayloadError, match="duplicate tag"):
        merge_payloads(duplicate, json.dumps([{"outbounds": [{"tag": "other", "protocol": "vless"}]}]))


def test_xray_duplicate_tag_does_not_rewrite_unrelated_string_fields() -> None:
    main = json.dumps([{"outbounds": [{"tag": "proxy", "protocol": "vless"}]}])
    secondary = json.dumps([{"outbounds": [{"tag": "proxy", "protocol": "vless", "remarks": "proxy"}]}])
    body, _ = merge_payloads(main, secondary)
    result = json.loads(body)
    assert result[0]["outbounds"][1]["tag"] == "proxy [addsub]"
    assert result[0]["outbounds"][1]["remarks"] == "proxy"


def test_xray_duplicate_tag_rewrites_known_reference_fields() -> None:
    main = json.dumps([{"outbounds": [{"tag": "proxy", "protocol": "vless"}]}])
    secondary = json.dumps([{
        "outbounds": [{"tag": "proxy", "protocol": "vless"},
                      {"tag": "wrapper", "protocol": "freedom", "detour": "proxy"}],
    }])
    body, _ = merge_payloads(main, secondary)
    result = json.loads(body)
    assert result[0]["outbounds"][2]["detour"] == "proxy [addsub]"


def test_xray_json_list_merge_preserves_main_and_adds_secondary_node() -> None:
    main = json.dumps([{
        "dns": {},
        "routing": {"rules": [{"outboundTag": "direct"}]},
        "inbounds": [{"tag": "socks"}],
        "outbounds": [
            {"tag": "direct", "protocol": "freedom"},
            {"tag": "block", "protocol": "blackhole"},
            {"tag": "proxy", "protocol": "vless", "settings": {"vnext": [{"address": "main"}]},
             "streamSettings": {"network": "xhttp"}},
        ],
        "remarks": "main",
    }])
    secondary = json.dumps([{
        "dns": {},
        "routing": {"rules": [{"outboundTag": "direct"}]},
        "inbounds": [{"tag": "socks"}],
        "outbounds": [
            {"tag": "direct", "protocol": "freedom"},
            {"tag": "block", "protocol": "blackhole"},
            {"tag": "proxy", "protocol": "vless", "settings": {"vnext": [{"address": "secondary"}]},
             "streamSettings": {"network": "xhttp"}},
        ],
        "remarks": "secondary",
    }])
    body, content_type = merge_payloads(main, secondary)
    result = json.loads(body)
    assert content_type == "application/json"
    assert len(result) == 1
    assert [x["tag"] for x in result[0]["outbounds"]] == ["direct", "block", "proxy", "proxy [addsub]"]
    assert result[0]["remarks"] == "main"
    assert result[0]["routing"]["rules"][0]["outboundTag"] == "direct"
    assert result[0]["outbounds"][2]["settings"]["vnext"][0]["address"] == "main"
    assert result[0]["outbounds"][3]["settings"]["vnext"][0]["address"] == "secondary"


def test_detect_xray_json_list() -> None:
    body = json.dumps([{"outbounds": [{"tag": "direct", "protocol": "freedom"}]}])
    assert detect_format(body) == "xray_json"


def test_singbox_duplicate_tag_rewrites_secondary_internal_reference() -> None:
    main = json.dumps({
        "outbounds": [
            {"tag": "proxy", "type": "vless", "server": "main"},
        ],
    })
    secondary = json.dumps({
        "outbounds": [
            {"tag": "proxy", "type": "vless", "server": "secondary"},
            {"tag": "selector", "type": "selector", "outbounds": ["proxy"]},
        ],
    })
    body, _ = merge_payloads(main, secondary)
    result = json.loads(body)
    selector = next(item for item in result["outbounds"] if item["tag"] == "selector")
    assert selector["outbounds"] == ["proxy [addsub]"]


def test_singbox_duplicate_tag_does_not_rewrite_unrelated_string_fields() -> None:
    main = json.dumps({"outbounds": [{"tag": "proxy", "type": "vless"}]})
    secondary = json.dumps({"outbounds": [{"tag": "proxy", "type": "vless", "server": "proxy"}]})
    body, _ = merge_payloads(main, secondary)
    result = json.loads(body)
    assert result["outbounds"][1]["tag"] == "proxy [addsub]"
    assert result["outbounds"][1]["server"] == "proxy"


def test_singbox_duplicate_tag_rewrites_nested_secondary_reference() -> None:
    main = json.dumps({
        "outbounds": [
            {"tag": "proxy", "type": "vless", "server": "main"},
        ],
    })
    secondary = json.dumps({
        "outbounds": [
            {"tag": "proxy", "type": "vless", "server": "secondary"},
            {"tag": "wrapper", "type": "urltest", "outbounds": ["proxy"]},
        ],
    })
    body, _ = merge_payloads(main, secondary)
    result = json.loads(body)
    wrapper = next(item for item in result["outbounds"] if item["tag"] == "wrapper")
    assert wrapper["outbounds"] == ["proxy [addsub]"]
