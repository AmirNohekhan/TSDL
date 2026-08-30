"""Inventory records shared by ingestion, synchronization, and export."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime
from uuid import UUID, uuid4


def require_aware(timestamp: datetime) -> datetime:
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("Timestamps must be timezone-aware")
    return timestamp.astimezone(UTC)


@dataclass(frozen=True)
class SignCandidate:
    """A geolocated and interpreted physical-sign observation."""

    sign_type: str
    sign_text: str
    latitude: float
    longitude: float
    observed_at: datetime
    horizontal_accuracy_m: float

    def __post_init__(self) -> None:
        if not self.sign_type.strip():
            raise ValueError("sign_type is required")
        if not self.sign_text.strip():
            raise ValueError("sign_text is required; use UNKNOWN when unreadable")
        if not -90.0 <= self.latitude <= 90.0:
            raise ValueError("Latitude must be in [-90, 90]")
        if not -180.0 <= self.longitude <= 180.0:
            raise ValueError("Longitude must be in [-180, 180]")
        if self.horizontal_accuracy_m < 0:
            raise ValueError("Horizontal accuracy cannot be negative")
        object.__setattr__(self, "observed_at", require_aware(self.observed_at))


@dataclass(frozen=True)
class TrafficSignRecord:
    id: UUID
    sign_type: str
    sign_text: str
    latitude: float
    longitude: float
    first_seen_at: datetime
    last_seen_at: datetime
    horizontal_accuracy_m: float
    observation_count: int

    @classmethod
    def from_candidate(cls, candidate: SignCandidate) -> TrafficSignRecord:
        return cls(
            id=uuid4(),
            sign_type=candidate.sign_type,
            sign_text=candidate.sign_text,
            latitude=candidate.latitude,
            longitude=candidate.longitude,
            first_seen_at=candidate.observed_at,
            last_seen_at=candidate.observed_at,
            horizontal_accuracy_m=candidate.horizontal_accuracy_m,
            observation_count=1,
        )

    def observe(self, candidate: SignCandidate) -> TrafficSignRecord:
        """Return the same asset with updated temporal bounds and best coordinate."""
        use_candidate_coordinate = candidate.horizontal_accuracy_m < self.horizontal_accuracy_m
        return replace(
            self,
            latitude=candidate.latitude if use_candidate_coordinate else self.latitude,
            longitude=candidate.longitude if use_candidate_coordinate else self.longitude,
            horizontal_accuracy_m=(
                candidate.horizontal_accuracy_m
                if use_candidate_coordinate
                else self.horizontal_accuracy_m
            ),
            first_seen_at=min(self.first_seen_at, candidate.observed_at),
            last_seen_at=max(self.last_seen_at, candidate.observed_at),
            observation_count=self.observation_count + 1,
        )
