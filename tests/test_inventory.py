from datetime import UTC, datetime, timedelta

import pytest

from tsdl.inventory import InMemoryInventory, MatchPolicy, SignCandidate

START = datetime(2026, 8, 1, 12, tzinfo=UTC)


def candidate(
    *,
    sign_type: str = "SPEED_LIMIT",
    sign_text: str = "35 MPH",
    latitude: float = 39.128473,
    longitude: float = -77.154821,
    observed_at: datetime = START,
    accuracy: float = 3.0,
) -> SignCandidate:
    return SignCandidate(
        sign_type,
        sign_text,
        latitude,
        longitude,
        observed_at,
        accuracy,
    )


def test_nearby_same_sign_updates_instead_of_duplicating() -> None:
    inventory = InMemoryInventory(MatchPolicy(tolerance_m=5.0))
    first, created = inventory.add_or_observe(candidate())
    second, created_again = inventory.add_or_observe(
        candidate(latitude=39.128491, observed_at=START + timedelta(days=2))
    )
    assert created is True
    assert created_again is False
    assert second.id == first.id
    assert len(inventory.records) == 1
    assert second.first_seen_at == START
    assert second.last_seen_at == START + timedelta(days=2)
    assert second.observation_count == 2


def test_different_meaning_at_same_coordinates_is_not_collapsed() -> None:
    inventory = InMemoryInventory()
    inventory.add_or_observe(candidate(sign_text="35 MPH"))
    inventory.add_or_observe(candidate(sign_text="25 MPH"))
    assert len(inventory.records) == 2


def test_same_sign_outside_tolerance_is_separate_asset() -> None:
    inventory = InMemoryInventory(MatchPolicy(tolerance_m=5.0))
    inventory.add_or_observe(candidate())
    inventory.add_or_observe(candidate(latitude=39.128573))
    assert len(inventory.records) == 2


def test_missing_report_uses_last_seen_without_deleting() -> None:
    inventory = InMemoryInventory()
    record, _ = inventory.add_or_observe(candidate())
    missing = inventory.not_seen_since(START + timedelta(days=10), timedelta(days=7))
    assert missing == (record,)
    assert inventory.records == (record,)


def test_better_observation_refines_coordinate_but_preserves_first_seen() -> None:
    inventory = InMemoryInventory()
    inventory.add_or_observe(candidate(accuracy=8.0))
    updated, _ = inventory.add_or_observe(
        candidate(latitude=39.12849, observed_at=START + timedelta(hours=1), accuracy=1.0)
    )
    assert updated.latitude == pytest.approx(39.12849)
    assert updated.horizontal_accuracy_m == 1.0
    assert updated.first_seen_at == START


def test_timezone_is_required() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        candidate(observed_at=datetime(2026, 8, 1, 12))  # noqa: DTZ001
