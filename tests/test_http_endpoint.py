import base64
import json

from fastapi.testclient import TestClient

import src.http_endpoint as endpoint
from src.http_endpoint import app
from src.remnawave.client import RemnawaveUser
from src.remnawave.config import RemnawaveConfig
from src.remnawave.subscription import SubscriptionPayload


def test_healthz() -> None:
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def _user(user_id: int, username: str, short_uuid: str) -> RemnawaveUser:
    return RemnawaveUser(
        id=user_id,
        username=username,
        short_uuid=short_uuid,
        status="ACTIVE",
        subscription_url=f"https://example.test/sub/{short_uuid}",
        expire_at=None,
    )


def _payload(body: str, userinfo: str | None = None) -> SubscriptionPayload:
    headers = {}
    if userinfo is not None:
        headers["subscription-userinfo"] = userinfo
    return SubscriptionPayload(body=body, content_type="text/plain", headers=headers)


def test_merged_subscription_success_and_metadata(monkeypatch) -> None:
    main = _user(1, "alice", "main-a")
    secondary = _user(2, "alice_addsub", "add-a")
    line_a = "vmess://main"
    line_b = "vless://secondary"
    body_a = base64.b64encode((line_a + "\n").encode()).decode()
    body_b = base64.b64encode((line_b + "\n").encode()).decode()

    class FakeUsers:
        http_client = object()

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def resolve_a2_pair(self, username):
            assert username == "alice"
            return main, secondary

    class FakeSubscriptions:
        def __init__(self, config, http_client):
            assert http_client is FakeUsers.http_client

        async def fetch_raw(self, short_uuid):
            return {
                "main-a": _payload(body_a, "download=10;upload=20;total=100;expire=200"),
                "add-a": _payload(body_b, "download=3;upload=4;total=50;expire=300"),
            }[short_uuid]

    monkeypatch.setattr(endpoint.RemnawaveConfig, "from_env", lambda: RemnawaveConfig(
        base_url="https://remna.test",
        api_token="test-token",
        timeout_seconds=5.0,
        secondary_suffix="_addsub",
    ))
    monkeypatch.setattr(endpoint, "RemnawaveClient", FakeUsers)
    monkeypatch.setattr(endpoint, "RemnawaveSubscriptionClient", FakeSubscriptions)

    response = TestClient(app).get("/sub/alice")

    assert response.status_code == 200
    decoded = base64.b64decode(response.text).decode()
    assert decoded.splitlines() == [line_a, line_b]
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["subscription-userinfo"] == (
        "download=13;upload=24;total=150;expire=300"
    )


def test_upstream_timeout_is_504(monkeypatch) -> None:
    class FakeUsers:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def resolve_a2_pair(self, username):
            raise __import__("httpx").ReadTimeout("timeout")

    monkeypatch.setattr(endpoint.RemnawaveConfig, "from_env", lambda: RemnawaveConfig(
        base_url="https://remna.test",
        api_token="test-token",
        timeout_seconds=5.0,
        secondary_suffix="_addsub",
    ))
    monkeypatch.setattr(endpoint, "RemnawaveClient", FakeUsers)

    response = TestClient(app).get("/sub/alice")

    assert response.status_code == 504


def test_malformed_subscription_is_502(monkeypatch) -> None:
    main = _user(1, "alice", "main-a")
    secondary = _user(2, "alice_addsub", "add-a")

    class FakeUsers:
        http_client = object()

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def resolve_a2_pair(self, username):
            return main, secondary

    class FakeSubscriptions:
        def __init__(self, config, http_client):
            pass

        async def fetch_raw(self, short_uuid):
            return _payload("not-valid-base64-%%") 

    monkeypatch.setattr(endpoint.RemnawaveConfig, "from_env", lambda: RemnawaveConfig(
        base_url="https://remna.test",
        api_token="test-token",
        timeout_seconds=5.0,
        secondary_suffix="_addsub",
    ))
    monkeypatch.setattr(endpoint, "RemnawaveClient", FakeUsers)
    monkeypatch.setattr(endpoint, "RemnawaveSubscriptionClient", FakeSubscriptions)

    response = TestClient(app).get("/sub/alice")

    assert response.status_code == 502
