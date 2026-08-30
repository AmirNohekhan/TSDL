package com.amirnohekhan.tsdl

import org.json.JSONObject
import org.maplibre.geojson.Feature
import org.maplibre.geojson.FeatureCollection

data class InventoryFeature(
    val id: String,
    val signType: String,
    val signText: String,
    val longitude: Double,
    val latitude: Double,
    val firstSeenAt: String,
    val lastSeenAt: String,
    val observationCount: Int,
) {
    companion object {
        fun collectionFromGeoJson(body: String): FeatureCollection {
            val root = JSONObject(body)
            require(root.getString("type") == "FeatureCollection") {
                "Inventory response is not a GeoJSON FeatureCollection"
            }
            return FeatureCollection.fromJson(body)
        }

        fun fromMapFeature(feature: Feature): InventoryFeature {
            val point = requireNotNull(feature.geometry() as? org.maplibre.geojson.Point) {
                "Inventory feature must have Point geometry"
            }
            return InventoryFeature(
                id = feature.id() ?: "unknown",
                signType = feature.getStringProperty("sign_type"),
                signText = feature.getStringProperty("sign_text"),
                longitude = point.longitude(),
                latitude = point.latitude(),
                firstSeenAt = feature.getStringProperty("first_seen_at"),
                lastSeenAt = feature.getStringProperty("last_seen_at"),
                observationCount = feature.getNumberProperty("observation_count").toInt(),
            )
        }
    }
}

