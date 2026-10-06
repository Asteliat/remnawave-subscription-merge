"""Fetch and validate client-facing Remnawave subscriptions."""

from dataclasses import dataclass
import json
from typing import Mapping

import httpx

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

    @property
    def http_client(self) -> httpx.AsyncClient:
        if self._http is None:
            raise RuntimeError("RemnawaveSubscriptionClient requires an async HTTP client")
        return self._http

    async def fetch_public(self, subscription_url: str, request_headers: Mapping[str, str] | None = None) -> SubscriptionPayload:
        if not subscription_url.strip():
            raise ValueError("subscription_url must not be empty")
        headers = {
            key: value
            for key, value in (request_headers or {}).items()
            if key.lower() in {"user-agent", "x-hwid", "x-device-os", "x-ver-os", "x-device-model"}
        }
        response = await self.http_client.get(subscription_url, headers=headers)
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
        return "base64_uri"
    if not isinstance(value, dict):
        raise SubscriptionPayloadError("JSON subscription must be an object")
    if isinstance(value.get("proxies"), list):
        return "clash_yaml"
    if isinstance(value.get("outbounds"), list):
        return "json_outbounds"
    raise SubscriptionPayloadError("unsupported JSON subscription format")
