# =======================
# main_v2_TD6_TD7.py
# =======================

import praw
import urllib.request
import xmltodict
from datetime import datetime
from DocumentFactory import DocumentFactory
from Corpus import Corpus
from SearchEngine import SearchEngine

# =========================== ACQUISITION ===========================
reddit = praw.Reddit(
    client_id="BYDoFFTvOpauop7YF9qB_w",
    client_secret="KvT1vhni559dKX07_CTs0TGrPy2s3w",
    user_agent="Test Praw script by u/VisibleEggplant3634"
)

query = "MachineLearning"
subreddit = reddit.subreddit(query)

corpus = Corpus("Corpus_ML")

# -------- Reddit --------
for post in subreddit.hot(limit=10):
    texte = post.selftext.strip() or post.title.strip()
    auteur = post.author.name if post.author else "Inconnu"

    doc = DocumentFactory.create_document(
        source="reddit",
        titre=post.title,
        auteur=auteur,
        date=datetime.fromtimestamp(post.created),
        url=post.url,
        texte=texte,
        nb_commentaires=post.num_comments
    )
    corpus.add_document(doc)

# -------- Arxiv --------
url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=10"

with urllib.request.urlopen(url) as response:
    data = response.read()

parsed = xmltodict.parse(data)
entries = parsed['feed']['entry']
if isinstance(entries, dict):
    entries = [entries]

for entry in entries:
    authors = entry['author']
    if isinstance(authors, list):
        auteur = authors[0]['name']
        co_auteurs = [a['name'] for a in authors[1:]]
    else:
        auteur = authors['name']
        co_auteurs = []

    doc = DocumentFactory.create_document(
        source="arxiv",
        titre=entry['title'],
        auteur=auteur,
        date=entry['published'],
        url=entry['id'],
        texte=entry['summary'].replace('\n', ' '),
        co_auteurs=co_auteurs
    )
    corpus.add_document(doc)

print(corpus)

# =========================== TD6 ===========================
print("\n=== Statistiques du corpus ===")
corpus.stats(n=10)

motif = input("Mot pour la concordance : ")
print(corpus.concorde(motif, contexte=30))

# =========================== TD7 ===========================
engine = SearchEngine(corpus)

requete = input("Entrez les mots-clés : ")
top_k = int(input("Nombre de documents à afficher : "))

resultats = engine.search(requete, top_k)
print("\n=== Résultats ===")
print(resultats)
