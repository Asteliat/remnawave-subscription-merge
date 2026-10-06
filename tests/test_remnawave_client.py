import json

import httpx
import pytest

from src.remnawave.client import (
    RemnawaveClient,
    RemnawaveNotFound,
    RemnawaveUpstreamError,
)
from src.remnawave.config import RemnawaveConfig


def _config() -> RemnawaveConfig:
    return RemnawaveConfig(
        base_url="https://remna.test",
        api_token="test-token",
        timeout_seconds=5.0,
        secondary_suffix="_addsub",
    )


@pytest.mark.asyncio
async def test_get_user_by_username_sends_bearer_and_encodes_username() -> None:
    seen: list[tuple[str, str]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append((str(request.url), request.headers["authorization"]))
        return httpx.Response(
            200,
            json={
                "response": {
                    "id": 1,
                    "username": "alice test",
                    "shortUuid": "main-a",
                    "status": "ACTIVE",
                    "subscriptionUrl": "https://sub.example/main-a",
                    "expireAt": "2026-12-31T00:00:00Z",
                }
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    async with RemnawaveClient(_config(), client) as users:
        user = await users.get_user_by_username("alice test")

    await client.aclose()

    assert seen == [
        (
            "https://remna.test/api/users/by-username/alice%20test",
            "Bearer test-token",
        )
    ]
    assert user.id == 1
    assert user.username == "alice test"
    assert user.short_uuid == "main-a"
    assert user.subscription_url == "https://sub.example/main-a"
    assert user.expire_at == "2026-12-31T00:00:00Z"


@pytest.mark.asyncio
async def test_get_user_accepts_root_level_response_shape() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "id": 1,
                "username": "alice",
                "shortUuid": "main-a",
                "status": "ACTIVE",
                "subscriptionUrl": "https://sub.example/main-a",
            },
        )

    async with RemnawaveClient(_config(), httpx.AsyncClient(transport=httpx.MockTransport(handler))) as users:
        user = await users.get_user_by_username("alice")

    assert user.username == "alice"


@pytest.mark.asyncio
async def test_not_found_is_mapped_to_safe_exception() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, text="secret upstream body")

    async with RemnawaveClient(_config(), httpx.AsyncClient(transport=httpx.MockTransport(handler))) as users:
        with pytest.raises(RemnawaveNotFound, match="resource not found"):
            await users.get_user_by_username("missing")


@pytest.mark.asyncio
async def test_upstream_http_error_does_not_include_response_body() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="private diagnostic and token")

    async with RemnawaveClient(_config(), httpx.AsyncClient(transport=httpx.MockTransport(handler))) as users:
        with pytest.raises(RemnawaveUpstreamError) as exc:
            await users.get_user_by_username("alice")

    assert str(exc.value) == "Remnawave returned HTTP 500"
    assert "private" not in str(exc.value)
    assert "token" not in str(exc.value)


@pytest.mark.asyncio
async def test_invalid_json_is_mapped_to_safe_exception() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="not json")

    async with RemnawaveClient(_config(), httpx.AsyncClient(transport=httpx.MockTransport(handler))) as users:
        with pytest.raises(RemnawaveUpstreamError, match="invalid JSON"):
            await users.get_user_by_username("alice")


@pytest.mark.asyncio
async def test_incomplete_user_response_is_rejected() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"response": {"id": 1, "username": "alice"}},
        )

    async with RemnawaveClient(_config(), httpx.AsyncClient(transport=httpx.MockTransport(handler))) as users:
        with pytest.raises(RemnawaveUpstreamError, match="incomplete user response"):
            await users.get_user_by_username("alice")


@pytest.mark.asyncio
async def test_a2_pair_derives_secondary_from_main_username_and_rejects_same_id() -> None:
    requested: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requested.append(request.url.path)
        username = request.url.path.rsplit("/", 1)[-1]
        return httpx.Response(
            200,
            json={
                "response": {
                    "id": 7,
                    "username": username,
                    "shortUuid": username,
                    "status": "ACTIVE",
                    "subscriptionUrl": f"https://sub.example/{username}",
                }
            },
        )

    async with RemnawaveClient(_config(), httpx.AsyncClient(transport=httpx.MockTransport(handler))) as users:
        with pytest.raises(RemnawaveUpstreamError, match="same Remnawave user twice"):
            await users.resolve_a2_pair("alice")

    assert requested == [
        "/api/users/by-username/alice",
        "/api/users/by-username/alice_addsub",
    ]


@pytest.mark.asyncio
async def test_get_user_by_short_uuid_uses_short_uuid_endpoint() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/users/by-short-uuid/main-a"
        return httpx.Response(200, json={"response": {
            "id": 1,
            "username": "alice",
            "shortUuid": "main-a",
            "status": "ACTIVE",
            "subscriptionUrl": "https://sub.example/main-a",
        }})

    async with RemnawaveClient(_config(), httpx.AsyncClient(transport=httpx.MockTransport(handler))) as users:
        user = await users.get_user_by_short_uuid("main-a")

    assert user.username == "alice"


@pytest.mark.asyncio
async def test_identifier_resolution_prefers_short_uuid_then_secondary_username() -> None:
    requested: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requested.append(request.url.path)
        if request.url.path == "/api/users/by-short-uuid/main-a":
            return httpx.Response(200, json={"response": {
                "id": 1, "username": "alice", "shortUuid": "main-a",
                "status": "ACTIVE", "subscriptionUrl": "https://sub.example/main-a",
            }})
        assert request.url.path == "/api/users/by-username/alice_addsub"
        return httpx.Response(200, json={"response": {
            "id": 2, "username": "alice_addsub", "shortUuid": "add-a",
            "status": "ACTIVE", "subscriptionUrl": "https://sub.example/add-a",
        }})

    async with RemnawaveClient(_config(), httpx.AsyncClient(transport=httpx.MockTransport(handler))) as users:
        main, secondary = await users.resolve_a2_pair_identifier("main-a")

    assert main.username == "alice"
    assert secondary.username == "alice_addsub"
    assert requested == [
        "/api/users/by-short-uuid/main-a",
        "/api/users/by-username/alice_addsub",
    ]
