plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.amirnohekhan.tsdl"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.amirnohekhan.tsdl"
        minSdk = 23
        targetSdk = 36
        versionCode = 1
        versionName = "0.1.0"

        val apiBaseUrl = providers.gradleProperty("TSDL_API_BASE_URL")
            .orElse("http://10.0.2.2:8080")
            .get()
        val tileUrl = providers.gradleProperty("TSDL_OSM_TILE_URL")
            .orElse("https://tile.openstreetmap.org/{z}/{x}/{y}.png")
            .get()
        buildConfigField("String", "TSDL_API_BASE_URL", "\"$apiBaseUrl\"")
        buildConfigField("String", "TSDL_OSM_TILE_URL", "\"$tileUrl\"")
    }

    buildFeatures {
        buildConfig = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    implementation("org.maplibre.gl:android-sdk-opengl:11.8.0")
}

