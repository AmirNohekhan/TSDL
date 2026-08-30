from datetime import UTC, datetime
from uuid import UUID

from fastapi.testclient import TestClient
from tsdl_cloud.app import create_app
from tsdl_cloud.geojson import InventoryMapRow


class FakeInventoryRepository:
    def __init__(self) -> None:
        self.last_query: tuple[float, float, float, float, int] | None = None

    def within_bounds(
        self, west: float, south: float, east: float, north: float, limit: int
    ) -> list[InventoryMapRow]:
        self.last_query = (west, south, east, north, limit)
        return [
            InventoryMapRow(
                UUID("d34ba71b-c3bb-4c22-b147-422ac5bd3bdb"),
                "STOP",
                "STOP",
                39.1,
                -77.1,
                datetime(2026, 8, 1, tzinfo=UTC),
                datetime(2026, 8, 2, tzinfo=UTC),
                2.0,
                3,
            )
        ]


def test_geojson_endpoint_passes_bounds_and_returns_feature() -> None:
    repository = FakeInventoryRepository()
    client = TestClient(create_app(repository))
    response = client.get("/v1/signs.geojson?bbox=-78,38,-76,40&limit=100")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/geo+json")
    assert repository.last_query == (-78.0, 38.0, -76.0, 40.0, 100)
    assert response.json()["features"][0]["geometry"]["coordinates"] == [-77.1, 39.1]


def test_geojson_endpoint_rejects_unordered_bounds() -> None:
    client = TestClient(create_app(FakeInventoryRepository()))
    response = client.get("/v1/signs.geojson?bbox=-76,38,-78,40")
    assert response.status_code == 422


def test_cloud_map_is_served() -> None:
    client = TestClient(create_app(FakeInventoryRepository()))
    response = client.get("/")
    assert response.status_code == 200
    assert "TSDL Traffic Sign Inventory" in response.text
