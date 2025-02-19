# AUTOGENERATED! DO NOT EDIT! File to edit: py mongo helper livres.ipynb.

# %% auto 0
__all__ = ["Livre"]

# %% py mongo helper livres.ipynb 2
from mongo import BaseEntity, Editeur
from mongo_auteur import Auteur


class Livre(BaseEntity):
    collection: str = "livres"

    def __init__(self, titre: str) -> None:
        """Initialise une instance de livre.

        Args:
            nom (str): Le titre du livre.
        """
        super().__init__(titre, self.collection)
        self.titre = titre  # je le duplique pour la comprehension du concept de livre
        self.auteur = None  # on mettra l'oid de l'auteur
        self.editeur = None  # on mettra l'oid de l'editeur

    def add_auteur(self, auteur: Auteur):
        self.auteur = auteur.get_oid()

    def add_editeur(self, editeur: Editeur):
        self.editeur = editeur.get_oid()

    def __str__(self) -> str:
        """Official string representation of the entity.

        Returns:
            str: The name of the entity: Titre, Auteur, Editeur.
        """
        return f"""
        Titre: {self.titre}
        Auteur: {Auteur.from_oid(self.auteur)}
        Editeur: {Editeur.from_oid(self.editeur)}
        """

    def __repr__(self) -> str:
        """Informal string representation of the entity.

        Returns:
            str: The name of the entity.
        """
        return self.nom
