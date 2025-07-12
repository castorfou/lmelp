#!/usr/bin/env python3
"""
Tests unitaires pour AvisCritiquesParser
"""
import unittest
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).resolve().parent))

from avis_critiques_parser import AvisCritiquesParser, BookData


class TestAvisCritiquesParser(unittest.TestCase):
    """Tests pour la classe AvisCritiquesParser"""

    def setUp(self):
        """Configuration avant chaque test"""
        self.parser = AvisCritiquesParser()

    def test_book_data_creation(self):
        """Test de création d'un BookData"""
        book = BookData(
            auteur="Mario Vargas Llosa",
            titre="Je vous dédie mon silence",
            editeur="Gallimard",
            note_moyenne=6.8,
            nb_critiques=4,
        )

        self.assertEqual(book.auteur, "Mario Vargas Llosa")
        self.assertEqual(book.titre, "Je vous dédie mon silence")
        self.assertEqual(book.editeur, "Gallimard")
        self.assertEqual(book.note_moyenne, 6.8)
        self.assertEqual(book.nb_critiques, 4)

    def test_book_data_cleaning(self):
        """Test du nettoyage des données BookData"""
        book = BookData(
            auteur="  | Mario Vargas Llosa |  ",
            titre="  Je vous dédie mon silence  ",
            editeur="  Gallimard  ",
        )

        self.assertEqual(book.auteur, "Mario Vargas Llosa")
        self.assertEqual(book.titre, "Je vous dédie mon silence")
        self.assertEqual(book.editeur, "Gallimard")

    def test_note_extraction(self):
        """Test d'extraction des notes moyennes"""
        # Test avec span HTML
        note_html = '<span style="background-color: #4CAF50;">8.8</span>'
        note = self.parser._extract_note_moyenne(note_html)
        self.assertEqual(note, 8.8)

        # Test avec note décimale
        note_html = "<span>6.5</span>"
        note = self.parser._extract_note_moyenne(note_html)
        self.assertEqual(note, 6.5)

        # Test avec note entière
        note_html = "<span>8</span>"
        note = self.parser._extract_note_moyenne(note_html)
        self.assertEqual(note, 8.0)

        # Test sans note
        note_html = "Pas de note"
        note = self.parser._extract_note_moyenne(note_html)
        self.assertIsNone(note)

    def test_nb_critiques_extraction(self):
        """Test d'extraction du nombre de critiques"""
        # Test normal
        nb = self.parser._extract_nb_critiques("4")
        self.assertEqual(nb, 4)

        # Test avec texte
        nb = self.parser._extract_nb_critiques("4 critiques")
        self.assertEqual(nb, 4)

        # Test sans nombre
        nb = self.parser._extract_nb_critiques("Aucun")
        self.assertIsNone(nb)

    def test_extract_books_simple(self):
        """Test d'extraction simple avec tableau basique"""
        summary = """
## 1. LIVRES DISCUTÉS
| Auteur | Titre | Éditeur | Avis détaillés des critiques | Note moyenne | Nb critiques | Coup de cœur | Chef d'œuvre |
|--------|-------|---------|------------------------------|--------------|--------------|-------------|-------------|
| Mario Vargas Llosa | Je vous dédie mon silence | Gallimard | Très bon livre | <span>6.8</span> | 4 | Arnaud Viviant | |
| Aslak Nord | Piège à loup | Le bruit du monde | Excellent | <span>8.8</span> | 4 | Patricia Martin | Patricia Martin |
"""

        books = self.parser.extract_books_from_summary(summary, "test")

        self.assertEqual(len(books), 2)

        # Premier livre
        self.assertEqual(books[0].auteur, "Mario Vargas Llosa")
        self.assertEqual(books[0].titre, "Je vous dédie mon silence")
        self.assertEqual(books[0].editeur, "Gallimard")
        self.assertEqual(books[0].note_moyenne, 6.8)
        self.assertEqual(books[0].nb_critiques, 4)
        self.assertEqual(books[0].coup_de_coeur, "Arnaud Viviant")

        # Deuxième livre
        self.assertEqual(books[1].auteur, "Aslak Nord")
        self.assertEqual(books[1].titre, "Piège à loup")
        self.assertEqual(books[1].chef_doeuvre, "Patricia Martin")

    def test_filter_generic_rows(self):
        """Test du filtrage des lignes génériques"""
        summary = """
| Auteur | Titre | Éditeur | Avis détaillés des critiques | Note moyenne | Nb critiques | Coup de cœur | Chef d'œuvre |
|--------|-------|---------|------------------------------|--------------|--------------|-------------|-------------|
| Auteur | Titre | Éditeur | Avis | Note | Nb | Coeur | Chef |
| Mario Vargas Llosa | Je vous dédie mon silence | Gallimard | Très bon | <span>6.8</span> | 4 | | |
"""

        books = self.parser.extract_books_from_summary(summary, "test")

        # Seul le livre valide doit être extrait
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].auteur, "Mario Vargas Llosa")

    def test_validation_stats(self):
        """Test des statistiques de validation"""
        books = [
            BookData(
                "Auteur1",
                "Titre1",
                "Editeur1",
                note_moyenne=8.0,
                coup_de_coeur="Critique1",
            ),
            BookData("Auteur2", "Titre2", "Editeur1", note_moyenne=6.5),
            BookData("Auteur1", "Titre3", "Editeur2", chef_doeuvre="Critique2"),
        ]

        stats = self.parser.validate_extraction(books)

        self.assertEqual(stats["total_books"], 3)
        self.assertEqual(stats["books_with_notes"], 2)
        self.assertEqual(stats["books_with_coup_coeur"], 1)
        self.assertEqual(stats["books_with_chef_doeuvre"], 1)
        self.assertEqual(stats["unique_authors"], 2)
        self.assertEqual(stats["unique_editors"], 2)
        self.assertEqual(len(stats["validation_errors"]), 0)

    def test_validation_errors(self):
        """Test de détection d'erreurs de validation"""
        books = [
            BookData("", "Titre1", "Editeur1"),  # Auteur vide
            BookData("Auteur2", "", "Editeur1"),  # Titre vide
            BookData(
                "Auteur3", "Titre3", "Editeur1", note_moyenne=-1.0
            ),  # Note invalide
            BookData(
                "Auteur4", "Titre4", "Editeur1", note_moyenne=15.0
            ),  # Note invalide
        ]

        stats = self.parser.validate_extraction(books)

        self.assertEqual(len(stats["validation_errors"]), 4)

    def test_empty_summary(self):
        """Test avec résumé vide ou sans tableau"""
        # Test résumé vide
        books = self.parser.extract_books_from_summary("", "test")
        self.assertEqual(len(books), 0)

        # Test résumé sans tableau
        summary = "Pas de tableau ici, juste du texte."
        books = self.parser.extract_books_from_summary(summary, "test")
        self.assertEqual(len(books), 0)

    def test_to_dict_conversion(self):
        """Test de conversion en dictionnaire"""
        book = BookData(
            auteur="Mario Vargas Llosa",
            titre="Je vous dédie mon silence",
            editeur="Gallimard",
            note_moyenne=6.8,
            nb_critiques=4,
            coup_de_coeur="Arnaud Viviant",
        )

        book_dict = book.to_dict()

        expected_keys = [
            "auteur",
            "titre",
            "editeur",
            "note_moyenne",
            "nb_critiques",
            "coup_de_coeur",
            "chef_doeuvre",
            "avis_details",
        ]

        for key in expected_keys:
            self.assertIn(key, book_dict)

        self.assertEqual(book_dict["auteur"], "Mario Vargas Llosa")
        self.assertEqual(book_dict["note_moyenne"], 6.8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
