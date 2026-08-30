package com.amirnohekhan.tsdl

import org.maplibre.geojson.FeatureCollection
import java.net.HttpURLConnection
import java.net.URI

class InventoryApi(private val baseUrl: String) {
    fun signsInBounds(west: Double, south: Double, east: Double, north: Double): FeatureCollection {
        val bbox = listOf(west, south, east, north).joinToString(",")
        val endpoint = URI.create("${baseUrl.trimEnd('/')}/v1/signs.geojson?bbox=$bbox").toURL()
        val connection = endpoint.openConnection() as HttpURLConnection
        return try {
            connection.requestMethod = "GET"
            connection.connectTimeout = 10_000
            connection.readTimeout = 15_000
            connection.setRequestProperty("Accept", "application/geo+json, application/json")
            connection.setRequestProperty("User-Agent", "TSDL-Android/${BuildConfig.VERSION_NAME}")
            if (connection.responseCode !in 200..299) {
                throw IllegalStateException("Inventory request failed (${connection.responseCode})")
            }
            InventoryFeature.collectionFromGeoJson(connection.inputStream.bufferedReader().use { it.readText() })
        } finally {
            connection.disconnect()
        }
    }
}

