# Italian Trainer – Android app

Android app that wraps the Italian Trainer web interface in a WebView. Set your server URL once and use the full web experience on your phone: vocabulary practice, grammar exercises, and statistics.

## What the web interface offers

- **Vocabolario** – Italian ↔ Greek practice in three ways:
  - **Italian → Greek** and **Greek → Italian**: type the translation. Word selection uses spaced repetition: words due for review and weaker words are prioritised.
  - **Multiple choice (both directions)**: choose the correct translation from four options. Wrong options are chosen from the same category when possible to make the quiz more useful.
- **Grammatica** – Fill-in exercises in four categories: Verbi al presente, Articoli, Verbi speciali (avercela, avere, essere, esserci), Sostantivi irregolari. Answers are checked on the server.
- **Statistiche** – Words practiced, total attempts, accuracy, and best streak (from the server).

All modes support Italian audio (🔊) after each answer. Progress and stats are stored on the server, so they stay in sync between the browser and the Android app.

## Requirements

- Android Studio (or command-line SDK)
- Min SDK 24, target SDK 34
- Italian Trainer backend deployed and reachable (e.g. [PythonAnywhere](https://www.pythonanywhere.com)) with the web app and API

## Setup

1. Open the `android` folder in Android Studio (or use the project root and select the `android` module).
2. Sync Gradle and build.

## First run

1. Open the app. If no server URL is set, the **Settings** screen opens.
2. Enter your server URL (e.g. `https://yourusername.pythonanywhere.com`), then tap **Salva**.
3. The app loads the web app in the WebView. Use **Vocabolario**, **Grammatica**, and **Statistiche** as in the browser.

## Settings (Impostazioni)

- **URL del server** – Base URL of your deployed Italian Trainer (must include `http://` or `https://`).
- **Testa connessione** – Checks that `/api/stats` is reachable.
- **Tema** – Sistema (follow device), Chiaro, or Scuro.

Open Settings from the overflow menu (⋮) in the app bar.

## Build

From Android Studio: **Build > Build Bundle(s) / APK(s) > Build APK(s)**.

From the command line (if the Gradle wrapper is present):

```bash
cd android
./gradlew assembleDebug    # debug APK (Windows: gradlew.bat assembleDebug)
./gradlew assembleRelease # release APK (configure signing in app/build.gradle.kts first)
```

Output: `app/build/outputs/apk/`

## Notes

- The app is a thin client: all logic (vocabulary, grammar, stats, audio) runs in the web app; the app only displays it and stores the base URL and theme.
- For HTTPS servers, no extra config is needed. For local HTTP (e.g. `http://192.168.1.x:5000`), the app uses `android:usesCleartextTraffic="true"` for development.
