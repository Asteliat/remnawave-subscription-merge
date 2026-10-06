"""HTTP API for operator-selected Rezeis subscription pairs."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from .pair_store import PairStore
from .rezeis import RezeisClient, RezeisError, RezeisNotFound, pair_response
from .remnawave.config import RemnawaveConfig


class PairSide(BaseModel):
    subscription_id: str = Field(min_length=1, max_length=128)
    user_telegram_id: str = Field(min_length=1, max_length=64)
    label: str = Field(default="", max_length=200)


class CreatePairRequest(BaseModel):
    main: PairSide
    secondary: PairSide


def build_router(store: PairStore, rezeis: RezeisClient) -> APIRouter:
    router = APIRouter(prefix="/api/admin/merge", tags=["merge-admin"])

    async def require_admin(authorization: str | None) -> str:
        if not authorization or not authorization.lower().startswith("bearer "):
            raise HTTPException(status_code=401, detail="Rezeis admin bearer token required")
        token = authorization[7:].strip()
        if not token:
            raise HTTPException(status_code=401, detail="Rezeis admin bearer token required")
        try:
            await rezeis.validate_admin(token)
        except RezeisError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
        return token

    @router.get("/pairs")
    async def list_pairs(authorization: str | None = Header(default=None)) -> dict[str, Any]:
        await require_admin(authorization)
        return {"items": [pair_response(pair) for pair in store.list()]}

    @router.post("/pairs")
    async def create_pair(
        body: CreatePairRequest,
        authorization: str | None = Header(default=None),
    ) -> dict[str, Any]:
        token = await require_admin(authorization)
        if body.main.subscription_id == body.secondary.subscription_id:
            raise HTTPException(status_code=400, detail="Choose two different subscriptions")
        try:
            main = await rezeis.get_subscription(
                token, body.main.user_telegram_id, body.main.subscription_id
            )
            secondary = await rezeis.get_subscription(
                token, body.secondary.user_telegram_id, body.secondary.subscription_id
            )
        except RezeisNotFound as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except RezeisError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        main_url = str(main["configUrl"]).strip()
        secondary_url = str(secondary["configUrl"]).strip()
        pair = store.create(
            main_subscription_id=body.main.subscription_id,
            secondary_subscription_id=body.secondary.subscription_id,
            main_url=main_url,
            secondary_url=secondary_url,
            main_label=body.main.label.strip(),
            secondary_label=body.secondary.label.strip(),
        )
        return pair_response(pair)

    @router.delete("/pairs/{pair_id}")
    async def delete_pair(
        pair_id: str, authorization: str | None = Header(default=None)
    ) -> dict[str, bool]:
        await require_admin(authorization)
        if not store.delete(pair_id):
            raise HTTPException(status_code=404, detail="Merge pair not found")
        return {"deleted": True}

    return router
