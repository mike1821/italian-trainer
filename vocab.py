#!/usr/bin/env python3
"""
Italian Vocabulary Practice Tool - Main Entry Point

A comprehensive vocabulary learning tool with features:
- Standard quizzes (Italian→Greek or Greek→Italian)
- Multiple choice quizzes
- Flashcard mode with self-assessment
- Sentence generation for practice
- Audio pronunciation (gTTS)
- Spaced repetition tracking (SQLite)
- Web interface (Flask)
- Progress statistics

Usage:
    vocab.py quiz [n] [--reverse] [--category CAT] [--difficulty 1-3]
    vocab.py mc [n]              - Multiple choice quiz
    vocab.py flashcard [n]       - Flashcard mode
    vocab.py sentences [n]       - Generate practice sentences
    vocab.py speak <word>        - Pronounce a word
    vocab.py stats               - Show statistics
    vocab.py web                 - Launch web interface
    vocab.py migrate             - Migrate old vocabulary format
"""

import sys
import argparse
from pathlib import Path

# Import modular components
from app.vocab_core import load_vocabulary, migrate_vocabulary
from database.vocab_db import init_db, get_stats
from app.vocab_quiz import run_quiz, run_multiple_choice, run_flashcards, generate_sentences
from app.vocab_audio import speak_word
from web.vocab_web import launch_web


def print_stats():
    """Display vocabulary statistics."""
    init_db()
    
    try:
        words = load_vocabulary()
        print(f"\n📚 Vocabulary: {len(words)} words")
    except FileNotFoundError:
        print("\n❌ No vocabulary file found.")
        print("Create 'vocabulary.xlsx' with columns: Italian | Greek | Category | Difficulty")
        return
    
    stats = get_stats()
    
    if stats["total_attempts"] == 0:
        print("\n📊 Statistics: No quizzes taken yet")
        print("\nStart practicing with: vocab.py quiz")
        return
    
    print(f"\n📊 Statistics:")
    print(f"   Total practice attempts: {stats['total_attempts']}")
    print(f"   Overall accuracy: {stats['accuracy']*100:.1f}%")
    print(f"   Words practiced: {stats['total_words']}")
    
    if stats["weak_words"]:
        print(f"\n📉 Words needing review:")
        for word, seen, correct, rate in stats["weak_words"][:5]:
            print(f"   • {word}: {correct}/{seen} correct ({rate*100:.0f}%)")


def main():
    parser = argparse.ArgumentParser(
        description="Italian Vocabulary Practice Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  vocab.py quiz 10                    # Quiz with 10 words
  vocab.py quiz --reverse             # Greek to Italian
  vocab.py quiz --category food       # Only food vocabulary
  vocab.py quiz --difficulty 3        # Only difficulty 3 words
  vocab.py mc 15                      # Multiple choice with 15 questions
  vocab.py flashcard 20               # Flashcard mode with 20 cards
  vocab.py sentences 10               # Generate 10 practice sentences
  vocab.py speak ciao                 # Hear pronunciation
  vocab.py web                        # Launch web interface
  vocab.py stats                      # View progress statistics
  vocab.py migrate                    # Migrate old vocabulary format
        """
    )
    
    parser.add_argument('command', 
                       choices=['quiz', 'mc', 'flashcard', 'sentences', 'speak', 'stats', 'web', 'migrate'],
                       help='Command to execute')
    parser.add_argument('args', nargs='*', help='Command arguments')
    parser.add_argument('--reverse', action='store_true', help='Reverse mode (Greek→Italian)')
    parser.add_argument('--category', type=str, help='Filter by category')
    parser.add_argument('--difficulty', type=int, choices=[1, 2, 3], help='Filter by difficulty')
    
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    # Initialize database on first run
    init_db()
    
    try:
        if args.command == 'quiz':
            n = int(args.args[0]) if args.args else 10
            run_quiz(n, args.reverse, args.category, args.difficulty)
        
        elif args.command == 'mc':
            n = int(args.args[0]) if args.args else 10
            run_multiple_choice(n)
        
        elif args.command == 'flashcard':
            n = int(args.args[0]) if args.args else 10
            run_flashcards(n)
        
        elif args.command == 'sentences':
            n = int(args.args[0]) if args.args else 5
            generate_sentences(n)
        
        elif args.command == 'speak':
            if not args.args:
                print("Error: Please provide a word to pronounce")
                print("Usage: vocab.py speak <word>")
                return
            word = ' '.join(args.args)
            speak_word(word)
        
        elif args.command == 'stats':
            print_stats()
        
        elif args.command == 'web':
            launch_web()
        
        elif args.command == 'migrate':
            migrate_vocabulary()
    
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nCreate 'vocabulary.xlsx' with columns: Italian | Greek | Category | Difficulty")
    except ValueError as e:
        print(f"\n❌ Error: {e}")
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
