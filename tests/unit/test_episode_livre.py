#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import datetime

# Ajouter le chemin vers nbs
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'nbs'))

# Mock des modules problématiques AVANT l'import
sys.modules['mongo_auteur'] = MagicMock()
sys.modules['mongo_livre'] = MagicMock()

from bson import ObjectId

# Mock des variables d'environnement pour éviter l'erreur Google API
os.environ['GOOGLE_CUSTOM_SEARCH_API_KEY'] = 'fake_key'
os.environ['SEARCH_ENGINE_ID'] = 'fake_id'


class TestEpisodeLivre(unittest.TestCase):
    """Tests unitaires complets pour EpisodeLivre."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.episode_oid = ObjectId()
        self.livre_oid = ObjectId()
        self.auteur_oid = ObjectId()
    
    @patch('mongo_episode_livre.get_DB_VARS')
    @patch('mongo_episode_livre.get_collection')
    def test_episode_livre_creation_with_patches(self, mock_get_collection, mock_get_db_vars):
        """Test de création d'EpisodeLivre avec patches locaux."""
        # Configuration des mocks
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        # Mock BaseEntity localement
        with patch('mongo_episode_livre.BaseEntity') as mock_base_entity:
            # Configurer le mock BaseEntity
            mock_base_entity.return_value = MagicMock()
            mock_base_entity.return_value.nom = "test_nom"
            
            # Import local avec patches
            from mongo_episode_livre import EpisodeLivre
            
            # Test de création
            episode_livre = EpisodeLivre(self.episode_oid, self.livre_oid, self.auteur_oid)
            
            # Vérifications de base
            self.assertEqual(episode_livre.episode_oid, self.episode_oid)
            self.assertEqual(episode_livre.livre_oid, self.livre_oid)
            self.assertEqual(episode_livre.auteur_oid, self.auteur_oid)
    
    @patch('mongo_episode_livre.get_DB_VARS')
    @patch('mongo_episode_livre.get_collection')
    def test_episode_livre_metadata_methods(self, mock_get_collection, mock_get_db_vars):
        """Test des méthodes d'ajout de métadonnées."""
        # Configuration des mocks
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        with patch('mongo_episode_livre.BaseEntity') as mock_base_entity:
            mock_base_entity.return_value = MagicMock()
            
            from mongo_episode_livre import EpisodeLivre
            
            episode_livre = EpisodeLivre(self.episode_oid, self.livre_oid, self.auteur_oid)
            
            # Test add_episode_metadata
            episode_date = datetime(2024, 12, 15)
            episode_title = "Episode Test"
            episode_livre.add_episode_metadata(episode_date, episode_title)
            
            self.assertEqual(episode_livre.episode_date, episode_date)
            self.assertEqual(episode_livre.episode_title, episode_title)
            
            # Test add_livre_metadata
            episode_livre.add_livre_metadata("Test Livre", "Test Auteur", "Test Editeur")
            
            self.assertEqual(episode_livre.livre_titre, "Test Livre")
            self.assertEqual(episode_livre.auteur_nom, "Test Auteur")
            self.assertEqual(episode_livre.editeur_nom, "Test Editeur")
            
            # Test add_avis_metadata
            episode_livre.add_avis_metadata(
                note_moyenne=8.5,
                nb_critiques=3,
                section="programme",
                commentaire="Excellent livre"
            )
            
            self.assertEqual(episode_livre.note_moyenne, 8.5)
            self.assertEqual(episode_livre.nb_critiques, 3)
            self.assertEqual(episode_livre.section, "programme")
            self.assertEqual(episode_livre.commentaire, "Excellent livre")
    
    @patch('mongo_episode_livre.get_DB_VARS')
    @patch('mongo_episode_livre.get_collection')
    def test_episode_livre_class_methods(self, mock_get_collection, mock_get_db_vars):
        """Test des méthodes de classe."""
        # Configuration des mocks
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        # Mock des résultats de recherche avec cursor qui a une méthode sort
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.__iter__.return_value = iter([])
        mock_collection.find.return_value = mock_cursor
        mock_collection.aggregate.return_value = [
            {
                "_id": {
                    "livre_oid": str(self.livre_oid),
                    "livre_titre": "Test Livre",
                    "auteur_nom": "Test Auteur",
                    "editeur_nom": "Test Editeur"
                },
                "nb_episodes": 2,
                "note_moyenne_globale": 8.5,
                "derniere_mention": datetime.now(),
                "episodes": [
                    {
                        "episode_oid": str(self.episode_oid),
                        "episode_title": "Test Episode",
                        "episode_date": datetime.now(),
                        "note_moyenne": 8.5,
                        "section": "programme"
                    }
                ]
            }
        ]
        
        with patch('mongo_episode_livre.BaseEntity'):
            from mongo_episode_livre import EpisodeLivre
            
            # Test find_by_livre
            results = EpisodeLivre.find_by_livre(self.livre_oid)
            mock_collection.find.assert_called_with({"livre_oid": self.livre_oid})
            self.assertIsInstance(results, list)
            
            # Test find_by_auteur
            results = EpisodeLivre.find_by_auteur(self.auteur_oid)
            mock_collection.find.assert_called_with({"auteur_oid": self.auteur_oid})
            self.assertIsInstance(results, list)
            
            # Test get_all_livres_uniques
            results = EpisodeLivre.get_all_livres_uniques()
            mock_collection.aggregate.assert_called()
            self.assertIsInstance(results, list)
            
            # Test search_livres
            results = EpisodeLivre.search_livres("tolkien")
            self.assertIsInstance(results, list)
            
            # Test search_livres avec requête vide
            results = EpisodeLivre.search_livres("")
            self.assertEqual(results, [])
    
    @patch('mongo_episode_livre.get_DB_VARS')
    @patch('mongo_episode_livre.get_collection')
    def test_from_book_mention(self, mock_get_collection, mock_get_db_vars):
        """Test de création depuis BookMention."""
        # Configuration des mocks
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        with patch('mongo_episode_livre.BaseEntity') as mock_base_entity:
            mock_base_entity.return_value = MagicMock()
            
            from mongo_episode_livre import EpisodeLivre
            
            # Mock BookMention
            class MockBookMention:
                def __init__(self):
                    self.titre = "Test Livre"
                    self.auteur = "Test Auteur"
                    self.editeur = "Test Editeur"
                    self.note = 8.0
                    self.nb_critiques = 2
                    self.section = "programme"
                    self.commentaire = "Très bon livre"
                    self.coup_de_coeur = "Test Critique"
                    self.chef_doeuvre = None
            
            book_mention = MockBookMention()
            episode_date = datetime(2024, 12, 15)
            episode_title = "Episode Test"
            
            episode_livre = EpisodeLivre.from_book_mention(
                self.episode_oid, self.livre_oid, self.auteur_oid,
                book_mention, episode_date, episode_title
            )
            
            # Vérifications
            self.assertEqual(episode_livre.livre_titre, "Test Livre")
            self.assertEqual(episode_livre.auteur_nom, "Test Auteur")
            self.assertEqual(episode_livre.note_moyenne, 8.0)
            self.assertEqual(episode_livre.episode_date, episode_date)
            self.assertEqual(episode_livre.episode_title, episode_title)
    
    @patch('mongo_episode_livre.get_DB_VARS')
    @patch('mongo_episode_livre.get_collection')
    def test_to_dict_serialization(self, mock_get_collection, mock_get_db_vars):
        """Test de la sérialisation to_dict."""
        # Configuration des mocks
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        with patch('mongo_episode_livre.BaseEntity') as mock_base_entity:
            mock_instance = MagicMock()
            mock_instance.to_dict.return_value = {"test": "data"}
            mock_base_entity.return_value = mock_instance
            
            from mongo_episode_livre import EpisodeLivre
            
            episode_livre = EpisodeLivre(self.episode_oid, self.livre_oid, self.auteur_oid)
            episode_livre.add_livre_metadata("Test Livre", "Test Auteur")
            
            # Test que to_dict est appelable (héritée de BaseEntity)
            result = episode_livre.to_dict()
            self.assertIsInstance(result, dict)
    
    @patch('mongo_episode_livre.get_DB_VARS')
    @patch('mongo_episode_livre.get_collection')
    def test_error_handling_search_livres(self, mock_get_collection, mock_get_db_vars):
        """Test de la gestion d'erreurs dans search_livres."""
        # Configuration des mocks
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        with patch('mongo_episode_livre.BaseEntity'):
            from mongo_episode_livre import EpisodeLivre
            
            # Test avec requête trop courte
            results = EpisodeLivre.search_livres("a")
            self.assertEqual(results, [])
            
            # Test avec requête None
            results = EpisodeLivre.search_livres(None)
            self.assertEqual(results, [])
            
            # Test avec requête vide
            results = EpisodeLivre.search_livres("")
            self.assertEqual(results, [])
    
    @patch('mongo_episode_livre.get_DB_VARS')
    @patch('mongo_episode_livre.get_collection')
    def test_from_document_error_handling(self, mock_get_collection, mock_get_db_vars):
        """Test de la gestion d'erreurs dans _from_document."""
        # Configuration des mocks
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        with patch('mongo_episode_livre.BaseEntity'):
            from mongo_episode_livre import EpisodeLivre
            
            # Test avec document invalide (clés manquantes)
            invalid_doc = {"invalid": "document"}
            result = EpisodeLivre._from_document(invalid_doc)
            self.assertIsNone(result)
            
            # Test avec document None
            result = EpisodeLivre._from_document(None)
            self.assertIsNone(result)
    
    @patch('mongo_episode_livre.get_DB_VARS')
    @patch('mongo_episode_livre.get_collection')
    def test_string_representations(self, mock_get_collection, mock_get_db_vars):
        """Test des méthodes __str__ et __repr__."""
        # Configuration des mocks
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        with patch('mongo_episode_livre.BaseEntity') as mock_base_entity:
            mock_base_entity.return_value = MagicMock()
            
            from mongo_episode_livre import EpisodeLivre
            
            episode_livre = EpisodeLivre(self.episode_oid, self.livre_oid, self.auteur_oid)
            episode_livre.add_livre_metadata("Le Hobbit", "J.R.R. Tolkien")
            episode_livre.add_episode_metadata(datetime.now(), "Episode Test")
            
            # Test __str__
            str_repr = str(episode_livre)
            self.assertIn("J.R.R. Tolkien", str_repr)
            self.assertIn("Le Hobbit", str_repr)
            self.assertIn("Episode Test", str_repr)
            
            # Test __repr__
            repr_str = repr(episode_livre)
            self.assertIn("EpisodeLivre", repr_str)
            self.assertIn(str(self.episode_oid), repr_str)
            self.assertIn(str(self.livre_oid), repr_str)
            self.assertIn(str(self.auteur_oid), repr_str)
    
    @patch('mongo_episode_livre.get_DB_VARS')
    @patch('mongo_episode_livre.get_collection')
    def test_metadata_validation(self, mock_get_collection, mock_get_db_vars):
        """Test de validation des métadonnées."""
        # Configuration des mocks
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection
        
        with patch('mongo_episode_livre.BaseEntity') as mock_base_entity:
            mock_base_entity.return_value = MagicMock()
            
            from mongo_episode_livre import EpisodeLivre
            
            episode_livre = EpisodeLivre(self.episode_oid, self.livre_oid, self.auteur_oid)
            
            # Test avec valeurs None
            episode_livre.add_livre_metadata("Titre", "Auteur", None)
            self.assertEqual(episode_livre.editeur_nom, None)
            
            # Test avec valeurs optionnelles
            episode_livre.add_avis_metadata(
                note_moyenne=None,
                nb_critiques=None,
                commentaire=None,
                coup_de_coeur=None,
                chef_doeuvre=None
            )
            self.assertIsNone(episode_livre.note_moyenne)
            self.assertIsNone(episode_livre.nb_critiques)
            self.assertIsNone(episode_livre.commentaire)
            self.assertIsNone(episode_livre.coup_de_coeur)
            self.assertIsNone(episode_livre.chef_doeuvre)
            
            # Vérifier que updated_at est mis à jour
            old_updated_at = episode_livre.updated_at
            episode_livre.add_avis_metadata(note_moyenne=9.0)
            self.assertGreater(episode_livre.updated_at, old_updated_at)


if __name__ == '__main__':
    unittest.main()