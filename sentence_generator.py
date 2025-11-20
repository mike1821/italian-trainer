#!/usr/bin/env python3
"""
Intelligent Italian sentence generator with proper grammar.
Handles articles, verb conjugations, and grammatical agreements.
"""
import random

# Italian articles
DEFINITE_ARTICLES = {
    'masculine_singular': ['il', 'lo', "l'"],  # il libro, lo studente, l'amico
    'masculine_plural': ['i', 'gli'],           # i libri, gli studenti
    'feminine_singular': ['la', "l'"],          # la casa, l'amica
    'feminine_plural': ['le']                   # le case
}

INDEFINITE_ARTICLES = {
    'masculine': ['un', 'uno'],  # un libro, uno studente
    'feminine': ['una', "un'"]   # una casa, un'amica
}

# Common verb conjugations (present tense)
VERB_ESSERE = {
    'io': 'sono', 'tu': 'sei', 'lui/lei': 'è',
    'noi': 'siamo', 'voi': 'siete', 'loro': 'sono'
}

VERB_AVERE = {
    'io': 'ho', 'tu': 'hai', 'lui/lei': 'ha',
    'noi': 'abbiamo', 'voi': 'avete', 'loro': 'hanno'
}

# Prepositions that combine with articles
PREPOSITION_ARTICLE = {
    'di': {'il': 'del', 'lo': 'dello', 'la': 'della', 'i': 'dei', 'gli': 'degli', 'le': 'delle'},
    'a': {'il': 'al', 'lo': 'allo', 'la': 'alla', 'i': 'ai', 'gli': 'agli', 'le': 'alle'},
    'da': {'il': 'dal', 'lo': 'dallo', 'la': 'dalla', 'i': 'dai', 'gli': 'dagli', 'le': 'dalle'},
    'in': {'il': 'nel', 'lo': 'nello', 'la': 'nella', 'i': 'nei', 'gli': 'negli', 'le': 'nelle'},
    'su': {'il': 'sul', 'lo': 'sullo', 'la': 'sulla', 'i': 'sui', 'gli': 'sugli', 'le': 'sulle'},
}


def get_article(word, definite=True, plural=False):
    """Get appropriate article for a word."""
    word_lower = word.lower()
    
    # Simple heuristics for gender (can be improved)
    is_masculine = word_lower.endswith(('o', 'ore', 'one'))
    is_feminine = word_lower.endswith(('a', 'ione', 'ice'))
    
    # Check if word starts with vowel
    starts_vowel = word_lower[0] in 'aeiou'
    
    # Check for special consonant clusters (z, s+consonant, gn, ps, etc.)
    starts_special = (word_lower.startswith(('z', 'gn', 'ps', 'pn')) or 
                     (word_lower.startswith('s') and len(word_lower) > 1 and word_lower[1] not in 'aeiou'))
    
    if definite:
        if plural:
            if is_masculine:
                return 'gli' if (starts_vowel or starts_special) else 'i'
            else:  # feminine
                return 'le'
        else:  # singular
            if is_masculine:
                if starts_vowel:
                    return "l'"
                elif starts_special:
                    return 'lo'
                else:
                    return 'il'
            else:  # feminine
                return "l'" if starts_vowel else 'la'
    else:  # indefinite
        if is_masculine:
            return 'uno' if starts_special else 'un'
        else:  # feminine
            return "un'" if starts_vowel else 'una'


def combine_preposition_article(prep, article):
    """Combine preposition with article (e.g., 'di' + 'il' = 'del')."""
    if prep in PREPOSITION_ARTICLE and article in PREPOSITION_ARTICLE[prep]:
        return PREPOSITION_ARTICLE[prep][article]
    return f"{prep} {article}"


class SentenceGenerator:
    """Generate grammatically correct Italian sentences."""
    
    def __init__(self, vocabulary):
        """Initialize with vocabulary list."""
        self.vocab = vocabulary
        
        # Categorize words
        self.nouns = [w for w in vocabulary if w['category'] in 
                     ['food', 'places', 'family', 'body', 'clothing', 'other']]
        self.verbs = [w for w in vocabulary if w['category'] == 'verbs']
        self.adjectives = [w for w in vocabulary if w['category'] == 'adjectives']
        self.time_words = [w for w in vocabulary if w['category'] == 'time']
    
    def generate_essere_sentence(self):
        """Generate sentence with verb 'essere' (to be)."""
        subject = random.choice(['io', 'tu', 'lui/lei', 'noi', 'voi', 'loro'])
        verb = VERB_ESSERE[subject]
        
        if self.adjectives:
            adj = random.choice(self.adjectives)['italian']
            if self.nouns:
                noun = random.choice(self.nouns)['italian']
                article = get_article(noun, definite=True)
                return {
                    'italian': f"{article.capitalize()} {noun} è {adj}.",
                    'pattern': 'definite_article + noun + essere + adjective',
                    'words_used': [noun, adj]
                }
        
        # Fallback: essere + noun
        if len(self.nouns) >= 2:
            noun1, noun2 = random.sample(self.nouns, 2)
            article1 = get_article(noun1['italian'], definite=False)
            article2 = get_article(noun2['italian'], definite=True)
            return {
                'italian': f"{article1.capitalize()} {noun1['italian']} è {article2} {noun2['italian']}.",
                'pattern': 'indefinite_article + noun + essere + definite_article + noun',
                'words_used': [noun1['italian'], noun2['italian']]
            }
        
        return None
    
    def generate_avere_sentence(self):
        """Generate sentence with verb 'avere' (to have)."""
        subject = random.choice(['io', 'tu', 'lui/lei', 'noi'])
        verb = VERB_AVERE[subject]
        
        if self.nouns:
            noun = random.choice(self.nouns)
            article = get_article(noun['italian'], definite=False)
            
            subject_str = subject if subject in ['io', 'tu', 'noi'] else 'lui'
            
            return {
                'italian': f"{subject_str.capitalize()} {verb} {article} {noun['italian']}.",
                'pattern': f'subject({subject}) + avere + indefinite_article + noun',
                'words_used': [noun['italian']]
            }
        
        return None
    
    def generate_preposition_sentence(self):
        """Generate sentence with preposition + article."""
        if len(self.nouns) < 2:
            return None
        
        prep = random.choice(['in', 'su', 'di', 'a'])
        verb = random.choice(['vado', 'sono', 'vivo', 'lavoro', 'studio'])
        
        noun = random.choice(self.nouns)
        article = get_article(noun['italian'], definite=True)
        combined = combine_preposition_article(prep, article)
        
        return {
            'italian': f"Io {verb} {combined} {noun['italian']}.",
            'pattern': f'io + verb + preposition({prep}) + article + noun',
            'words_used': [noun['italian']]
        }
    
    def generate_complex_sentence(self):
        """Generate more complex sentence with multiple elements."""
        if len(self.nouns) < 2:
            return None
        
        subject = random.choice(['io', 'tu', 'lui'])
        verb_avere = VERB_AVERE[subject]
        
        noun1, noun2 = random.sample(self.nouns, 2)
        article1 = get_article(noun1['italian'], definite=False)
        article2 = get_article(noun2['italian'], definite=True)
        
        prep = random.choice(['in', 'su', 'con'])
        combined = combine_preposition_article(prep, article2)
        
        subject_str = subject if subject in ['io', 'tu'] else 'lui'
        
        return {
            'italian': f"{subject_str.capitalize()} {verb_avere} {article1} {noun1['italian']} {combined} {noun2['italian']}.",
            'pattern': f'subject + avere + noun + preposition + noun',
            'words_used': [noun1['italian'], noun2['italian']]
        }
    
    def generate_time_sentence(self):
        """Generate sentence with time expression."""
        if not self.time_words or not self.verbs:
            return None
        
        time_word = random.choice(self.time_words)
        verb = random.choice(self.verbs)
        
        return {
            'italian': f"{time_word['italian'].capitalize()} io {verb['italian']}.",
            'pattern': 'time_expression + io + verb',
            'words_used': [time_word['italian'], verb['italian']]
        }
    
    def generate(self):
        """Generate a random grammatically correct sentence."""
        generators = [
            self.generate_essere_sentence,
            self.generate_avere_sentence,
            self.generate_preposition_sentence,
            self.generate_complex_sentence,
        ]
        
        if self.time_words and self.verbs:
            generators.append(self.generate_time_sentence)
        
        # Try generators until we get a valid sentence
        random.shuffle(generators)
        for gen in generators:
            sentence = gen()
            if sentence:
                return sentence
        
        # Fallback to simple pattern
        if self.nouns:
            noun = random.choice(self.nouns)
            article = get_article(noun['italian'], definite=True)
            return {
                'italian': f"Ecco {article} {noun['italian']}.",
                'pattern': 'ecco + article + noun',
                'words_used': [noun['italian']]
            }
        
        return {
            'italian': "Ciao! Come stai?",
            'pattern': 'greeting',
            'words_used': ['ciao', 'stai']
        }


def generate_smart_sentence(vocabulary):
    """Generate a grammatically correct Italian sentence from vocabulary."""
    generator = SentenceGenerator(vocabulary)
    return generator.generate()
