#!/usr/bin/env python3
"""
Generate grammar exercise JSON files with 100+ exercises per category.
Run from project root: python data/grammar/generate_grammar_data.py
"""
import json
import random
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent

# --- 1. VERBS PRESENT (present indicative, all persons) ---
PERSONS = ["io", "tu", "lui/lei", "noi", "voi", "loro"]

# -are: o, i, a, iamo, ate, ano
VERBS_ARE = [
    ("parlare", {"io": "parlo", "tu": "parli", "lui/lei": "parla", "noi": "parliamo", "voi": "parlate", "loro": "parlano"}),
    ("mangiare", {"io": "mangio", "tu": "mangi", "lui/lei": "mangia", "noi": "mangiamo", "voi": "mangiate", "loro": "mangiano"}),
    ("lavorare", {"io": "lavoro", "tu": "lavori", "lui/lei": "lavora", "noi": "lavoriamo", "voi": "lavorate", "loro": "lavorano"}),
    ("amare", {"io": "amo", "tu": "ami", "lui/lei": "ama", "noi": "amiamo", "voi": "amate", "loro": "amano"}),
    ("cantare", {"io": "canto", "tu": "canti", "lui/lei": "canta", "noi": "cantiamo", "voi": "cantate", "loro": "cantano"}),
    ("comprare", {"io": "compro", "tu": "compri", "lui/lei": "compra", "noi": "compriamo", "voi": "comprate", "loro": "comprano"}),
    ("ascoltare", {"io": "ascolto", "tu": "ascolti", "lui/lei": "ascolta", "noi": "ascoltiamo", "voi": "ascoltate", "loro": "ascoltano"}),
    ("guardare", {"io": "guardo", "tu": "guardi", "lui/lei": "guarda", "noi": "guardiamo", "voi": "guardate", "loro": "guardano"}),
    ("studiare", {"io": "studio", "tu": "studi", "lui/lei": "studia", "noi": "studiamo", "voi": "studiate", "loro": "studiano"}),
    ("viaggiare", {"io": "viaggio", "tu": "viaggi", "lui/lei": "viaggia", "noi": "viaggiamo", "voi": "viaggiate", "loro": "viaggiano"}),
    ("abitare", {"io": "abito", "tu": "abiti", "lui/lei": "abita", "noi": "abitiamo", "voi": "abitate", "loro": "abitano"}),
    ("ballare", {"io": "ballo", "tu": "balli", "lui/lei": "balla", "noi": "balliamo", "voi": "ballate", "loro": "ballano"}),
    ("cucinare", {"io": "cucino", "tu": "cucini", "lui/lei": "cucina", "noi": "cuciniamo", "voi": "cucinate", "loro": "cucinano"}),
    ("aspettare", {"io": "aspetto", "tu": "aspetti", "lui/lei": "aspetta", "noi": "aspettiamo", "voi": "aspettate", "loro": "aspettano"}),
    ("telefonare", {"io": "telefono", "tu": "telefoni", "lui/lei": "telefona", "noi": "telefoniamo", "voi": "telefonate", "loro": "telefonano"}),
    ("giocare", {"io": "gioco", "tu": "giochi", "lui/lei": "gioca", "noi": "giochiamo", "voi": "giocate", "loro": "giocano"}),
    ("pensare", {"io": "penso", "tu": "pensi", "lui/lei": "pensa", "noi": "pensiamo", "voi": "pensate", "loro": "pensano"}),
    ("tornare", {"io": "torno", "tu": "torni", "lui/lei": "torna", "noi": "torniamo", "voi": "tornate", "loro": "tornano"}),
    ("entrare", {"io": "entro", "tu": "entri", "lui/lei": "entra", "noi": "entriamo", "voi": "entrate", "loro": "entrano"}),
    ("camminare", {"io": "cammino", "tu": "cammini", "lui/lei": "cammina", "noi": "camminiamo", "voi": "camminate", "loro": "camminano"}),
]

# -ere: o, i, e, iamo, ete, ono
VERBS_ERE = [
    ("scrivere", {"io": "scrivo", "tu": "scrivi", "lui/lei": "scrive", "noi": "scriviamo", "voi": "scrivete", "loro": "scrivono"}),
    ("leggere", {"io": "leggo", "tu": "leggi", "lui/lei": "legge", "noi": "leggiamo", "voi": "leggete", "loro": "leggono"}),
    ("vedere", {"io": "vedo", "tu": "vedi", "lui/lei": "vede", "noi": "vediamo", "voi": "vedete", "loro": "vedono"}),
    ("prendere", {"io": "prendo", "tu": "prendi", "lui/lei": "prende", "noi": "prendiamo", "voi": "prendete", "loro": "prendono"}),
    ("rispondere", {"io": "rispondo", "tu": "rispondi", "lui/lei": "risponde", "noi": "rispondiamo", "voi": "rispondete", "loro": "rispondono"}),
    ("vendere", {"io": "vendo", "tu": "vendi", "lui/lei": "vende", "noi": "vendiamo", "voi": "vendete", "loro": "vendono"}),
    ("perdere", {"io": "perdo", "tu": "perdi", "lui/lei": "perde", "noi": "perdiamo", "voi": "perdete", "loro": "perdono"}),
    ("correre", {"io": "corro", "tu": "corri", "lui/lei": "corre", "noi": "corriamo", "voi": "correte", "loro": "corrono"}),
    ("credere", {"io": "credo", "tu": "credi", "lui/lei": "crede", "noi": "crediamo", "voi": "credete", "loro": "credono"}),
    ("chiedere", {"io": "chiedo", "tu": "chiedi", "lui/lei": "chiede", "noi": "chiediamo", "voi": "chiedete", "loro": "chiedono"}),
    ("chiudere", {"io": "chiudo", "tu": "chiudi", "lui/lei": "chiude", "noi": "chiudiamo", "voi": "chiudete", "loro": "chiudono"}),
    ("conoscere", {"io": "conosco", "tu": "conosci", "lui/lei": "conosce", "noi": "conosciamo", "voi": "conoscete", "loro": "conoscono"}),
    ("decidere", {"io": "decido", "tu": "decidi", "lui/lei": "decide", "noi": "decidiamo", "voi": "decidete", "loro": "decidono"}),
    ("mettere", {"io": "metto", "tu": "metti", "lui/lei": "mette", "noi": "mettiamo", "voi": "mettete", "loro": "mettono"}),
    ("rompere", {"io": "rompo", "tu": "rompi", "lui/lei": "rompe", "noi": "rompiamo", "voi": "rompete", "loro": "rompono"}),
    ("scendere", {"io": "scendo", "tu": "scendi", "lui/lei": "scende", "noi": "scendiamo", "voi": "scendete", "loro": "scendono"}),
    ("sapere", {"io": "so", "tu": "sai", "lui/lei": "sa", "noi": "sappiamo", "voi": "sapete", "loro": "sanno"}),
    ("bere", {"io": "bevo", "tu": "bevi", "lui/lei": "beve", "noi": "beviamo", "voi": "bevete", "loro": "bevono"}),
    ("tenere", {"io": "tengo", "tu": "tieni", "lui/lei": "tiene", "noi": "teniamo", "voi": "tenete", "loro": "tengono"}),
    ("volere", {"io": "voglio", "tu": "vuoi", "lui/lei": "vuole", "noi": "vogliamo", "voi": "volete", "loro": "vogliono"}),
]

# -ire: isco/o, isci/i, isce/e, iamo, ite, iscono/ono
VERBS_IRE = [
    ("finire", {"io": "finisco", "tu": "finisci", "lui/lei": "finisce", "noi": "finiamo", "voi": "finite", "loro": "finiscono"}),
    ("capire", {"io": "capisco", "tu": "capisci", "lui/lei": "capisce", "noi": "capiamo", "voi": "capite", "loro": "capiscono"}),
    ("preferire", {"io": "preferisco", "tu": "preferisci", "lui/lei": "preferisce", "noi": "preferiamo", "voi": "preferite", "loro": "preferiscono"}),
    ("pulire", {"io": "pulisco", "tu": "pulisci", "lui/lei": "pulisce", "noi": "puliamo", "voi": "pulite", "loro": "puliscono"}),
    ("dormire", {"io": "dormo", "tu": "dormi", "lui/lei": "dorme", "noi": "dormiamo", "voi": "dormite", "loro": "dormono"}),
    ("aprire", {"io": "apro", "tu": "apri", "lui/lei": "apre", "noi": "apriamo", "voi": "aprite", "loro": "aprono"}),
    ("offrire", {"io": "offro", "tu": "offri", "lui/lei": "offre", "noi": "offriamo", "voi": "offrite", "loro": "offrono"}),
    ("partire", {"io": "parto", "tu": "parti", "lui/lei": "parte", "noi": "partiamo", "voi": "partite", "loro": "partono"}),
    ("sentire", {"io": "sento", "tu": "senti", "lui/lei": "sente", "noi": "sentiamo", "voi": "sentite", "loro": "sentono"}),
    ("servire", {"io": "servo", "tu": "servi", "lui/lei": "serve", "noi": "serviamo", "voi": "servite", "loro": "servono"}),
    ("vestire", {"io": "vesto", "tu": "vesti", "lui/lei": "veste", "noi": "vestiamo", "voi": "vestite", "loro": "vestono"}),
    ("costruire", {"io": "costruisco", "tu": "costruisci", "lui/lei": "costruisce", "noi": "costruiamo", "voi": "costruite", "loro": "costruiscono"}),
    ("spedire", {"io": "spedisco", "tu": "spedisci", "lui/lei": "spedisce", "noi": "spediamo", "voi": "spedite", "loro": "spediscono"}),
    ("ubbidire", {"io": "ubbidisco", "tu": "ubbidisci", "lui/lei": "ubbidisce", "noi": "ubbidiamo", "voi": "ubbidite", "loro": "ubbidiscono"}),
    ("colpire", {"io": "colpisco", "tu": "colpisci", "lui/lei": "colpisce", "noi": "colpiamo", "voi": "colpite", "loro": "colpiscono"}),
]

# Irregular
VERBS_IRREGULAR = [
    ("essere", {"io": "sono", "tu": "sei", "lui/lei": "è", "noi": "siamo", "voi": "siete", "loro": "sono"}),
    ("avere", {"io": "ho", "tu": "hai", "lui/lei": "ha", "noi": "abbiamo", "voi": "avete", "loro": "hanno"}),
    ("fare", {"io": "faccio", "tu": "fai", "lui/lei": "fa", "noi": "facciamo", "voi": "fate", "loro": "fanno"}),
    ("andare", {"io": "vado", "tu": "vai", "lui/lei": "va", "noi": "andiamo", "voi": "andate", "loro": "vanno"}),
    ("stare", {"io": "sto", "tu": "stai", "lui/lei": "sta", "noi": "stiamo", "voi": "state", "loro": "stanno"}),
    ("dare", {"io": "do", "tu": "dai", "lui/lei": "dà", "noi": "diamo", "voi": "date", "loro": "danno"}),
    ("dire", {"io": "dico", "tu": "dici", "lui/lei": "dice", "noi": "diciamo", "voi": "dite", "loro": "dicono"}),
    ("uscire", {"io": "esco", "tu": "esci", "lui/lei": "esce", "noi": "usciamo", "voi": "uscite", "loro": "escono"}),
    ("venire", {"io": "vengo", "tu": "vieni", "lui/lei": "viene", "noi": "veniamo", "voi": "venite", "loro": "vengono"}),
    ("potere", {"io": "posso", "tu": "puoi", "lui/lei": "può", "noi": "possiamo", "voi": "potete", "loro": "possono"}),
    ("dovere", {"io": "devo", "tu": "devi", "lui/lei": "deve", "noi": "dobbiamo", "voi": "dovete", "loro": "devono"}),
    ("rimanere", {"io": "rimango", "tu": "rimani", "lui/lei": "rimane", "noi": "rimaniamo", "voi": "rimanete", "loro": "rimangono"}),
    ("salire", {"io": "salgo", "tu": "sali", "lui/lei": "sale", "noi": "saliamo", "voi": "salite", "loro": "salgono"}),
]


def generate_verbs_present():
    exercises = []
    all_verbs = VERBS_ARE + VERBS_ERE + VERBS_IRE + VERBS_IRREGULAR
    for inf, forms in all_verbs:
        for person in PERSONS:
            answer = forms[person]
            exercises.append({
                "prompt": f"{inf}, {person} →",
                "answer": answer
            })
    # Shuffle and ensure 100+
    random.seed(42)
    random.shuffle(exercises)
    return exercises


# --- 2. ARTICLES (definite & indefinite, M/F, S/P) ---
ARTICLE_EXERCISES_TEMPLATES = [
    # definite M S: il, lo, l'
    ("___ libro (M, S, definito)", "il"),
    ("___ amico (M, S, definito, vocale)", "l'"),
    ("___ studente (M, S, definito, s+cons)", "lo"),
    ("___ zio (M, S, definito)", "lo"),
    ("___ albero (M, S, definito)", "l'"),
    ("___ orologio (M, S, definito)", "l'"),
    ("___ bambino (M, S, definito)", "il"),
    ("___ tavolo (M, S, definito)", "il"),
    ("___ gnocco (M, S, definito)", "lo"),
    ("___ psicologo (M, S, definito)", "lo"),
    # definite F S: la, l'
    ("___ casa (F, S, definito)", "la"),
    ("___ amica (F, S, definito, vocale)", "l'"),
    ("___ donna (F, S, definito)", "la"),
    ("___ acqua (F, S, definito)", "l'"),
    ("___ ora (F, S, definito)", "l'"),
    ("___ scuola (F, S, definito)", "la"),
    ("___ finestra (F, S, definito)", "la"),
    ("___ estate (F, S, definito)", "l'"),
    # definite M P: i, gli
    ("___ libri (M, P, definito)", "i"),
    ("___ amici (M, P, definito)", "gli"),
    ("___ studenti (M, P, definito)", "gli"),
    ("___ bambini (M, P, definito)", "i"),
    ("___ alberi (M, P, definito)", "gli"),
    ("___ tavoli (M, P, definito)", "i"),
    ("___ zii (M, P, definito)", "gli"),
    # definite F P: le
    ("___ case (F, P, definito)", "le"),
    ("___ donne (F, P, definito)", "le"),
    ("___ amiche (F, P, definito)", "le"),
    ("___ scuole (F, P, definito)", "le"),
    ("___ finestre (F, P, definito)", "le"),
    # indefinite M S: un, uno
    ("___ libro (M, S, indefinito)", "un"),
    ("___ studente (M, S, indefinito)", "uno"),
    ("___ amico (M, S, indefinito)", "un"),
    ("___ zio (M, S, indefinito)", "uno"),
    ("___ bambino (M, S, indefinito)", "un"),
    ("___ psicologo (M, S, indefinito)", "uno"),
    ("___ gnocco (M, S, indefinito)", "uno"),
    ("___ tavolo (M, S, indefinito)", "un"),
    # indefinite F S: una, un'
    ("___ casa (F, S, indefinito)", "una"),
    ("___ amica (F, S, indefinito)", "un'"),
    ("___ donna (F, S, indefinito)", "una"),
    ("___ ora (F, S, indefinito)", "un'"),
    ("___ estate (F, S, indefinito)", "un'"),
    ("___ scuola (F, S, indefinito)", "una"),
]


def generate_articles():
    exercises = []
    # Repeat templates to get 100+
    while len(exercises) < 100:
        for prompt, answer in ARTICLE_EXERCISES_TEMPLATES:
            exercises.append({"prompt": prompt, "answer": answer})
    random.seed(43)
    random.shuffle(exercises)
    return exercises[:120]


# --- 3. AVERCELA, AVERE, ESSERE, ESSERCI ---
AVERE_ESSERE_SENTENCES = [
    ("Io ___ fame.", "ho"),
    ("Tu ___ sete?", "hai"),
    ("Lui ___ ragione.", "ha"),
    ("Noi ___ tempo.", "abbiamo"),
    ("Voi ___ un gatto.", "avete"),
    ("Loro ___ una casa.", "hanno"),
    ("Io ___ italiano.", "sono"),
    ("Tu ___ stanco?", "sei"),
    ("Maria ___ alta.", "è"),
    ("Noi ___ a Roma.", "siamo"),
    ("Voi ___ italiani?", "siete"),
    ("Loro ___ studenti.", "sono"),
    ("___ un libro sul tavolo.", "C'è"),
    ("___ molti libri qui.", "Ci sono"),
    ("In Italia ___ molte chiese.", "ci sono"),
    ("___ un problema.", "C'è"),
    ("Non ___ latte.", "c'è"),
    ("___ due bagni in casa.", "Ci sono"),
    ("Io ___ freddo.", "ho"),
    ("Lei ___ sonno.", "ha"),
    ("Noi ___ paura.", "abbiamo"),
    ("Loro ___ fame.", "hanno"),
    ("Io ___ a casa.", "sono"),
    ("Tu ___ in ritardo.", "sei"),
    ("Lui ___ mio amico.", "è"),
    ("Noi ___ pronti.", "siamo"),
    ("Voi ___ a Napoli?", "siete"),
    ("Loro ___ in vacanza.", "sono"),
    ("___ una bella giornata.", "È"),
    ("Qui ___ troppa gente.", "c'è"),
    ("___ tre stanze.", "Ci sono"),
    ("Non ___ niente da fare.", "c'è"),
    ("Io non ___ voglia.", "ho"),
    ("Tu ___ fretta?", "hai"),
    ("Marco ___ 25 anni.", "ha"),
    ("Noi ___ fame e sete.", "abbiamo"),
    ("Voi ___ ragione.", "avete"),
    ("I bambini ___ paura.", "hanno"),
    ("Io ___ di Milano.", "sono"),
    ("Tu ___ molto gentile.", "sei"),
    ("La casa ___ grande.", "è"),
    ("Noi ___ felici.", "siamo"),
    ("Voi ___ stanchi?", "siete"),
    ("Loro ___ a scuola.", "sono"),
    ("___ tempo per mangiare?", "C'è"),
    ("In piazza ___ molti turisti.", "ci sono"),
    ("___ una festa stasera.", "C'è"),
    ("Non ___ più pane.", "c'è"),
    ("___ due opzioni.", "Ci sono"),
    # avercela (ce l'ho, ce l'hai, etc.)
    ("Io ___ con te. (avercela)", "ce l'ho"),
    ("Tu ___ con me? (avercela)", "ce l'hai"),
    ("Lui ___ con loro. (avercela)", "ce l'ha"),
    ("Noi ___ con voi. (avercela)", "ce l'abbiamo"),
    ("Voi ___ con noi? (avercela)", "ce l'avete"),
    ("Loro ___ con lui. (avercela)", "ce l'hanno"),
    ("Non ___ ancora. (avercela, io)", "ce l'ho"),
    ("Sì, ___! (avercela, noi)", "ce l'abbiamo"),
]


def generate_avercela_avere_essere():
    exercises = []
    while len(exercises) < 100:
        for prompt, answer in AVERE_ESSERE_SENTENCES:
            exercises.append({"prompt": prompt, "answer": answer})
    random.seed(44)
    random.shuffle(exercises)
    return exercises[:110]


# --- 4. IRREGULAR NOUNS (singular → plural) ---
IRREGULAR_NOUNS = [
    ("uomo", "uomini"),
    ("donna", "donne"),
    ("bambino", "bambini"),
    ("bambina", "bambine"),
    ("amico", "amici"),
    ("amica", "amiche"),
    ("uomo", "uomini"),
    ("figlio", "figli"),
    ("figlia", "figlie"),
    ("fratello", "fratelli"),
    ("sorella", "sorelle"),
    ("padre", "padri"),
    ("madre", "madri"),
    ("marito", "mariti"),
    ("moglie", "mogli"),
    ("dottore", "dottori"),
    ("dottoressa", "dottoresse"),
    ("studente", "studenti"),
    ("studentessa", "studentesse"),
    ("signore", "signori"),
    ("signora", "signore"),
    ("tempo", "tempi"),
    ("uovo", "uova"),
    ("braccio", "braccia"),
    ("occhio", "occhi"),
    ("orecchio", "orecchi"),
    ("ginocchio", "ginocchia"),
    ("dito", "dita"),
    ("muro", "muri"),
    ("paio", "paia"),
    ("caffè", "caffè"),
    ("cinema", "cinema"),
    ("sport", "sport"),
    ("re", "re"),
    ("città", "città"),
    ("crisi", "crisi"),
    ("analisi", "analisi"),
    ("tesi", "tesi"),
    ("problema", "problemi"),
    ("sistema", "sistemi"),
    ("programma", "programmi"),
    ("film", "film"),
    ("bar", "bar"),
    ("lago", "laghi"),
    ("ago", "aghi"),
    ("luogo", "luoghi"),
    ("gioco", "giochi"),
    ("fuoco", "fuochi"),
    ("uomo", "uomini"),
    ("bue", "buoi"),
    ("ala", "ali"),
    ("arma", "armi"),
    ("ala", "ali"),
    ("lenzuolo", "lenzuola"),
    ("osso", "ossa"),
    ("labbro", "labbra"),
    ("centinaio", "centinaia"),
    ("migliaio", "migliaia"),
    ("miglio", "miglia"),
    ("inizio", "inizi"),
    ("negozio", "negozi"),
    ("zio", "zii"),
    ("figlio", "figli"),
    ("moglie", "mogli"),
    ("valigia", "valigie"),
    ("bugia", "bugie"),
    ("camicia", "camicie"),
    ("farmacia", "farmacie"),
    ("grazia", "grazie"),
    ("spiaggia", "spiagge"),
    ("legge", "leggi"),
    ("chiave", "chiavi"),
    ("mano", "mani"),
    ("eco", "echi"),
    ("lago", "laghi"),
    ("parco", "parchi"),
    ("albergo", "alberghi"),
    ("asparago", "asparagi"),
    ("medico", "medici"),
    ("nemico", "nemici"),
    ("sindaco", "sindaci"),
    ("cuoco", "cuochi"),
    ("greco", "greci"),
    ("porco", "porci"),
    ("belga", "belgi"),
    ("monarca", "monarchi"),
    ("patriarca", "patriarchi"),
    ("stomaco", "stomaci"),
    ("carico", "carichi"),
    ("amico", "amici"),
    ("tedesco", "tedeschi"),
    ("pesco", "peschi"),
    ("bosco", "boschi"),
    ("banco", "banchi"),
    ("castello", "castelli"),
    ("cavallo", "cavalli"),
    ("uccello", "uccelli"),
    ("martello", "martelli"),
    ("anello", "anelli"),
    ("libro", "libri"),
    ("albero", "alberi"),
    ("numero", "numeri"),
    ("piano", "piani"),
    ("treno", "treni"),
    ("tetto", "tetti"),
    ("gatto", "gatti"),
    ("letto", "letti"),
    ("piatto", "piatti"),
    ("bambino", "bambini"),
    ("tempo", "tempi"),
    ("nome", "nomi"),
    ("fiume", "fiumi"),
    ("uomo", "uomini"),
]


def generate_irregular_nouns():
    exercises = []
    for sing, pl in IRREGULAR_NOUNS:
        exercises.append({
            "prompt": f"Plurale di: {sing}",
            "answer": pl
        })
    # Need 100+; we have 80+ unique, duplicate some
    while len(exercises) < 100:
        for sing, pl in IRREGULAR_NOUNS[:40]:
            exercises.append({"prompt": f"Plurale di: {sing}", "answer": pl})
    random.seed(45)
    random.shuffle(exercises)
    return exercises[:110]


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    verbs = generate_verbs_present()
    articles = generate_articles()
    avere_essere = generate_avercela_avere_essere()
    nouns = generate_irregular_nouns()
    with open(DATA_DIR / "verbs_present.json", "w", encoding="utf-8") as f:
        json.dump(verbs, f, ensure_ascii=False, indent=0)
    with open(DATA_DIR / "articles.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=0)
    with open(DATA_DIR / "avercela_avere_essere_esserci.json", "w", encoding="utf-8") as f:
        json.dump(avere_essere, f, ensure_ascii=False, indent=0)
    with open(DATA_DIR / "irregular_nouns.json", "w", encoding="utf-8") as f:
        json.dump(nouns, f, ensure_ascii=False, indent=0)
    print(f"Generated: verbs_present={len(verbs)}, articles={len(articles)}, avercela_avere_essere_esserci={len(avere_essere)}, irregular_nouns={len(nouns)}")


if __name__ == "__main__":
    main()
