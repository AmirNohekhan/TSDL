"""GeoJSON serialization shared by API tests and the HTTP layer."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class InventoryMapRow:
    id: UUID
    sign_type: str
    sign_text: str
    latitude: float
    longitude: float
    first_seen_at: datetime
    last_seen_at: datetime
    horizontal_accuracy_m: float
    observation_count: int


def feature_collection(rows: Iterable[InventoryMapRow]) -> dict[str, Any]:
    """Create RFC 7946 longitude/latitude Point features."""
    features: list[dict[str, Any]] = []
    for row in rows:
        features.append(
            {
                "type": "Feature",
                "id": str(row.id),
                "geometry": {
                    "type": "Point",
                    "coordinates": [row.longitude, row.latitude],
                },
                "properties": {
                    "sign_type": row.sign_type,
                    "sign_text": row.sign_text,
                    "first_seen_at": row.first_seen_at.isoformat(),
                    "last_seen_at": row.last_seen_at.isoformat(),
                    "horizontal_accuracy_m": row.horizontal_accuracy_m,
                    "observation_count": row.observation_count,
                },
            }
        )
    return {"type": "FeatureCollection", "features": features}
