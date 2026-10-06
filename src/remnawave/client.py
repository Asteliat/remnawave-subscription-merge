"""Small authenticated client for the Remnawave v3 REST API."""

from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import httpx

from .config import RemnawaveConfig


class RemnawaveError(RuntimeError):
    """Base class for safe upstream errors."""


class RemnawaveNotFound(RemnawaveError):
    """Requested Remnawave resource does not exist."""


class RemnawaveUpstreamError(RemnawaveError):
    """Remnawave returned an unexpected or invalid response."""


@dataclass(frozen=True, slots=True)
class RemnawaveUser:
    id: int
    username: str
    short_uuid: str
    status: str
    subscription_url: str
    expire_at: str | None

    @classmethod
    def from_response(cls, payload: dict[str, Any]) -> "RemnawaveUser":
        data = payload.get("response", payload)
        if not isinstance(data, dict):
            raise RemnawaveUpstreamError("invalid user response")
        required = ("id", "username", "shortUuid", "status", "subscriptionUrl")
        if any(key not in data for key in required):
            raise RemnawaveUpstreamError("incomplete user response")
        return cls(
            id=int(data["id"]),
            username=str(data["username"]),
            short_uuid=str(data["shortUuid"]),
            status=str(data["status"]),
            subscription_url=str(data["subscriptionUrl"]),
            expire_at=data.get("expireAt"),
        )


class RemnawaveClient:
    """Authenticated read-only Remnawave API client for A2 resolution."""

    def __init__(self, config: RemnawaveConfig, http_client: httpx.AsyncClient | None = None) -> None:
        self.config = config
        self._http = http_client
        self._owns_http = http_client is None

    async def __aenter__(self) -> "RemnawaveClient":
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=self.config.timeout_seconds, follow_redirects=False)
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if self._http is not None and self._owns_http:
            await self._http.aclose()
            self._http = None

    @property
    def http_client(self) -> httpx.AsyncClient:
        if self._http is None:
            raise RuntimeError("RemnawaveClient must be used as an async context manager")
        return self._http

    async def _get_json(self, path: str) -> dict[str, Any]:
        response = await self.http_client.get(
            f"{self.config.base_url}{path}",
            headers={"Authorization": f"Bearer {self.config.api_token}"},
        )
        if response.status_code == 404:
            raise RemnawaveNotFound("Remnawave resource not found")
        if response.status_code >= 400:
            raise RemnawaveUpstreamError(f"Remnawave returned HTTP {response.status_code}")
        try:
            data = response.json()
        except ValueError as exc:
            raise RemnawaveUpstreamError("Remnawave returned invalid JSON") from exc
        if not isinstance(data, dict):
            raise RemnawaveUpstreamError("Remnawave returned an invalid response shape")
        return data

    async def get_user_by_username(self, username: str) -> RemnawaveUser:
        if not username.strip():
            raise ValueError("username must not be empty")
        encoded_username = quote(username, safe="")
        payload = await self._get_json(f"/api/users/by-username/{encoded_username}")
        return RemnawaveUser.from_response(payload)

    async def get_user_by_short_uuid(self, short_uuid: str) -> RemnawaveUser:
        if not short_uuid.strip():
            raise ValueError("short_uuid must not be empty")
        encoded_short_uuid = quote(short_uuid.strip(), safe="")
        payload = await self._get_json(f"/api/users/by-short-uuid/{encoded_short_uuid}")
        return RemnawaveUser.from_response(payload)

    async def resolve_a2_pair_by_short_uuid(
        self, short_uuid: str
    ) -> tuple[RemnawaveUser, RemnawaveUser]:
        main = await self.get_user_by_short_uuid(short_uuid)
        secondary_username = self.config.secondary_username(main.username)
        secondary = await self.get_user_by_username(secondary_username)
        if main.id == secondary.id:
            raise RemnawaveUpstreamError("A2 mapping resolved the same Remnawave user twice")
        return main, secondary

    async def resolve_a2_pair_identifier(self, identifier: str) -> tuple[RemnawaveUser, RemnawaveUser]:
        """Resolve the client-facing identifier as short UUID first, then username."""
        try:
            return await self.resolve_a2_pair_by_short_uuid(identifier)
        except RemnawaveNotFound:
            return await self.resolve_a2_pair(identifier)

    async def resolve_a2_pair(self, main_username: str) -> tuple[RemnawaveUser, RemnawaveUser]:
        main = await self.get_user_by_username(main_username)
        secondary_username = self.config.secondary_username(main.username)
        secondary = await self.get_user_by_username(secondary_username)
        if main.id == secondary.id:
            raise RemnawaveUpstreamError("A2 mapping resolved the same Remnawave user twice")
        return main, secondary
