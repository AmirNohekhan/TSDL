CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE traffic_sign_inventory (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    sign_type text NOT NULL CHECK (btrim(sign_type) <> ''),
    sign_text text NOT NULL CHECK (btrim(sign_text) <> ''),
    latitude double precision NOT NULL CHECK (latitude BETWEEN -90 AND 90),
    longitude double precision NOT NULL CHECK (longitude BETWEEN -180 AND 180),
    location geography(Point, 4326) GENERATED ALWAYS AS
        (ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)::geography) STORED,
    first_seen_at timestamptz NOT NULL,
    last_seen_at timestamptz NOT NULL,
    horizontal_accuracy_m double precision NOT NULL
        CHECK (horizontal_accuracy_m >= 0),
    observation_count integer NOT NULL DEFAULT 1 CHECK (observation_count > 0),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CHECK (last_seen_at >= first_seen_at)
);

CREATE INDEX traffic_sign_inventory_location_gix
    ON traffic_sign_inventory USING gist (location);

CREATE INDEX traffic_sign_inventory_identity_idx
    ON traffic_sign_inventory (sign_type, sign_text);

-- Assets potentially missing on later surveys remain visible; callers choose an age
-- appropriate for survey frequency instead of treating one missed frame/pass as removal.
CREATE VIEW traffic_sign_inventory_recency AS
SELECT
    inventory.*,
    now() - last_seen_at AS time_since_last_seen
FROM traffic_sign_inventory AS inventory;

