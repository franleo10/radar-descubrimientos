import java.util.Properties
import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

// IDs de prueba de Google: muestran anuncios de ejemplo y no cuentan clics (se usan en debug y mientras
// no estén los reales en gradle.properties).
val testAppId = "ca-app-pub-3940256099942544~3347511713"
val testBannerId = "ca-app-pub-3940256099942544/9214589741"
val testInterstitialId = "ca-app-pub-3940256099942544/1033173712"
fun prop(name: String, fallback: String): String =
    (project.findProperty(name) as String?)?.takeIf { it.isNotBlank() } ?: fallback

// Firma de la versión para Play Store: keystore.properties en android/ o en la carpeta WastedMap-firma del
// usuario (fuera del repo, para que la clave no se suba ni se pierda). storeFile es relativo a ese archivo.
val keystoreFile = listOf(
    rootProject.file("keystore.properties"),
    File(System.getProperty("user.home"), "WastedMap-firma/keystore.properties"),
).firstOrNull { it.exists() }
val keystoreProps = Properties().apply { keystoreFile?.inputStream()?.use { load(it) } }

android {
    namespace = "com.wastedmap.app"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.wastedmap.app"
        minSdk = 24
        targetSdk = 36
        versionCode = 1
        versionName = "1.0"
        buildConfigField("String", "SITE", "\"https://wastedmap.com\"")
    }

    signingConfigs {
        if (keystoreProps.getProperty("storeFile") != null) {
            create("release") {
                storeFile = File(keystoreFile!!.parentFile, keystoreProps.getProperty("storeFile"))
                storePassword = keystoreProps.getProperty("storePassword")
                keyAlias = keystoreProps.getProperty("keyAlias")
                keyPassword = keystoreProps.getProperty("keyPassword")
            }
        }
    }

    buildTypes {
        debug {
            manifestPlaceholders["admobAppId"] = testAppId
            buildConfigField("String", "BANNER_ID", "\"$testBannerId\"")
            buildConfigField("String", "INTERSTITIAL_ID", "\"$testInterstitialId\"")
        }
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            manifestPlaceholders["admobAppId"] = prop("admobAppId", testAppId)
            buildConfigField("String", "BANNER_ID", "\"${prop("admobBannerId", testBannerId)}\"")
            buildConfigField("String", "INTERSTITIAL_ID", "\"${prop("admobInterstitialId", testInterstitialId)}\"")
            signingConfigs.findByName("release")?.let { signingConfig = it }
        }
    }

    buildFeatures { buildConfig = true }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

kotlin {
    compilerOptions { jvmTarget.set(JvmTarget.JVM_17) }
}

dependencies {
    implementation("androidx.core:core-ktx:1.16.0")
    implementation("androidx.appcompat:appcompat:1.7.1")
    implementation("androidx.activity:activity-ktx:1.10.1")
    implementation("androidx.core:core-splashscreen:1.0.1")
    implementation("androidx.swiperefreshlayout:swiperefreshlayout:1.1.0")
    implementation("androidx.webkit:webkit:1.17.1")
    implementation("com.google.android.material:material:1.13.0")
    implementation("com.google.android.gms:play-services-ads:25.4.0")
    implementation("com.google.android.ump:user-messaging-platform:3.2.0")
}
