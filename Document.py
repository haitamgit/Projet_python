#Document.py
from datetime import datetime

class Document:
    def __init__(self, titre, auteur, date, url, texte):
        self.titre = titre
        self.auteur = auteur
        self.date = self._convertir_date(date)
        self.url = url
        self.texte = texte
        self.type = "Document"

    def _convertir_date(self, date):
        if date is None or date == "":
            return "Inconnue"
        try:
            return str(date)
        except Exception:
            return "Inconnue"

    def getType(self):
        return self.type

    def __str__(self):
        return f"[{self.type}] {self.titre} par {self.auteur} | Date : {self.date}"

class RedditDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, nb_commentaires=0):
        super().__init__(titre, auteur, date, url, texte)
        self._nb_commentaires = nb_commentaires
        self.type = "Reddit"

    @property
    def nb_commentaires(self):
        return self._nb_commentaires

    @nb_commentaires.setter
    def nb_commentaires(self, value):
        self._nb_commentaires = value

    def __str__(self):
        return f"[Reddit] Titre : {self.titre} | Auteur : {self.auteur} | Date : {self.date} | {self.nb_commentaires} commentaires"

class ArxivDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, co_auteurs=None):
        super().__init__(titre, auteur, date, url, texte)
        self._co_auteurs = co_auteurs if co_auteurs else []
        self.type = "Arxiv"

    @property
    def co_auteurs(self):
        return self._co_auteurs

    @co_auteurs.setter
    def co_auteurs(self, value):
        self._co_auteurs = value

    def __str__(self):
        coaut = ", ".join(self.co_auteurs) if self.co_auteurs else "Aucun co-auteur"
        return f"[Arxiv] Titre : {self.titre} | Auteur : {self.auteur} | Date : {self.date} | Co-Auteur : {coaut}"
