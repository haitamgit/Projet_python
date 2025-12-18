#TD8

#PARITE 1 

#Chargement fichier
import pandas as pd
df = pd.read_csv("data_corpus/discours_us.csv", sep="\t")

df.head()

# Distribution des auteurs
distribution_auteurs = df['speaker'].value_counts()

print("Distribution des auteurs :")
print(distribution_auteurs)

from Corpus import Corpus
from Document import Document
import re  # Pour découper les phrases
from tqdm.notebook import tqdm  # Barre de progression

# Création du corpus
corpus = Corpus(nom="Corpus_US")

# Parcours de chaque discours et ajout des phrases comme documents
for idx, row in tqdm(df.iterrows(), total=len(df), desc="Ajout des documents au corpus"):
    texte = str(row['text'])
    
# Découpage simple en phrases avec regex
    phrases = re.split(r'(?<=[.!?])\s+', texte)
    
    for i, phrase in enumerate(phrases):
        doc = Document(
            titre=f"{row['speaker']} - phrase {i+1}",
            auteur=row['speaker'],
            date=row['date'],
            url=row.get('link', ''),
            texte=phrase
        )
        corpus.add_document(doc)

# Recherche simple
resultats_search = corpus.search("america")
print("Exemple de recherche 'america' :")
for r in resultats_search[:5]:   # 5 premiers résultats
    print(r) 

# Concordance
df_concorde = corpus.concorde("america", contexte=40)
print("Exemple de concordance 'america' :")
df_concorde.head()

#PARTIE 2
# 2.1 Initialisation du moteur de recherche

from SearchEngine import SearchEngine

search_engine = SearchEngine(corpus)

# Exemple de recherche
requete = ["america", "president"]
requete_str = " ".join(requete)  # -> "america president"
resultats = search_engine.search(requete_str, top_k=5)

print("Résultats de la recherche :")
print(resultats)

from tqdm.notebook import tqdm
from collections import Counter
from scipy.sparse import csr_matrix
from math import log

# Construction des matrices TF/TF-IDF avec barre de progression
docs_texts = [search_engine.corpus.nettoyer_texte(doc.texte).split()
              for doc in search_engine.corpus.id2doc.values()]

all_words = [mot for words in docs_texts for mot in words]
mots_uniques = sorted(set(all_words))

search_engine.vocab = {mot: {"id": idx, "tf": 0, "df": 0} for idx, mot in enumerate(mots_uniques)}

nd, nw = len(docs_texts), len(mots_uniques)
data, row_ind, col_ind = [], [], []

# Boucle avec tqdm
for i, words in enumerate(tqdm(docs_texts, desc="Construction TF-IDF")):
    counts = Counter(words)
    for mot, c in counts.items():
        j = search_engine.vocab[mot]["id"]
        data.append(c)
        row_ind.append(i)
        col_ind.append(j)
        search_engine.vocab[mot]["tf"] += c
        search_engine.vocab[mot]["df"] += 1

# Matrice TF
search_engine.mat_tf = csr_matrix((data, (row_ind, col_ind)), shape=(nd, nw))

# Matrice TF-IDF
tfidf_data = []
for i, j, tf in zip(row_ind, col_ind, data):
    df_word = search_engine.vocab[mots_uniques[j]]["df"]
    idf = log(nd / (1 + df_word))
    tfidf_data.append(tf * idf)
search_engine.mat_tfidf = csr_matrix((tfidf_data, (row_ind, col_ind)), shape=(nd, nw))


#________________________________________________________




#TD9_10______________________________________


import pandas as pd
from IPython.display import display
import re
from Corpus import Corpus
from CompareCorpus import CompareCorpus

# -------------------------
# Stopwords FR + EN
# -------------------------
stopwords = set([
    "le","la","les","un","une","des","du","de","d'","et","à","au","aux","ce","ces","cet","cette","dans","en",
    "pour","par","sur","avec","sans","sous","chez","entre","mais","ou","où","donc","or","ni","car","ne","pas",
    "que","qui","quoi","dont","lorsque","comme","si","être","l","le","la","les","et","de","des","du","un","une",
    "the","a","an","and","or","but","if","then","for","on","in","at","with","without","by","of","to","from",
    "up","down","over","under","between","into","about","as","is","are","was","were","be","been","being","he",
    "she","it","they","them","his","her","its","their","i","you","we","me","him","us"
])

# -------------------------
# Charger corpus
# -------------------------
reddit = Corpus("Reddit")
reddit.load("data_corpus/reddit_fr.csv")
arxiv = Corpus("Arxiv")
arxiv.load("data_corpus/arxiv_fr.csv")
compare = CompareCorpus(reddit, arxiv)

df_reddit = pd.read_csv("data_corpus/reddit_fr.csv")
df_arxiv = pd.read_csv("data_corpus/arxiv_fr.csv")

# -------------------------
# Préparer vocabulaire et mots communs/spécifiques
# -------------------------
def get_vocab(df):
    all_text = ' '.join(df['texte'].astype(str)).lower()
    words = re.findall(r'\b\w+\b', all_text)
    vocab = {}
    for w in words:
        if w not in stopwords:
            vocab[w] = vocab.get(w,0)+1
    return vocab

vocab_r = get_vocab(df_reddit)
vocab_a = get_vocab(df_arxiv)

mots_communs = {w:vocab_r[w]+vocab_a[w] for w in vocab_r if w in vocab_a}
mots_spec = {
    "Reddit": {w:v for w,v in vocab_r.items() if w not in mots_communs},
    "Arxiv": {w:v for w,v in vocab_a.items() if w not in mots_communs}
}

# -------------------------
# Affichage corpus
# -------------------------
print()

print("VOICI LE CODE DU TD9")
print()

print("Corpus Reddit :")
display(df_reddit)
print(f"Documents Reddit : {len(df_reddit)} | Auteurs : {df_reddit['auteur'].nunique()}\n")

print()

print("Corpus Arxiv :")
display(df_arxiv)
print(f"Documents Arxiv : {len(df_arxiv)} | Auteurs : {df_arxiv['auteur'].nunique()}\n")

total_docs = len(df_reddit)+len(df_arxiv)
total_auteurs = df_reddit['auteur'].nunique()+df_arxiv['auteur'].nunique()
print(f"Corpus total : Documents = {total_docs} | Auteurs = {total_auteurs}\n")

# -------------------------
# Affichage mots spécifiques / communs
# -------------------------
print("Mots spécifiques Reddit")
for w,c in sorted(mots_spec["Reddit"].items()):
    print(f"{w} : {c}")

print("\nMots spécifiques Arxiv")
for w,c in sorted(mots_spec["Arxiv"].items()):
    print(f"{w} : {c}")

print("\nMots communs (Reddit + Arxiv)")
for w,c in sorted(mots_communs.items()):
    print(f"{w} : {c}")
