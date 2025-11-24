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
    
    # Word statistics table for spaced repetition (SM-2 algorithm)
    c.execute('''CREATE TABLE IF NOT EXISTS word_stats
                 (word_italian TEXT PRIMARY KEY,
                  times_seen INTEGER DEFAULT 0,
                  times_correct INTEGER DEFAULT 0,
                  last_seen DATETIME,
                  next_review DATETIME,
                  easiness_factor REAL DEFAULT 2.5,
                  interval_days REAL DEFAULT 1,
                  consecutive_correct INTEGER DEFAULT 0)''')
    
    # Add new columns if upgrading from old schema
    try:
        c.execute("ALTER TABLE word_stats ADD COLUMN easiness_factor REAL DEFAULT 2.5")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        c.execute("ALTER TABLE word_stats ADD COLUMN interval_days REAL DEFAULT 1")
    except sqlite3.OperationalError:
        pass
    
    try:
        c.execute("ALTER TABLE word_stats ADD COLUMN consecutive_correct INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    
    conn.commit()
    conn.close()


def record_quiz_result(word, correct, quiz_type="standard"):
    """Record quiz result and update spaced repetition schedule using SM-2 algorithm.
    
    SM-2 Algorithm (SuperMemo 2):
    - Easiness Factor (EF): 1.3 to 2.5, starts at 2.5
    - Interval: Days until next review
    - Quality: 0-5 rating (we use 5 for correct, 2 for incorrect)
    """
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    
    # Insert into history
    c.execute("INSERT INTO quiz_history (word_italian, correct, quiz_type) VALUES (?, ?, ?)",
              (word, 1 if correct else 0, quiz_type))
    
    # Update or insert word stats with SM-2
    now = datetime.now()
    c.execute("""SELECT times_seen, times_correct, easiness_factor, interval_days, consecutive_correct 
                 FROM word_stats WHERE word_italian = ?""", (word,))
    result = c.fetchone()
    
    if result:
        times_seen, times_correct, ef, interval, streak = result
        # Handle NULL values from old schema
        ef = ef if ef is not None else 2.5
        interval = interval if interval is not None else 1
        streak = streak if streak is not None else 0
        
        times_seen += 1
        if correct:
            times_correct += 1
            streak += 1
        else:
            streak = 0
        
        # SM-2 Algorithm
        # Quality: 5 for correct answer, 2 for incorrect
        quality = 5 if correct else 2
        
        # Update easiness factor
        ef = max(1.3, ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        
        # Calculate next interval
        if not correct:
            # Reset interval on wrong answer
            interval = 1
            next_review = now + timedelta(days=interval)
        elif streak == 1:
            # First repetition: 1 day
            interval = 1
            next_review = now + timedelta(days=1)
        elif streak == 2:
            # Second repetition: 6 days
            interval = 6
            next_review = now + timedelta(days=6)
        else:
            # Subsequent repetitions: multiply by EF
            interval = interval * ef
            next_review = now + timedelta(days=interval)
        
        c.execute("""UPDATE word_stats 
                     SET times_seen = ?, times_correct = ?, last_seen = ?, next_review = ?,
                         easiness_factor = ?, interval_days = ?, consecutive_correct = ?
                     WHERE word_italian = ?""",
                  (times_seen, times_correct, now, next_review, ef, interval, streak, word))
    else:
        # First time seeing this word
        ef = 2.5  # Default easiness factor
        interval = 1 if correct else 0.5
        streak = 1 if correct else 0
        next_review = now + timedelta(days=interval)
        
        c.execute("""INSERT INTO word_stats 
                     (word_italian, times_seen, times_correct, last_seen, next_review,
                      easiness_factor, interval_days, consecutive_correct)
                     VALUES (?, 1, ?, ?, ?, ?, ?, ?)""",
                  (word, 1 if correct else 0, now, next_review, ef, interval, streak))
    
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


def get_detailed_stats():
    """Get detailed statistics for dashboard with charts data."""
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    
    # Basic stats
    c.execute("SELECT COUNT(*) FROM word_stats")
    total_words = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM quiz_history")
    total_attempts = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM quiz_history WHERE correct = 1")
    total_correct = c.fetchone()[0]
    
    # Performance over time (last 30 days)
    c.execute("""SELECT DATE(timestamp) as date, 
                        COUNT(*) as attempts,
                        SUM(correct) as correct
                 FROM quiz_history
                 WHERE timestamp >= datetime('now', '-30 days')
                 GROUP BY DATE(timestamp)
                 ORDER BY date ASC""")
    daily_performance = [{"date": row[0], "attempts": row[1], "correct": row[2], 
                          "accuracy": row[2]/row[1]*100 if row[1] > 0 else 0} 
                         for row in c.fetchall()]
    
    # Category performance (using vocabulary file categories)
    c.execute("""SELECT quiz_type, COUNT(*) as count, 
                        SUM(correct) as correct,
                        CAST(SUM(correct) AS FLOAT) / COUNT(*) * 100 as accuracy
                 FROM quiz_history
                 GROUP BY quiz_type""")
    quiz_types = [{"type": row[0], "count": row[1], "correct": row[2], "accuracy": row[3]} 
                  for row in c.fetchall()]
    
    # Streak calculation
    c.execute("""SELECT MAX(consecutive_correct) as best_streak,
                        AVG(consecutive_correct) as avg_streak
                 FROM word_stats""")
    streak_data = c.fetchone()
    best_streak = streak_data[0] if streak_data[0] else 0
    avg_streak = streak_data[1] if streak_data[1] else 0
    
    # Top performing words
    c.execute("""SELECT word_italian, times_seen, times_correct,
                        CAST(times_correct AS FLOAT) / times_seen * 100 as success_rate,
                        easiness_factor, consecutive_correct
                 FROM word_stats
                 WHERE times_seen >= 3
                 ORDER BY success_rate DESC, consecutive_correct DESC
                 LIMIT 10""")
    top_words = [{"word": row[0], "seen": row[1], "correct": row[2], 
                  "rate": row[3], "ef": row[4], "streak": row[5]} 
                 for row in c.fetchall()]
    
    # Weakest words
    c.execute("""SELECT word_italian, times_seen, times_correct,
                        CAST(times_correct AS FLOAT) / times_seen * 100 as success_rate,
                        easiness_factor
                 FROM word_stats
                 ORDER BY success_rate ASC, times_seen DESC
                 LIMIT 10""")
    weak_words = [{"word": row[0], "seen": row[1], "correct": row[2], 
                   "rate": row[3], "ef": row[4]} 
                  for row in c.fetchall()]
    
    # Words due for review
    now = datetime.now()
    c.execute("""SELECT COUNT(*) FROM word_stats WHERE next_review <= ?""", (now,))
    due_count = c.fetchone()[0]
    
    conn.close()
    
    return {
        "total_words": total_words,
        "total_attempts": total_attempts,
        "total_correct": total_correct,
        "accuracy": total_correct / total_attempts * 100 if total_attempts > 0 else 0,
        "daily_performance": daily_performance,
        "quiz_types": quiz_types,
        "best_streak": int(best_streak),
        "avg_streak": round(avg_streak, 1),
        "top_words": top_words,
        "weak_words": weak_words,
        "due_for_review": due_count
    }
