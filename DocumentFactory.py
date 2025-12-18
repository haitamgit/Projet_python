#Documentfactory.py

from Document import Document, RedditDocument, ArxivDocument

class DocumentFactory:
    @staticmethod
    def create_document(source, titre, auteur, date, url, texte, **kwargs):
        if source.lower() == "reddit":
            nb_comments = kwargs.get("nb_commentaires", 0)
            return RedditDocument(titre, auteur, date, url, texte, nb_comments)
        elif source.lower() == "arxiv":
            co_auteurs = kwargs.get("co_auteurs", [])
            return ArxivDocument(titre, auteur, date, url, texte, co_auteurs)
        else:
            return Document(titre, auteur, date, url, texte)