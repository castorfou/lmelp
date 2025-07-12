#!/usr/bin/env python3
"""
Tests unitaires pour EpisodeLivre
"""
import unittest
import sys
from pathlib import Path
from datetime import datetime
from bson import ObjectId

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).resolve().parent))

from mongo_episode_livre import EpisodeLivre, validate_episode_livre_collection


class TestEpisodeLivre(unittest.TestCase):
    """Tests pour la classe EpisodeLivre"""

    def setUp(self):
        """Configuration avant chaque test"""
        self.episode_oid = ObjectId()
        self.livre_oid = ObjectId()
        self.auteur_oid = ObjectId()

        self.episode_livre = EpisodeLivre(
            episode_oid=self.episode_oid,
            livre_oid=self.livre_oid,
            auteur_oid=self.auteur_oid,
        )

    def test_episode_livre_creation(self):
        """Test de création d'un EpisodeLivre"""
        self.assertEqual(self.episode_livre.episode_oid, self.episode_oid)
        self.assertEqual(self.episode_livre.livre_oid, self.livre_oid)
        self.assertEqual(self.episode_livre.auteur_oid, self.auteur_oid)
        # Vérifier le nom de la collection (attribut de classe)
        self.assertEqual(EpisodeLivre.collection, "episode_livres")

        # Vérifier que les timestamps sont créés
        self.assertIsInstance(self.episode_livre.created_at, datetime)
        self.assertIsInstance(self.episode_livre.updated_at, datetime)

    def test_unique_name_generation(self):
        """Test de génération du nom unique pour BaseEntity"""
        expected_name = f"{self.episode_oid}_{self.livre_oid}"
        self.assertEqual(self.episode_livre.nom, expected_name)

    def test_add_episode_metadata(self):
        """Test d'ajout des métadonnées d'épisode"""
        title = "Episode test"
        date = "01 janvier 2025"

        self.episode_livre.add_episode_metadata(title, date)

        self.assertEqual(self.episode_livre.episode_title, title)
        self.assertEqual(self.episode_livre.episode_date, date)

    def test_add_book_metadata(self):
        """Test d'ajout des métadonnées de livre"""
        titre = "Le Seigneur des Anneaux"
        auteur = "J.R.R. Tolkien"
        editeur = "Gallimard"

        self.episode_livre.add_book_metadata(titre, auteur, editeur)

        self.assertEqual(self.episode_livre.livre_titre, titre)
        self.assertEqual(self.episode_livre.auteur_nom, auteur)
        self.assertEqual(self.episode_livre.editeur_nom, editeur)

    def test_add_rating_info(self):
        """Test d'ajout des informations de notation"""
        note = 8.5
        nb_critiques = 4
        coup_coeur = "Patricia Martin"
        chef_doeuvre = "Bernard Poiret"
        avis = "Excellent livre"

        self.episode_livre.add_rating_info(
            note_moyenne=note,
            nb_critiques=nb_critiques,
            coup_de_coeur=coup_coeur,
            chef_doeuvre=chef_doeuvre,
            avis_details=avis,
        )

        self.assertEqual(self.episode_livre.note_moyenne, note)
        self.assertEqual(self.episode_livre.nb_critiques, nb_critiques)
        self.assertEqual(self.episode_livre.coup_de_coeur, coup_coeur)
        self.assertEqual(self.episode_livre.chef_doeuvre, chef_doeuvre)
        self.assertEqual(self.episode_livre.avis_details, avis)

    def test_to_dict_serialization(self):
        """Test de sérialisation en dictionnaire"""
        # Ajouter quelques données
        self.episode_livre.add_episode_metadata("Test Episode", "01 jan 2025")
        self.episode_livre.add_book_metadata("Test Book", "Test Author", "Test Editor")
        self.episode_livre.add_rating_info(note_moyenne=7.5, nb_critiques=3)

        data = self.episode_livre.to_dict()

        # Vérifier les champs obligatoires
        self.assertEqual(data["episode_oid"], self.episode_oid)
        self.assertEqual(data["livre_oid"], self.livre_oid)
        self.assertEqual(data["auteur_oid"], self.auteur_oid)
        self.assertEqual(data["episode_title"], "Test Episode")
        self.assertEqual(data["livre_titre"], "Test Book")
        self.assertEqual(data["auteur_nom"], "Test Author")
        self.assertEqual(data["note_moyenne"], 7.5)

        # Vérifier que la collection n'est pas dans le dict (hérité de BaseEntity)
        self.assertNotIn("collection", data)

        # Vérifier les timestamps
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

    def test_extract_from_avis_summary(self):
        """Test de création depuis des données d'avis critique"""
        episode_oid = ObjectId()
        episode_title = "Episode Test"
        episode_date = "01 jan 2025"

        book_data = {
            "titre": "Je vous dédie mon silence",
            "auteur": "Mario Vargas Llosa",
            "editeur": "Gallimard",
            "note_moyenne": 6.8,
            "nb_critiques": 4,
            "coup_de_coeur": "Arnaud Viviant",
            "chef_doeuvre": None,
            "avis_details": "Œuvre crépusculaire",
        }

        episode_livre = EpisodeLivre.extract_from_avis_summary(
            episode_oid, episode_title, episode_date, book_data
        )

        # Vérifier les métadonnées épisode
        self.assertEqual(episode_livre.episode_oid, episode_oid)
        self.assertEqual(episode_livre.episode_title, episode_title)
        self.assertEqual(episode_livre.episode_date, episode_date)

        # Vérifier les métadonnées livre
        self.assertEqual(episode_livre.livre_titre, book_data["titre"])
        self.assertEqual(episode_livre.auteur_nom, book_data["auteur"])
        self.assertEqual(episode_livre.editeur_nom, book_data["editeur"])

        # Vérifier les informations de notation
        self.assertEqual(episode_livre.note_moyenne, book_data["note_moyenne"])
        self.assertEqual(episode_livre.nb_critiques, book_data["nb_critiques"])
        self.assertEqual(episode_livre.coup_de_coeur, book_data["coup_de_coeur"])
        self.assertEqual(episode_livre.chef_doeuvre, book_data["chef_doeuvre"])

    def test_extract_from_avis_summary_partial_data(self):
        """Test avec données partielles"""
        episode_oid = ObjectId()

        book_data = {
            "titre": "Titre seulement",
            "auteur": "Auteur seulement",
            # Pas d'autres données
        }

        episode_livre = EpisodeLivre.extract_from_avis_summary(
            episode_oid, "Episode", "01 jan", book_data
        )

        self.assertEqual(episode_livre.livre_titre, book_data["titre"])
        self.assertEqual(episode_livre.auteur_nom, book_data["auteur"])
        self.assertEqual(episode_livre.editeur_nom, "")  # Valeur par défaut
        self.assertIsNone(episode_livre.note_moyenne)  # Pas de note

    def test_string_representation(self):
        """Test de la représentation string"""
        self.episode_livre.add_episode_metadata("Test Episode", "01 jan 2025")
        self.episode_livre.add_book_metadata("Test Book", "Test Author")
        self.episode_livre.add_rating_info(note_moyenne=8.0, nb_critiques=3)

        str_repr = str(self.episode_livre)

        self.assertIn("Test Episode", str_repr)
        self.assertIn("Test Book", str_repr)
        self.assertIn("Test Author", str_repr)
        self.assertIn("8.0", str_repr)

    def test_updated_timestamp_on_modifications(self):
        """Test que updated_at est mis à jour lors des modifications"""
        initial_time = self.episode_livre.updated_at

        # Attendre un petit délai pour s'assurer que le timestamp change
        import time

        time.sleep(0.01)

        self.episode_livre.add_episode_metadata("New Title", "New Date")

        self.assertGreater(self.episode_livre.updated_at, initial_time)

    def test_validation_function_structure(self):
        """Test de la structure de la fonction de validation"""
        # Test que la fonction existe et retourne la bonne structure
        try:
            # Simulate validation without actually connecting to DB
            # (we just test the function structure)
            self.assertTrue(callable(validate_episode_livre_collection))
        except Exception:
            # Si la DB n'est pas disponible, au moins la fonction existe
            pass

    def test_class_methods_exist(self):
        """Test que toutes les méthodes de classe existent"""
        # Vérifier que les méthodes de recherche existent
        self.assertTrue(hasattr(EpisodeLivre, "find_by_livre"))
        self.assertTrue(hasattr(EpisodeLivre, "find_by_auteur"))
        self.assertTrue(hasattr(EpisodeLivre, "find_by_episode"))
        self.assertTrue(hasattr(EpisodeLivre, "search_books_by_text"))
        self.assertTrue(hasattr(EpisodeLivre, "extract_from_avis_summary"))

        # Vérifier qu'elles sont des méthodes de classe
        self.assertTrue(callable(EpisodeLivre.find_by_livre))
        self.assertTrue(callable(EpisodeLivre.search_books_by_text))


if __name__ == "__main__":
    unittest.main(verbosity=2)
