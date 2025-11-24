#!/usr/bin/env python3
"""
Audio pronunciation functions using Google Text-to-Speech.
"""
import os
import sys
import tempfile
from pathlib import Path

def speak_word(word, lang='it'):
    """Speak a word using text-to-speech."""
    try:
        from gtts import gTTS
    except ImportError:
        print("Error: gTTS not installed. Run: pip install gTTS")
        return False
    
    try:
        tts = gTTS(text=word, lang=lang)
        
        audio_file = Path(tempfile.gettempdir()) / "vocab_speak.mp3"
        tts.save(str(audio_file))
        
        # Play audio based on platform
        if sys.platform == "darwin":  # macOS
            os.system(f"afplay {audio_file}")
        elif sys.platform.startswith("linux"):
            # Try multiple players
            if os.system(f"which mpg123 > /dev/null 2>&1") == 0:
                os.system(f"mpg123 -q {audio_file}")
            elif os.system(f"which ffplay > /dev/null 2>&1") == 0:
                os.system(f"ffplay -nodisp -autoexit -hide_banner -loglevel panic {audio_file}")
            else:
                print("No audio player found. Install mpg123 or ffplay.")
                return False
        else:  # Windows
            # Try pygame first (Python 3.13 compatible), fallback to playsound, then Windows Media Player
            if _play_with_pygame(str(audio_file)):
                return True
            elif _play_with_playsound(str(audio_file)):
                return True
            else:
                # Fallback to default player (opens GUI)
                os.system(f"start {audio_file}")
        
        return True
        
    except Exception as e:
        print(f"Error playing audio: {e}")
        return False


def _play_with_playsound(audio_file):
    """Try to play audio with playsound library (no GUI)."""
    try:
        from playsound import playsound
        playsound(audio_file, block=True)
        return True
    except ImportError:
        return False
    except Exception:
        return False


def _play_with_pygame(audio_file):
    """Try to play audio with pygame library (no GUI)."""
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.quit()
        return True
    except ImportError:
        return False
    except Exception:
        return False


def get_audio_base64(word, lang='it'):
    """Get base64-encoded audio for web interface."""
    try:
        from gtts import gTTS
        import base64
        import io
        
        tts = gTTS(text=word, lang=lang)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        audio_b64 = base64.b64encode(audio_bytes.read()).decode('utf-8')
        
        return audio_b64
    except Exception as e:
        # gTTS fails on PythonAnywhere free tier (no external connections)
        # Return empty string instead of None to prevent JavaScript errors
        print(f"Error generating audio: {e}")
        return ""
