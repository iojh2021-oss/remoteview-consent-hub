plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.remoteview.agent"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.remoteview.agent"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "0.2.0"
        buildConfigField("String", "CONTROL_PLANE_URL", "\"https://127.0.0.1\"")
    }
    buildFeatures { buildConfig = true }
}

dependencies {
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.activity:activity-ktx:1.10.0")
    implementation("androidx.lifecycle:lifecycle-service:2.8.7")
    implementation("androidx.work:work-runtime-ktx:2.10.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.10.1")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.8.0")
}
