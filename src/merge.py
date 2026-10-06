"""Deterministic merging for supported client-facing subscription formats."""

import base64
import binascii
import json
from copy import deepcopy
from urllib.parse import unquote, urlsplit, urlunsplit
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


def _base64_entry_name(entry: str) -> str | None:
    try:
        fragment = urlsplit(entry).fragment
    except ValueError:
        return None
    return unquote(fragment) if fragment else None


def _rename_base64_entry(entry: str, used_names: set[str]) -> tuple[str, str | None]:
    name = _base64_entry_name(entry)
    if not name or name not in used_names:
        return entry, name

    new_name = _unique_name(name, used_names)
    parts = urlsplit(entry)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, new_name)), new_name


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


def _validate_unique_names(items: list[Any], key: str, label: str) -> None:
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, dict) or not item.get(key):
            raise SubscriptionPayloadError(f"{label} is missing {key}")
        name = str(item[key])
        if name in seen:
            raise SubscriptionPayloadError(f"{label} has duplicate {key}: {name}")
        seen.add(name)


def _replace_singbox_references(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, list):
        return [_replace_singbox_references(item, replacements) for item in value]
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if key == "outbounds" and isinstance(item, list):
                result[key] = [replacements.get(ref, ref) if isinstance(ref, str) else ref for ref in item]
            elif key == "detour" and isinstance(item, str):
                result[key] = replacements.get(item, item)
            else:
                result[key] = _replace_singbox_references(item, replacements)
        return result
    return value


def _merge_clash(main: dict[str, Any], secondary: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(main)
    main_proxies = result.get("proxies")
    secondary_proxies = secondary.get("proxies")
    if not isinstance(main_proxies, list) or not isinstance(secondary_proxies, list):
        raise SubscriptionPayloadError("Clash subscription has no valid proxies list")

    _validate_unique_names(main_proxies, "name", "Clash proxy")
    _validate_unique_names(secondary_proxies, "name", "Clash proxy")
    used = {item["name"] for item in main_proxies}
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


def _merge_singbox(main: dict[str, Any], secondary: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(main)
    main_outbounds = result.get("outbounds")
    secondary_outbounds = secondary.get("outbounds")
    if not isinstance(main_outbounds, list) or not isinstance(secondary_outbounds, list):
        raise SubscriptionPayloadError("Sing-box subscription has no valid outbounds list")

    _validate_unique_names(main_outbounds, "tag", "Sing-box outbound")
    _validate_unique_names(secondary_outbounds, "tag", "Sing-box outbound")
    used = {item["tag"] for item in main_outbounds}
    replacements: dict[str, str] = {}
    secondary_nodes: list[dict[str, Any]] = []

    for item in secondary_outbounds:
        if not isinstance(item, dict) or not item.get("tag") or not item.get("type"):
            raise SubscriptionPayloadError("Sing-box outbound is missing tag/type")
        clone = deepcopy(item)
        tag = str(clone["tag"])
        outbound_type = str(clone["type"])

        if tag in used:
            main_same = next(
                (existing for existing in main_outbounds if isinstance(existing, dict) and existing.get("tag") == tag),
                None,
            )
            if outbound_type == "selector" and isinstance(main_same, dict) and main_same.get("type") == "selector":
                secondary_selector_refs = clone.get("outbounds", [])
                main_selector_refs = main_same.get("outbounds")
                if isinstance(secondary_selector_refs, list) and isinstance(main_selector_refs, list):
                    for ref in secondary_selector_refs:
                        replacements.setdefault(str(ref), str(ref))
                continue
            if outbound_type == "direct" and isinstance(main_same, dict) and main_same.get("type") == "direct":
                continue

            new_tag = _unique_name(tag, used)
            replacements[tag] = new_tag
            clone["tag"] = new_tag

        used.add(str(clone["tag"]))
        secondary_nodes.append(clone)

    secondary_nodes = [_replace_singbox_references(item, replacements) for item in secondary_nodes]
    result_outbounds = main_outbounds + secondary_nodes
    result["outbounds"] = result_outbounds

    main_selector = next(
        (
            item for item in result_outbounds
            if isinstance(item, dict)
            and item.get("type") == "selector"
            and item.get("tag") == "→ Remnawave"
        ),
        None,
    )
    if isinstance(main_selector, dict):
        refs = main_selector.get("outbounds")
        if isinstance(refs, list):
            for item in secondary_nodes:
                if item.get("type") == "vless" and item.get("tag") not in refs:
                    refs.append(item["tag"])

    return result


def _merge_xray(main: list[Any], secondary: list[Any]) -> list[Any]:
    if len(main) != 1 or len(secondary) != 1 or not isinstance(main[0], dict) or not isinstance(secondary[0], dict):
        raise SubscriptionPayloadError("Xray JSON subscription must contain exactly one object")

    result = deepcopy(main[0])
    secondary_config = secondary[0]
    main_outbounds = result.get("outbounds")
    secondary_outbounds = secondary_config.get("outbounds")
    if not isinstance(main_outbounds, list) or not isinstance(secondary_outbounds, list):
        raise SubscriptionPayloadError("Xray JSON subscription has no valid outbounds list")

    _validate_unique_names(main_outbounds, "tag", "Xray outbound")
    _validate_unique_names(secondary_outbounds, "tag", "Xray outbound")
    used = {item["tag"] for item in main_outbounds}
    secondary_out: list[dict[str, Any]] = []
    replacements: dict[str, str] = {}

    for item in secondary_outbounds:
        if not isinstance(item, dict) or not item.get("tag") or not item.get("protocol"):
            raise SubscriptionPayloadError("Xray outbound is missing tag/protocol")
        clone = deepcopy(item)
        tag = str(clone["tag"])
        if tag in used:
            main_same = next(
                (existing for existing in main_outbounds if isinstance(existing, dict) and existing.get("tag") == tag),
                None,
            )
            if (
                isinstance(main_same, dict)
                and main_same.get("protocol") == clone.get("protocol")
                and clone.get("protocol") in {"freedom", "blackhole"}
            ):
                continue
            new_tag = _unique_name(tag, used)
            replacements[tag] = new_tag
            clone["tag"] = new_tag
        used.add(str(clone["tag"]))
        secondary_out.append(clone)

    result["outbounds"] = main_outbounds + [_replace_strings(item, replacements) for item in secondary_out]
    return [result]


def _merge_json(main_value: Any, secondary_value: Any) -> tuple[Any, str]:
    if isinstance(main_value, dict) and isinstance(secondary_value, dict):
        if isinstance(main_value.get("outbounds"), list) and isinstance(secondary_value.get("outbounds"), list):
            return _merge_singbox(main_value, secondary_value), "singbox_json"
        raise SubscriptionPayloadError("unsupported JSON object subscription format")

    if isinstance(main_value, list) and isinstance(secondary_value, list):
        return _merge_xray(main_value, secondary_value), "xray_json"

    raise SubscriptionPayloadError("JSON subscription root types do not match")


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
        main_entries = _decode_base64(main)
        secondary_entries = _decode_base64(secondary)
        merged = list(dict.fromkeys(main_entries))
        used_names = {
            name for entry in merged if (name := _base64_entry_name(entry))
        }
        for entry in secondary_entries:
            if entry in merged:
                continue
            renamed, name = _rename_base64_entry(entry, used_names)
            merged.append(renamed)
            if name:
                used_names.add(name)
        return _encode_base64(merged), "text/plain"

    if main_format in {"singbox_json", "xray_json"}:
        try:
            main_json = json.loads(main)
            secondary_json = json.loads(secondary)
        except json.JSONDecodeError as exc:
            raise SubscriptionPayloadError("invalid JSON subscription") from exc
        result, _ = _merge_json(main_json, secondary_json)
        return json.dumps(result, ensure_ascii=False, separators=(",", ":")), "application/json"

    main_yaml = _load_yaml(main)
    secondary_yaml = _load_yaml(secondary)
    result = _merge_clash(main_yaml, secondary_yaml)
    return yaml.safe_dump(result, allow_unicode=True, sort_keys=False), "text/yaml"
