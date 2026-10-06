"""HTTP entry point for the client-facing merged subscription."""

import httpx
from fastapi import FastAPI, HTTPException, Response

from src.merge import merge_payloads
from src.metadata import merge_userinfo
from src.remnawave.client import RemnawaveClient, RemnawaveError
from src.remnawave.config import RemnawaveConfig
from src.remnawave.subscription import RemnawaveSubscriptionClient

app = FastAPI(title="Remnawave Subscription Merge")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/sub/{username}")
async def merged_subscription(username: str) -> Response:
    try:
        config = RemnawaveConfig.from_env()
        async with RemnawaveClient(config) as users:
            main, secondary = await users.resolve_a2_pair(username)
            subscriptions = RemnawaveSubscriptionClient(config, users.http_client)
            first = await subscriptions.fetch_raw(main.short_uuid)
            second = await subscriptions.fetch_raw(secondary.short_uuid)

        body, content_type = merge_payloads(first.body, second.body)
        headers = {"Cache-Control": "no-store"}

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
