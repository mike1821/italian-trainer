#!/usr/bin/env python3
"""
Load grammar exercises from JSON and check answers with normalized comparison.
"""
import json
import unicodedata
import random
from pathlib import Path

# Data dir: same folder as this file is in app/, data/ is sibling
PROJECT_ROOT = Path(__file__).resolve().parent.parent
GRAMMAR_DIR = PROJECT_ROOT / "data" / "grammar"

GRAMMAR_CATEGORIES = [
    "verbs_present",
    "articles",
    "avercela_avere_essere_esserci",
    "irregular_nouns",
]

_CACHE = {}


def _normalize(s):
    """Normalize for comparison: strip, lower, NFD, remove combining chars."""
    if not s or not isinstance(s, str):
        return ""
    s = s.strip().lower()
    # NFD and remove combining characters (accents become separate)
    nfd = unicodedata.normalize("NFD", s)
    no_accents = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    return no_accents.strip()


def _load_category(category_id):
    if category_id not in GRAMMAR_CATEGORIES:
        return None
    if category_id in _CACHE:
        return _CACHE[category_id]
    path = GRAMMAR_DIR / f"{category_id}.json"
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None
    # Normalize to list of {prompt, answer} or {prompt, answers}
    out = []
    for item in data:
        if isinstance(item, dict):
            prompt = item.get("prompt", "")
            answer = item.get("answer")
            answers = item.get("answers")
            if answer:
                out.append({"prompt": prompt, "answers": [answer]})
            elif answers:
                out.append({"prompt": prompt, "answers": list(answers)})
    _CACHE[category_id] = out
    return out


def get_exercises(category_id, n=20):
    """Return up to n random exercises for the category. Max n capped at 50.
    Each item is {prompt, answer} with answer = canonical form for display.
    """
    exercises = _load_category(category_id)
    if not exercises:
        return []
    n = min(max(1, int(n)), 50)
    sample = random.sample(exercises, min(n, len(exercises)))
    return [{"prompt": ex["prompt"], "answer": ex["answers"][0]} for ex in sample]


def check_answer(category_id, prompt, user_answer):
    """
    Check user answer against stored answers for this prompt in category.
    Returns (correct: bool, correct_answer: str).
    """
    exercises = _load_category(category_id)
    if not exercises:
        return False, ""
    user_n = _normalize(user_answer)
    for ex in exercises:
        if ex.get("prompt") == prompt and ex.get("answers"):
            for correct in ex["answers"]:
                if _normalize(correct) == user_n:
                    return True, correct
            return False, ex["answers"][0]
    return False, ""
