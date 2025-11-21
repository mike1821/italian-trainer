# Migration Guide: Updating to New Folder Structure

## What Changed?

The project has been reorganized from flat structure to modular folders:

**Before:**
```
italian-trainer/
├── vocab.py
├── vocab_core.py
├── vocab_db.py
├── vocab_quiz.py
├── vocab_audio.py
├── vocab_web.py
├── sentence_generator.py
└── wsgi.py
```

**After:**
```
italian-trainer/
├── vocab.py
├── app/
│   ├── vocab_core.py
│   ├── vocab_quiz.py
│   ├── vocab_audio.py
│   └── sentence_generator.py
├── database/
│   └── vocab_db.py
├── web/
│   ├── vocab_web.py
│   └── wsgi.py
└── docs/
    ├── STRUCTURE.md
    ├── WINDOWS_SHARE.md
    └── PYTHONANYWHERE_DEPLOY.md
```

## Local Development (Your Computer)

### If You're Using Git:
```bash
cd /root/italian-trainer
git add .
git commit -m "Restructure project into modular folders"
git push
```

### Testing Locally:
```bash
# All commands still work the same!
python vocab.py quiz 10
python vocab.py web
python vocab.py stats
```

## PythonAnywhere Update

### Option 1: Upload New Files (Recommended)

1. **Delete old files** on PythonAnywhere (or move to backup folder):
   - vocab_core.py
   - vocab_db.py
   - vocab_quiz.py
   - vocab_audio.py
   - vocab_web.py
   - sentence_generator.py
   - wsgi.py (old location)

2. **Upload new folders:**
   - Upload entire `app/` folder
   - Upload entire `database/` folder
   - Upload entire `web/` folder
   - Upload entire `docs/` folder (optional)

3. **Keep these files unchanged:**
   - vocab.py (updated with new imports)
   - vocabulary.xlsx
   - requirements.txt
   - vocab_progress.db (your quiz history - don't delete!)

### Option 2: Git Clone (If Repository is Public)

```bash
# In PythonAnywhere Bash console
cd ~
mv italian-trainer italian-trainer.backup
git clone https://github.com/mike1821/italian-trainer.git
cd italian-trainer
pip3 install --user -r requirements.txt
```

Then copy your data files:
```bash
cp ~/italian-trainer.backup/vocabulary.xlsx ~/italian-trainer/
cp ~/italian-trainer.backup/vocab_progress.db ~/italian-trainer/
```

### Update WSGI Configuration

Edit your WSGI file (`/var/www/yourusername_pythonanywhere_com_wsgi.py`):

**Change this:**
```python
from vocab_web import application
```

**To this:**
```python
from web.vocab_web import application
```

Full WSGI file should be:
```python
import sys
import os

project_home = '/home/yourusername/italian-trainer'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from web.vocab_web import application
```

### Reload Web App

1. Go to PythonAnywhere **Web** tab
2. Click green **Reload** button
3. Test at your URL: `https://yourusername.pythonanywhere.com`

## Verification Checklist

- [ ] Local: `python vocab.py quiz 5` works
- [ ] Local: `python vocab.py web` launches successfully
- [ ] Local: All 5 web modes work (IT→GR, GR→IT, MC, Flashcards, Sentences)
- [ ] PythonAnywhere: Files uploaded to correct folders
- [ ] PythonAnywhere: WSGI file updated with `web.vocab_web`
- [ ] PythonAnywhere: Web app reloaded
- [ ] PythonAnywhere: Live URL accessible
- [ ] PythonAnywhere: All 5 modes functional
- [ ] Database preserved (quiz history intact)

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'vocab_core'"
**Solution:** Imports not updated. Make sure `vocab.py` has:
```python
from app.vocab_core import load_vocabulary, migrate_vocabulary
from database.vocab_db import init_db, get_stats
from app.vocab_quiz import run_quiz, run_multiple_choice, run_flashcards, generate_sentences
from app.vocab_audio import speak_word
from web.vocab_web import launch_web
```

### Error: "ModuleNotFoundError: No module named 'app'"
**Solution:** Missing `__init__.py` files. Make sure these exist:
- `app/__init__.py`
- `database/__init__.py`
- `web/__init__.py`

### PythonAnywhere Error: "ImportError: cannot import name 'application'"
**Solution:** WSGI file not updated. Edit WSGI configuration:
```python
from web.vocab_web import application  # NOT from vocab_web
```

### Lost Quiz History
**Solution:** The database file is `vocab_progress.db` in the root folder. Make sure you didn't delete it during migration. If you have a backup, just copy it back:
```bash
cp vocab_progress.db.backup vocab_progress.db
```

## Rolling Back (If Something Breaks)

If the new structure causes issues, you can temporarily revert:

1. Keep the old flat structure files as backup
2. Change imports in `vocab.py` back to:
   ```python
   from vocab_core import load_vocabulary
   from vocab_db import init_db
   # etc.
   ```
3. Use the old WSGI configuration: `from vocab_web import application`

## Benefits of New Structure

✅ **Better Organization:** Related files grouped together  
✅ **Easier Navigation:** Find files by their purpose (app/database/web)  
✅ **Professional Structure:** Standard Python project layout  
✅ **Documentation:** Separate docs/ folder for guides  
✅ **Scalability:** Easy to add new modules without cluttering root  
✅ **Deployment:** Clearer separation of concerns  

## Questions?

See detailed documentation:
- **Architecture:** [docs/STRUCTURE.md](STRUCTURE.md)
- **Deployment:** [docs/PYTHONANYWHERE_DEPLOY.md](PYTHONANYWHERE_DEPLOY.md)
- **Sharing:** [docs/WINDOWS_SHARE.md](WINDOWS_SHARE.md)
