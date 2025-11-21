#!/usr/bin/env python3
"""
Quiz and practice mode functions.
"""
import random
from app.vocab_core import load_vocabulary, filter_words
from database.vocab_db import record_quiz_result, get_weak_words
from app.vocab_audio import speak_word


def run_quiz(n=10, reverse=False, category=None, difficulty=None):
    """Run a standard quiz with typed answers."""
    words = load_vocabulary()
    words = filter_words(words, category, difficulty)
    
    if not words:
        print("No words match the specified filters.")
        return
    
    # Prioritize weak words
    weak = get_weak_words(n // 2)
    weak_words = [w for w in words if w["italian"] in weak]
    other_words = [w for w in words if w["italian"] not in weak]
    
    selected = weak_words[:n//2] + random.sample(other_words, min(n - len(weak_words[:n//2]), len(other_words)))
    random.shuffle(selected)
    
    score = 0
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
        
        record_quiz_result(word["italian"], correct, "standard")
        speak_word(word["italian"])
    
    print(f"\n{'='*50}")
    print(f"Quiz complete! Score: {score}/{len(selected)} ({score*100//len(selected)}%)")


def run_multiple_choice(n=10):
    """Run a multiple choice quiz."""
    words = load_vocabulary()
    
    if len(words) < 4:
        print("Need at least 4 words for multiple choice quiz")
        return
    
    selected = random.sample(words, min(n, len(words)))
    score = 0
    
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
        
        record_quiz_result(word["italian"], correct, "multiple_choice")
        speak_word(word["italian"])
    
    print(f"\n{'='*50}")
    print(f"Quiz complete! Score: {score}/{len(selected)} ({score*100//len(selected)}%)")


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
