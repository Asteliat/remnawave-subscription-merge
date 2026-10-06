"""Deterministic merging for supported client-facing subscription formats."""

import base64
import binascii
import json
from copy import deepcopy
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


def _unique_name(name: str, used: set[str], suffix: str = "addsub") -> str:
    candidate = f"{name} [{suffix}]"
    index = 2
    while candidate in used:
        candidate = f"{name} [{suffix}-{index}]"
        index += 1
    return candidate


def _replace_strings(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, str):
        return replacements.get(value, value)
    if isinstance(value, list):
        return [_replace_strings(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: _replace_strings(item, replacements) for key, item in value.items()}
    return value


def _merge_clash(main: dict[str, Any], secondary: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(main)
    main_proxies = result.get("proxies")
    secondary_proxies = secondary.get("proxies")
    if not isinstance(main_proxies, list) or not isinstance(secondary_proxies, list):
        raise SubscriptionPayloadError("Clash subscription has no valid proxies list")

    used = {item.get("name") for item in main_proxies if isinstance(item, dict) and item.get("name")}
    replacements: dict[str, str] = {}
    secondary_out = []
    for item in secondary_proxies:
        if not isinstance(item, dict) or not item.get("name"):
            raise SubscriptionPayloadError("Clash proxy is missing name")
        clone = deepcopy(item)
        old_name = str(clone["name"])
        if old_name in used:
            new_name = _unique_name(old_name, used)
            replacements[old_name] = new_name
            clone["name"] = new_name
        used.add(str(clone["name"]))
        secondary_out.append(clone)
    result["proxies"] = main_proxies + secondary_out

    main_groups = result.get("proxy-groups")
    secondary_groups = secondary.get("proxy-groups")
    if isinstance(main_groups, list) and isinstance(secondary_groups, list):
        groups_by_name = {item.get("name"): item for item in main_groups if isinstance(item, dict) and item.get("name")}
        for raw_group in secondary_groups:
            if not isinstance(raw_group, dict) or not raw_group.get("name"):
                raise SubscriptionPayloadError("Clash proxy-group is missing name")
            group = _replace_strings(deepcopy(raw_group), replacements)
            name = str(group["name"])
            existing = groups_by_name.get(name)
            if existing is None:
                main_groups.append(group)
                groups_by_name[name] = group
            else:
                existing_proxies = existing.get("proxies")
                incoming_proxies = group.get("proxies")
                if isinstance(existing_proxies, list) and isinstance(incoming_proxies, list):
                    for proxy in incoming_proxies:
                        if proxy not in existing_proxies:
                            existing_proxies.append(proxy)
    return result


def _merge_json(main: dict[str, Any], secondary: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(main)
    main_outbounds = result.get("outbounds")
    secondary_outbounds = secondary.get("outbounds")
    if not isinstance(main_outbounds, list) or not isinstance(secondary_outbounds, list):
        raise SubscriptionPayloadError("JSON subscription has no valid outbounds list")

    used = {item.get("tag") for item in main_outbounds if isinstance(item, dict) and item.get("tag")}
    replacements: dict[str, str] = {}
    secondary_out = []
    for item in secondary_outbounds:
        if not isinstance(item, dict) or not item.get("tag"):
            raise SubscriptionPayloadError("JSON outbound is missing tag")
        clone = deepcopy(item)
        old_tag = str(clone["tag"])
        if old_tag in used:
            new_tag = _unique_name(old_tag, used)
            replacements[old_tag] = new_tag
            clone["tag"] = new_tag
        used.add(str(clone["tag"]))
        secondary_out.append(clone)

    result["outbounds"] = main_outbounds + [_replace_strings(item, replacements) for item in secondary_out]
    # Secondary routing/selectors that referred to a renamed tag must follow it.
    for key in ("routing", "route", "balancers", "observatory"):
        if key in result and key in secondary:
            # Keep main configuration as the source of truth; only add no
            # secondary routing because cross-template semantics are ambiguous.
            pass
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
        result = _merge_json(main_json, secondary_json)
        return json.dumps(result, ensure_ascii=False, separators=(",", ":")), "application/json"

    main_yaml = _load_yaml(main)
    secondary_yaml = _load_yaml(secondary)
    result = _merge_clash(main_yaml, secondary_yaml)
    return yaml.safe_dump(result, allow_unicode=True, sort_keys=False), "text/yaml"
