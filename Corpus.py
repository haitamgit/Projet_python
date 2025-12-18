#Corpus.py
import pandas as pd
import re
from collections import Counter
import numpy as np
from scipy.sparse import csr_matrix
from math import log, sqrt
from Author import Author
from Document import RedditDocument, ArxivDocument, Document

# ===========================
# CORPUS
# ===========================
class Corpus:
    def __init__(self, nom="Corpus"):
        self.nom = nom
        self.id2doc = {}
        self.authors = {}
        self.ndoc = 0
        self.naut = 0
        self._next_id = 1
        self._full_text = None

    # ===========================
    # AJOUT D’UN DOCUMENT
    # ===========================
    def add_document(self, doc):
        if not isinstance(doc, Document):
            raise TypeError("Seuls les objets Document ou dérivés peuvent être ajoutés.")
        doc_id = self._next_id
        self.id2doc[doc_id] = doc
        self.ndoc += 1
        self._next_id += 1

        # Auteur principal
        if doc.auteur not in self.authors:
            self.authors[doc.auteur] = Author(doc.auteur)
            self.naut += 1
        self.authors[doc.auteur].add(doc_id, doc)

        # Co-auteurs Arxiv
        if isinstance(doc, ArxivDocument):
            for co in getattr(doc, "co_auteurs", []):
                if co not in self.authors:
                    self.authors[co] = Author(co)
                    self.naut += 1
                self.authors[co].add(doc_id, doc)

    # ===========================
    # AFFICHAGE
    # ===========================
    def afficher_documents(self, n=None):
        docs = list(self.id2doc.values())
        if n is None:
            n = len(docs)
        for doc in docs[:n]:
            print(doc)
            print("")

    def stats_auteur(self, name):
        if name in self.authors:
            aut = self.authors[name]
            print(f"{aut.name} : {aut.get_nombre_documents()} document(s), taille moyenne = {aut.get_taille_moyenne_documents():.1f} caractères")
        else:
            print(f"Auteur '{name}' non trouvé.")

    # ===========================
    # SAUVEGARDE / CHARGEMENT
    # ===========================
    def save(self, filename):
        rows = []
        for doc_id, doc in self.id2doc.items():
            rows.append({
                "id": doc_id,
                "titre": doc.titre,
                "auteur": doc.auteur,
                "co_auteurs": ','.join(getattr(doc, "co_auteurs", [])) if isinstance(doc, ArxivDocument) else "",
                "date":( doc.date.isoformat()
                  if hasattr(doc.date, "isoformat")
                  else str(doc.date) if doc.date is not None
                  else ""
                  ),
                "url": getattr(doc, "url", ""),
                "texte": getattr(doc, "texte", ""),
                "type": doc.type
            })
        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False)

    def load(self, filename):
        df = pd.read_csv(filename)
        for _, row in df.iterrows():
            co_auteurs = row['co_auteurs'].split(',') if 'co_auteurs' in row and pd.notna(row['co_auteurs']) else []
            if row['type'] == "Reddit":
                doc = RedditDocument(row['titre'], row['auteur'], row['date'], row['url'], row['texte'])
            elif row['type'] == "Arxiv":
                doc = ArxivDocument(row['titre'], row['auteur'], row['date'], row['url'], row['texte'], co_auteurs)
            else:
                doc = Document(row['titre'], row['auteur'], row['date'], row['url'], row['texte'])
            self.add_document(doc)

    # ===========================
    # NETTOYAGE DE TEXTE
    # ===========================
    @staticmethod
    def nettoyer_texte(texte):
        if texte is None or pd.isna(texte):
            return ""
        texte = str(texte).lower()
        texte = re.sub(r"\n", " ", texte)
        texte = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ\s]", " ", texte)
        texte = re.sub(r"\s+", " ", texte)
        return texte.strip()

    def _build_full_text(self):
        if self._full_text is None:
            self._full_text = " ".join([self.nettoyer_texte(doc.texte) for doc in self.id2doc.values()])

    # ===========================
    # RECHERCHE / CONCORDE
    # ===========================
    def search(self, motif):
        self._build_full_text()
        resultats = re.findall(rf".{{0,30}}{motif}.{{0,30}}", self._full_text, re.IGNORECASE)
        return resultats

    def concorde(self, motif, contexte=30):
        self._build_full_text()
        pattern = re.compile(rf"(.{{0,{contexte}}})({motif})(.{{0,{contexte}}})", re.IGNORECASE)
        matches = pattern.findall(self._full_text)
        df = pd.DataFrame(matches, columns=["contexte_gauche", "motif_trouve", "contexte_droit"])
        return df

    # ===========================
    # STATISTIQUES CORPUS
    # ===========================
    def stats(self, n=10):
        self._build_full_text()
        mots = self._full_text.split()
        vocab = set(mots)
        print(f"Nombre de mots différents : {len(vocab)}")
        
        counter = Counter(mots)
        df_counts = {mot: sum(1 for doc in self.id2doc.values() if mot in self.nettoyer_texte(doc.texte).split()) for mot in vocab}
        freq = pd.DataFrame(counter.items(), columns=["mot", "term_frequency"])
        freq["document_frequency"] = freq["mot"].map(df_counts)
        freq = freq.sort_values(by="term_frequency", ascending=False).reset_index(drop=True)
        print(f"\nTop {n} mots les plus fréquents :")
        print(freq.head(n))
        return freq

    def __repr__(self):
        return f"Corpus '{self.nom}' : {self.ndoc} documents, {self.naut} auteurs"


