# PythonAnywhere Deployment Guide

## What is WSGI?

**WSGI (Web Server Gateway Interface)** is a standard interface between web servers and Python web applications. It allows production web servers (like those on PythonAnywhere) to communicate with your Flask application.

### Key Differences:

**Development (vocab.py web):**
```python
app.run(debug=True, port=5000, host='0.0.0.0')
```
- Uses Flask's built-in development server
- NOT suitable for production
- You manually start/stop it

**Production (WSGI on PythonAnywhere):**
```python
application = create_wsgi_app()
```
- Uses production-grade WSGI server (like uWSGI)
- Automatically handles requests 24/7
- No `app.run()` needed - the server imports your `application` object

## Files to Upload to PythonAnywhere

Upload these **9 files** to `/home/yourusername/italian-trainer/`:

1. `vocab.py` - Main entry point (for CLI, not used by web)
2. `vocab_core.py` - Vocabulary loading
3. `vocab_db.py` - Database functions
4. `vocab_audio.py` - Audio generation (note: gTTS may have rate limits)
5. `vocab_quiz.py` - Quiz logic
6. `vocab_web.py` - Flask app (modified with WSGI support)
7. `sentence_generator.py` - Grammar engine
8. `vocabulary.xlsx` - Your word list
9. `requirements.txt` - Dependencies
10. `wsgi.py` - WSGI configuration file

## Deployment Steps

### 1. Sign Up
- Go to https://www.pythonanywhere.com
- Create a free account ("Beginner" tier is fine)

### 2. Upload Files
- Click **Files** tab
- Create directory: `/home/yourusername/italian-trainer`
- Upload all 10 files listed above

### 3. Install Dependencies
- Click **Consoles** tab → Start a new **Bash console**
- Run:
```bash
cd ~/italian-trainer
pip3 install --user -r requirements.txt
```

### 4. Create Web App
- Click **Web** tab → **Add a new web app**
- Choose **Manual configuration** (not Flask wizard!)
- Select **Python 3.10** (or latest available)

### 5. Configure WSGI File
- In the **Web** tab, find section "Code:"
- Click the **WSGI configuration file** link (e.g., `/var/www/yourusername_pythonanywhere_com_wsgi.py`)
- Delete ALL contents and replace with:

```python
import sys
import os

# CHANGE THIS PATH to match your username
project_home = '/home/yourusername/italian-trainer'

if project_home not in sys.path:
    sys.path.insert(0, project_home)

from vocab_web import application
```

**Important:** Replace `yourusername` with your actual PythonAnywhere username!

### 6. Set Working Directory
- In **Web** tab, find "Working directory:" field
- Set it to: `/home/yourusername/italian-trainer`

### 7. Reload Web App
- Scroll to top of **Web** tab
- Click the big green **Reload** button
- Your app will be live at: `https://yourusename.pythonanywhere.com`

## Testing

Visit your URL: `https://yourusername.pythonanywhere.com`

You should see:
- 🇮🇹 Italian Vocabulary Practice 🇬🇷
- 5 mode buttons (Italian→Greek, Greek→Italian, etc.)
- All features working (audio, sentences, multiple choice)

## Troubleshooting

### Error: "ImportError: No module named 'flask'"
**Solution:** Install dependencies in bash console:
```bash
pip3 install --user flask openpyxl gtts
```

### Error: "No such file or directory: vocabulary.xlsx"
**Solution:** Make sure `vocabulary.xlsx` is uploaded to the same directory as your Python files.

### Error: Audio not working
**Issue:** PythonAnywhere may rate-limit gTTS (Google Text-to-Speech).
**Solution:** Audio might be slower or fail occasionally on free tier. Consider upgrading or caching audio files.

### Error: Database permission denied
**Solution:** PythonAnywhere creates `vocab_progress.db` automatically. If issues persist, check file permissions in bash console:
```bash
chmod 644 vocab_progress.db
```

## Important Notes

1. **Free Tier Limits:**
   - CPU seconds per day limited
   - Slower performance than localhost
   - gTTS may be rate-limited

2. **Your URL:**
   - Format: `https://yourusername.pythonanywhere.com`
   - Permanent (doesn't change like ngrok)
   - Accessible from anywhere (including Nokia corporate network!)

3. **Updates:**
   - To update code: Upload new files, click **Reload** in Web tab
   - Database persists between reloads

4. **Sharing:**
   - Just send your PythonAnywhere URL to colleagues
   - No firewall issues (uses standard HTTPS port 443)
   - Works from any network

## Comparison: ngrok vs PythonAnywhere

| Feature | ngrok | PythonAnywhere |
|---------|-------|----------------|
| Setup Time | 5 minutes | 15 minutes |
| URL Stability | Changes on restart | Permanent |
| Performance | Fast (local) | Slower (cloud) |
| Uptime | Only when your PC runs | 24/7 |
| Corporate Firewall | Bypasses | Bypasses |
| Free Tier | 2 hours, then new URL | Always on |

**Recommendation:** Use PythonAnywhere for permanent sharing with colleagues. Use ngrok for quick testing.
