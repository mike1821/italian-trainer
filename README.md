# Italian Vocabulary Practice Tool

An enhanced vocabulary learning tool for practicing Italian–Greek translations and Italian grammar, with a web interface and an Android app.

## Features

1. **Categories & Difficulty Levels**: Organize words by topics and difficulty (1–3)
2. **Spaced Repetition**: Automatically tracks weak words and schedules reviews; vocabulary quizzes prioritise words due for review and weaker words
3. **Audio Pronunciation**: Italian text-to-speech using Google TTS
4. **Multiple Choice**: 4-option quiz (Italian→Greek and Greek→Italian); wrong options are drawn from the same category when possible for harder, more useful practice
5. **Grammar Exercises**: Fill-in exercises for verbs (present), articles, special verbs (avercela, avere, essere, esserci), and irregular nouns; answers checked on the server
6. **Web Interface**: Browser-based practice at localhost:5000 – Vocabolario, Grammatica, Statistiche
7. **Android App**: WebView app that uses the same backend; set your server URL and practice on your phone (see [android/README.md](android/README.md))

## Installation

```bash
pip install -r requirements.txt
```

## Vocabulary Format

Create `vocabulary.xlsx` with 4 columns:
```
Italian | Greek | Category | Difficulty
uno     | ένα   | numbers  | 1
ciao    | γεια  | greetings| 1
```

Migrate from old 2-column format:
```bash
python vocab.py migrate
```

## Project Structure

```
italian-trainer/
├── vocab.py                    # Main entry point
├── app/
│   ├── vocab_core.py          # Vocabulary loading and management
│   ├── vocab_quiz.py          # Quiz modes (standard, MC)
│   ├── vocab_audio.py         # Text-to-speech pronunciation
│   ├── grammar_loader.py      # Grammar exercise loading and answer checking
│   └── sentence_generator.py  # Italian sentence generation (legacy)
├── data/grammar/               # Grammar exercise data (JSON)
├── database/
│   └── vocab_db.py            # SQLite database and spaced repetition
├── web/
│   ├── vocab_web.py           # Flask web interface
│   └── wsgi.py                # WSGI config for PythonAnywhere
├── android/                    # Android WebView app (see android/README.md)
├── docs/
│   ├── STRUCTURE.md           # Detailed architecture documentation
│   ├── MIGRATION.md           # Guide for updating existing deployments
│   ├── WINDOWS_SHARE.md       # Windows network sharing with ngrok
│   └── PYTHONANYWHERE_DEPLOY.md # Cloud deployment guide
├── requirements.txt            # Python dependencies
├── vocabulary.xlsx             # Your vocabulary data
└── vocab_progress.db           # Progress tracking database (auto-created)
```

📖 **[See detailed architecture documentation](docs/STRUCTURE.md)**

## Usage

```bash
# Standard quiz (Italian → Greek)
python vocab.py quiz 10

# Reverse quiz (Greek → Italian)
python vocab.py quiz 10 --reverse

# Filter by category
python vocab.py quiz --category food

# Filter by difficulty
python vocab.py quiz --difficulty 3

# Multiple choice quiz
python vocab.py mc 15

# Pronounce a word
python vocab.py speak ciao

# View statistics
python vocab.py stats

# Launch web interface (recommended: Vocabolario, Grammatica, Statistiche)
python vocab.py web
```

## Web Interface

Launch with `python vocab.py web` and open http://localhost:5000

- **Vocabolario**: Italian→Greek and Greek→Italian (typed answers), plus multiple choice in both directions. Word selection uses spaced repetition; multiple choice uses wrong options from the same category when possible.
- **Grammatica**: Fill-in exercises – Verbi al presente, Articoli, Verbi speciali, Sostantivi irregolari. Answers are checked on the server.
- **Statistiche**: Words practiced, total attempts, accuracy, best streak.

All modes include audio pronunciation (🔊) after each answer.

### Sharing & Deployment

Want to share with friends or colleagues?

- **📡 [Windows Network Sharing Guide](docs/WINDOWS_SHARE.md)** – Share on local network or internet using ngrok
- **☁️ [PythonAnywhere Deployment](docs/PYTHONANYWHERE_DEPLOY.md)** – Deploy to cloud for 24/7 access (free tier available)

### Android app

An Android app in the `android/` folder wraps the web interface in a WebView. Set your server URL (e.g. your PythonAnywhere site), and use Vocabolario, Grammatica, and Statistiche on your phone. See **[android/README.md](android/README.md)** for setup and build.

## Database

Progress tracked in `vocab_progress.db` with spaced repetition algorithm:
- 90%+ success → review in 7 days
- 70-89% → review in 3 days
- 50-69% → review in 1 day
- <50% → review in 12 hours

Weak words automatically prioritized in quizzes.

## Legacy Tools

- `tool.py` - Simple CLI tool (basic quiz, lookup, add, list)
- `vocab_enhanced.py` - Monolithic version (all features in one file)

**Recommended:** Use `vocab.py` for the modular, maintainable version.