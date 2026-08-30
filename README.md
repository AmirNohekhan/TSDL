# TSDL

TSDL is an offline-first traffic-sign detection, localization, and inventory platform. Its
target pipeline combines on-device YOLO detection, category-specific recognition,
timestamped GNSS/orientation data, multi-view geometry, a local Android inventory, and
optional synchronization to a PostGIS-backed service.

This repository is at **foundation milestone 0/4**, not production ready. It currently
contains a tested Python geometry kernel, a versioned sign taxonomy, architecture and audit
records, and CI. It does **not** yet contain trained weights, measured detector metrics, an
Android APK, or deployed cloud infrastructure.

## Implemented

- Validated pinhole camera intrinsics and pixel-to-ray conversion using the OpenCV optical
  frame (`+x` right, `+y` down, `+z` forward).
- WGS84/ECEF conversion with round-trip tests.
- Weighted least-squares multi-ray triangulation with residual reporting and degeneracy
  rejection.
- A canonical, versioned broad sign taxonomy and explicit second-stage routing.
- Python lint, type-check, and test workflow.

## Development

Python 3.11 or newer is required.

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
pytest
ruff check .
mypy
```

No model files are committed. Model artifacts must enter through a registry with provenance,
license, checksum, taxonomy version, input contract, evaluation record, and promotion status.

## Planned milestone sequence

1. Data adapters, dataset validation, YOLO training/export, and honest evaluation reports.
2. Kotlin/Compose/CameraX application with timestamp buffers, Room, bundled validated models,
   and recorded-session replay.
3. Tracking, temporal consensus, world-ray creation, robust triangulation with uncertainty,
   and local inventory/map/export.
4. Authenticated idempotent Cloud Run sync API, PostGIS inventory, model registry, and safe
   signed model updates.

See [current state](docs/CURRENT_STATE.md), [architecture](docs/ARCHITECTURE.md), and
[geolocation conventions](docs/GEOLOCATION.md). Drivers must never interact with the app
while a vehicle is moving; start mapping while parked or have a passenger operate it.

## Privacy and limitations

The intended default is sign crops only; continuous windshield video upload is out of scope.
Coordinates must always carry method and uncertainty. Current triangulation returns fit
residuals, not a complete uncertainty model, and must not yet be used to commit field assets.
No accuracy, performance, or ML quality claims are made before reproducible evaluation.

