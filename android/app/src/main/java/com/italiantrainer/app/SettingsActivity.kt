package com.italiantrainer.app

import android.os.Bundle
import android.widget.AdapterView
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.Spinner
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.Executors

class SettingsActivity : AppCompatActivity() {

    private val executor = Executors.newSingleThreadExecutor()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)

        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        title = getString(R.string.settings_title)

        val prefs = getSharedPreferences(MainActivity.PREFS_NAME, MODE_PRIVATE)
        val editUrl = findViewById<EditText>(R.id.editBaseUrl)
        editUrl.setText(prefs.getString(MainActivity.KEY_BASE_URL, "") ?: "")

        val spinnerTheme = findViewById<Spinner>(R.id.spinnerTheme)
        val themeOptions = listOf(
            getString(R.string.theme_system),
            getString(R.string.theme_light),
            getString(R.string.theme_dark)
        )
        spinnerTheme.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, themeOptions)
        spinnerTheme.setSelection(prefs.getInt(MainActivity.KEY_THEME, MainActivity.THEME_SYSTEM))
        spinnerTheme.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: android.view.View?, position: Int, id: Long) {
                prefs.edit().putInt(MainActivity.KEY_THEME, position).apply()
            }
            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }

        findViewById<Button>(R.id.buttonSave).setOnClickListener {
            val url = editUrl.text.toString().trim().removeSuffix("/")
            if (url.isBlank()) {
                Toast.makeText(this, getString(R.string.base_url_hint), Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            if (!url.startsWith("http://") && !url.startsWith("https://")) {
                Toast.makeText(this, "URL deve iniziare con http:// o https://", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            prefs.edit()
                .putString(MainActivity.KEY_BASE_URL, url)
                .putInt(MainActivity.KEY_THEME, spinnerTheme.selectedItemPosition)
                .putBoolean(MainActivity.KEY_NEED_RELOAD, true)
                .apply()
            Toast.makeText(this, getString(R.string.save), Toast.LENGTH_SHORT).show()
            finish()
        }

        val testButton = findViewById<Button>(R.id.buttonTestConnection)
        testButton.setOnClickListener {
            val url = editUrl.text.toString().trim().removeSuffix("/")
            if (url.isBlank()) {
                Toast.makeText(this, getString(R.string.base_url_hint), Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            val testUrl = "$url/api/stats"
            testButton.isEnabled = false
            executor.execute {
                var success = false
                try {
                    val connection = URL(testUrl).openConnection() as HttpURLConnection
                    connection.requestMethod = "GET"
                    connection.connectTimeout = 8000
                    connection.readTimeout = 8000
                    val code = connection.responseCode
                    connection.disconnect()
                    success = code in 200..399
                } catch (_: Exception) { }
                runOnUiThread {
                    testButton.isEnabled = true
                    Toast.makeText(
                        this@SettingsActivity,
                        if (success) getString(R.string.connection_ok) else getString(R.string.connection_error),
                        Toast.LENGTH_SHORT
                    ).show()
                }
            }
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
