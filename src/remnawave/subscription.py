"""Fetching and parsing Remnawave subscription payloads."""

from dataclasses import dataclass
import json
from typing import Any

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
    def __init__(self, config: RemnawaveConfig, http_client: httpx.AsyncClient | None = None) -> None:
        self.config = config
        self._http = http_client

    @property
    def http_client(self) -> httpx.AsyncClient:
        if self._http is None:
            raise RuntimeError("RemnawaveSubscriptionClient requires an async HTTP client")
        return self._http

    async def fetch_raw(self, short_uuid: str) -> SubscriptionPayload:
        if not short_uuid.strip():
            raise ValueError("short_uuid must not be empty")
        response = await self.http_client.get(
            f"{self.config.base_url}/api/subscriptions/by-short-uuid/{short_uuid}/raw",
            params={"withDisabledHosts": "false"},
            headers={"Authorization": f"Bearer {self.config.api_token}"},
        )
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
            headers={k.lower(): v for k, v in response.headers.items()},
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
        return "clash"
    if isinstance(value.get("outbounds"), list):
        return "sing_box"
    raise SubscriptionPayloadError("unsupported JSON subscription format")
