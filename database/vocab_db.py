#!/usr/bin/env python3
"""
Database functions for tracking quiz progress and spaced repetition.
"""
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_FILE = Path("vocab_progress.db")

def init_db():
    """Initialize SQLite database for progress tracking."""
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    
    # Quiz history table
    c.execute('''CREATE TABLE IF NOT EXISTS quiz_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  word_italian TEXT NOT NULL,
                  correct INTEGER NOT NULL,
                  quiz_type TEXT NOT NULL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Word statistics table for spaced repetition
    c.execute('''CREATE TABLE IF NOT EXISTS word_stats
                 (word_italian TEXT PRIMARY KEY,
                  times_seen INTEGER DEFAULT 0,
                  times_correct INTEGER DEFAULT 0,
                  last_seen DATETIME,
                  next_review DATETIME)''')
    
    conn.commit()
    conn.close()


def record_quiz_result(word, correct, quiz_type="standard"):
    """Record a quiz result and update spaced repetition schedule."""
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    
    # Insert into history
    c.execute("INSERT INTO quiz_history (word_italian, correct, quiz_type) VALUES (?, ?, ?)",
              (word, 1 if correct else 0, quiz_type))
    
    # Update or insert word stats
    now = datetime.now()
    c.execute("SELECT times_seen, times_correct FROM word_stats WHERE word_italian = ?", (word,))
    result = c.fetchone()
    
    if result:
        times_seen, times_correct = result
        times_seen += 1
        if correct:
            times_correct += 1
        
        success_rate = times_correct / times_seen
        
        # Calculate next review based on success rate
        if success_rate >= 0.9:
            next_review = now + timedelta(days=7)
        elif success_rate >= 0.7:
            next_review = now + timedelta(days=3)
        elif success_rate >= 0.5:
            next_review = now + timedelta(days=1)
        else:
            next_review = now + timedelta(hours=12)
        
        c.execute("""UPDATE word_stats 
                     SET times_seen = ?, times_correct = ?, last_seen = ?, next_review = ?
                     WHERE word_italian = ?""",
                  (times_seen, times_correct, now, next_review, word))
    else:
        next_review = now + timedelta(days=1 if correct else 0.5)
        c.execute("""INSERT INTO word_stats 
                     (word_italian, times_seen, times_correct, last_seen, next_review)
                     VALUES (?, 1, ?, ?, ?)""",
                  (word, 1 if correct else 0, now, next_review))
    
    conn.commit()
    conn.close()


def get_weak_words(limit=10):
    """Get words that need review (due or low success rate)."""
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    
    now = datetime.now()
    
    # Get words due for review or with low success rate
    c.execute("""SELECT word_italian, 
                        CAST(times_correct AS FLOAT) / times_seen as success_rate,
                        next_review
                 FROM word_stats
                 WHERE next_review <= ? OR (CAST(times_correct AS FLOAT) / times_seen) < 0.7
                 ORDER BY next_review ASC, success_rate ASC
                 LIMIT ?""", (now, limit))
    
    weak_words = [row[0] for row in c.fetchall()]
    conn.close()
    
    return weak_words


def get_stats():
    """Get overall statistics."""
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM word_stats")
    total_words = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM quiz_history")
    total_attempts = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM quiz_history WHERE correct = 1")
    total_correct = c.fetchone()[0]
    
    c.execute("""SELECT word_italian, times_seen, times_correct,
                        CAST(times_correct AS FLOAT) / times_seen as success_rate
                 FROM word_stats
                 ORDER BY success_rate ASC, times_seen DESC
                 LIMIT 10""")
    weak = c.fetchall()
    
    conn.close()
    
    return {
        "total_words": total_words,
        "total_attempts": total_attempts,
        "total_correct": total_correct,
        "accuracy": total_correct / total_attempts if total_attempts > 0 else 0,
        "weak_words": weak
    }
