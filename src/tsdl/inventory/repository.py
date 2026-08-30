"""Reference inventory matching and lifecycle behavior.

The cloud implementation performs the same operation transactionally in PostGIS.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta

from .models import SignCandidate, TrafficSignRecord, require_aware

EARTH_MEAN_RADIUS_M = 6_371_008.8


def haversine_distance_m(
    latitude_a: float, longitude_a: float, latitude_b: float, longitude_b: float
) -> float:
    latitude_a_rad = math.radians(latitude_a)
    latitude_b_rad = math.radians(latitude_b)
    latitude_delta = latitude_b_rad - latitude_a_rad
    longitude_delta = math.radians(longitude_b - longitude_a)
    haversine = (
        math.sin(latitude_delta / 2.0) ** 2
        + math.cos(latitude_a_rad)
        * math.cos(latitude_b_rad)
        * math.sin(longitude_delta / 2.0) ** 2
    )
    return 2.0 * EARTH_MEAN_RADIUS_M * math.asin(min(1.0, math.sqrt(haversine)))


@dataclass(frozen=True)
class MatchPolicy:
    tolerance_m: float = 5.0

    def __post_init__(self) -> None:
        if self.tolerance_m <= 0:
            raise ValueError("Deduplication tolerance must be positive")


class InMemoryInventory:
    """Deterministic reference implementation for inventory matching tests."""

    def __init__(self, policy: MatchPolicy | None = None) -> None:
        self.policy = policy or MatchPolicy()
        self._records: dict[object, TrafficSignRecord] = {}

    @property
    def records(self) -> tuple[TrafficSignRecord, ...]:
        return tuple(self._records.values())

    def add_or_observe(self, candidate: SignCandidate) -> tuple[TrafficSignRecord, bool]:
        """Return `(record, created)` after matching type, meaning, and position."""
        candidates = [
            record
            for record in self._records.values()
            if record.sign_type == candidate.sign_type
            and record.sign_text == candidate.sign_text
            and haversine_distance_m(
                record.latitude,
                record.longitude,
                candidate.latitude,
                candidate.longitude,
            )
            <= self.policy.tolerance_m
        ]
        if candidates:
            closest = min(
                candidates,
                key=lambda record: haversine_distance_m(
                    record.latitude,
                    record.longitude,
                    candidate.latitude,
                    candidate.longitude,
                ),
            )
            updated = closest.observe(candidate)
            self._records[closest.id] = updated
            return updated, False
        created = TrafficSignRecord.from_candidate(candidate)
        self._records[created.id] = created
        return created, True

    def not_seen_since(
        self, reference_time: datetime, missing_after: timedelta
    ) -> tuple[TrafficSignRecord, ...]:
        """Return assets whose last sighting predates a configurable threshold.

        Absence is evidence for review, not automatic proof that a sign was removed.
        """
        reference_time = require_aware(reference_time)
        if missing_after < timedelta(0):
            raise ValueError("missing_after cannot be negative")
        cutoff = reference_time - missing_after
        return tuple(record for record in self._records.values() if record.last_seen_at < cutoff)

