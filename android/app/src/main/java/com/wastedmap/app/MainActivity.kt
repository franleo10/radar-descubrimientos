package com.wastedmap.app

import android.annotation.SuppressLint
import android.content.ActivityNotFoundException
import android.content.Intent
import android.graphics.Bitmap
import android.net.Uri
import android.os.Bundle
import android.text.SpannableString
import android.text.Spanned
import android.text.style.ForegroundColorSpan
import android.view.HapticFeedbackConstants
import android.view.View
import android.view.ViewGroup
import android.webkit.CookieManager
import android.webkit.WebChromeClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.FrameLayout
import androidx.activity.OnBackPressedCallback
import androidx.appcompat.app.AppCompatActivity
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import androidx.core.view.ViewCompat
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import androidx.webkit.WebViewCompat
import androidx.webkit.WebViewFeature
import com.google.android.material.appbar.MaterialToolbar
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.google.android.material.button.MaterialButton
import com.google.android.material.progressindicator.LinearProgressIndicator
import org.json.JSONArray
import org.json.JSONObject
import java.util.Locale

/**
 * La app muestra wastedmap.com adentro, pero con forma de app:
 * - Arriba, una barra propia con el título de la página, "atrás" y un menú (compartir, idioma, navegador).
 * - Abajo, pestañas: Inicio, Mapa, Guías y Mi lista (en el idioma del sitio que se está viendo).
 * - La web, al ver "WastedMapApp" en el User-Agent, esconde su barra, su pie y la cinta de novedades.
 * - Banner de AdMob entre el contenido y las pestañas; anuncio de pantalla completa al abrir guías (ver Ads).
 */
class MainActivity : AppCompatActivity() {

    private lateinit var web: WebView
    private lateinit var refresh: SwipeRefreshLayout
    private lateinit var offline: View
    private lateinit var toolbar: MaterialToolbar
    private lateinit var nav: BottomNavigationView
    private lateinit var progress: LinearProgressIndicator
    private lateinit var ads: Ads
    private var fullscreenView: View? = null
    private var fullscreenCallback: WebChromeClient.CustomViewCallback? = null
    private var mainFrameError = false
    private var syncingTab = false

    private val site = Uri.parse(BuildConfig.SITE)
    private val prefs by lazy { getSharedPreferences("app", MODE_PRIVATE) }

    /** Rutas de cada pestaña según el idioma del sitio. */
    private val tabs = mapOf(
        "es" to listOf("/", "/mapa/", "/guias/", "/lista/"),
        "pt" to listOf("/pt/", "/pt/mapa/", "/pt/guias/", "/pt/100-por-cento/"),
        "en" to listOf("/en/", "/en/mapa/", "/en/guias/", "/en/100-percent/"),
    )
    private val tabIds by lazy { listOf(R.id.tab_home, R.id.tab_map, R.id.tab_guides, R.id.tab_list) }

    override fun onCreate(savedInstanceState: Bundle?) {
        installSplashScreen()
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        WindowCompat.setDecorFitsSystemWindows(window, false)
        val root = findViewById<View>(R.id.root)
        ViewCompat.setOnApplyWindowInsetsListener(root) { v, insets ->
            val bars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(bars.left, bars.top, bars.right, bars.bottom)
            insets
        }
        WindowInsetsControllerCompat(window, root).apply {
            isAppearanceLightStatusBars = false
            isAppearanceLightNavigationBars = false
        }

        web = findViewById(R.id.web)
        refresh = findViewById(R.id.refresh)
        offline = findViewById(R.id.offline)
        progress = findViewById(R.id.progress)
        toolbar = findViewById(R.id.toolbar)
        nav = findViewById(R.id.nav)
        findViewById<MaterialButton>(R.id.retry).setOnClickListener { offline.visibility = View.GONE; web.reload() }
        refresh.setColorSchemeColors(getColor(R.color.pink), getColor(R.color.orange))
        refresh.setProgressBackgroundColorSchemeColor(getColor(R.color.card))
        refresh.setOnRefreshListener { web.reload() }

        setupToolbar()
        setupTabs()
        setupWebView()
        ads = Ads(this, findViewById(R.id.banner))
        // Solo en la versión de prueba: "--ez capturas true" abre sin anuncios, para las capturas de la tienda.
        if (!(BuildConfig.DEBUG && intent.getBooleanExtra("capturas", false))) ads.start()

        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                when {
                    fullscreenView != null -> exitFullscreen()
                    web.canGoBack() -> web.goBack()
                    else -> { isEnabled = false; onBackPressedDispatcher.onBackPressed() }
                }
            }
        })

        val restored = savedInstanceState?.let { web.restoreState(it) }
        if (restored == null || web.url.isNullOrEmpty()) web.loadUrl(startUrl(intent))
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        intent.data?.takeIf { isOurs(it) }?.let { web.loadUrl(it.toString()) }
    }

    // ------------------------------------------------------------------ barra de arriba

    private fun setupToolbar() {
        toolbar.title = brandTitle()
        toolbar.setNavigationContentDescription(R.string.back)
        toolbar.overflowIcon?.setTint(getColor(R.color.ink))
        toolbar.setNavigationOnClickListener { if (web.canGoBack()) web.goBack() }
        toolbar.setOnMenuItemClickListener { item ->
            when (item.itemId) {
                R.id.action_share -> share()
                R.id.action_browser -> web.url?.let { openOutside(Uri.parse(it)) }
                R.id.action_privacy -> ads.showPrivacyOptions()
                R.id.lang_es -> switchLanguage("es")
                R.id.lang_pt -> switchLanguage("pt")
                R.id.lang_en -> switchLanguage("en")
            }
            true
        }
    }

    /** Actualiza título, flecha de atrás, idioma marcado y pestaña según la página actual. */
    private fun refreshChrome(url: String?, title: String? = null) {
        val path = url?.let { Uri.parse(it).path } ?: "/"
        val lang = langOf(path)
        val atTab = tabs.getValue(lang).indexOf(path)
        toolbar.navigationIcon = if (web.canGoBack() && atTab < 0)
            getDrawable(R.drawable.ic_back)?.apply { setTint(getColor(R.color.ink)) } else null
        // En Inicio: el logo y "WastedMap" con "Map" en rosa, como la marca.
        toolbar.logo = if (atTab == 0) logo else null
        val clean = (title ?: web.title).orEmpty().substringBefore(" | ").trim()

        toolbar.menu.findItem(R.id.lang_es).isChecked = lang == "es"
        toolbar.menu.findItem(R.id.lang_pt).isChecked = lang == "pt"
        toolbar.menu.findItem(R.id.lang_en).isChecked = lang == "en"
        toolbar.menu.findItem(R.id.action_privacy).isVisible = ads.privacyOptionsRequired()
        prefs.edit().putString("lang", lang).apply()
        // La última pestaña dice "Mi lista" en español y "Lista 100 %" en los otros idiomas (va a otra página).
        nav.menu.findItem(R.id.tab_list).setTitle(if (lang == "es") R.string.tab_list else R.string.tab_list_100)
        toolbar.title = when {
            atTab == 0 || clean.isEmpty() || clean.startsWith("http") -> brandTitle()
            atTab > 0 -> nav.menu.findItem(tabIds[atTab]).title   // en una pestaña: su nombre
            else -> clean
        }
        // Fuera de las pestañas, se marca la sección a la que pertenece la página.
        val section = if (atTab >= 0) atTab else sectionOf(path)
        if (nav.selectedItemId != tabIds[section]) {
            syncingTab = true
            nav.selectedItemId = tabIds[section]
            syncingTab = false
        }
    }

    /** El pin con un poco de aire a la derecha, para que no quede pegado al nombre. */
    private val logo by lazy {
        android.graphics.drawable.InsetDrawable(getDrawable(R.drawable.ic_logo),
            0, 0, (10 * resources.displayMetrics.density).toInt(), 0)
    }

    private fun brandTitle(): CharSequence {
        val name = getString(R.string.app_name)          // "WastedMap"
        return SpannableString(name).apply {
            setSpan(ForegroundColorSpan(getColor(R.color.pink)), 6, name.length, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
        }
    }

    /** Pestaña a la que pertenece una página que no es pestaña: guías -> Guías, zonas -> Mapa, Mi lista. */
    private fun sectionOf(path: String): Int {
        val p = path.removePrefix("/pt").removePrefix("/en")
        val guides = listOf("/trucos/", "/truques/", "/cheats/", "/100-por-ciento/", "/100-por-cento/", "/100-percent/",
            "/trofeos/", "/trofeus/", "/trophies/", "/no-te-lo-pierdas/", "/nao-perca/", "/missables/",
            "/ganar-dinero/", "/ganhar-dinheiro/", "/make-money/")
        return when {
            p.startsWith("/z/") -> 1
            guides.any { p.startsWith(it) } -> 2
            p.startsWith("/lista/") -> 3
            else -> 0      // secretos, categorías, top de la semana: Inicio
        }
    }

    private fun langOf(path: String): String = when {
        path.startsWith("/pt/") || path == "/pt" -> "pt"
        path.startsWith("/en/") || path == "/en" -> "en"
        else -> "es"
    }

    private fun share() {
        val url = web.url ?: return
        val text = listOfNotNull(web.title?.substringBefore(" | ")?.takeIf { it.isNotBlank() }, url).joinToString("\n")
        startActivity(Intent.createChooser(Intent(Intent.ACTION_SEND).apply {
            type = "text/plain"
            putExtra(Intent.EXTRA_TEXT, text)
        }, getString(R.string.share)))
    }

    /** Va a la misma página en el otro idioma (según los enlaces hreflang de la página) o a su portada. */
    private fun switchLanguage(lang: String) {
        val hreflang = mapOf("es" to "es", "pt" to "pt-BR", "en" to "en").getValue(lang)
        val js = "JSON.stringify([...document.querySelectorAll('link[rel=alternate][hreflang]')].map(l=>[l.hreflang,l.href]))"
        web.evaluateJavascript(js) { raw ->
            val target = try {
                val arr = JSONArray(JSONArray("[$raw]").getString(0))
                (0 until arr.length()).map { arr.getJSONArray(it) }
                    .firstOrNull { it.getString(0) == hreflang }?.getString(1)
            } catch (_: Exception) { null }
            web.loadUrl(target ?: (BuildConfig.SITE + tabs.getValue(lang)[0]))
        }
    }

    // ------------------------------------------------------------------ pestañas de abajo

    private fun setupTabs() {
        nav.setOnItemSelectedListener { item ->
            if (!syncingTab) {
                nav.performHapticFeedback(HapticFeedbackConstants.CONTEXT_CLICK)
                val lang = langOf(web.url?.let { Uri.parse(it).path } ?: (prefs.getString("lang", "es") ?: "es").let { "/$it/" })
                web.loadUrl(BuildConfig.SITE + tabs.getValue(lang)[tabIds.indexOf(item.itemId)])
            }
            true
        }
        // Tocar la pestaña en la que ya estás: vuelve arriba de todo.
        nav.setOnItemReselectedListener { web.evaluateJavascript("window.scrollTo({top:0,behavior:'smooth'})", null) }
    }

    // ------------------------------------------------------------------ web

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

    /** Script que marca la página como "app" y le agrega el estilo propio (assets/app.css). */
    private val appStyleJs by lazy {
        val css = assets.open("app.css").bufferedReader().use { it.readText() }
        "(function(){var d=document.documentElement;if(!d)return;d.classList.add('app');" +
            "if(document.getElementById('wm-app-css'))return;var s=document.createElement('style');" +
            "s.id='wm-app-css';s.textContent=${JSONObject.quote(css)};(document.head||d).appendChild(s);})();"
    }
    private var styleAtStart = false

    @SuppressLint("SetJavaScriptEnabled", "RequiresFeature")
    private fun setupWebView() {
        web.setBackgroundColor(getColor(R.color.bg))
        // Lo ideal: el estilo entra antes de que se dibuje la página (sin parpadeo).
        if (WebViewFeature.isFeatureSupported(WebViewFeature.DOCUMENT_START_SCRIPT)) {
            WebViewCompat.addDocumentStartJavaScript(web, appStyleJs, setOf(BuildConfig.SITE))
            styleAtStart = true
        }
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
                if (!refresh.isRefreshing) progress.visibility = View.VISIBLE
                if (!styleAtStart) view.evaluateJavascript(appStyleJs, null)
                // Transición corta entre páginas en lugar del corte seco del navegador.
                view.animate().alpha(0.4f).setDuration(120).start()
            }

            override fun onPageCommitVisible(view: WebView, url: String) {
                if (!styleAtStart) view.evaluateJavascript(appStyleJs, null)
                view.animate().alpha(1f).setDuration(180).start()
            }

            override fun onPageFinished(view: WebView, url: String) {
                refresh.isRefreshing = false
                progress.visibility = View.GONE
                view.animate().alpha(1f).setDuration(120).start()
                if (!mainFrameError) {
                    offline.visibility = View.GONE
                    prefs.edit().putString("last", url).apply()
                }
                if (ads.privacyOptionsRequired()) {
                    view.evaluateJavascript("document.documentElement.classList.add('app-privacy')", null)
                }
                refreshChrome(url)
            }

            override fun doUpdateVisitedHistory(view: WebView, url: String, isReload: Boolean) {
                refreshChrome(url)
            }

            override fun onReceivedError(view: WebView, request: WebResourceRequest, error: WebResourceError) {
                if (request.isForMainFrame) {
                    mainFrameError = true
                    refresh.isRefreshing = false
                    progress.visibility = View.GONE
                    offline.visibility = View.VISIBLE
                }
            }
        }

        web.webChromeClient = object : WebChromeClient() {
            override fun onReceivedTitle(view: WebView, title: String) = refreshChrome(view.url, title)

            // Videos de YouTube a pantalla completa.
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
