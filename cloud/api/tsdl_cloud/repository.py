"""Read-only PostGIS inventory access for map clients."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Protocol

from psycopg import Connection
from psycopg.rows import class_row
from psycopg_pool import ConnectionPool

from .geojson import InventoryMapRow


class InventoryMapRepository(Protocol):
    def within_bounds(
        self, west: float, south: float, east: float, north: float, limit: int
    ) -> list[InventoryMapRow]: ...


class PostgresInventoryMapRepository:
    def __init__(self, database_url: str) -> None:
        self._pool: ConnectionPool[Connection[InventoryMapRow]] = ConnectionPool(
            conninfo=database_url,
            kwargs={"row_factory": class_row(InventoryMapRow)},
            min_size=0,
            max_size=5,
            open=False,
        )

    def open(self) -> None:
        self._pool.open()

    def close(self) -> None:
        self._pool.close()

    @contextmanager
    def _connection(self) -> Iterator[Connection[InventoryMapRow]]:
        with self._pool.connection() as connection:
            yield connection

    def within_bounds(
        self, west: float, south: float, east: float, north: float, limit: int
    ) -> list[InventoryMapRow]:
        query = """
            SELECT id, sign_type, sign_text, latitude, longitude,
                   first_seen_at, last_seen_at, horizontal_accuracy_m, observation_count
            FROM traffic_sign_inventory
            WHERE location && ST_MakeEnvelope(%s, %s, %s, %s, 4326)::geography
            ORDER BY last_seen_at DESC
            LIMIT %s
        """
        with self._connection() as connection:
            return list(connection.execute(query, (west, south, east, north, limit)).fetchall())

