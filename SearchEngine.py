#SearchEngine.py
import numpy as np
import pandas as pd
from collections import defaultdict
from BM25 import BM25
from sklearn.preprocessing import normalize
from scipy.sparse import csr_matrix

class SearchEngine:
    def __init__(self, corpus):
        """
        corpus : objet Corpus (avec corpus.id2doc)
        """
        self.corpus = corpus
        self.vocab = {}          # mot -> { "id": int, "TF": total, "DF": nb_docs }
        self.doc_ids = list(corpus.id2doc.keys())
        self.vocab_size = 0

        # Construction du vocabulaire et des matrices
        self._construire_vocab()
        self._construire_matrices()

        
    # ============================
    # Nettoyage du texte
    # ============================
    def _nettoyer_texte(self, texte: str) -> str:

        texte = str(texte).lower().replace("\n", " ")
        texte = "".join(c if c.isalpha() or c.isspace() else " " for c in texte)
        return texte

    # ============================
    # 1.1 Construction du vocabulaire
    # ============================
    def _construire_vocab(self):
        mots_set = set()
        for doc in self.corpus.id2doc.values():
            texte = self._nettoyer_texte(doc.texte)
            mots_set.update(texte.split())
        mots_list = sorted(list(mots_set))
        self.vocab = {mot: {"id": i, "TF": 0, "DF": 0} for i, mot in enumerate(mots_list)}
        self.vocab_size = len(self.vocab)

    # ============================
    # 1.2, 1.3, 1.4 Matrices TF et TF-IDF
    # ============================
    def _construire_matrices(self):
        rows, cols, data = [], [], []

        for r, doc_id in enumerate(self.doc_ids):
            doc = self.corpus.id2doc[doc_id]
            texte = self._nettoyer_texte(doc.texte)
            mots = texte.split()
            compte_doc = defaultdict(int)
            for mot in mots:
                if mot in self.vocab:
                    compte_doc[mot] += 1
            for mot, count in compte_doc.items():
                c = self.vocab[mot]["id"]
                rows.append(r)
                cols.append(c)
                data.append(count)
                self.vocab[mot]["TF"] += count
                self.vocab[mot]["DF"] += 1

        nb_docs = len(self.doc_ids)
        self.mat_TF = csr_matrix((data, (rows, cols)), shape=(nb_docs, self.vocab_size), dtype=float)

        # Calcul IDF
        idf = np.zeros(self.vocab_size)
        for mot, info in self.vocab.items():
            j = info["id"]
            df = info["DF"]
            idf[j] = np.log((nb_docs + 1) / (df + 1)) + 1.0

        self.mat_TF_IDF = self.mat_TF.multiply(idf)

    # ============================
    # Vectorisation de la requête
    # ============================
    def _vectoriser_requete(self, requete: str) -> np.ndarray:
        vect = np.zeros(self.vocab_size)
        mots = self._nettoyer_texte(requete).split()
        for mot in mots:
            if mot in self.vocab:
                j = self.vocab[mot]["id"]
                vect[j] += 1
        return vect

    # ============================
    # Recherche
    # ============================
    def search(self, requete: str, top_k: int = 5) -> pd.DataFrame:
        if not requete.strip():
            return pd.DataFrame()

        q = self._vectoriser_requete(requete)
        if np.all(q == 0):
            return pd.DataFrame()

        mat_norm = normalize(self.mat_TF_IDF)
        q_norm = q / (np.linalg.norm(q) + 1e-9)
        scores = mat_norm.dot(q_norm)

        indices_top = np.argsort(-scores)[:top_k]

        resultats = []
        for idx in indices_top:
            score = float(scores[idx])
            if score <= 0:
                continue
            doc_id = self.doc_ids[idx]
            doc = self.corpus.id2doc[doc_id]
            resultats.append({
                "id": doc_id,
                "Titre": doc.titre,
                "Auteur": doc.auteur,
                "Date": doc.date if doc.date else "Inconnue",
                "Score": score,
                "URL": doc.url,
            })

        return pd.DataFrame(resultats)
