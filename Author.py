#author.py
class Author:
    """Classe représentant un auteur avec documents associés"""
    def __init__(self, name):
        self.name = name
        self.ndoc = 0
        self.production = {}

    def add(self, doc_id, document):
        self.production[doc_id] = document
        self.ndoc = len(self.production)

    def get_nombre_documents(self):
        return self.ndoc

    def get_taille_moyenne_documents(self):
        if self.ndoc == 0:
            return 0
        total_caracteres = sum(len(doc.texte) for doc in self.production.values())
        return total_caracteres / self.ndoc

    def __str__(self):
        return f"Auteur: {self.name}, {self.ndoc} document(s)"

    def __repr__(self):
        return f"Author({self.name}, {self.ndoc} documents)"



