"""FastAPI application serving inventory GeoJSON and the cloud map."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .geojson import feature_collection
from .repository import InventoryMapRepository, PostgresInventoryMapRepository

STATIC_DIRECTORY = Path(__file__).parent / "static"


def parse_bbox(value: str) -> tuple[float, float, float, float]:
    try:
        west, south, east, north = (float(part) for part in value.split(","))
    except (TypeError, ValueError) as error:
        raise HTTPException(422, "bbox must be west,south,east,north") from error
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        raise HTTPException(422, "bbox coordinates are invalid or unordered")
    return west, south, east, north


def create_app(repository: InventoryMapRepository | None = None) -> FastAPI:
    managed_repository = repository
    if managed_repository is None:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL is required")
        managed_repository = PostgresInventoryMapRepository(database_url)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        if isinstance(managed_repository, PostgresInventoryMapRepository):
            managed_repository.open()
        yield
        if isinstance(managed_repository, PostgresInventoryMapRepository):
            managed_repository.close()

    app = FastAPI(title="TSDL Inventory API", version="1.0.0", lifespan=lifespan)
    app.mount("/static", StaticFiles(directory=STATIC_DIRECTORY), name="static")

    def get_repository() -> InventoryMapRepository:
        return managed_repository

    @app.get("/", include_in_schema=False)
    def map_page() -> FileResponse:
        return FileResponse(STATIC_DIRECTORY / "map.html")

    @app.get("/v1/signs.geojson")
    def signs_geojson(
        bbox: Annotated[str, Query(description="west,south,east,north")],
        limit: Annotated[int, Query(ge=1, le=10_000)] = 5_000,
        inventory: InventoryMapRepository = Depends(get_repository),  # noqa: B008
    ) -> JSONResponse:
        west, south, east, north = parse_bbox(bbox)
        return JSONResponse(
            feature_collection(inventory.within_bounds(west, south, east, north, limit)),
            media_type="application/geo+json",
        )

    @app.get("/healthz", include_in_schema=False)
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


def application_from_environment() -> FastAPI:
    return create_app()
