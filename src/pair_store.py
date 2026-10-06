"""Persistent operator-selected subscription pairings.

The core middleware remains stateless for A2, while the Rezeis admin integration
needs explicit arbitrary pairings. SQLite keeps those pairings outside Rezeis.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class SubscriptionPair:
    id: str
    main_subscription_id: str
    secondary_subscription_id: str
    main_url: str
    secondary_url: str
    main_label: str
    secondary_label: str
    created_at: str


class PairStore:
    def __init__(self, data_dir: str) -> None:
        self.path = Path(data_dir).expanduser() / "pairs.sqlite3"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS subscription_pairs (
                    id TEXT PRIMARY KEY,
                    main_subscription_id TEXT NOT NULL,
                    secondary_subscription_id TEXT NOT NULL,
                    main_url TEXT NOT NULL,
                    secondary_url TEXT NOT NULL,
                    main_label TEXT NOT NULL,
                    secondary_label TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            db.commit()

    def create(
        self,
        *,
        main_subscription_id: str,
        secondary_subscription_id: str,
        main_url: str,
        secondary_url: str,
        main_label: str,
        secondary_label: str,
    ) -> SubscriptionPair:
        if main_subscription_id == secondary_subscription_id:
            raise ValueError("main and secondary subscriptions must differ")
        pair = SubscriptionPair(
            id=uuid4().hex,
            main_subscription_id=main_subscription_id,
            secondary_subscription_id=secondary_subscription_id,
            main_url=main_url,
            secondary_url=secondary_url,
            main_label=main_label,
            secondary_label=secondary_label,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        with sqlite3.connect(self.path) as db:
            db.execute(
                """
                INSERT INTO subscription_pairs
                (id, main_subscription_id, secondary_subscription_id, main_url,
                 secondary_url, main_label, secondary_label, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pair.id,
                    pair.main_subscription_id,
                    pair.secondary_subscription_id,
                    pair.main_url,
                    pair.secondary_url,
                    pair.main_label,
                    pair.secondary_label,
                    pair.created_at,
                ),
            )
            db.commit()
        return pair

    def get(self, pair_id: str) -> SubscriptionPair | None:
        with sqlite3.connect(self.path) as db:
            row = db.execute(
                """
                SELECT id, main_subscription_id, secondary_subscription_id,
                       main_url, secondary_url, main_label, secondary_label, created_at
                FROM subscription_pairs WHERE id = ?
                """,
                (pair_id,),
            ).fetchone()
        return SubscriptionPair(*row) if row else None

    def list(self) -> list[SubscriptionPair]:
        with sqlite3.connect(self.path) as db:
            rows = db.execute(
                """
                SELECT id, main_subscription_id, secondary_subscription_id,
                       main_url, secondary_url, main_label, secondary_label, created_at
                FROM subscription_pairs ORDER BY created_at DESC
                """
            ).fetchall()
        return [SubscriptionPair(*row) for row in rows]

    def delete(self, pair_id: str) -> bool:
        with sqlite3.connect(self.path) as db:
            cursor = db.execute("DELETE FROM subscription_pairs WHERE id = ?", (pair_id,))
            db.commit()
            return cursor.rowcount == 1
