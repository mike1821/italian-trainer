#!/usr/bin/env python3
"""
Quiz and practice mode functions.
"""
import random
from app.vocab_core import load_vocabulary, filter_words
from database.vocab_db import record_quiz_result, get_weak_words, get_words_for_quiz
from app.vocab_audio import speak_word


def run_quiz(n=10, reverse=False, category=None, difficulty=None, retry_wrong=True):
    """Run a standard quiz with typed answers.
    
    Args:
        n: Number of words to quiz
        reverse: If True, quiz Greek→Italian instead of Italian→Greek
        category: Filter by category
        difficulty: Filter by difficulty level
        retry_wrong: If True, retry wrong answers at end of quiz
    """
    words = load_vocabulary()
    words = filter_words(words, category, difficulty)
    
    if not words:
        print("No words match the specified filters.")
        return
    
    # Get balanced selection: 30% new, 40% weak, 30% review words
    selected = get_words_for_quiz(words, n)
    
    score = 0
    wrong_answers = []  # Track words that need retry
    
    print(f"\n{'='*50}")
    print(f"📚 Quiz Mode: {'Greek→Italian' if reverse else 'Italian→Greek'}")
    if retry_wrong:
        print("💡 Wrong answers will be retried at the end")
    print(f"{'='*50}")
    
    for i, word in enumerate(selected, 1):
        question = word["greek"] if reverse else word["italian"]
        answer = word["italian"] if reverse else word["greek"]
        
        print(f"\n[{i}/{len(selected)}] {question}")
        user_answer = input("Your answer: ").strip()
        
        correct = user_answer.lower() == answer.lower()
        if correct:
            print("✓ Correct!")
            score += 1
        else:
            print(f"✗ Wrong. Answer: {answer}")
            if retry_wrong:
                wrong_answers.append(word)
        
        record_quiz_result(word["italian"], correct, "standard")
        speak_word(word["italian"])
    
    # Immediate retry of wrong answers
    if retry_wrong and wrong_answers:
        print(f"\n{'='*50}")
        print(f"🔄 Review Time! Let's retry the {len(wrong_answers)} words you missed")
        print(f"{'='*50}")
        
        retry_score = 0
        for i, word in enumerate(wrong_answers, 1):
            question = word["greek"] if reverse else word["italian"]
            answer = word["italian"] if reverse else word["greek"]
            
            print(f"\n[Retry {i}/{len(wrong_answers)}] {question}")
            user_answer = input("Your answer: ").strip()
            
            correct = user_answer.lower() == answer.lower()
            if correct:
                print("✓ Correct! Well done! 🎉")
                retry_score += 1
            else:
                print(f"✗ Still wrong. Remember: {answer}")
            
            record_quiz_result(word["italian"], correct, "retry")
            speak_word(word["italian"])
        
        print(f"\n{'='*50}")
        print(f"Retry Results: {retry_score}/{len(wrong_answers)} correct")
    
    print(f"\n{'='*50}")
    accuracy = score*100//len(selected) if selected else 0
    print(f"Quiz complete! Score: {score}/{len(selected)} ({accuracy}%)")
    
    if wrong_answers:
        improvement = retry_score*100//len(wrong_answers) if wrong_answers else 0
        print(f"Retry accuracy: {improvement}%")
        if improvement >= 80:
            print("🌟 Excellent improvement!")
        elif improvement >= 50:
            print("👍 Good progress!")
        else:
            print("💪 Keep practicing these words!")
    print(f"{'='*50}")


def run_multiple_choice(n=10, retry_wrong=True):
    """Run a multiple choice quiz.
    
    Args:
        n: Number of words to quiz
        retry_wrong: If True, retry wrong answers at end of quiz
    """
    words = load_vocabulary()
    
    if len(words) < 4:
        print("Need at least 4 words for multiple choice quiz")
        return
    
    # Get balanced selection: 30% new, 40% weak, 30% review words
    selected = get_words_for_quiz(words, min(n, len(words)))
    score = 0
    wrong_answers = []  # Track words that need retry
    
    print(f"\n{'='*50}")
    print(f"📝 Multiple Choice Quiz")
    if retry_wrong:
        print("💡 Wrong answers will be retried at the end")
    print(f"{'='*50}")
    
    for i, word in enumerate(selected, 1):
        question = word["italian"]
        correct_answer = word["greek"]
        
        # Generate wrong answers
        wrong = random.sample([w["greek"] for w in words if w["greek"] != correct_answer], 3)
        options = [correct_answer] + wrong
        random.shuffle(options)
        
        print(f"\n[{i}/{len(selected)}] {question}")
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
            print("✓ Correct!")
            score += 1
        else:
            print(f"✗ Wrong. Answer: {correct_answer}")
            if retry_wrong:
                wrong_answers.append(word)
        
        record_quiz_result(word["italian"], correct, "multiple_choice")
        speak_word(word["italian"])
    
    # Immediate retry of wrong answers
    if retry_wrong and wrong_answers:
        print(f"\n{'='*50}")
        print(f"🔄 Review Time! Let's retry the {len(wrong_answers)} words you missed")
        print(f"{'='*50}")
        
        retry_score = 0
        for i, word in enumerate(wrong_answers, 1):
            question = word["italian"]
            correct_answer = word["greek"]
            
            # Generate new wrong answers for retry
            wrong = random.sample([w["greek"] for w in words if w["greek"] != correct_answer], 3)
            options = [correct_answer] + wrong
            random.shuffle(options)
            
            print(f"\n[Retry {i}/{len(wrong_answers)}] {question}")
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
                print("✓ Correct! Well done! 🎉")
                retry_score += 1
            else:
                print(f"✗ Still wrong. Remember: {correct_answer}")
            
            record_quiz_result(word["italian"], correct, "retry")
            speak_word(word["italian"])
        
        print(f"\n{'='*50}")
        print(f"Retry Results: {retry_score}/{len(wrong_answers)} correct")
    
    print(f"\n{'='*50}")
    accuracy = score*100//len(selected) if selected else 0
    print(f"Quiz complete! Score: {score}/{len(selected)} ({accuracy}%)")
    
    if wrong_answers:
        improvement = retry_score*100//len(wrong_answers) if wrong_answers else 0
        print(f"Retry accuracy: {improvement}%")
        if improvement >= 80:
            print("🌟 Excellent improvement!")
        elif improvement >= 50:
            print("👍 Good progress!")
        else:
            print("💪 Keep practicing these words!")
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
