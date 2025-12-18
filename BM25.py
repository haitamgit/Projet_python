# BM25.py
import math
from collections import Counter

class BM25:
    def __init__(self, corpus, k1=1.5, b=0.75):
        
        self.corpus = corpus
        self.k1 = k1
        self.b = b
        self.N = len(corpus)
        self.avgdl = sum(len(doc) for doc in corpus) / self.N
        self.df = Counter()
        for doc in corpus:
            for w in set(doc):
                self.df[w] += 1

    def score(self, word, doc):
        if word not in doc:
            return 0
        df = self.df.get(word, 0)
        idf = math.log((self.N - df + 0.5) / (df + 0.5) + 1)
        tf = doc.count(word)
        dl = len(doc)
        return idf * ((tf * (self.k1 + 1)) / 
                      (tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl)))

