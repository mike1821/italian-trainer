#!/usr/bin/env python3
"""
Quiz and practice mode functions with interleaved repetition for better learning.
"""
import random
from collections import deque
from app.vocab_core import load_vocabulary, filter_words
from database.vocab_db import record_quiz_result, get_weak_words, get_words_for_quiz
from app.vocab_audio import speak_word


# Session mastery settings
CORRECT_NEEDED_TO_MASTER = 2  # Must answer correctly twice to master a word
MAX_RETRIES_PER_WORD = 3      # Maximum times to retry a single word
RETRY_DELAY_MIN = 3           # Minimum questions before retry
RETRY_DELAY_MAX = 7           # Maximum questions before retry


def run_quiz(n=10, reverse=False, category=None, difficulty=None, retry_wrong=True):
    """Run a standard quiz with typed answers and interleaved repetition.
    
    Features:
    - Wrong answers are re-inserted 3-7 questions later (interleaved repetition)
    - Words must be answered correctly twice to be considered mastered
    - Maximum 3 retries per word to avoid frustrating loops
    
    Args:
        n: Number of words to quiz
        reverse: If True, quiz Greek→Italian instead of Italian→Greek
        category: Filter by category
        difficulty: Filter by difficulty level
        retry_wrong: If True, use interleaved repetition for wrong answers
    """
    words = load_vocabulary()
    words = filter_words(words, category, difficulty)
    
    if not words:
        print("No words match the specified filters.")
        return
    
    # Get balanced selection: 30% new, 40% weak, 30% review words
    selected = get_words_for_quiz(words, n)
    
    # Initialize quiz queue and tracking
    quiz_queue = deque(selected)
    word_stats = {}  # Track correct count and retry count per word
    
    for word in selected:
        word_stats[word["italian"]] = {"correct": 0, "retries": 0}
    
    questions_answered = 0
    total_correct = 0
    mastered_words = set()
    
    # Pending retries: list of (word, insert_after_question_number)
    pending_retries = []
    
    print(f"\n{'='*50}")
    print(f"📚 Quiz Mode: {'Greek→Italian' if reverse else 'Italian→Greek'}")
    if retry_wrong:
        print("💡 Interleaved repetition: wrong answers return later")
        print(f"🎯 Master each word by answering correctly {CORRECT_NEEDED_TO_MASTER}x")
    print(f"{'='*50}")
    
    while quiz_queue:
        # Check if any pending retries should be inserted
        if retry_wrong:
            retries_to_insert = [r for r in pending_retries if r[1] <= questions_answered]
            for retry_item in retries_to_insert:
                pending_retries.remove(retry_item)
                quiz_queue.append(retry_item[0])
        
        word = quiz_queue.popleft()
        word_key = word["italian"]
        stats = word_stats[word_key]
        
        questions_answered += 1
        
        question = word["greek"] if reverse else word["italian"]
        answer = word["italian"] if reverse else word["greek"]
        
        # Show retry indicator if this is a repeated word
        retry_indicator = ""
        if stats["retries"] > 0:
            retry_indicator = f" [retry {stats['retries']}/{MAX_RETRIES_PER_WORD}]"
        
        # Calculate progress (unique words answered at least once)
        progress = len([w for w in word_stats.values() if w["correct"] > 0 or w["retries"] > 0])
        print(f"\n[{progress}/{n}]{retry_indicator} {question}")
        user_answer = input("Your answer: ").strip()
        
        correct = user_answer.lower() == answer.lower()
        
        if correct:
            stats["correct"] += 1
            total_correct += 1
            
            if stats["correct"] >= CORRECT_NEEDED_TO_MASTER:
                mastered_words.add(word_key)
                print(f"✓ Correct! 🌟 Mastered!")
            elif stats["correct"] == 1 and stats["retries"] > 0:
                print(f"✓ Correct! Well done! 🎉")
            else:
                remaining = CORRECT_NEEDED_TO_MASTER - stats["correct"]
                print(f"✓ Correct! ({remaining} more to master)")
        else:
            print(f"✗ Wrong. Answer: {answer}")
            
            # Schedule retry if enabled and not maxed out
            if retry_wrong and stats["retries"] < MAX_RETRIES_PER_WORD:
                stats["retries"] += 1
                # Insert retry 3-7 questions later
                delay = random.randint(RETRY_DELAY_MIN, RETRY_DELAY_MAX)
                insert_after = questions_answered + delay
                pending_retries.append((word, insert_after))
                print(f"   ↩ Will retry in ~{delay} questions")
        
        record_quiz_result(word["italian"], correct, "standard" if stats["retries"] == 0 else "retry")
        speak_word(word["italian"])
    
    # Process any remaining pending retries
    still_pending = [r[0] for r in pending_retries]
    final_retry_score = 0
    final_retry_total = 0
    
    if still_pending:
        print(f"\n{'='*50}")
        print(f"🔄 Final Review: {len(still_pending)} words remaining")
        print(f"{'='*50}")
        
        for word in still_pending:
            word_key = word["italian"]
            stats = word_stats[word_key]
            final_retry_total += 1
            
            question = word["greek"] if reverse else word["italian"]
            answer = word["italian"] if reverse else word["greek"]
            
            print(f"\n[Final] {question}")
            user_answer = input("Your answer: ").strip()
            
            correct = user_answer.lower() == answer.lower()
            if correct:
                print("✓ Correct! 🎉")
                final_retry_score += 1
                stats["correct"] += 1
                if stats["correct"] >= CORRECT_NEEDED_TO_MASTER:
                    mastered_words.add(word_key)
            else:
                print(f"✗ Wrong. Remember: {answer}")
            
            record_quiz_result(word["italian"], correct, "final_retry")
            speak_word(word["italian"])
    
    # Summary
    print(f"\n{'='*50}")
    print(f"📊 Quiz Summary")
    print(f"{'='*50}")
    print(f"Words mastered: {len(mastered_words)}/{n}")
    print(f"Total answers: {total_correct} correct out of {questions_answered}")
    
    not_mastered = [w for w in selected if w["italian"] not in mastered_words]
    if not_mastered:
        print(f"\n⚠️  Words needing more practice:")
        for word in not_mastered[:5]:  # Show up to 5
            print(f"   • {word['italian']} = {word['greek']}")
        if len(not_mastered) > 5:
            print(f"   ... and {len(not_mastered) - 5} more")
    else:
        print(f"\n🌟 Perfect! All words mastered!")
    
    print(f"{'='*50}")


def run_multiple_choice(n=10, retry_wrong=True):
    """Run a multiple choice quiz with interleaved repetition.
    
    Features:
    - Wrong answers are re-inserted 3-7 questions later (interleaved repetition)
    - Words must be answered correctly twice to be considered mastered
    - Maximum 3 retries per word to avoid frustrating loops
    
    Args:
        n: Number of words to quiz
        retry_wrong: If True, use interleaved repetition for wrong answers
    """
    words = load_vocabulary()
    
    if len(words) < 4:
        print("Need at least 4 words for multiple choice quiz")
        return
    
    # Get balanced selection: 30% new, 40% weak, 30% review words
    selected = get_words_for_quiz(words, min(n, len(words)))
    
    # Initialize quiz queue and tracking
    quiz_queue = deque(selected)
    word_stats = {}  # Track correct count and retry count per word
    
    for word in selected:
        word_stats[word["italian"]] = {"correct": 0, "retries": 0}
    
    questions_answered = 0
    total_correct = 0
    mastered_words = set()
    
    # Pending retries: list of (word, insert_after_question_number)
    pending_retries = []
    
    print(f"\n{'='*50}")
    print(f"📝 Multiple Choice Quiz")
    if retry_wrong:
        print("💡 Interleaved repetition: wrong answers return later")
        print(f"🎯 Master each word by answering correctly {CORRECT_NEEDED_TO_MASTER}x")
    print(f"{'='*50}")
    
    while quiz_queue:
        # Check if any pending retries should be inserted
        if retry_wrong:
            retries_to_insert = [r for r in pending_retries if r[1] <= questions_answered]
            for retry_item in retries_to_insert:
                pending_retries.remove(retry_item)
                quiz_queue.append(retry_item[0])
        
        word = quiz_queue.popleft()
        word_key = word["italian"]
        stats = word_stats[word_key]
        
        questions_answered += 1
        
        question = word["italian"]
        correct_answer = word["greek"]
        
        # Generate wrong answers
        wrong = random.sample([w["greek"] for w in words if w["greek"] != correct_answer], 3)
        options = [correct_answer] + wrong
        random.shuffle(options)
        
        # Show retry indicator if this is a repeated word
        retry_indicator = ""
        if stats["retries"] > 0:
            retry_indicator = f" [retry {stats['retries']}/{MAX_RETRIES_PER_WORD}]"
        
        # Calculate progress (unique words answered at least once)
        progress = len([w for w in word_stats.values() if w["correct"] > 0 or w["retries"] > 0])
        print(f"\n[{progress}/{n}]{retry_indicator} {question}")
        for j, opt in enumerate(options, 1):
            print(f"  {j}. {opt}")
        
        while True:
            try:
                choice = int(input("Your choice (1-4): "))
                if 1 <= choice <= 4:
                    break
            except ValueError:
                pass
            print("Please enter 1, 2, 3, or 4")
        
        user_answer = options[choice - 1]
        correct = user_answer == correct_answer
        
        if correct:
            stats["correct"] += 1
            total_correct += 1
            
            if stats["correct"] >= CORRECT_NEEDED_TO_MASTER:
                mastered_words.add(word_key)
                print(f"✓ Correct! 🌟 Mastered!")
            elif stats["correct"] == 1 and stats["retries"] > 0:
                print(f"✓ Correct! Well done! 🎉")
            else:
                remaining = CORRECT_NEEDED_TO_MASTER - stats["correct"]
                print(f"✓ Correct! ({remaining} more to master)")
        else:
            print(f"✗ Wrong. Answer: {correct_answer}")
            
            # Schedule retry if enabled and not maxed out
            if retry_wrong and stats["retries"] < MAX_RETRIES_PER_WORD:
                stats["retries"] += 1
                # Insert retry 3-7 questions later
                delay = random.randint(RETRY_DELAY_MIN, RETRY_DELAY_MAX)
                insert_after = questions_answered + delay
                pending_retries.append((word, insert_after))
                print(f"   ↩ Will retry in ~{delay} questions")
        
        record_quiz_result(word["italian"], correct, "multiple_choice" if stats["retries"] == 0 else "retry")
        speak_word(word["italian"])
    
    # Process any remaining pending retries
    still_pending = [r[0] for r in pending_retries]
    final_retry_score = 0
    
    if still_pending:
        print(f"\n{'='*50}")
        print(f"🔄 Final Review: {len(still_pending)} words remaining")
        print(f"{'='*50}")
        
        for word in still_pending:
            word_key = word["italian"]
            stats = word_stats[word_key]
            
            question = word["italian"]
            correct_answer = word["greek"]
            
            # Generate new wrong answers for final retry
            wrong = random.sample([w["greek"] for w in words if w["greek"] != correct_answer], 3)
            options = [correct_answer] + wrong
            random.shuffle(options)
            
            print(f"\n[Final] {question}")
            for j, opt in enumerate(options, 1):
                print(f"  {j}. {opt}")
            
            while True:
                try:
                    choice = int(input("Your choice (1-4): "))
                    if 1 <= choice <= 4:
                        break
                except ValueError:
                    pass
                print("Please enter 1, 2, 3, or 4")
            
            user_answer = options[choice - 1]
            correct = user_answer == correct_answer
            
            if correct:
                print("✓ Correct! 🎉")
                final_retry_score += 1
                stats["correct"] += 1
                if stats["correct"] >= CORRECT_NEEDED_TO_MASTER:
                    mastered_words.add(word_key)
            else:
                print(f"✗ Wrong. Remember: {correct_answer}")
            
            record_quiz_result(word["italian"], correct, "final_retry")
            speak_word(word["italian"])
    
    # Summary
    print(f"\n{'='*50}")
    print(f"📊 Quiz Summary")
    print(f"{'='*50}")
    print(f"Words mastered: {len(mastered_words)}/{n}")
    print(f"Total answers: {total_correct} correct out of {questions_answered}")
    
    not_mastered = [w for w in selected if w["italian"] not in mastered_words]
    if not_mastered:
        print(f"\n⚠️  Words needing more practice:")
        for word in not_mastered[:5]:  # Show up to 5
            print(f"   • {word['italian']} = {word['greek']}")
        if len(not_mastered) > 5:
            print(f"   ... and {len(not_mastered) - 5} more")
    else:
        print(f"\n🌟 Perfect! All words mastered!")
    
    print(f"{'='*50}")


def run_flashcards(n=10):
    """Run flashcard mode with self-assessment."""
    words = load_vocabulary()
    selected = random.sample(words, min(n, len(words)))
    
    score = 0
    for i, word in enumerate(selected, 1):
        print(f"\n[{i}/{len(selected)}] Flashcard")
        print("="*50)
        print(f"\n  {word['italian']}")
        speak_word(word["italian"])
        input("\n  [Press Enter to see answer]")
        print(f"\n  → {word['greek']}")
        
        while True:
            response = input("\nDid you know it? (y/n): ").lower()
            if response in ['y', 'n']:
                break
        
        correct = response == 'y'
        if correct:
            score += 1
        
        record_quiz_result(word["italian"], correct, "flashcard")
    
    print(f"\n{'='*50}")
    print(f"Flashcard session complete! You knew {score}/{len(selected)} ({score*100//len(selected)}%)")


def generate_sentences(n=5):
    """Generate practice sentences using vocabulary."""
    words = load_vocabulary()
    
    templates = [
        lambda w: f"{w[0]['italian'].capitalize()} è {w[1]['italian']}.",
        lambda w: f"Ho visto {w[0]['italian']} nel {w[1]['italian']}.",
        lambda w: f"Mi piace {w[0]['italian']} e {w[1]['italian']}.",
        lambda w: f"Domani vado al {w[0]['italian']} con {w[1]['italian']}.",
        lambda w: f"Il {w[0]['italian']} è più grande del {w[1]['italian']}.",
        lambda w: f"Voglio comprare {w[0]['italian']} per {w[1]['italian']}.",
    ]
    
    print("\n" + "="*60)
    print("Generated Practice Sentences:")
    print("="*60)
    
    for i in range(n):
        selected_words = random.sample(words, min(3, len(words)))
        template = random.choice(templates)
        sentence = template(selected_words)
        
        words_used = ", ".join([f"{w['italian']}={w['greek']}" for w in selected_words[:2]])
        print(f"\n{i+1}. {sentence}")
        print(f"   Words: {words_used}")
    
    print()
