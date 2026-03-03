# Italian Trainer – Android (WebView)

Minimal Android app that wraps the Italian Trainer web app in a WebView. Configure your server URL once and use the full web experience (vocabulary, grammar, statistics) on your phone.

## Requirements

- Android Studio (or command-line SDK)
- Min SDK 24, target SDK 34
- Deployed Italian Trainer backend (e.g. [PythonAnywhere](https://www.pythonanywhere.com)) with the web app and API

## Setup

1. Open the `android` folder in Android Studio (or use the project root and select the `android` module).
2. Sync Gradle and build.

## First run

1. Open the app. If no server URL is set, the **Settings** screen opens.
2. Enter your server URL (e.g. `https://yourusername.pythonanywhere.com`), then tap **Salva**.
3. The app loads the web app in the WebView. Use it like the browser version (Vocabolario, Grammatica, Statistiche).

## Settings (Impostazioni)

- **URL del server** – Base URL of your deployed Italian Trainer (must include `http://` or `https://`).
- **Testa connessione** – Checks that `/api/stats` is reachable.
- **Tema** – Sistema (follow device), Chiaro, or Scuro.

Access Settings from the overflow menu (⋮) in the app bar.

## Build

From Android Studio: **Build > Build Bundle(s) / APK(s) > Build APK(s)**.

From the command line, generate the Gradle wrapper first (if missing) then build:

```bash
cd android
# If gradlew is missing: in Android Studio use File > New > Import Project, or run: gradle wrapper
./gradlew assembleDebug   # debug APK (Windows: gradlew.bat assembleDebug)
./gradlew assembleRelease # release APK (configure signing in app/build.gradle.kts first)
```

Output: `app/build/outputs/apk/`

## Notes

- All logic (quiz, grammar, stats, audio) runs in the web app; the app only displays it and stores the base URL and theme.
- Progress and stats are stored on the server (same as in the browser).
- For HTTPS servers, no extra config is needed. For local HTTP (e.g. `http://192.168.1.x:5000`), the app uses `android:usesCleartextTraffic="true"` for development.
