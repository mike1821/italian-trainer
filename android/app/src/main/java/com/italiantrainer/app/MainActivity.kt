package com.italiantrainer.app

import android.annotation.SuppressLint
import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatDelegate
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.webkit.WebChromeClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.activity.OnBackPressedCallback
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.isVisible

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private lateinit var loadingLayout: View
    private lateinit var progressBar: View
    private lateinit var retryButton: android.widget.Button

    override fun onCreate(savedInstanceState: Bundle?) {
        applyTheme()
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        setSupportActionBar(findViewById(R.id.toolbar))
        supportActionBar?.title = getString(R.string.app_name)

        webView = findViewById(R.id.webView)
        loadingLayout = findViewById(R.id.loadingLayout)
        progressBar = findViewById(R.id.progressBar)
        retryButton = findViewById(R.id.retryButton)

        setupWebView()
        retryButton.setOnClickListener { loadUrl() }
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (webView.canGoBack()) webView.goBack() else finish()
            }
        })
        loadUrl()
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun setupWebView() {
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
        }
        webView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                loadingLayout.isVisible = false
                progressBar.isVisible = false
            }

            override fun onReceivedError(
                view: WebView?,
                request: WebResourceRequest?,
                error: WebResourceError?
            ) {
                if (request?.isForMainFrame == true) {
                    loadingLayout.isVisible = true
                    progressBar.isVisible = false
                }
            }
        }
        webView.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView?, newProgress: Int) {
                progressBar.isVisible = newProgress < 100
            }
        }
    }

    private fun loadUrl() {
        val baseUrl = getStoredBaseUrl()
        if (baseUrl.isBlank()) {
            startActivity(Intent(this, SettingsActivity::class.java))
            return
        }
        val url = baseUrl.trim().removeSuffix("/")
        loadingLayout.isVisible = true
        progressBar.isVisible = true
        webView.loadUrl(url)
    }

    private fun getStoredBaseUrl(): String {
        return getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
            .getString(KEY_BASE_URL, "") ?: ""
    }

    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        menu.add(0, MENU_SETTINGS, 0, R.string.menu_settings)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        if (item.itemId == MENU_SETTINGS) {
            startActivity(Intent(this, SettingsActivity::class.java))
            return true
        }
        return super.onOptionsItemSelected(item)
    }

    override fun onResume() {
        super.onResume()
        // If we returned from Settings with a new URL, reload
        val prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        if (prefs.getBoolean(KEY_NEED_RELOAD, false)) {
            prefs.edit().putBoolean(KEY_NEED_RELOAD, false).apply()
            loadUrl()
        }
    }

    private fun applyTheme() {
        val mode = getSharedPreferences(PREFS_NAME, MODE_PRIVATE).getInt(KEY_THEME, THEME_SYSTEM)
        val delegateMode = when (mode) {
            THEME_LIGHT -> AppCompatDelegate.MODE_NIGHT_NO
            THEME_DARK -> AppCompatDelegate.MODE_NIGHT_YES
            else -> AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM
        }
        AppCompatDelegate.setDefaultNightMode(delegateMode)
    }

    companion object {
        const val PREFS_NAME = "italian_trainer"
        const val KEY_BASE_URL = "base_url"
        const val KEY_NEED_RELOAD = "need_reload"
        const val KEY_THEME = "theme"
        const val THEME_SYSTEM = 0
        const val THEME_LIGHT = 1
        const val THEME_DARK = 2
        private const val MENU_SETTINGS = 1
    }
}
