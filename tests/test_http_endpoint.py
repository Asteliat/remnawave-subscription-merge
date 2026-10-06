import base64

from fastapi.testclient import TestClient

import src.http_endpoint as endpoint
from src.http_endpoint import app
from src.remnawave.client import RemnawaveUser
from src.remnawave.config import RemnawaveConfig
from src.remnawave.subscription import RemnawaveSubscriptionClient, SubscriptionPayload, SubscriptionPayloadError


def test_healthz() -> None:
    response = TestClient(app).get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def _user(user_id: int, username: str, short_uuid: str) -> RemnawaveUser:
    return RemnawaveUser(id=user_id, username=username, short_uuid=short_uuid, status="ACTIVE",
                         subscription_url=f"https://sub.example/{short_uuid}", expire_at=None)


def _payload(body: str, userinfo: str | None = None) -> SubscriptionPayload:
    return SubscriptionPayload(body=body, content_type="text/plain",
                               headers={"subscription-userinfo": userinfo} if userinfo else {})


def _config() -> RemnawaveConfig:
    return RemnawaveConfig(base_url="https://remna.test", api_token="test-token",
                           timeout_seconds=5.0, secondary_suffix="_addsub")


def test_merged_subscription_success_forwards_client_headers(monkeypatch) -> None:
    main = _user(1, "alice", "main-a")
    secondary = _user(2, "alice_addsub", "add-a")
    body_a = base64.b64encode(b"vless://main\n").decode()
    body_b = base64.b64encode(b"vless://secondary\n").decode()
    seen = []

    class FakeUsers:
        def __init__(self, config): assert config.base_url == "https://remna.test"
        http_client = object()
        async def __aenter__(self): return self
        async def __aexit__(self, *args): return None
        async def resolve_a2_pair(self, username): return main, secondary

    class FakeSubscriptions:
        def __init__(self, config, http_client): assert http_client is FakeUsers.http_client
        async def fetch_public(self, subscription_url, request_headers, suffix=""):
            assert suffix == ""
            seen.append((subscription_url, request_headers))
            return {
                "https://sub.example/main-a": _payload(body_a, "download=10;upload=20;total=0;expire=200"),
                "https://sub.example/add-a": _payload(body_b, "download=3;upload=4;total=50;expire=300"),
            }[subscription_url]

    monkeypatch.setattr(endpoint.RemnawaveConfig, "from_env", _config)
    monkeypatch.setattr(endpoint, "RemnawaveClient", FakeUsers)
    monkeypatch.setattr(endpoint, "RemnawaveSubscriptionClient", FakeSubscriptions)
    response = TestClient(app).get("/sub/alice", headers={
        "User-Agent": "v2rayNG/1.10.5", "x-hwid": "test-hwid",
        "x-device-os": "Android", "x-ver-os": "14", "x-device-model": "Test Device",
    })
    assert response.status_code == 200
    assert base64.b64decode(response.text).decode().splitlines() == ["vless://main", "vless://secondary"]
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["subscription-userinfo"] == "upload=24;download=13;total=0;expire=300"
    assert all(item[1] == {
        "user-agent": "v2rayNG/1.10.5", "x-hwid": "test-hwid", "x-device-os": "Android",
        "x-ver-os": "14", "x-device-model": "Test Device",
    } for item in seen)


def test_profile_url_is_not_forwarded(monkeypatch) -> None:
    main = _user(1, "alice", "main-a")
    secondary = _user(2, "alice_addsub", "add-a")
    class FakeUsers:
        def __init__(self, config): assert config.base_url == "https://remna.test"
        http_client = object()
        async def __aenter__(self): return self
        async def __aexit__(self, *args): return None
        async def resolve_a2_pair(self, username): return main, secondary
    class FakeSubscriptions:
        def __init__(self, config, http_client): pass
        async def fetch_public(self, subscription_url, request_headers, suffix=""):
            assert suffix == ""
            return SubscriptionPayload(
                body=base64.b64encode(b"vless://one\n").decode(), content_type="text/plain",
                headers={"subscription-userinfo": "download=0;upload=0;total=0;expire=100",
                         "profile-web-page-url": "https://private.example/one"})
    monkeypatch.setattr(endpoint.RemnawaveConfig, "from_env", _config)
    monkeypatch.setattr(endpoint, "RemnawaveClient", FakeUsers)
    monkeypatch.setattr(endpoint, "RemnawaveSubscriptionClient", FakeSubscriptions)
    response = TestClient(app).get("/sub/alice")
    assert "profile-web-page-url" not in response.headers


def test_upstream_timeout_is_504(monkeypatch) -> None:
    class FakeUsers:
        def __init__(self, config): assert config.base_url == "https://remna.test"
        async def __aenter__(self): return self
        async def __aexit__(self, *args): return None
        async def resolve_a2_pair(self, username):
            raise __import__("httpx").ReadTimeout("timeout")
    monkeypatch.setattr(endpoint.RemnawaveConfig, "from_env", _config)
    monkeypatch.setattr(endpoint, "RemnawaveClient", FakeUsers)
    assert TestClient(app).get("/sub/alice").status_code == 504


def test_malformed_subscription_is_502(monkeypatch) -> None:
    main = _user(1, "alice", "main-a")
    secondary = _user(2, "alice_addsub", "add-a")
    class FakeUsers:
        def __init__(self, config): assert config.base_url == "https://remna.test"
        http_client = object()
        async def __aenter__(self): return self
        async def __aexit__(self, *args): return None
        async def resolve_a2_pair(self, username): return main, secondary
    class FakeSubscriptions:
        def __init__(self, config, http_client): pass
        async def fetch_public(self, subscription_url, request_headers, suffix=""): return _payload("not-valid-base64-%%")
    monkeypatch.setattr(endpoint.RemnawaveConfig, "from_env", _config)
    monkeypatch.setattr(endpoint, "RemnawaveClient", FakeUsers)
    monkeypatch.setattr(endpoint, "RemnawaveSubscriptionClient", FakeSubscriptions)
    assert TestClient(app).get("/sub/alice").status_code == 502


def test_explicit_json_suffix_is_forwarded_to_both_subscriptions(monkeypatch) -> None:
    main = _user(1, "alice", "main-a")
    secondary = _user(2, "alice_addsub", "add-a")
    body = base64.b64encode(b"vless://one\n").decode()
    seen = []

    class FakeUsers:
        def __init__(self, config): pass
        http_client = object()
        async def __aenter__(self): return self
        async def __aexit__(self, *args): return None
        async def resolve_a2_pair(self, username): return main, secondary

    class FakeSubscriptions:
        def __init__(self, config, http_client): pass
        async def fetch_public(self, subscription_url, request_headers, suffix=""):
            seen.append((subscription_url, suffix))
            return _payload(body)

    monkeypatch.setattr(endpoint.RemnawaveConfig, "from_env", _config)
    monkeypatch.setattr(endpoint, "RemnawaveClient", FakeUsers)
    monkeypatch.setattr(endpoint, "RemnawaveSubscriptionClient", FakeSubscriptions)

    response = TestClient(app).get("/sub/alice/json")
    assert response.status_code == 200
    assert [item[1] for item in seen] == ["json", "json"]


def test_explicit_singbox_suffix_is_forwarded_to_both_subscriptions(monkeypatch) -> None:
    main = _user(1, "alice", "main-a")
    secondary = _user(2, "alice_addsub", "add-a")
    body = base64.b64encode(b"vless://one\n").decode()
    seen = []

    class FakeUsers:
        def __init__(self, config): pass
        http_client = object()
        async def __aenter__(self): return self
        async def __aexit__(self, *args): return None
        async def resolve_a2_pair(self, username): return main, secondary

    class FakeSubscriptions:
        def __init__(self, config, http_client): pass
        async def fetch_public(self, subscription_url, request_headers, suffix=""):
            seen.append((subscription_url, suffix))
            return _payload(body)

    monkeypatch.setattr(endpoint.RemnawaveConfig, "from_env", _config)
    monkeypatch.setattr(endpoint, "RemnawaveClient", FakeUsers)
    monkeypatch.setattr(endpoint, "RemnawaveSubscriptionClient", FakeSubscriptions)

    response = TestClient(app).get("/sub/alice/singbox")
    assert response.status_code == 200
    assert [item[1] for item in seen] == ["singbox", "singbox"]



@pytest.mark.asyncio
async def _small_config() -> RemnawaveConfig:
    return RemnawaveConfig(base_url="https://remna.test", api_token="test-token", timeout_seconds=5.0, secondary_suffix="_addsub", max_subscription_bytes=16)


def test_public_subscription_rejects_oversized_content_length() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-length": "17"}, text="x" * 17)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        subscriptions = RemnawaveSubscriptionClient(_small_config(), client)
        with pytest.raises(SubscriptionPayloadError, match="too large"):
            await subscriptions.fetch_public("https://sub.example/alice")


@pytest.mark.asyncio
async def test_public_subscription_rejects_oversized_stream_without_content_length() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="x" * 17)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        subscriptions = RemnawaveSubscriptionClient(_config(), client)
        with pytest.raises(SubscriptionPayloadError, match="too large"):
            await subscriptions.fetch_public("https://sub.example/alice")
