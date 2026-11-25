# App de WastedMap para Android

La app muestra wastedmap.com adentro (WebView) con anuncios de Google AdMob:

- **Banner** fijo abajo, fuera de la página.
- **Pantalla completa** al abrir una guía: una cada 5 guías y como mucho una cada 90 segundos
  (`Ads.EVERY` y `Ads.GAP_MS` en `Ads.kt`).
- **Consentimiento**: el aviso de Google (UMP) aparece solo donde la ley lo pide (Europa, Reino Unido, Suiza).
  En la política de privacidad del sitio hay un enlace "Opciones de privacidad de anuncios" que solo se ve
  dentro de la app cuando hace falta (`wastedmap://privacy-options`).

Otras cosas que hace: abre la última página que viste (o la portada en el idioma del teléfono), los enlaces
de afuera (YouTube, Telegram, mail) se abren en su app, deslizar hacia abajo recarga, los videos van a pantalla
completa, y si no hay internet muestra un aviso con "Reintentar". El sitio la reconoce porque el User-Agent
termina en `WastedMapApp/<versión>`.

## Compilar

```
cd android
./gradlew assembleDebug     # versión de prueba: app/build/outputs/apk/debug/app-debug.apk
./gradlew bundleRelease     # para Play Store: app/build/outputs/bundle/release/app-release.aab
```

Necesita el SDK de Android (la ruta va en `local.properties`, que no se sube) y Java 17 o más nuevo.

## Antes de subirla a Play Store

1. **IDs de AdMob**: en `gradle.properties` completá `admobAppId`, `admobBannerId` y `admobInterstitialId`
   con los de tu cuenta de AdMob. Mientras estén vacíos, la versión final usa los anuncios de prueba de Google.
   La versión de prueba (debug) usa siempre los de prueba, para no generar clics inválidos.
2. **Firma**: creá la clave una sola vez y guardala en un lugar seguro (si la perdés, no podés actualizar la app):
   ```
   keytool -genkeypair -v -keystore wastedmap-release.jks -alias wastedmap -keyalg RSA -keysize 2048 -validity 10000
   ```
   Después creá `android/keystore.properties` (no se sube al repo):
   ```
   storeFile=wastedmap-release.jks
   storePassword=...
   keyAlias=wastedmap
   keyPassword=...
   ```
3. **Versión**: en cada actualización subí `versionCode` (y `versionName`) en `app/build.gradle.kts`.
4. **app-ads.txt**: cuando tengas el ID de editor de AdMob (`pub-...`), va en `docs/app-ads.txt` del sitio.
