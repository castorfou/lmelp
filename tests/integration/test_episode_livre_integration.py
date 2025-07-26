#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from datetime import datetime

# Ajouter le chemin vers nbs
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'nbs'))

# Mock BaseEntity avec les méthodes nécessaires
class MockBaseEntity:
    def __init__(self, nom, collection_name):
        self.nom = nom
        self.collection_name = collection_name
        self.collection = MagicMock()
    
    def exists(self):
        return False
    
    def keep(self):
        """Mock keep() method that mimics real BaseEntity behavior"""
        data = self.to_dict()
        if not self.exists():
            self.collection.insert_one(data)
        else:
            self.collection.replace_one({"nom": self.nom}, data)
    
    def remove(self):
        pass
    
    def to_dict(self):
        data = self.__dict__.copy()
        data.pop("collection", None)
        return data
    
    def get_oid(self):
        return None

# Mock des dépendances
sys.modules['config'] = MagicMock()
sys.modules['config'].get_DB_VARS = MagicMock(return_value=("localhost", "test_db", "true"))

sys.modules['mongo'] = MagicMock()
sys.modules['mongo'].BaseEntity = MockBaseEntity
sys.modules['mongo'].mongolog = MagicMock()

sys.modules['mongo_auteur'] = MagicMock()
sys.modules['mongo_livre'] = MagicMock()

from bson import ObjectId
from mongo_episode_livre import EpisodeLivre


class TestEpisodeLivreIntegration(unittest.TestCase):
    """Tests d'intégration pour EpisodeLivre avec workflow complet."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.episode_oid = ObjectId()
        self.livre_oid = ObjectId()
        self.auteur_oid = ObjectId()
        
        # Mock collection avec comportement plus réaliste
        self.mock_collection = MagicMock()
        
        # Mock cursor pour simuler le comportement MongoDB
        mock_cursor = MagicMock()
        mock_cursor.sort.return_value = []
        mock_cursor.__iter__ = lambda self: iter([])
        
        self.mock_collection.find.return_value = mock_cursor
        self.mock_collection.find_one.return_value = None
        self.mock_collection.aggregate.return_value = []
        
        # Patch get_collection
        self.collection_patcher = patch('mongo_episode_livre.get_collection')
        self.mock_get_collection = self.collection_patcher.start()
        self.mock_get_collection.return_value = self.mock_collection
        
        # Patch get_DB_VARS
        self.db_vars_patcher = patch('mongo_episode_livre.get_DB_VARS')
        self.mock_get_db_vars = self.db_vars_patcher.start()
        self.mock_get_db_vars.return_value = ("localhost", "test_db", "true")
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        self.collection_patcher.stop()
        self.db_vars_patcher.stop()
    
    def test_workflow_complet_creation_et_recherche(self):
        """Test du workflow complet : création, sauvegarde et recherche."""
        
        # 1. Créer une instance EpisodeLivre
        episode_livre = EpisodeLivre(self.episode_oid, self.livre_oid, self.auteur_oid)
        
        # 2. Ajouter toutes les métadonnées
        episode_date = datetime(2024, 12, 15, 10, 0, 0)
        episode_title = "Episode du 15 décembre 2024"
        
        episode_livre.add_episode_metadata(episode_date, episode_title)
        episode_livre.add_livre_metadata(
            livre_titre="Le Seigneur des Anneaux",
            auteur_nom="J.R.R. Tolkien",
            editeur_nom="Gallimard"
        )
        episode_livre.add_avis_metadata(
            note_moyenne=9.2,
            nb_critiques=4,
            section="programme",
            commentaire="Un chef-d'œuvre de la fantasy",
            coup_de_coeur="Elisabeth Philippe"
        )
        
        # 3. Vérifier que toutes les données sont correctement assignées
        self.assertEqual(episode_livre.episode_date, episode_date)
        self.assertEqual(episode_livre.episode_title, episode_title)
        self.assertEqual(episode_livre.livre_titre, "Le Seigneur des Anneaux")
        self.assertEqual(episode_livre.auteur_nom, "J.R.R. Tolkien")
        self.assertEqual(episode_livre.editeur_nom, "Gallimard")
        self.assertEqual(episode_livre.note_moyenne, 9.2)
        self.assertEqual(episode_livre.nb_critiques, 4)
        self.assertEqual(episode_livre.section, "programme")
        self.assertEqual(episode_livre.commentaire, "Un chef-d'œuvre de la fantasy")
        self.assertEqual(episode_livre.coup_de_coeur, "Elisabeth Philippe")
        
        # 4. Simuler la sauvegarde
        with patch.object(episode_livre, 'collection', self.mock_collection):
            episode_livre.keep()
            
            # Vérifier que insert_one a été appelé (car exists() retourne False)
            self.mock_collection.insert_one.assert_called_once()
            
            # Vérifier le contenu sauvegardé
            saved_data = self.mock_collection.insert_one.call_args[0][0]
            self.assertEqual(saved_data['livre_titre'], "Le Seigneur des Anneaux")
            self.assertEqual(saved_data['note_moyenne'], 9.2)
        
        # 5. Tester les méthodes de recherche
        EpisodeLivre.find_by_livre(self.livre_oid)
        self.mock_collection.find.assert_called_with({"livre_oid": self.livre_oid})
        
        EpisodeLivre.find_by_auteur(self.auteur_oid)
        self.mock_collection.find.assert_called_with({"auteur_oid": self.auteur_oid})
        
        EpisodeLivre.find_by_episode(self.episode_oid)
        self.mock_collection.find.assert_called_with({"episode_oid": self.episode_oid})
    
    def test_workflow_from_book_mention(self):
        """Test du workflow de création depuis un BookMention."""
        
        # Mock BookMention (comme celui du parser)
        class MockBookMention:
            def __init__(self):
                self.titre = "1984"
                self.auteur = "George Orwell"
                self.editeur = "Gallimard"
                self.note = 8.7
                self.nb_critiques = 3
                self.section = "programme"
                self.commentaire = "Un classique incontournable"
                self.coup_de_coeur = "Michel Crépu"
                self.chef_doeuvre = None
        
        book_mention = MockBookMention()
        episode_date = datetime(2024, 12, 20)
        episode_title = "Episode spécial dystopies"
        
        # Créer l'instance depuis BookMention
        episode_livre = EpisodeLivre.from_book_mention(
            self.episode_oid, self.livre_oid, self.auteur_oid,
            book_mention, episode_date, episode_title
        )
        
        # Vérifier que toutes les données ont été correctement transférées
        self.assertEqual(episode_livre.livre_titre, "1984")
        self.assertEqual(episode_livre.auteur_nom, "George Orwell")
        self.assertEqual(episode_livre.editeur_nom, "Gallimard")
        self.assertEqual(episode_livre.note_moyenne, 8.7)
        self.assertEqual(episode_livre.nb_critiques, 3)
        self.assertEqual(episode_livre.section, "programme")
        self.assertEqual(episode_livre.commentaire, "Un classique incontournable")
        self.assertEqual(episode_livre.coup_de_coeur, "Michel Crépu")
        self.assertEqual(episode_livre.episode_date, episode_date)
        self.assertEqual(episode_livre.episode_title, episode_title)
        
        # Vérifier les métadonnées de création
        self.assertIsNotNone(episode_livre.created_at)
        self.assertIsNotNone(episode_livre.updated_at)
    
    def test_aggregation_queries(self):
        """Test des requêtes d'agrégation MongoDB."""
        
        # Mock des résultats d'agrégation
        mock_aggregation_result = [
            {
                "_id": {
                    "livre_oid": str(self.livre_oid),
                    "livre_titre": "Le Seigneur des Anneaux",
                    "auteur_nom": "J.R.R. Tolkien",
                    "editeur_nom": "Gallimard"
                },
                "nb_episodes": 3,
                "note_moyenne_globale": 8.8,
                "derniere_mention": datetime(2024, 12, 15),
                "episodes": [
                    {
                        "episode_oid": str(self.episode_oid),
                        "episode_title": "Episode 1",
                        "episode_date": datetime(2024, 12, 15),
                        "note_moyenne": 8.8,
                        "section": "programme"
                    }
                ]
            }
        ]
        
        self.mock_collection.aggregate.return_value = mock_aggregation_result
        
        # Test get_all_livres_uniques
        livres_uniques = EpisodeLivre.get_all_livres_uniques()
        
        self.assertEqual(len(livres_uniques), 1)
        livre = livres_uniques[0]
        
        self.assertEqual(livre["livre_titre"], "Le Seigneur des Anneaux")
        self.assertEqual(livre["auteur_nom"], "J.R.R. Tolkien")
        self.assertEqual(livre["nb_episodes"], 3)
        self.assertEqual(livre["note_moyenne_globale"], 8.8)
        self.assertIn("episodes", livre)
        
        # Vérifier que l'agrégation a été appelée
        self.mock_collection.aggregate.assert_called()
        
        # Vérifier la structure du pipeline d'agrégation
        pipeline = self.mock_collection.aggregate.call_args[0][0]
        self.assertIsInstance(pipeline, list)
        
        # Le pipeline devrait contenir au moins un $group et un $sort
        has_group = any("$group" in stage for stage in pipeline)
        has_sort = any("$sort" in stage for stage in pipeline)
        
        self.assertTrue(has_group, "Le pipeline devrait contenir un stage $group")
        self.assertTrue(has_sort, "Le pipeline devrait contenir un stage $sort")
    
    def test_search_functionality(self):
        """Test de la fonctionnalité de recherche."""
        
        # Mock des résultats de recherche
        mock_search_result = [
            {
                "_id": {
                    "livre_oid": str(self.livre_oid),
                    "livre_titre": "Le Hobbit",
                    "auteur_nom": "J.R.R. Tolkien",
                    "editeur_nom": "Gallimard"
                },
                "nb_episodes": 2,
                "note_moyenne_globale": 8.5,
                "derniere_mention": datetime(2024, 12, 10)
            }
        ]
        
        self.mock_collection.aggregate.return_value = mock_search_result
        
        # Test de recherche par auteur
        results = EpisodeLivre.search_livres("tolkien")
        
        self.assertEqual(len(results), 1)
        result = results[0]
        
        self.assertEqual(result["livre_titre"], "Le Hobbit")
        self.assertEqual(result["auteur_nom"], "J.R.R. Tolkien")
        self.assertEqual(result["nb_episodes"], 2)
        
        # Vérifier que l'agrégation a été appelée avec un $match
        self.mock_collection.aggregate.assert_called()
        pipeline = self.mock_collection.aggregate.call_args[0][0]
        
        # Le premier stage devrait être un $match
        match_stage = pipeline[0]
        self.assertIn("$match", match_stage)
        
        # Vérifier que la recherche porte sur titre et auteur
        match_query = match_stage["$match"]
        self.assertIn("$or", match_query)
        
        or_conditions = match_query["$or"]
        self.assertEqual(len(or_conditions), 2)
        
        # Vérifier les conditions de recherche
        titre_condition = or_conditions[0]
        auteur_condition = or_conditions[1]
        
        self.assertIn("livre_titre", titre_condition)
        self.assertIn("auteur_nom", auteur_condition)
        
        # Vérifier que c'est une recherche insensible à la casse
        self.assertEqual(titre_condition["livre_titre"]["$options"], "i")
        self.assertEqual(auteur_condition["auteur_nom"]["$options"], "i")


if __name__ == '__main__':
    unittest.main()