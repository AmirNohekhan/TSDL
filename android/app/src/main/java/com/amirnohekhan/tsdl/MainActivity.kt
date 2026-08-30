package com.amirnohekhan.tsdl

import android.app.Activity
import android.app.AlertDialog
import android.os.Bundle
import android.view.Gravity
import android.widget.FrameLayout
import android.widget.ProgressBar
import android.widget.TextView
import org.json.JSONArray
import org.json.JSONObject
import org.maplibre.android.MapLibre
import org.maplibre.android.camera.CameraPosition
import org.maplibre.android.geometry.LatLng
import org.maplibre.android.maps.MapView
import org.maplibre.android.maps.MapLibreMap
import org.maplibre.android.maps.Style
import org.maplibre.android.style.layers.CircleLayer
import org.maplibre.android.style.layers.PropertyFactory.circleColor
import org.maplibre.android.style.layers.PropertyFactory.circleRadius
import org.maplibre.android.style.layers.PropertyFactory.circleStrokeColor
import org.maplibre.android.style.layers.PropertyFactory.circleStrokeWidth
import org.maplibre.android.style.sources.GeoJsonSource
import java.util.concurrent.Executors

class MainActivity : Activity() {
    private lateinit var mapView: MapView
    private lateinit var mapLibreMap: MapLibreMap
    private lateinit var status: TextView
    private lateinit var progress: ProgressBar
    private val executor = Executors.newSingleThreadExecutor()
    private val inventoryApi = InventoryApi(BuildConfig.TSDL_API_BASE_URL)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        MapLibre.getInstance(this)
        val root = FrameLayout(this)
        mapView = MapView(this)
        status = TextView(this).apply {
            setBackgroundColor(0xEEFFFFFF.toInt())
            setPadding(20, 12, 20, 12)
            text = "Loading traffic signs…"
        }
        progress = ProgressBar(this)
        root.addView(mapView, FrameLayout.LayoutParams(-1, -1))
        root.addView(status, FrameLayout.LayoutParams(-2, -2).apply {
            gravity = Gravity.TOP or Gravity.CENTER_HORIZONTAL
            topMargin = 24
        })
        root.addView(progress, FrameLayout.LayoutParams(64, 64).apply {
            gravity = Gravity.CENTER
        })
        setContentView(root)
        mapView.onCreate(savedInstanceState)
        mapView.getMapAsync { map ->
            mapLibreMap = map
            map.cameraPosition = CameraPosition.Builder()
                .target(LatLng(39.128473, -77.154821)).zoom(11.0).build()
            map.setStyle(Style.Builder().fromJson(osmStyleJson(BuildConfig.TSDL_OSM_TILE_URL))) { style ->
                style.addSource(GeoJsonSource(SIGNS_SOURCE))
                style.addLayer(
                    CircleLayer(SIGNS_LAYER, SIGNS_SOURCE).withProperties(
                        circleRadius(7f),
                        circleColor("#FCA311"),
                        circleStrokeColor("#14213D"),
                        circleStrokeWidth(2f),
                    ),
                )
                map.addOnMapClickListener { point ->
                    val features = map.queryRenderedFeatures(map.projection.toScreenLocation(point), SIGNS_LAYER)
                    if (features.isNotEmpty()) showSign(InventoryFeature.fromMapFeature(features.first()))
                    features.isNotEmpty()
                }
                map.addOnCameraIdleListener { refreshVisibleInventory() }
                refreshVisibleInventory()
            }
        }
    }

    private fun refreshVisibleInventory() {
        if (!::mapLibreMap.isInitialized) return
        val map = mapLibreMap
        val bounds = map.projection.visibleRegion.latLngBounds
        progress.visibility = android.view.View.VISIBLE
        executor.execute {
            runCatching {
                inventoryApi.signsInBounds(
                    bounds.longitudeWest,
                    bounds.latitudeSouth,
                    bounds.longitudeEast,
                    bounds.latitudeNorth,
                )
            }.onSuccess { collection ->
                runOnUiThread {
                    map.style?.getSourceAs<GeoJsonSource>(SIGNS_SOURCE)?.setGeoJson(collection)
                    val count = collection.features()?.size ?: 0
                    status.text = "$count traffic signs in view"
                    progress.visibility = android.view.View.GONE
                }
            }.onFailure { error ->
                runOnUiThread {
                    status.text = error.message ?: "Unable to load inventory"
                    progress.visibility = android.view.View.GONE
                }
            }
        }
    }

    private fun showSign(sign: InventoryFeature) {
        AlertDialog.Builder(this)
            .setTitle(sign.signType)
            .setMessage(
                "${sign.signText}\n\n" +
                    "Coordinates: %.6f, %.6f\n".format(sign.latitude, sign.longitude) +
                    "First seen: ${sign.firstSeenAt}\n" +
                    "Last seen: ${sign.lastSeenAt}\n" +
                    "Observations: ${sign.observationCount}",
            )
            .setPositiveButton(android.R.string.ok, null)
            .show()
    }

    private fun osmStyleJson(tileUrl: String): String = JSONObject().apply {
        put("version", 8)
        put("name", "TSDL OpenStreetMap")
        put("sources", JSONObject().put("osm", JSONObject().apply {
            put("type", "raster")
            put("tiles", JSONArray().put(tileUrl))
            put("tileSize", 256)
            put("attribution", "© OpenStreetMap contributors")
        }))
        put("layers", JSONArray().put(JSONObject().apply {
            put("id", "osm-tiles")
            put("type", "raster")
            put("source", "osm")
        }))
    }.toString()

    override fun onStart() { super.onStart(); mapView.onStart() }
    override fun onResume() { super.onResume(); mapView.onResume() }
    override fun onPause() { mapView.onPause(); super.onPause() }
    override fun onStop() { mapView.onStop(); super.onStop() }
    override fun onLowMemory() { super.onLowMemory(); mapView.onLowMemory() }
    override fun onDestroy() { executor.shutdownNow(); mapView.onDestroy(); super.onDestroy() }
    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        mapView.onSaveInstanceState(outState)
    }

    companion object {
        private const val SIGNS_SOURCE = "traffic-signs"
        private const val SIGNS_LAYER = "traffic-sign-markers"
    }
}
