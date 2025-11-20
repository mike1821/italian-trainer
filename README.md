Italian-Greek Vocabulary Practice Tool

Usage tool.py:

    python tool.py quiz <n>       - Random quiz with n words (Italian->Greek)
    python tool.py quiz-reverse <n> - Quiz Greek->Italian
    python tool.py lookup <word>  - Find translation
    python tool.py add <italian> <greek> - Add new word to xlsx
    python tool.py list           - Show all words
    python tool.py stats          - Show vocabulary statistics
    python tool.py export <n>     - Export n random words for AI sentence practice


Usage vocab_enhanced.py

Setup:
    cd /root/sources
    pip install -r requirements.txt
    python vocab_enhanced.py migrate  # Add Category & Difficulty columns to your xlsx

Categories - Filter by verbs/nouns/etc:
    python vocab_enhanced.py quiz 10 --category verbs
    python vocab_enhanced.py list --category nouns

Difficulty levels (1=easy, 2=medium, 3=hard):
    python vocab_enhanced.py quiz 10 --difficulty 3
    python vocab_enhanced.py add "parlare" "μιλάω" verbs 2

Audio pronunciation:
    python vocab_enhanced.py speak matrimonio

Flashcard mode (interactive flip cards):
    python vocab_enhanced.py flashcard 15

Sentence generation (simple templates using your words):
    python vocab_enhanced.py sentence

Multiple choice quiz:
    python vocab_enhanced.py quiz-mc 10

Web interface (browser-based practice):
    python vocab_enhanced.py web
    # Open http://localhost:5000

Bonus - Spaced repetition:
    Tracks which words you struggle with
    Prioritizes weak words in quizzes automatically
    Shows words needing review:
    Try python vocab_enhanced.py help for full command list.