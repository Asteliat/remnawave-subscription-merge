from pathlib import Path

from src.pair_store import PairStore


def test_pair_store_round_trip(tmp_path: Path) -> None:
    store = PairStore(str(tmp_path))
    pair = store.create(
        main_subscription_id="main-1",
        secondary_subscription_id="secondary-1",
        main_url="https://panel.example/sub/main",
        secondary_url="https://panel.example/sub/secondary",
        main_label="Main",
        secondary_label="AddSub",
    )

    assert store.get(pair.id) == pair
    assert store.list() == [pair]
    assert store.delete(pair.id) is True
    assert store.get(pair.id) is None
    assert store.delete(pair.id) is False


def test_pair_store_rejects_same_subscription(tmp_path: Path) -> None:
    store = PairStore(str(tmp_path))
    try:
        store.create(
            main_subscription_id="same",
            secondary_subscription_id="same",
            main_url="https://panel.example/a",
            secondary_url="https://panel.example/b",
            main_label="",
            secondary_label="",
        )
    except ValueError as exc:
        assert "must differ" in str(exc)
    else:
        raise AssertionError("same subscription pair was accepted")
