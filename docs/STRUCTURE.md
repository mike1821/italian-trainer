# Project Structure Documentation

## Directory Layout

```
italian-trainer/
├── vocab.py                    # Main CLI entry point
├── vocabulary.xlsx             # Vocabulary data (Italian|Greek|Category|Difficulty)
├── vocab_progress.db          # SQLite database (auto-created)
├── requirements.txt           # Python dependencies
├── categorize_words.py        # One-time tool for auto-categorization
│
├── app/                       # Application Logic
│   ├── __init__.py
│   ├── vocab_core.py         # Vocabulary loading & filtering
│   ├── vocab_quiz.py         # Quiz modes (standard, MC, flashcards)
│   ├── vocab_audio.py        # Text-to-speech (gTTS)
│   └── sentence_generator.py # Italian grammar engine
│
├── database/                  # Data Persistence
│   ├── __init__.py
│   └── vocab_db.py           # SQLite operations & spaced repetition
│
├── web/                       # Web Interface
│   ├── __init__.py
│   ├── vocab_web.py          # Flask application
│   └── wsgi.py               # WSGI config for production deployment
│
└── docs/                      # Documentation
    ├── STRUCTURE.md          # This file
    ├── WINDOWS_SHARE.md      # Network sharing guide (ngrok)
    └── PYTHONANYWHERE_DEPLOY.md  # Cloud deployment guide
```

## Module Responsibilities

### `vocab.py` - Entry Point
- Command-line argument parsing (argparse)
- Routes commands to appropriate modules
- Prints statistics and help messages
- **Commands:** quiz, mc, flashcard, sentences, speak, stats, web, migrate

### `app/` - Core Application Logic

#### `vocab_core.py`
- `load_vocabulary()` - Reads vocabulary.xlsx
- `filter_words()` - Filters by category/difficulty
- `migrate_vocabulary()` - Upgrades 2-column → 4-column format
- **No external dependencies** (pure data loading)

#### `vocab_quiz.py`
- `run_quiz()` - Standard typed-answer quiz
- `run_multiple_choice()` - 4-option quiz
- `run_flashcards()` - Flip-card mode with self-assessment
- `generate_sentences()` - Legacy template-based sentences (deprecated)
- **Dependencies:** vocab_core, vocab_db, vocab_audio

#### `vocab_audio.py`
- `speak_word()` - CLI pronunciation (saves to /tmp, plays via mpg123/afplay/ffplay)
- `get_audio_base64()` - Returns base64-encoded MP3 for web interface
- **External:** gTTS (Google Text-to-Speech API)
- **Note:** Fails on PythonAnywhere free tier (external connections blocked)

#### `sentence_generator.py`
- `SentenceGenerator` class with Italian grammar rules
- **Grammar Features:**
  - Definite articles: il/lo/l'/la/i/gli/le (gender & vowel aware)
  - Indefinite articles: un/uno/una/un' (special consonant rules)
  - Verb conjugations: essere, avere
  - Preposition+article contractions: del/al/dal/nel/sul
- **Patterns:** 5 sentence types (essere, avere, prepositions, complex, time)

### `database/` - Persistence Layer

#### `vocab_db.py`
- `init_db()` - Creates quiz_history and word_stats tables
- `record_quiz_result()` - Logs attempts, calculates next review date
- `get_weak_words()` - Returns words due for review (<70% success)
- `get_stats()` - Overall statistics & top weak words
- **Spaced Repetition:**
  - 90%+ success → 7 days
  - 70-89% → 3 days
  - 50-69% → 1 day
  - <50% → 12 hours

### `web/` - Web Interface

#### `vocab_web.py`
- `launch_web()` - Development server (localhost:5000)
- `create_wsgi_app()` - Production WSGI application
- **Routes:**
  - `GET /` - Main HTML page (embedded JS)
  - `GET /api/words?n=10` - Random vocabulary JSON
  - `GET /api/speak?word=ciao` - Base64 audio
  - `GET /api/sentence` - Smart sentence with grammar pattern
- **UI Features:** Gradient design, animations, 5 practice modes

#### `wsgi.py`
- WSGI configuration for PythonAnywhere/production
- Sets up Python path
- Imports `application` object from `web.vocab_web`

## Import Structure

```
vocab.py
├── app.vocab_core
├── app.vocab_quiz
│   ├── app.vocab_core
│   ├── app.vocab_audio
│   └── database.vocab_db
├── app.vocab_audio
├── database.vocab_db
└── web.vocab_web
    ├── app.vocab_core
    ├── app.vocab_audio
    └── app.sentence_generator

wsgi.py
└── web.vocab_web (same as above)
```

## Data Flow

### Quiz Mode (CLI)
1. **vocab.py** receives `quiz 10 --category food`
2. Calls `app.vocab_quiz.run_quiz(n=10, category="food")`
3. `vocab_quiz` loads words via `app.vocab_core.load_vocabulary()`
4. Filters via `app.vocab_core.filter_words()`
5. Gets weak words via `database.vocab_db.get_weak_words()`
6. Loops through questions:
   - Prompts user for answer
   - Records result via `database.vocab_db.record_quiz_result()`
   - Plays audio via `app.vocab_audio.speak_word()`

### Web Mode
1. **vocab.py** calls `web.vocab_web.launch_web()`
2. Flask app starts on port 5000
3. User opens browser → `GET /`
4. HTML page loads with JavaScript
5. User clicks "Italian→Greek" → JS calls `GET /api/words?n=10`
6. Flask returns JSON vocabulary
7. User answers question → JS evaluates locally
8. On correct answer → JS calls `GET /api/speak?word=ciao`
9. Flask calls `app.vocab_audio.get_audio_base64()`
10. Returns base64 MP3 → JS plays in browser

### Sentence Generation
1. User clicks "Sentences" mode → JS calls `GET /api/sentence`
2. Flask calls `app.sentence_generator.generate_smart_sentence(vocabulary)`
3. `SentenceGenerator` picks random pattern (essere/avere/preposition)
4. Applies grammar rules (articles, conjugations, contractions)
5. Returns: `{italian: "Il libro è grande", pattern: "Essere sentence", words_used: ["libro"]}`
6. JS displays sentence + pattern + word meanings

## Development vs Production

### Development (localhost)
```bash
python vocab.py web
# Uses Flask development server
# Debug mode enabled
# Audio works (direct internet access to gTTS)
# Listens on 0.0.0.0:5000
```

### Production (PythonAnywhere)
```bash
# Upload entire project folder
# WSGI server imports web.vocab_web.application
# No app.run() called
# Audio fails (free tier blocks external APIs)
# URL: https://username.pythonanywhere.com
```

## Key Design Decisions

1. **Modular Structure:** Separated concerns (core, quiz, audio, db, web) for maintainability
2. **Folder Organization:** Logical grouping (app/ for logic, database/ for persistence, web/ for interface)
3. **WSGI Support:** Dual mode (development + production) in same codebase
4. **Grammar Engine:** Separate module for Italian language rules (extendable)
5. **Spaced Repetition:** Built into database layer, transparent to quiz logic
6. **Audio Fallback:** Graceful degradation when gTTS unavailable

## Adding New Features

### New Quiz Mode
1. Add function to `app/vocab_quiz.py`
2. Import in `vocab.py`
3. Add command-line argument in `vocab.py`
4. Optionally add web route in `web/vocab_web.py`

### New Grammar Rule
1. Add method to `SentenceGenerator` in `app/sentence_generator.py`
2. Add to pattern list in `generate()` method
3. No other changes needed

### New Category
1. Add words with new category to `vocabulary.xlsx`
2. Optionally update `categorize_words.py` rules
3. Use immediately: `python vocab.py quiz --category newcategory`

## Testing Checklist

- [ ] CLI quiz works: `python vocab.py quiz 5`
- [ ] Stats display: `python vocab.py stats`
- [ ] Web launches: `python vocab.py web`
- [ ] All 5 web modes functional
- [ ] Sentence generation uses grammar rules
- [ ] Database records quiz results
- [ ] Audio plays on localhost (if mpg123/ffplay installed)
- [ ] Imports resolve correctly from all modules

## Deployment Checklist

- [ ] All Python files in correct folders (app/, database/, web/)
- [ ] `__init__.py` files present in each folder
- [ ] `requirements.txt` up to date
- [ ] `vocabulary.xlsx` included
- [ ] WSGI file imports `web.vocab_web.application`
- [ ] PythonAnywhere path configured correctly
- [ ] Dependencies installed: `pip3 install --user -r requirements.txt`
- [ ] Web app reloaded after upload
- [ ] Test all 5 modes on live URL
