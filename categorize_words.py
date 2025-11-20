#!/usr/bin/env python3
"""
Automatically categorize Italian vocabulary words based on semantic analysis.
"""
import openpyxl
from pathlib import Path
from collections import defaultdict

VOCAB_FILE = Path("vocabulary.xlsx")

# Define category patterns based on word endings, meanings, and common patterns
CATEGORY_RULES = {
    'verbs': {
        'endings': ['are', 'ere', 'ire', 'rsi'],
        'keywords': ['parlare', 'mangiare', 'bere', 'andare', 'fare', 'dire', 'venire', 
                     'vedere', 'sapere', 'volere', 'potere', 'dovere']
    },
    'food': {
        'keywords': ['pane', 'pasta', 'carne', 'pesce', 'formaggio', 'vino', 'acqua', 
                     'caffè', 'tè', 'latte', 'frutta', 'verdura', 'dolce', 'zucchero',
                     'sale', 'olio', 'riso', 'pizza', 'gelato', 'biscotti']
    },
    'numbers': {
        'keywords': ['uno', 'due', 'tre', 'quattro', 'cinque', 'sei', 'sette', 'otto',
                     'nove', 'dieci', 'cento', 'mille', 'primo', 'secondo', 'terzo']
    },
    'time': {
        'keywords': ['ora', 'giorno', 'settimana', 'mese', 'anno', 'oggi', 'domani', 
                     'ieri', 'mattina', 'sera', 'notte', 'pomeriggio', 'momento',
                     'tempo', 'lunedì', 'martedì', 'mercoledì', 'giovedì', 'venerdì',
                     'sabato', 'domenica']
    },
    'family': {
        'keywords': ['madre', 'padre', 'figlio', 'figlia', 'fratello', 'sorella',
                     'nonno', 'nonna', 'zio', 'zia', 'cugino', 'marito', 'moglie',
                     'famiglia', 'bambino', 'bambina', 'ragazzo', 'ragazza']
    },
    'body': {
        'keywords': ['testa', 'occhio', 'orecchio', 'naso', 'bocca', 'mano', 'piede',
                     'braccio', 'gamba', 'cuore', 'corpo', 'dito', 'capelli']
    },
    'colors': {
        'keywords': ['rosso', 'blu', 'verde', 'giallo', 'nero', 'bianco', 'grigio',
                     'marrone', 'arancione', 'rosa', 'viola', 'colore']
    },
    'places': {
        'keywords': ['casa', 'città', 'paese', 'strada', 'piazza', 'chiesa', 'scuola',
                     'ospedale', 'negozio', 'ristorante', 'bar', 'hotel', 'aeroporto',
                     'stazione', 'museo', 'teatro', 'parco', 'centro', 'posto', 'luogo']
    },
    'clothing': {
        'keywords': ['vestito', 'camicia', 'pantaloni', 'gonna', 'cappello', 'scarpe',
                     'giacca', 'cappotto', 'maglietta', 'calze', 'vestiti']
    },
    'travel': {
        'keywords': ['viaggio', 'treno', 'aereo', 'autobus', 'macchina', 'biglietto',
                     'partenza', 'arrivo', 'valigia', 'passaporto', 'turista']
    },
    'weather': {
        'keywords': ['tempo', 'sole', 'pioggia', 'neve', 'vento', 'caldo', 'freddo',
                     'nuvola', 'cielo', 'temperatura']
    },
    'adjectives': {
        'endings': ['o', 'a', 'e'],
        'keywords': ['bello', 'brutto', 'grande', 'piccolo', 'buono', 'cattivo',
                     'nuovo', 'vecchio', 'giovane', 'alto', 'basso', 'lungo', 'corto',
                     'facile', 'difficile', 'importante', 'necessario', 'possibile']
    },
    'greetings': {
        'keywords': ['ciao', 'buongiorno', 'buonasera', 'buonanotte', 'arrivederci',
                     'grazie', 'prego', 'scusa', 'permesso', 'salve']
    },
    'pronouns': {
        'keywords': ['io', 'tu', 'lui', 'lei', 'noi', 'voi', 'loro', 'mi', 'ti',
                     'ci', 'vi', 'questo', 'quello', 'qualche', 'tutto']
    },
    'prepositions': {
        'keywords': ['di', 'a', 'da', 'in', 'con', 'su', 'per', 'tra', 'fra']
    },
    'conjunctions': {
        'keywords': ['e', 'ma', 'o', 'però', 'quindi', 'perché', 'se', 'quando', 'come']
    }
}


def categorize_word(italian, greek=''):
    """Determine the best category for a word."""
    italian_lower = italian.lower().strip()
    greek_lower = greek.lower().strip()
    
    # Check each category
    scores = defaultdict(int)
    
    for category, rules in CATEGORY_RULES.items():
        # Check keywords (exact match or contains)
        if 'keywords' in rules:
            for keyword in rules['keywords']:
                if italian_lower == keyword or keyword in italian_lower:
                    scores[category] += 10
                    
        # Check endings for verbs/adjectives
        if 'endings' in rules:
            for ending in rules['endings']:
                if italian_lower.endswith(ending):
                    scores[category] += 5
    
    # Return best match or 'other'
    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]
    return 'other'


def analyze_and_categorize():
    """Analyze vocabulary and suggest categories."""
    if not VOCAB_FILE.exists():
        print(f"Error: {VOCAB_FILE} not found")
        return
    
    wb = openpyxl.load_workbook(VOCAB_FILE)
    ws = wb.active
    
    print("Analyzing vocabulary...")
    print("="*60)
    
    # Collect categorizations
    categorizations = []
    category_counts = defaultdict(int)
    
    for row in range(2, ws.max_row + 1):
        italian = ws.cell(row, 1).value
        greek = ws.cell(row, 2).value
        
        if not italian:
            continue
            
        italian = str(italian).strip()
        greek = str(greek).strip() if greek else ""
        
        suggested_category = categorize_word(italian, greek)
        categorizations.append((row, italian, greek, suggested_category))
        category_counts[suggested_category] += 1
    
    # Show summary
    print(f"\nTotal words: {len(categorizations)}")
    print(f"\nSuggested categorization:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count} words")
    
    # Ask for confirmation
    print("\n" + "="*60)
    response = input("\nApply these categories? (y/n): ").lower()
    
    if response != 'y':
        print("Cancelled.")
        wb.close()
        return
    
    # Apply categories
    print("\nApplying categories...")
    for row, italian, greek, category in categorizations:
        ws.cell(row, 3, category)
    
    wb.save(VOCAB_FILE)
    wb.close()
    
    print(f"✓ Categories updated in {VOCAB_FILE}")
    print("\nYou can now filter by category:")
    print("  python vocab.py quiz --category verbs")
    print("  python vocab.py quiz --category food")
    print("  etc.")


if __name__ == "__main__":
    analyze_and_categorize()
