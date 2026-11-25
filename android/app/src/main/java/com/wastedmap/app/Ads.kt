package com.wastedmap.app

import android.app.Activity
import android.os.SystemClock
import android.util.DisplayMetrics
import android.view.View
import android.widget.FrameLayout
import com.google.android.gms.ads.AdListener
import com.google.android.gms.ads.AdRequest
import com.google.android.gms.ads.AdSize
import com.google.android.gms.ads.AdView
import com.google.android.gms.ads.FullScreenContentCallback
import com.google.android.gms.ads.LoadAdError
import com.google.android.gms.ads.MobileAds
import com.google.android.gms.ads.interstitial.InterstitialAd
import com.google.android.gms.ads.interstitial.InterstitialAdLoadCallback
import com.google.android.ump.ConsentInformation
import com.google.android.ump.ConsentRequestParameters
import com.google.android.ump.UserMessagingPlatform
import java.util.concurrent.atomic.AtomicBoolean

/**
 * Anuncios de la app:
 * - Primero el aviso de consentimiento de Google (UMP), que solo aparece donde la ley lo pide.
 * - Un banner fijo abajo, fuera de la página.
 * - Un anuncio de pantalla completa al abrir una guía, cada [EVERY] guías y con al menos [GAP_MS] entre uno y otro.
 */
class Ads(private val activity: Activity, private val bannerSlot: FrameLayout) {

    companion object {
        const val EVERY = 5
        const val GAP_MS = 90_000L
    }

    private val consent: ConsentInformation = UserMessagingPlatform.getConsentInformation(activity)
    private val started = AtomicBoolean(false)
    private var banner: AdView? = null
    private var interstitial: InterstitialAd? = null
    private var guidesOpened = 0
    private var lastShown = 0L

    /** Pide el consentimiento (si hace falta) y después arranca los anuncios. */
    fun start() {
        val params = ConsentRequestParameters.Builder().build()
        consent.requestConsentInfoUpdate(activity, params, {
            UserMessagingPlatform.loadAndShowConsentFormIfRequired(activity) { _ ->
                if (consent.canRequestAds()) initAds()
            }
        }, { _ -> if (consent.canRequestAds()) initAds() })
        // Si ya había consentimiento de antes, no esperamos.
        if (consent.canRequestAds()) initAds()
    }

    /** ¿Hay que ofrecer "Opciones de privacidad de anuncios"? (lo pide la ley en algunos países). */
    fun privacyOptionsRequired(): Boolean =
        consent.privacyOptionsRequirementStatus == ConsentInformation.PrivacyOptionsRequirementStatus.REQUIRED

    fun showPrivacyOptions() {
        UserMessagingPlatform.showPrivacyOptionsForm(activity) { _ -> }
    }

    private fun initAds() {
        if (!started.compareAndSet(false, true)) return
        MobileAds.initialize(activity) {}
        loadBanner()
        loadInterstitial()
    }

    private fun loadBanner() {
        val view = AdView(activity)
        view.adUnitId = BuildConfig.BANNER_ID
        view.setAdSize(bannerSize())
        view.adListener = object : AdListener() {
            override fun onAdLoaded() { bannerSlot.visibility = View.VISIBLE }
            override fun onAdFailedToLoad(error: LoadAdError) { bannerSlot.visibility = View.GONE }
        }
        bannerSlot.removeAllViews()
        bannerSlot.addView(view)
        banner = view
        view.loadAd(AdRequest.Builder().build())
    }

    private fun bannerSize(): AdSize {
        val metrics: DisplayMetrics = activity.resources.displayMetrics
        val widthDp = (metrics.widthPixels / metrics.density).toInt()
        return AdSize.getCurrentOrientationAnchoredAdaptiveBannerAdSize(activity, widthDp)
    }

    private fun loadInterstitial() {
        InterstitialAd.load(activity, BuildConfig.INTERSTITIAL_ID, AdRequest.Builder().build(),
            object : InterstitialAdLoadCallback() {
                override fun onAdLoaded(ad: InterstitialAd) { interstitial = ad }
                override fun onAdFailedToLoad(error: LoadAdError) { interstitial = null }
            })
    }

    /**
     * Se llama cuando la persona abre una guía. Si toca anuncio, lo muestra y recién al cerrarlo
     * sigue con [proceed]; si no, sigue directo.
     */
    fun onGuideOpened(proceed: () -> Unit) {
        guidesOpened++
        val ad = interstitial
        val now = SystemClock.elapsedRealtime()
        if (ad == null || guidesOpened % EVERY != 0 || now - lastShown < GAP_MS) {
            proceed(); return
        }
        ad.fullScreenContentCallback = object : FullScreenContentCallback() {
            override fun onAdDismissedFullScreenContent() { interstitial = null; loadInterstitial(); proceed() }
            override fun onAdFailedToShowFullScreenContent(e: com.google.android.gms.ads.AdError) {
                interstitial = null; loadInterstitial(); proceed()
            }
        }
        lastShown = now
        ad.show(activity)
    }

    fun pause() = banner?.pause()
    fun resume() = banner?.resume()
    fun destroy() = banner?.destroy()
}
