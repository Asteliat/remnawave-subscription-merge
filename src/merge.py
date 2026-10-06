"""Deterministic merging for supported client-facing subscription formats."""

import base64
import binascii
import json
from typing import Any

import yaml

from src.remnawave.subscription import SubscriptionPayloadError, detect_format


def _decode_base64(text: str) -> list[str]:
    compact = "".join(text.split())
    try:
        raw = base64.b64decode(compact + "=" * (-len(compact) % 4), validate=True)
    except (binascii.Error, ValueError) as exc:
        raise SubscriptionPayloadError("invalid base64 subscription") from exc
    try:
        decoded = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SubscriptionPayloadError("subscription is not UTF-8") from exc
    return [line.strip() for line in decoded.splitlines() if line.strip()]


def _encode_base64(entries: list[str]) -> str:
    return base64.b64encode(("\n".join(entries) + "\n").encode()).decode()


def _merge_named_lists(main: list[Any], secondary: list[Any], name_key: str) -> list[Any]:
    result = list(main)
    seen = {item.get(name_key) for item in main if isinstance(item, dict) and item.get(name_key)}
    for item in secondary:
        if not isinstance(item, dict):
            raise SubscriptionPayloadError("subscription collection contains a non-object")
        name = item.get(name_key)
        if name and name in seen:
            continue
        result.append(item)
        if name:
            seen.add(name)
    return result


def _load_yaml(body: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(body)
    except yaml.YAMLError as exc:
        raise SubscriptionPayloadError("invalid YAML subscription") from exc
    if not isinstance(value, dict):
        raise SubscriptionPayloadError("YAML subscription must be an object")
    return value


def merge_payloads(main: str, secondary: str) -> tuple[str, str]:
    main_format = detect_format(main)
    secondary_format = detect_format(secondary)
    if main_format != secondary_format:
        raise SubscriptionPayloadError("subscription formats do not match")
    if main_format == "base64_uri":
        merged = list(dict.fromkeys(_decode_base64(main) + _decode_base64(secondary)))
        return _encode_base64(merged), "text/plain"
    if main_format == "json_outbounds":
        try:
            main_json = json.loads(main)
            secondary_json = json.loads(secondary)
        except json.JSONDecodeError as exc:
            raise SubscriptionPayloadError("invalid JSON subscription") from exc
        result = dict(main_json)
        result["outbounds"] = _merge_named_lists(main_json["outbounds"], secondary_json["outbounds"], "tag")
        return json.dumps(result, ensure_ascii=False, separators=(",", ":")), "application/json"
    main_yaml = _load_yaml(main)
    secondary_yaml = _load_yaml(secondary)
    result = dict(main_yaml)
    result["proxies"] = _merge_named_lists(main_yaml["proxies"], secondary_yaml["proxies"], "name")
    if isinstance(main_yaml.get("proxy-groups"), list) and isinstance(secondary_yaml.get("proxy-groups"), list):
        result["proxy-groups"] = _merge_named_lists(main_yaml["proxy-groups"], secondary_yaml["proxy-groups"], "name")
    return yaml.safe_dump(result, allow_unicode=True, sort_keys=False), "text/yaml"
