"""Small server-side adapter for the Rezeis admin API."""
from __future__ import annotations

from typing import Any
from urllib.parse import quote

import httpx

from .pair_store import SubscriptionPair


class RezeisError(RuntimeError):
    pass


class RezeisNotFound(RezeisError):
    pass


class RezeisClient:
    def __init__(self, base_url: str, timeout_seconds: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def _get(
        self, path: str, token: str
    ) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=False) as client:
            response = await client.get(
                f"{self.base_url}{path}",
                headers={"Authorization": f"Bearer {token}"},
            )
        if response.status_code == 401:
            raise RezeisError("Rezeis admin token is invalid or expired")
        if response.status_code == 403:
            raise RezeisError("Rezeis admin token lacks the required permission")
        if response.status_code == 404:
            raise RezeisNotFound("Rezeis resource not found")
        if response.status_code >= 400:
            raise RezeisError(f"Rezeis returned HTTP {response.status_code}")
        try:
            payload = response.json()
        except ValueError as exc:
            raise RezeisError("Rezeis returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise RezeisError("Rezeis returned an invalid response shape")
        return payload

    async def validate_admin(self, token: str) -> dict[str, Any]:
        return await self._get("/api/admin/auth/me", token)

    async def get_subscription(
        self, token: str, telegram_id: str, subscription_id: str
    ) -> dict[str, Any]:
        payload = await self._get(
            f"/api/admin/users/{quote(telegram_id.strip(), safe='')}", token
        )
        subscriptions = payload.get("subscriptions")
        if not isinstance(subscriptions, list):
            raise RezeisError("Rezeis user response has no subscriptions list")
        for subscription in subscriptions:
            if isinstance(subscription, dict) and str(subscription.get("id")) == subscription_id:
                config_url = subscription.get("configUrl")
                if not isinstance(config_url, str) or not config_url.strip():
                    raise RezeisError(
                        f"Rezeis subscription {subscription_id} has no configUrl"
                    )
                return subscription
        raise RezeisNotFound(f"Rezeis subscription {subscription_id} not found for user")


def pair_response(pair: SubscriptionPair) -> dict[str, Any]:
    return {
        "id": pair.id,
        "mainSubscriptionId": pair.main_subscription_id,
        "secondarySubscriptionId": pair.secondary_subscription_id,
        "mainLabel": pair.main_label,
        "secondaryLabel": pair.secondary_label,
        "createdAt": pair.created_at,
        "subscriptionUrl": f"/sub/merge/{pair.id}",
    }
