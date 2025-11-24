# Windows Audio Setup Guide

## Problem
By default, Windows uses `start` command which opens Windows Media Player GUI when playing audio in CLI mode.

## Solution
Install `playsound` library for in-terminal audio playback (no GUI popup).

## Installation

```powershell
pip install playsound
```

Or install all dependencies:
```powershell
pip install -r requirements.txt
```

## How It Works

The audio player tries methods in this order:

1. **playsound** (recommended) - Plays audio in terminal without GUI
2. **pygame** (alternative) - Also plays without GUI, heavier library
3. **Windows Media Player** (fallback) - Opens GUI if above not installed

## Testing

```powershell
python vocab.py speak ciao
```

**With playsound installed:** Audio plays in terminal, no window opens  
**Without playsound:** Windows Media Player window opens

## Troubleshooting

### Error: "No module named 'playsound'"
```powershell
pip install playsound
```

### playsound not working?
Try pygame as alternative:
```powershell
pip install pygame
```

### Still opens Media Player?
Both playsound and pygame failed to install/work. The app falls back to `start` command. This still works but opens a GUI window.

## Alternative: Use Web Interface

If CLI audio is problematic, use the web interface which plays audio in the browser:

```powershell
python vocab.py web
```

Then open http://localhost:5000 in your browser. Audio works perfectly without any external players.

## Note for PythonAnywhere

playsound and pygame won't work on PythonAnywhere (server environment, no audio hardware). The web interface on PythonAnywhere also won't work due to gTTS being blocked. Audio only works on your local Windows machine.
