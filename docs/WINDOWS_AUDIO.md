# Windows Audio Setup Guide

## Problem
By default, Windows uses `start` command which opens Windows Media Player GUI when playing audio in CLI mode.

## Solution
Install `pygame` library for in-terminal audio playback (no GUI popup). This works with **Python 3.13+**.

## Installation

```powershell
pip install pygame
```

Or install all dependencies:
```powershell
pip install -r requirements.txt
```

## How It Works

The audio player tries methods in this order:

1. **pygame** (recommended) - Plays audio in terminal without GUI, Python 3.13 compatible
2. **playsound** (legacy) - Older library, incompatible with Python 3.13
3. **Windows Media Player** (fallback) - Opens GUI if above not installed

## Testing

```powershell
python vocab.py speak ciao
```

**With pygame installed:** Audio plays in terminal, no window opens  
**Without pygame:** Windows Media Player window opens

## Troubleshooting

### Error: "No module named 'pygame'"
```powershell
pip install pygame
```

### pygame installation fails?
Make sure you have Visual C++ redistributables installed. Download from:
https://aka.ms/vs/17/release/vc_redist.x64.exe

### Python 3.13 compatibility
- ✅ **pygame** - Works perfectly with Python 3.13
- ❌ **playsound** - Broken on Python 3.13 (use pygame instead)

### Still opens Media Player?
pygame failed to install/work. The app falls back to `start` command. This still works but opens a GUI window.

## Alternative: Use Web Interface

If CLI audio is problematic, use the web interface which plays audio in the browser:

```powershell
python vocab.py web
```

Then open http://localhost:5000 in your browser. Audio works perfectly without any external players.

## Note for PythonAnywhere

playsound and pygame won't work on PythonAnywhere (server environment, no audio hardware). The web interface on PythonAnywhere also won't work due to gTTS being blocked. Audio only works on your local Windows machine.
