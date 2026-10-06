"""HTTP entry point for the client-facing merged subscription."""

import asyncio

import httpx
from fastapi import FastAPI, HTTPException, Request, Response

from src.merge import merge_payloads
from src.metadata import merge_userinfo
from src.merge_pairs import build_router
from src.pair_store import PairStore
from src.rezeis import RezeisClient
from src.remnawave.client import RemnawaveClient, RemnawaveError
from src.remnawave.config import RemnawaveConfig
from src.remnawave.subscription import RemnawaveSubscriptionClient

app = FastAPI(title="Remnawave Subscription Merge")

_FORWARD_HEADERS = ("user-agent", "x-hwid", "x-device-os", "x-ver-os", "x-device-model")
_RESPONSE_HEADERS = (
    "content-disposition",
    "support-url",
    "profile-title",
    "profile-update-interval",
    "x-hwid-active",
    "x-hwid-limit",
    "x-hwid-not-supported",
)

_config = RemnawaveConfig.from_env()
_pair_store = PairStore(_config.merge_data_dir)
_rezeis_client = RezeisClient(_config.rezeis_base_url, _config.timeout_seconds)
app.include_router(build_router(_pair_store, _rezeis_client))


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


async def _render_pair(pair_id: str, request: Request, suffix: str = "") -> Response:
    pair = _pair_store.get(pair_id)
    if pair is None:
        raise HTTPException(status_code=404, detail="merge pair not found")

    try:
        request_headers = {
            key: value for key, value in request.headers.items() if key in _FORWARD_HEADERS
        }
        config = RemnawaveConfig.from_env()
        async with httpx.AsyncClient(
            timeout=config.timeout_seconds, follow_redirects=False
        ) as client:
            subscriptions = RemnawaveSubscriptionClient(config, client)
            first, second = await asyncio.gather(
                subscriptions.fetch_public(pair.main_url, request_headers, suffix=suffix),
                subscriptions.fetch_public(
                    pair.secondary_url, request_headers, suffix=suffix
                ),
            )

        body, content_type = merge_payloads(
            first.body,
            second.body,
            secondary_label=pair.secondary_label,
        )
        headers = {"Cache-Control": "no-store"}
        for key in _RESPONSE_HEADERS:
            value = first.headers.get(key)
            if value:
                headers[key] = value

        userinfo = merge_userinfo(
            first.headers.get("subscription-userinfo"),
            second.headers.get("subscription-userinfo"),
        )
        if userinfo is not None:
            headers["subscription-userinfo"] = userinfo
        return Response(content=body, media_type=content_type, headers=headers)
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="subscription upstream timeout") from exc
    except (httpx.HTTPError, ValueError, RemnawaveError) as exc:
        raise HTTPException(status_code=502, detail="subscription upstream error") from exc


async def _merged_subscription(identifier: str, request: Request, suffix: str = "") -> Response:
    try:
        config = RemnawaveConfig.from_env()
        request_headers = {
            key: value for key, value in request.headers.items() if key in _FORWARD_HEADERS
        }

        async with RemnawaveClient(config) as users:
            main, secondary = await users.resolve_a2_pair_identifier(identifier)
            subscriptions = RemnawaveSubscriptionClient(config, users.http_client)
            first, second = await asyncio.gather(
                subscriptions.fetch_public(main.subscription_url, request_headers, suffix=suffix),
                subscriptions.fetch_public(
                    secondary.subscription_url, request_headers, suffix=suffix
                ),
            )

        body, content_type = merge_payloads(
            first.body, second.body, secondary_label=config.secondary_label
        )
        headers = {"Cache-Control": "no-store"}
        for key in _RESPONSE_HEADERS:
            value = first.headers.get(key)
            if value:
                headers[key] = value

        userinfo = merge_userinfo(
            first.headers.get("subscription-userinfo"),
            second.headers.get("subscription-userinfo"),
        )
        if userinfo is not None:
            headers["subscription-userinfo"] = userinfo

        # profile-web-page-url points to one individual subscription and would
        # be misleading after merging, so it is intentionally omitted.
        return Response(content=body, media_type=content_type, headers=headers)
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="subscription upstream timeout") from exc
    except (httpx.HTTPError, ValueError, RemnawaveError) as exc:
        raise HTTPException(status_code=502, detail="subscription upstream error") from exc


@app.get("/sub/{identifier}")
async def merged_subscription(identifier: str, request: Request) -> Response:
    return await _merged_subscription(identifier, request)


@app.get("/sub/{identifier}/json")
async def merged_xray_json_subscription(identifier: str, request: Request) -> Response:
    return await _merged_subscription(identifier, request, suffix="json")


@app.get("/sub/{identifier}/singbox")
async def merged_singbox_subscription(identifier: str, request: Request) -> Response:
    return await _merged_subscription(identifier, request, suffix="singbox")


@app.get("/sub/merge/{pair_id}")
async def merged_selected_subscription(pair_id: str, request: Request) -> Response:
    return await _render_pair(pair_id, request)


@app.get("/sub/merge/{pair_id}/json")
async def merged_selected_xray_subscription(pair_id: str, request: Request) -> Response:
    return await _render_pair(pair_id, request, suffix="json")


@app.get("/sub/merge/{pair_id}/singbox")
async def merged_selected_singbox_subscription(pair_id: str, request: Request) -> Response:
    return await _render_pair(pair_id, request, suffix="singbox")
