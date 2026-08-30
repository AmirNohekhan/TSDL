# Current State Audit

Audit date: 2026-08-30. Repository inspected: `AmirNohekhan/TSDL` via the configured `origin`.

## Initial repository state

The GitHub repository was reachable but empty: it exposed no branches, tags, commits, source
files, datasets, model artifacts, documentation, build definitions, or release assets. The
local workspace was likewise an empty Git repository. Consequently there was no existing
functionality to preserve, no reusable application code, and no obsolete code to remove.

## Foundation added

- Python packaging and CI quality gates.
- Dependency-free camera, geodesy, and weighted ray-intersection primitives with tests.
- Canonical broad-class taxonomy with an explicit recognition strategy per class.
- Architecture, coordinate-convention, risk, and staged delivery documentation.

The geometry work is reusable in offline simulation, model evaluation, backend validation,
and as the behavioral reference for a Kotlin port. The taxonomy is the contract between
datasets, detector outputs, classifiers, Android storage, APIs, and inventory records.

## Missing and technical debt

There is currently no public dataset adapter, reviewed dataset snapshot, YOLO training run,
secondary classifier, model artifact, Android project, recorded-session format, tracker,
sensor fusion, uncertainty propagation, Room schema, map/export UI, backend, PostGIS migration,
authentication, or deployment. There are also no device benchmarks or field results.

The current ray solver minimizes distance to infinite lines; downstream commit logic must
reject negative-depth solutions, insufficient baselines, weak intersection angles, excessive
residuals, and uncertainty above policy limits. Robust outlier rejection and covariance/Monte
Carlo uncertainty remain required. Camera distortion and ENU frame transforms are also pending.

## Migration decision

Because no prior code exists, use a monorepo with independently buildable `android`, `ml`,
`geolocation`/Python, and `cloud` areas sharing versioned contracts in `config`. Do not create
empty modules solely to resemble a desired directory tree. Add each module with working code,
tests, ownership, and documentation when its phase begins.

## Immediate next work

1. Add licensed dataset manifests and adapters without downloading or redistributing data.
2. Implement deterministic split validation and YOLO experiment/run metadata.
3. Select an Android inference runtime only after exporting candidate YOLO models and measuring
   supported operators, latency, memory, and accelerator behavior on target hardware.
4. Build the Android recorded-session replay path before requiring field driving.
5. Port the geometry reference to Kotlin and verify it against common golden test vectors.

