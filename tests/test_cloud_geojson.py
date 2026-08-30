from datetime import UTC, datetime
from uuid import UUID

from tsdl_cloud.geojson import InventoryMapRow, feature_collection


def test_geojson_uses_longitude_latitude_order() -> None:
    row = InventoryMapRow(
        id=UUID("d34ba71b-c3bb-4c22-b147-422ac5bd3bdb"),
        sign_type="STOP",
        sign_text="STOP",
        latitude=39.128473,
        longitude=-77.154821,
        first_seen_at=datetime(2026, 8, 1, tzinfo=UTC),
        last_seen_at=datetime(2026, 8, 2, tzinfo=UTC),
        horizontal_accuracy_m=2.7,
        observation_count=4,
    )
    collection = feature_collection([row])
    feature = collection["features"][0]
    assert feature["geometry"]["coordinates"] == [-77.154821, 39.128473]
    assert feature["properties"]["last_seen_at"] == "2026-08-02T00:00:00+00:00"
