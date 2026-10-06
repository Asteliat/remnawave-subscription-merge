"""Fetch and validate client-facing Remnawave subscriptions."""

from dataclasses import dataclass
import json
from typing import Mapping
from urllib.parse import urlsplit, urlunsplit

import httpx
import yaml

from .client import RemnawaveError
from .config import RemnawaveConfig


class SubscriptionPayloadError(RemnawaveError):
    """Upstream subscription content is malformed or unsupported."""


@dataclass(frozen=True, slots=True)
class SubscriptionPayload:
    body: str
    content_type: str
    headers: dict[str, str]


class RemnawaveSubscriptionClient:
    """Fetch the public rendered subscription, not the protected raw DTO."""

    def __init__(self, config: RemnawaveConfig, http_client: httpx.AsyncClient | None = None) -> None:
        self.config = config
        self._http = http_client

    @staticmethod
    def _with_suffix(subscription_url: str, suffix: str) -> str:
        if not suffix:
            return subscription_url
        parts = urlsplit(subscription_url)
        path = parts.path.rstrip("/") + f"/{suffix}"
        return urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))

    @property
    def http_client(self) -> httpx.AsyncClient:
        if self._http is None:
            raise RuntimeError("RemnawaveSubscriptionClient requires an async HTTP client")
        return self._http

    async def fetch_public(
        self,
        subscription_url: str,
        request_headers: Mapping[str, str] | None = None,
        suffix: str = "",
    ) -> SubscriptionPayload:
        if not subscription_url.strip():
            raise ValueError("subscription_url must not be empty")
        if suffix not in {"", "json", "singbox"}:
            raise ValueError("unsupported subscription suffix")
        url = self._with_suffix(subscription_url, suffix)
        headers = {
            key: value
            for key, value in (request_headers or {}).items()
            if key.lower() in {"user-agent", "x-hwid", "x-device-os", "x-ver-os", "x-device-model"}
        }
        response = await self.http_client.get(url, headers=headers)
        if response.status_code == 404:
            raise SubscriptionPayloadError("subscription not found")
        if response.status_code >= 400:
            raise SubscriptionPayloadError(f"subscription upstream HTTP {response.status_code}")
        body = response.text.strip()
        if not body:
            raise SubscriptionPayloadError("empty subscription payload")
        return SubscriptionPayload(
            body=body,
            content_type=response.headers.get("content-type", "text/plain").split(";", 1)[0].strip(),
            headers={key.lower(): value for key, value in response.headers.items()},
        )


def detect_format(body: str) -> str:
    text = body.strip()
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        value = None
    else:
        if isinstance(value, dict):
            if isinstance(value.get("proxies"), list):
                return "clash_yaml"
            if isinstance(value.get("outbounds"), list):
                return "singbox_json"
            raise SubscriptionPayloadError("unsupported JSON subscription format")
        if isinstance(value, list):
            if len(value) == 1 and isinstance(value[0], dict) and isinstance(value[0].get("outbounds"), list):
                return "xray_json"
            raise SubscriptionPayloadError("unsupported JSON subscription format")

    try:
        yaml_value = yaml.safe_load(text)
    except yaml.YAMLError:
        yaml_value = None
    if isinstance(yaml_value, dict) and isinstance(yaml_value.get("proxies"), list):
        return "clash_yaml"
    return "base64_uri"
