#CompareCorpus.py
from SearchEngine import SearchEngine
from BM25 import BM25
import math

class CompareCorpus:
    def __init__(self, corpus1, corpus2):
        self.corpus1 = corpus1
        self.corpus2 = corpus2
        self.se1 = SearchEngine(corpus1)
        self.se2 = SearchEngine(corpus2)

    def analyser_mot(self, mot):
        """
        Retourne deux dictionnaires pour le mot donné : Reddit et Arxiv
        {"TF":..., "IDF":..., "BM25":...}
        """
        def analyse(se):
            if mot not in se.vocab:
                return {"TF": 0, "IDF": 0, "BM25": 0}
            
            tf_total = se.vocab[mot]["TF"]
            df = se.vocab[mot]["DF"]
            nb_docs = len(se.doc_ids)
            idf = math.log((nb_docs + 1) / (df + 1)) + 1.0

            corpus_texts = [list(se._nettoyer_texte(doc.texte).split()) for doc in se.corpus.id2doc.values()]
            bm25_model = BM25(corpus_texts)
            bm25_score = sum(bm25_model.score(mot, doc) for doc in corpus_texts)
            return {"TF": tf_total, "IDF": idf, "BM25": bm25_score}

        return analyse(self.se1), analyse(self.se2)


