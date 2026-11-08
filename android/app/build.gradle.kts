plugins { id("com.android.application") }

// Adresse, von der die App ihre Oberfläche lädt (wird beim Bauen auf GitHub gesetzt).
// Leer = nur die eingebaute Version aus assets/www verwenden.
val webUrl: String = (project.findProperty("webUrl") as String?) ?: ""

android {
    namespace = "de.klaviertrainer.app"
    compileSdk = 35
    defaultConfig {
        applicationId = "de.klaviertrainer.app"
        minSdk = 26
        targetSdk = 35
        versionCode = 3
        versionName = "0.3"
        buildConfigField("String", "WEB_URL", "\"$webUrl\"")
    }
    signingConfigs {
        create("klavier") {
            storeFile = file("klavier.keystore")
            storePassword = "klavier123"
            keyAlias = "klavier"
            keyPassword = "klavier123"
        }
    }
    buildTypes {
        debug { signingConfig = signingConfigs.getByName("klavier") }
        release { isMinifyEnabled = false; signingConfig = signingConfigs.getByName("klavier") }
    }
    buildFeatures { buildConfig = true }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

dependencies { implementation("androidx.webkit:webkit:1.12.1") }
