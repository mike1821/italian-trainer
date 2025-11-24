#!/usr/bin/env python3
"""
Greek sentence generator for practicing Greek→Italian translation.
Handles Greek articles, verb conjugations, and grammatical agreements.
"""
import random

# Greek articles (definite)
GREEK_ARTICLES = {
    'masculine_singular': ['ο'],     # ο άντρας (the man)
    'masculine_plural': ['οι'],      # οι άντρες (the men)
    'feminine_singular': ['η'],      # η γυναίκα (the woman)
    'feminine_plural': ['οι'],       # οι γυναίκες (the women)
    'neuter_singular': ['το'],       # το παιδί (the child)
    'neuter_plural': ['τα']          # τα παιδιά (the children)
}

# Common Greek verb conjugations (present tense)
VERB_ΕΙΜΑΙ = {  # to be
    'εγώ': 'είμαι',
    'εσύ': 'είσαι',
    'αυτός/αυτή': 'είναι',
    'εμείς': 'είμαστε',
    'εσείς': 'είστε',
    'αυτοί/αυτές': 'είναι'
}

VERB_ΕΧΩ = {  # to have
    'εγώ': 'έχω',
    'εσύ': 'έχεις',
    'αυτός/αυτή': 'έχει',
    'εμείς': 'έχουμε',
    'εσείς': 'έχετε',
    'αυτοί/αυτές': 'έχουν'
}


def get_greek_article(word):
    """Get appropriate Greek article for a word (simplified heuristics)."""
    word_lower = word.lower()
    
    # Simplified gender determination based on endings
    # Masculine: -ος, -ης, -ας
    if word_lower.endswith(('ος', 'ης', 'ας')):
        return 'ο'
    # Feminine: -α, -η
    elif word_lower.endswith(('α', 'η')):
        return 'η'
    # Neuter: -ο, -ι, -μα
    elif word_lower.endswith(('ο', 'ι', 'μα')):
        return 'το'
    else:
        return 'το'  # default to neuter


class GreekSentenceGenerator:
    """Generate grammatically correct Greek sentences."""
    
    def __init__(self, vocabulary):
        """Initialize with vocabulary list."""
        self.vocab = vocabulary
        
        # Categorize words
        self.nouns = [w for w in vocabulary if w['category'] in 
                     ['food', 'places', 'family', 'body', 'clothing', 'other']]
        self.verbs = [w for w in vocabulary if w['category'] == 'verbs']
        self.adjectives = [w for w in vocabulary if w['category'] == 'adjectives']
        self.time_words = [w for w in vocabulary if w['category'] == 'time']
        self.numbers = [w for w in vocabulary if w['category'] == 'numbers']
    
    def generate_ειμαι_sentence(self):
        """Generate sentence with verb 'είμαι' (to be)."""
        if not self.nouns or not self.adjectives:
            return None
        
        noun = random.choice(self.nouns)
        adj = random.choice(self.adjectives)
        article = get_greek_article(noun['greek'])
        
        # "Το βιβλίο είναι καλό" (The book is good)
        return {
            'greek': f"{article.capitalize()} {noun['greek']} είναι {adj['greek']}.",
            'italian': f"{self.get_italian_article(noun['italian'])} {noun['italian']} è {adj['italian']}.",
            'pattern': 'article + noun + είμαι + adjective',
            'words_used': [noun['greek'], adj['greek']]
        }
    
    def generate_εχω_sentence(self):
        """Generate sentence with verb 'έχω' (to have)."""
        if not self.nouns:
            return None
        
        subject = random.choice(['εγώ', 'εσύ', 'αυτός/αυτή'])
        verb = VERB_ΕΧΩ[subject]
        noun = random.choice(self.nouns)
        article = get_greek_article(noun['greek'])
        
        subject_str = subject.split('/')[0] if '/' in subject else subject
        italian_subject = {'εγώ': 'io', 'εσύ': 'tu', 'αυτός': 'lui'}[subject_str]
        italian_verb = {'εγώ': 'ho', 'εσύ': 'hai', 'αυτός': 'ha'}[subject_str]
        
        # "Εγώ έχω ένα βιβλίο" (I have a book)
        return {
            'greek': f"{subject_str.capitalize()} {verb} {article} {noun['greek']}.",
            'italian': f"{italian_subject.capitalize()} {italian_verb} {self.get_italian_article(noun['italian'], definite=False)} {noun['italian']}.",
            'pattern': f'subject + έχω + article + noun',
            'words_used': [noun['greek']]
        }
    
    def generate_simple_statement(self):
        """Generate simple statement with demonstrative."""
        if not self.nouns:
            return None
        
        noun = random.choice(self.nouns)
        article = get_greek_article(noun['greek'])
        
        # "Αυτό είναι το βιβλίο" (This is the book)
        return {
            'greek': f"Αυτό είναι {article} {noun['greek']}.",
            'italian': f"Questo è {self.get_italian_article(noun['italian'])} {noun['italian']}.",
            'pattern': 'demonstrative + είμαι + article + noun',
            'words_used': [noun['greek']]
        }
    
    def generate_location_sentence(self):
        """Generate sentence with location."""
        if not self.nouns:
            return None
        
        noun = random.choice([n for n in self.nouns if n['category'] == 'places'] or self.nouns)
        article = get_greek_article(noun['greek'])
        
        # "Πάω στο σπίτι" (I go to the house)
        return {
            'greek': f"Πάω στο {noun['greek']}.",
            'italian': f"Vado a casa." if noun['italian'] == 'casa' else f"Vado al {noun['italian']}.",
            'pattern': 'verb + preposition + noun',
            'words_used': [noun['greek']]
        }
    
    def generate_time_sentence(self):
        """Generate sentence with time expression."""
        if not self.time_words:
            return None
        
        time_word = random.choice(self.time_words)
        
        if self.verbs:
            verb = random.choice(self.verbs)
            # "Σήμερα τρώω" (Today I eat)
            return {
                'greek': f"{time_word['greek'].capitalize()} {verb['greek']}.",
                'italian': f"{time_word['italian'].capitalize()} {verb['italian']}.",
                'pattern': 'time_word + verb',
                'words_used': [time_word['greek'], verb['greek']]
            }
        else:
            # "Σήμερα είναι καλά" (Today is good)
            return {
                'greek': f"{time_word['greek'].capitalize()} είναι καλά.",
                'italian': f"{time_word['italian'].capitalize()} va bene.",
                'pattern': 'time_word + είμαι',
                'words_used': [time_word['greek']]
            }
    
    def generate_number_sentence(self):
        """Generate sentence with numbers."""
        if not self.numbers or not self.nouns:
            return None
        
        number = random.choice(self.numbers)
        noun = random.choice(self.nouns)
        
        # "Έχω πέντε βιβλία" (I have five books)
        return {
            'greek': f"Έχω {number['greek']} {noun['greek']}.",
            'italian': f"Ho {number['italian']} {noun['italian']}.",
            'pattern': 'έχω + number + noun',
            'words_used': [number['greek'], noun['greek']]
        }
    
    def get_italian_article(self, italian_word, definite=True):
        """Get Italian article for a word (simplified)."""
        word_lower = italian_word.lower()
        starts_vowel = word_lower[0] in 'aeiou'
        is_masculine = word_lower.endswith(('o', 'ore', 'one'))
        
        if definite:
            if is_masculine:
                return "l'" if starts_vowel else 'il'
            else:
                return "l'" if starts_vowel else 'la'
        else:
            if is_masculine:
                return 'un'
            else:
                return "un'" if starts_vowel else 'una'
    
    def generate(self):
        """Generate a random grammatically correct Greek sentence."""
        generators = [
            self.generate_ειμαι_sentence,
            self.generate_εχω_sentence,
            self.generate_simple_statement,
        ]
        
        if any(n['category'] == 'places' for n in self.nouns):
            generators.append(self.generate_location_sentence)
        
        if self.time_words:
            generators.append(self.generate_time_sentence)
        
        if self.numbers:
            generators.append(self.generate_number_sentence)
        
        # Try generators until we get a valid sentence
        random.shuffle(generators)
        for gen in generators:
            sentence = gen()
            if sentence:
                return sentence
        
        # Fallback to simple pattern
        if self.nouns:
            noun = random.choice(self.nouns)
            article = get_greek_article(noun['greek'])
            return {
                'greek': f"Αυτό είναι {article} {noun['greek']}.",
                'italian': f"Questo è {self.get_italian_article(noun['italian'])} {noun['italian']}.",
                'pattern': 'demonstrative + noun',
                'words_used': [noun['greek']]
            }
        
        return {
            'greek': "Γεια σου! Τι κάνεις;",
            'italian': "Ciao! Come stai?",
            'pattern': 'greeting',
            'words_used': []
        }


def generate_greek_sentence(vocabulary):
    """Generate a grammatically correct Greek sentence from vocabulary."""
    generator = GreekSentenceGenerator(vocabulary)
    return generator.generate()
