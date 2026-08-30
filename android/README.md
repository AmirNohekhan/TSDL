# Android inventory map

The app renders the cloud inventory through MapLibre Native and the versioned GeoJSON endpoint.
Each marker opens sign type, interpreted text/value, coordinates, first/last timestamps, and
observation count. The map requests only the current viewport.

Open the `android` directory in Android Studio. Set these Gradle properties in your user-level
`gradle.properties` or on the command line:

```properties
TSDL_API_BASE_URL=https://your-cloud-run-service.example
TSDL_OSM_TILE_URL=https://your-approved-osm-provider/{z}/{x}/{y}.png
```

The debug default API URL is `http://10.0.2.2:8080`, which reaches a backend running on the host
from the Android emulator. Cleartext traffic is enabled in the debug manifest only; release
builds reject cleartext and must use HTTPS.

The development tile default is OSM Standard. It is for ordinary interactive viewing only: do
not bulk download, prefetch, or build offline packs from `tile.openstreetmap.org`. Production
deployments must use a provider/self-hosted service sized and licensed for expected traffic.
Visible OSM attribution is provided by the map style.
