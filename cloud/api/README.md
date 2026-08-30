# Cloud inventory map API

The Cloud Run-compatible service exposes:

- `GET /` — interactive Leaflet/OpenStreetMap inventory map;
- `GET /v1/signs.geojson?bbox=west,south,east,north` — bounded inventory features;
- `GET /healthz` — process health.

The API queries the PostGIS table created by `cloud/database/migrations/001_inventory.sql`.
Set `DATABASE_URL` to a PostgreSQL connection URI, then run:

```bash
python -m pip install -e cloud/api
uvicorn tsdl_cloud.app:application_from_environment --factory --reload
```

For Cloud Run, build `cloud/api/Dockerfile` and inject `DATABASE_URL` through Secret Manager.
Do not put database credentials in an image, source file, Gradle property, or GitHub secret that
is exposed to pull requests.

The map queries only its visible bounding box and HTML-escapes inventory values shown in popups.
The public OSM Standard raster endpoint is a development default, not production infrastructure.
Before public deployment, configure an approved OSM-derived tile provider or self-hosted tiles.

