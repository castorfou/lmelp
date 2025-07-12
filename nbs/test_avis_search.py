#!/usr/bin/env python3
"""
Tests unitaires pour AvisSearchEngine
"""
import unittest
import sys
from pathlib import Path
from bson import ObjectId
from unittest.mock import patch, MagicMock

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).resolve().parent))

from avis_search import AvisSearchEngine, AutocompleteResult, EpisodeAvis


class TestAvisSearchEngine(unittest.TestCase):
    """Tests pour la classe AvisSearchEngine"""

    def setUp(self):
        """Configuration avant chaque test"""
        self.engine = AvisSearchEngine(min_chars=3, fuzzy_threshold=70)

    def test_search_engine_creation(self):
        """Test de création du moteur de recherche"""
        self.assertEqual(self.engine.min_chars, 3)
        self.assertEqual(self.engine.fuzzy_threshold, 70)

    def test_format_suggestion(self):
        """Test de formatage des suggestions"""
        suggestion = self.engine.format_suggestion(
            "Mario Vargas Llosa", "Je vous dédie mon silence"
        )
        expected = "Mario Vargas Llosa - Je vous dédie mon silence"
        self.assertEqual(suggestion, expected)

        # Test avec espaces
        suggestion2 = self.engine.format_suggestion(
            "  J.R.R. Tolkien  ", "  Le Seigneur des Anneaux  "
        )
        expected2 = "  J.R.R. Tolkien   -   Le Seigneur des Anneaux  "
        self.assertEqual(suggestion2, expected2)

    def test_parse_selected_suggestion(self):
        """Test de parsing des suggestions sélectionnées"""
        # Test normal
        suggestion = "Mario Vargas Llosa - Je vous dédie mon silence"
        parsed = self.engine.parse_selected_suggestion(suggestion)
        expected = ("Mario Vargas Llosa", "Je vous dédie mon silence")
        self.assertEqual(parsed, expected)

        # Test avec plusieurs tirets
        suggestion2 = "Jean-Baptiste Del Amo - La Nuit - Version longue"
        parsed2 = self.engine.parse_selected_suggestion(suggestion2)
        expected2 = ("Jean-Baptiste Del Amo", "La Nuit - Version longue")
        self.assertEqual(parsed2, expected2)

        # Test avec suggestion invalide
        suggestion3 = "Pas de tiret ici"
        parsed3 = self.engine.parse_selected_suggestion(suggestion3)
        self.assertIsNone(parsed3)

        # Test avec suggestion vide
        parsed4 = self.engine.parse_selected_suggestion("")
        self.assertIsNone(parsed4)

    def test_autocomplete_result_creation(self):
        """Test de création d'AutocompleteResult"""
        result = AutocompleteResult(
            display_text="Mario Vargas Llosa - Je vous dédie mon silence",
            auteur_nom="Mario Vargas Llosa",
            livre_titre="Je vous dédie mon silence",
            livre_oid=ObjectId(),
            nb_episodes=3,
            note_moyenne_globale=7.5,
            score_fuzzy=85,
        )

        self.assertEqual(result.auteur_nom, "Mario Vargas Llosa")
        self.assertEqual(result.livre_titre, "Je vous dédie mon silence")
        self.assertEqual(result.nb_episodes, 3)
        self.assertEqual(result.note_moyenne_globale, 7.5)
        self.assertEqual(result.score_fuzzy, 85)
        self.assertIsInstance(result.livre_oid, ObjectId)

    def test_episode_avis_creation(self):
        """Test de création d'EpisodeAvis"""
        episode_oid = ObjectId()
        episode = EpisodeAvis(
            episode_oid=episode_oid,
            episode_title="Episode test",
            episode_date="01 janvier 2025",
            note_moyenne=8.5,
            nb_critiques=4,
            coup_de_coeur="Patricia Martin",
        )

        self.assertEqual(episode.episode_oid, episode_oid)
        self.assertEqual(episode.episode_title, "Episode test")
        self.assertEqual(episode.note_moyenne, 8.5)
        self.assertEqual(episode.nb_critiques, 4)
        self.assertEqual(episode.coup_de_coeur, "Patricia Martin")

    def test_search_combined_min_chars(self):
        """Test que la recherche respecte le minimum de caractères"""
        # Recherche trop courte
        results = self.engine.search_combined("ab")
        self.assertEqual(len(results), 0)

        # Recherche vide
        results2 = self.engine.search_combined("")
        self.assertEqual(len(results2), 0)

    @patch("avis_search.EpisodeLivre.search_books_by_text")
    def test_perform_direct_search(self, mock_search):
        """Test de la recherche directe avec mock"""
        # Mock des données retournées par MongoDB
        mock_data = [
            {
                "auteur_nom": "Mario Vargas Llosa",
                "livre_titre": "Je vous dédie mon silence",
                "livre_oid": ObjectId(),
                "auteur_oid": ObjectId(),
                "nb_episodes": 2,
                "note_moyenne_globale": 6.8,
                "dernier_episode": "2025-07-01",
            },
            {
                "auteur_nom": "Aslak Nord",
                "livre_titre": "Piège à loup",
                "livre_oid": ObjectId(),
                "auteur_oid": ObjectId(),
                "nb_episodes": 1,
                "note_moyenne_globale": 8.8,
                "dernier_episode": "2025-06-29",
            },
        ]
        mock_search.return_value = mock_data

        # Test de la recherche directe
        results = AvisSearchEngine._perform_direct_search("vargas", 5)

        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[0], AutocompleteResult)
        self.assertEqual(results[0].auteur_nom, "Mario Vargas Llosa")
        self.assertEqual(results[0].livre_titre, "Je vous dédie mon silence")
        self.assertEqual(
            results[0].display_text, "Mario Vargas Llosa - Je vous dédie mon silence"
        )
        self.assertEqual(
            results[0].score_fuzzy, 100
        )  # Score parfait pour recherche directe

        # Vérifier que la méthode MongoDB a été appelée
        mock_search.assert_called_once_with("vargas", 5)

    def test_fuzzy_search_simple(self):
        """Test de la méthode fuzzy_search simple"""
        # Mock des données pour éviter la base de données
        with patch.object(self.engine, "search_combined") as mock_search:
            mock_results = [
                AutocompleteResult(
                    display_text="Mario Vargas Llosa - Je vous dédie mon silence",
                    auteur_nom="Mario Vargas Llosa",
                    livre_titre="Je vous dédie mon silence",
                    score_fuzzy=85,
                ),
                AutocompleteResult(
                    display_text="Aslak Nord - Piège à loup",
                    auteur_nom="Aslak Nord",
                    livre_titre="Piège à loup",
                    score_fuzzy=75,
                ),
            ]
            mock_search.return_value = mock_results

            # Test fuzzy_search
            results = self.engine.fuzzy_search("vargas", 3)

            self.assertEqual(len(results), 2)
            self.assertEqual(
                results[0], ("Mario Vargas Llosa", "Je vous dédie mon silence")
            )
            self.assertEqual(results[1], ("Aslak Nord", "Piège à loup"))

            mock_search.assert_called_once_with("vargas", 3)

    @patch("avis_search.get_collection")
    def test_get_all_books(self, mock_get_collection):
        """Test de récupération de tous les livres avec mock MongoDB"""
        # Mock de la collection MongoDB
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection

        # Mock des résultats d'agrégation
        mock_aggregation_results = [
            {
                "auteur_nom": "Mario Vargas Llosa",
                "livre_titre": "Je vous dédie mon silence",
                "livre_oid": ObjectId(),
                "auteur_oid": ObjectId(),
                "nb_episodes": 2,
                "note_moyenne_globale": 6.8,
            }
        ]
        mock_collection.aggregate.return_value = mock_aggregation_results

        # Test de la méthode
        results = AvisSearchEngine._get_all_books()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["auteur_nom"], "Mario Vargas Llosa")
        self.assertEqual(results[0]["livre_titre"], "Je vous dédie mon silence")

        # Vérifier que aggregate a été appelé
        mock_collection.aggregate.assert_called_once()

    def test_get_book_episodes_insufficient_params(self):
        """Test get_book_episodes avec paramètres insuffisants"""
        results = self.engine.get_book_episodes()
        self.assertEqual(len(results), 0)

    @patch("avis_search.EpisodeLivre.find_by_livre")
    def test_get_book_episodes_by_oid(self, mock_find_by_livre):
        """Test get_book_episodes avec ObjectId"""
        # Mock EpisodeLivre
        mock_episode_livre = MagicMock()
        mock_episode_livre.episode_oid = ObjectId()
        mock_episode_livre.episode_title = "Test Episode"
        mock_episode_livre.episode_date = "01 jan 2025"
        mock_episode_livre.note_moyenne = 8.0
        mock_episode_livre.nb_critiques = 3
        mock_episode_livre.coup_de_coeur = "Patricia Martin"
        mock_episode_livre.chef_doeuvre = None
        mock_episode_livre.avis_details = "Excellent livre"

        mock_find_by_livre.return_value = [mock_episode_livre]

        # Test
        livre_oid = ObjectId()
        results = self.engine.get_book_episodes(livre_oid=livre_oid)

        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], EpisodeAvis)
        self.assertEqual(results[0].episode_title, "Test Episode")
        self.assertEqual(results[0].note_moyenne, 8.0)
        self.assertEqual(results[0].coup_de_coeur, "Patricia Martin")

        mock_find_by_livre.assert_called_once_with(livre_oid, True)

    def test_search_combined_empty_query(self):
        """Test avec query vide après min_chars"""
        # Initialiser avec min_chars=0 pour ce test
        engine = AvisSearchEngine(min_chars=0)
        results = engine.search_combined("")
        self.assertEqual(len(results), 0)

    def test_engine_methods_exist(self):
        """Test que toutes les méthodes publiques existent"""
        # Vérifier les méthodes principales
        self.assertTrue(hasattr(self.engine, "search_combined"))
        self.assertTrue(hasattr(self.engine, "get_book_episodes"))
        self.assertTrue(hasattr(self.engine, "fuzzy_search"))
        self.assertTrue(hasattr(self.engine, "format_suggestion"))
        self.assertTrue(hasattr(self.engine, "parse_selected_suggestion"))

        # Vérifier qu'elles sont callables
        self.assertTrue(callable(self.engine.search_combined))
        self.assertTrue(callable(self.engine.get_book_episodes))
        self.assertTrue(callable(self.engine.fuzzy_search))


class TestAvisSearchEngineIntegration(unittest.TestCase):
    """Tests d'intégration (nécessitent potentiellement MongoDB)"""

    def test_search_engine_initialization(self):
        """Test d'initialisation avec différents paramètres"""
        # Paramètres par défaut
        engine1 = AvisSearchEngine()
        self.assertEqual(engine1.min_chars, 3)
        self.assertEqual(engine1.fuzzy_threshold, 70)

        # Paramètres personnalisés
        engine2 = AvisSearchEngine(min_chars=2, fuzzy_threshold=80)
        self.assertEqual(engine2.min_chars, 2)
        self.assertEqual(engine2.fuzzy_threshold, 80)

    def test_error_handling(self):
        """Test de gestion d'erreurs"""
        engine = AvisSearchEngine()

        # Test avec None
        parsed = engine.parse_selected_suggestion(None)
        self.assertIsNone(parsed)

        # Test format avec chaînes vides
        suggestion = engine.format_suggestion("", "")
        self.assertEqual(suggestion, " - ")


if __name__ == "__main__":
    unittest.main(verbosity=2)
