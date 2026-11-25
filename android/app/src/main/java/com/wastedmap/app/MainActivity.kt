package com.wastedmap.app

import android.annotation.SuppressLint
import android.content.ActivityNotFoundException
import android.content.Intent
import android.graphics.Bitmap
import android.net.Uri
import android.os.Bundle
import android.util.Log
import android.view.View
import android.view.ViewGroup
import android.webkit.CookieManager
import android.webkit.WebChromeClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.FrameLayout
import androidx.activity.OnBackPressedCallback
import androidx.appcompat.app.AppCompatActivity
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import androidx.core.view.ViewCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import java.util.Locale

/**
 * La app es la web de WastedMap adentro, con un banner de AdMob fijo abajo.
 * - Los enlaces de wastedmap.com se quedan en la app; los demás (YouTube, Telegram, mail) se abren afuera.
 * - Recuerda la última página y, la primera vez, abre la portada en el idioma del teléfono.
 * - El sitio sabe que está en la app porque el User-Agent termina en "WastedMapApp/<versión>".
 */
class MainActivity : AppCompatActivity() {

    private lateinit var web: WebView
    private lateinit var refresh: SwipeRefreshLayout
    private lateinit var offline: View
    private lateinit var ads: Ads
    private var fullscreenView: View? = null
    private var fullscreenCallback: WebChromeClient.CustomViewCallback? = null
    private var mainFrameError = false

    private val site = Uri.parse(BuildConfig.SITE)
    private val prefs by lazy { getSharedPreferences("app", MODE_PRIVATE) }

    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Pantalla de borde a borde: la barra de estado y la de navegación no tapan la página.
        WindowCompat.setDecorFitsSystemWindows(window, false)
        val root = findViewById<View>(R.id.root)
        ViewCompat.setOnApplyWindowInsetsListener(root) { v, insets ->
            val bars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(bars.left, bars.top, bars.right, bars.bottom)
            insets
        }
        WindowInsetsControllerCompat(window, root).isAppearanceLightStatusBars = true

        web = findViewById(R.id.web)
        refresh = findViewById(R.id.refresh)
        offline = findViewById(R.id.offline)
        findViewById<Button>(R.id.retry).setOnClickListener { offline.visibility = View.GONE; web.reload() }
        refresh.setColorSchemeColors(getColor(R.color.pink))
        refresh.setOnRefreshListener { web.reload() }

        setupWebView()
        ads = Ads(this, findViewById(R.id.banner))
        ads.start()

        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                when {
                    fullscreenView != null -> exitFullscreen()
                    web.canGoBack() -> web.goBack()
                    else -> { isEnabled = false; onBackPressedDispatcher.onBackPressed() }
                }
            }
        })

        // Si la pantalla se volvió a crear (por ejemplo, al girar), recupera la página; si no hay nada que
        // recuperar, carga la de inicio.
        val restored = savedInstanceState?.let { web.restoreState(it) }
        if (restored == null || web.url.isNullOrEmpty()) {
            Log.d("WastedMap", "cargando ${startUrl(intent)}")
            web.loadUrl(startUrl(intent))
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        intent.data?.takeIf { isOurs(it) }?.let { web.loadUrl(it.toString()) }
    }

    /** Un enlace a wastedmap.com, la última página vista o la portada en el idioma del teléfono. */
    private fun startUrl(intent: Intent?): String {
        intent?.data?.takeIf { isOurs(it) }?.let { return it.toString() }
        prefs.getString("last", null)?.let { return it }
        return when (Locale.getDefault().language) {
            "pt" -> "${BuildConfig.SITE}/pt/"
            "es" -> "${BuildConfig.SITE}/"
            else -> "${BuildConfig.SITE}/en/"
        }
    }

    private fun isOurs(uri: Uri): Boolean =
        uri.scheme == "https" && (uri.host == site.host || uri.host?.endsWith("." + site.host) == true)

    @SuppressLint("SetJavaScriptEnabled")
    private fun setupWebView() {
        web.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true            // "Mi lista", el 100 % y los trofeos se guardan acá
            mediaPlaybackRequiresUserGesture = true
            userAgentString = "$userAgentString WastedMapApp/${BuildConfig.VERSION_NAME}"
        }
        CookieManager.getInstance().apply {
            setAcceptCookie(true)
            setAcceptThirdPartyCookies(web, true)   // el anti-robots de los comentarios y los videos
        }

        web.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                val uri = request.url
                if (uri.scheme == "wastedmap" && uri.host == "privacy-options") {
                    ads.showPrivacyOptions(); return true
                }
                if (!isOurs(uri)) { openOutside(uri); return true }
                if (request.isForMainFrame && uri.path?.contains("/d/") == true && !request.isRedirect) {
                    // Al abrir una guía puede tocar anuncio de pantalla completa: se muestra antes de entrar.
                    ads.onGuideOpened { view.loadUrl(uri.toString()) }
                    return true
                }
                return false
            }

            override fun onPageStarted(view: WebView, url: String, favicon: Bitmap?) {
                mainFrameError = false
            }

            override fun onPageFinished(view: WebView, url: String) {
                refresh.isRefreshing = false
                if (!mainFrameError) {
                    offline.visibility = View.GONE
                    prefs.edit().putString("last", url).apply()
                }
                // Avisa a la página si hay que mostrar "Opciones de privacidad de anuncios".
                if (ads.privacyOptionsRequired()) {
                    view.evaluateJavascript("document.documentElement.classList.add('app-privacy')", null)
                }
            }

            override fun onReceivedError(view: WebView, request: WebResourceRequest, error: WebResourceError) {
                if (request.isForMainFrame) {
                    mainFrameError = true
                    refresh.isRefreshing = false
                    offline.visibility = View.VISIBLE
                }
            }
        }

        // Videos de YouTube a pantalla completa.
        web.webChromeClient = object : WebChromeClient() {
            override fun onShowCustomView(view: View, callback: CustomViewCallback) {
                if (fullscreenView != null) { callback.onCustomViewHidden(); return }
                fullscreenView = view
                fullscreenCallback = callback
                (window.decorView as ViewGroup).addView(view, FrameLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
                WindowInsetsControllerCompat(window, view).apply {
                    hide(WindowInsetsCompat.Type.systemBars())
                    systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
                }
            }

            override fun onHideCustomView() = exitFullscreen()
        }
    }

    private fun exitFullscreen() {
        val view = fullscreenView ?: return
        (window.decorView as ViewGroup).removeView(view)
        WindowInsetsControllerCompat(window, window.decorView).show(WindowInsetsCompat.Type.systemBars())
        fullscreenCallback?.onCustomViewHidden()
        fullscreenView = null
        fullscreenCallback = null
    }

    private fun openOutside(uri: Uri) {
        try {
            startActivity(Intent(Intent.ACTION_VIEW, uri))
        } catch (_: ActivityNotFoundException) {
            // Sin app para abrirlo: no hacemos nada.
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        web.saveState(outState)
    }

    override fun onPause() { ads.pause(); web.onPause(); super.onPause() }
    override fun onResume() { super.onResume(); web.onResume(); ads.resume() }
    override fun onDestroy() { ads.destroy(); web.destroy(); super.onDestroy() }
}
