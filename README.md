# Italian Vocabulary Practice Tool

An enhanced vocabulary learning tool for practicing Italian-Greek translations with multiple study modes.

## Features

1. **Categories & Difficulty Levels**: Organize words by topics and difficulty (1-3)
2. **Spaced Repetition**: Automatically tracks weak words and schedules reviews
3. **Audio Pronunciation**: Italian text-to-speech using Google TTS
4. **Flashcard Mode**: Interactive flip cards with self-assessment
5. **Multiple Choice**: 4-option quiz format
6. **Sentence Generation**: Practice with auto-generated sentences
7. **Web Interface**: Modern browser-based practice at localhost:5000

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
│   ├── vocab_quiz.py          # Quiz modes (standard, MC, flashcards)
│   ├── vocab_audio.py         # Text-to-speech pronunciation
│   └── sentence_generator.py  # Intelligent Italian sentence generation
├── database/
│   └── vocab_db.py            # SQLite database and spaced repetition
├── web/
│   ├── vocab_web.py           # Flask web interface
│   └── wsgi.py                # WSGI config for PythonAnywhere
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

# Flashcard mode
python vocab.py flashcard 20

# Generate practice sentences
python vocab.py sentences 10

# Pronounce a word
python vocab.py speak ciao

# View statistics
python vocab.py stats

# Launch web interface
python vocab.py web
```

## Web Interface

Launch with `python vocab.py web` and open http://localhost:5000

Modes available:
- **Italian → Greek**: Direct translation with typed answers
- **Greek → Italian**: Reverse translation practice
- **Multiple Choice**: 4-option quiz format
- **Flashcards**: Click to flip, self-assess
- **Sentences**: Translate generated Italian sentences

All modes include audio pronunciation (🔊 icon) that plays automatically after each answer.

### Sharing & Deployment

Want to share with friends or colleagues?

- **📡 [Windows Network Sharing Guide](docs/WINDOWS_SHARE.md)** - Share on local network or internet using ngrok
- **☁️ [PythonAnywhere Deployment](docs/PYTHONANYWHERE_DEPLOY.md)** - Deploy to cloud for 24/7 access (free tier available)

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