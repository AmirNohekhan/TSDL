# Cloud inventory database

The canonical inventory has six required user-facing values: `sign_type`, `sign_text`,
`latitude`, `longitude`, `first_seen_at`, and `last_seen_at`. Stable ID, coordinate accuracy,
observation count, and audit timestamps are retained because safe synchronization and honest
geolocation require them.

Deduplication is an atomic ingestion operation, not a unique constraint on rounded coordinates.
Within one transaction, ingestion must:

1. take an advisory lock derived from the candidate's spatial cell and identity;
2. find the nearest row with equal canonical `sign_type` and `sign_text` using
   `ST_DWithin(location, candidate_location, tolerance_m)`;
3. update `first_seen_at = LEAST(...)`, `last_seen_at = GREATEST(...)`, and increment
   `observation_count`, refining coordinates only under the approved accuracy policy; or
4. insert a new row when no match exists.

The API supplies a bounded, server-configured tolerance (initial proposal: 5 m). Client-provided
tolerance is not trusted. Type and text are part of identity so nearby distinct signs are not
collapsed merely because their uncertainty regions overlap. Direction/road-side evidence will
be added before intersection-scale production use.

The recency view exposes how long each asset has gone unseen. A scheduled report can label rows
`POSSIBLY_MISSING` after a configurable number of comparable completed survey passes. The system
must not declare a sign removed after one missed detection because occlusion, route coverage,
weather, or model recall can produce absence.

