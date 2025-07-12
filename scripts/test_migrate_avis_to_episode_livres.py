#!/usr/bin/env python3
"""
Tests de validation pour le script de migration migrate_avis_to_episode_livres.py

Ces tests valident :
1. La création et configuration du gestionnaire de migration
2. Les statistiques et dataclasses
3. La logique de migration avec mocks
4. La validation post-migration
5. Les modes dry-run et production
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import tempfile
from pathlib import Path
from datetime import datetime
from dataclasses import asdict

# Ajout du répertoire scripts et nbs au path
scripts_path = Path(__file__).parent.parent / "scripts"
nbs_path = Path(__file__).parent.parent / "nbs"
sys.path.insert(0, str(scripts_path))
sys.path.insert(0, str(nbs_path))

from migrate_avis_to_episode_livres import (
    MigrationAvisToEpisodeLivres,
    MigrationStats,
    main,
)


class TestMigrationStats(unittest.TestCase):
    """Tests pour la dataclass MigrationStats"""

    def test_migration_stats_creation(self):
        """Test de création de MigrationStats"""
        stats = MigrationStats()

        # Vérification valeurs par défaut
        self.assertEqual(stats.episodes_traites, 0)
        self.assertEqual(stats.episodes_avec_avis, 0)
        self.assertEqual(stats.livres_extraits, 0)
        self.assertEqual(stats.documents_crees, 0)
        self.assertEqual(stats.documents_mis_a_jour, 0)
        self.assertEqual(stats.erreurs, 0)
        self.assertIsInstance(stats.erreurs_details, list)
        self.assertEqual(len(stats.erreurs_details), 0)

    def test_migration_stats_with_values(self):
        """Test de création avec valeurs"""
        stats = MigrationStats(
            episodes_traites=100,
            episodes_avec_avis=50,
            livres_extraits=75,
            documents_crees=60,
            documents_mis_a_jour=10,
            erreurs=2,
            erreurs_details=["Erreur 1", "Erreur 2"],
        )

        self.assertEqual(stats.episodes_traites, 100)
        self.assertEqual(stats.episodes_avec_avis, 50)
        self.assertEqual(stats.livres_extraits, 75)
        self.assertEqual(stats.documents_crees, 60)
        self.assertEqual(stats.documents_mis_a_jour, 10)
        self.assertEqual(stats.erreurs, 2)
        self.assertEqual(len(stats.erreurs_details), 2)


class TestMigrationAvisToEpisodeLivres(unittest.TestCase):
    """Tests pour la classe MigrationAvisToEpisodeLivres"""

    def setUp(self):
        """Configuration avant chaque test"""
        # Mock des imports pour éviter les dépendances MongoDB
        self.mock_parser = Mock()
        self.mock_episode = Mock()
        self.mock_episode_livre = Mock()

        # Patch des imports
        self.patcher_parser = patch(
            "migrate_avis_to_episode_livres.AvisCritiquesParser",
            return_value=self.mock_parser,
        )
        self.patcher_episode = patch(
            "migrate_avis_to_episode_livres.Episode", self.mock_episode
        )
        self.patcher_episodes = patch("migrate_avis_to_episode_livres.Episodes")
        self.patcher_episode_livre = patch(
            "migrate_avis_to_episode_livres.EpisodeLivre", self.mock_episode_livre
        )

        self.patcher_parser.start()
        self.patcher_episode.start()
        self.patcher_episodes.start()
        self.patcher_episode_livre.start()

    def tearDown(self):
        """Nettoyage après chaque test"""
        self.patcher_parser.stop()
        self.patcher_episode.stop()
        self.patcher_episodes.stop()
        self.patcher_episode_livre.stop()

    def test_migration_creation_dry_run(self):
        """Test de création en mode dry-run"""
        migration = MigrationAvisToEpisodeLivres(dry_run=True)

        self.assertTrue(migration.dry_run)
        self.assertIsNotNone(migration.parser)
        self.assertIsInstance(migration.stats, MigrationStats)
        self.assertIsNotNone(migration.logger)

    def test_migration_creation_production(self):
        """Test de création en mode production"""
        migration = MigrationAvisToEpisodeLivres(dry_run=False)

        self.assertFalse(migration.dry_run)
        self.assertIsNotNone(migration.parser)
        self.assertIsInstance(migration.stats, MigrationStats)
        self.assertIsNotNone(migration.logger)

    @patch("migrate_avis_to_episode_livres.logging.getLogger")
    def test_logging_setup(self, mock_get_logger):
        """Test de configuration du logging"""
        mock_logger = Mock()
        mock_logger.handlers = []  # Simule un logger sans handlers
        mock_get_logger.return_value = mock_logger

        migration = MigrationAvisToEpisodeLivres()

        # Vérification que le logger est récupéré et configuré
        mock_get_logger.assert_called_with("migration_avis")
        self.assertIsNotNone(migration.logger)

    def test_migrate_episode_sans_avis(self):
        """Test migration épisode sans avis critiques"""
        migration = MigrationAvisToEpisodeLivres(dry_run=True)

        # Mock épisode sans avis
        mock_episode = Mock()
        mock_episode.get_oid.return_value = "episode_123"
        mock_episode.avis_critiques = None  # Pas d'avis critiques

        migration._migrate_episode(mock_episode)

        # Vérifications
        self.assertEqual(migration.stats.episodes_traites, 1)
        self.assertEqual(migration.stats.episodes_avec_avis, 0)
        self.assertEqual(migration.stats.livres_extraits, 0)

    def test_migrate_episode_avec_avis_mais_aucun_livre(self):
        """Test migration épisode avec avis mais aucun livre extrait"""
        migration = MigrationAvisToEpisodeLivres(dry_run=True)

        # Mock épisode avec avis mais parser ne trouve rien
        mock_episode = Mock()
        mock_episode.get_oid.return_value = "episode_123"
        mock_episode.avis_critiques = (
            "Avis critiques très long mais sans livre identifiable pour le parser..."
        )

        self.mock_parser.extraire_livres_auteurs.return_value = []  # Aucun livre trouvé

        migration._migrate_episode(mock_episode)

        # Vérifications
        self.assertEqual(migration.stats.episodes_traites, 1)
        self.assertEqual(migration.stats.episodes_avec_avis, 1)
        self.assertEqual(migration.stats.livres_extraits, 0)

    def test_migrate_episode_avec_livres_dry_run(self):
        """Test migration épisode avec livres en mode dry-run"""
        migration = MigrationAvisToEpisodeLivres(dry_run=True)

        # Mock épisode avec avis
        mock_episode = Mock()
        mock_episode.get_oid.return_value = "episode_123"
        mock_episode.avis_critiques = (
            "Avis critiques avec livres détectables par le parser..."
        )

        # Mock parser trouve des livres
        livres_mock = [
            {
                "livre": "Le Livre Test",
                "auteur": "Auteur Test",
                "type": "livre",
                "avis": "Excellent livre",
            },
            {
                "livre": "Autre Livre",
                "auteur": "Autre Auteur",
                "type": "roman",
                "avis": "Livre moyen",
            },
        ]
        self.mock_parser.extraire_livres_auteurs.return_value = livres_mock

        # Mock EpisodeLivre.find_by_episode_and_book retourne None (nouveaux documents)
        self.mock_episode_livre.find_by_episode_and_book.return_value = None

        migration._migrate_episode(mock_episode)

        # Vérifications
        self.assertEqual(migration.stats.episodes_traites, 1)
        self.assertEqual(migration.stats.episodes_avec_avis, 1)
        self.assertEqual(migration.stats.livres_extraits, 2)
        self.assertEqual(
            migration.stats.documents_crees, 2
        )  # 2 nouveaux documents (dry-run)
        self.assertEqual(migration.stats.documents_mis_a_jour, 0)

    def test_create_new_episode_livre(self):
        """Test de création d'un nouveau EpisodeLivre"""
        migration = MigrationAvisToEpisodeLivres(dry_run=False)

        # Mock épisode
        mock_episode = Mock()
        mock_episode.get_oid.return_value = "episode_123"
        mock_episode.emission = "Le Masque et la Plume"
        mock_episode.date = datetime(2024, 1, 15)
        mock_episode.titre = "Titre Episode Test"
        mock_episode.url_telechargement = "https://example.com/episode"

        # Mock livre data
        livre_data = {
            "livre": "Test Livre",
            "auteur": "Test Auteur",
            "type": "roman",
            "avis": "Critique test",
        }

        # Mock EpisodeLivre instance
        mock_instance = Mock()
        self.mock_episode_livre.return_value = mock_instance

        migration._create_new_episode_livre(mock_episode, livre_data)

        # Vérifications
        self.mock_episode_livre.assert_called_once()
        mock_instance.set_field.assert_any_call("episode_id", "episode_123")
        mock_instance.set_field.assert_any_call("livre", "Test Livre")
        mock_instance.set_field.assert_any_call("auteur", "Test Auteur")
        mock_instance.set_field.assert_any_call(
            "migration_source", "avis_critiques_parser"
        )
        mock_instance.save.assert_called_once()

    def test_update_episode_livre_modification_necessaire(self):
        """Test de mise à jour EpisodeLivre avec modification nécessaire"""
        migration = MigrationAvisToEpisodeLivres(dry_run=False)

        # Mock EpisodeLivre existant
        mock_existing = Mock()
        mock_existing.get_field.return_value = "Ancien avis"

        # Mock épisode
        mock_episode = Mock()

        # Nouveau livre data avec avis différent
        livre_data = {"avis": "Nouveau avis modifié"}

        result = migration._update_episode_livre(
            mock_existing, mock_episode, livre_data
        )

        # Vérifications
        self.assertTrue(result)
        mock_existing.set_field.assert_any_call("avis_critique", "Nouveau avis modifié")
        mock_existing.save.assert_called_once()

    def test_update_episode_livre_aucune_modification(self):
        """Test de mise à jour EpisodeLivre sans modification nécessaire"""
        migration = MigrationAvisToEpisodeLivres(dry_run=False)

        # Mock EpisodeLivre existant avec même avis
        mock_existing = Mock()
        mock_existing.get_field.return_value = "Même avis"

        # Mock épisode
        mock_episode = Mock()

        # Livre data avec même avis
        livre_data = {"avis": "Même avis"}

        result = migration._update_episode_livre(
            mock_existing, mock_episode, livre_data
        )

        # Vérifications
        self.assertFalse(result)
        mock_existing.save.assert_not_called()

    @patch("mongo.get_collection")
    @patch("mongo.get_DB_VARS")
    def test_validate_migration(self, mock_get_db_vars, mock_get_collection):
        """Test de validation de migration"""
        migration = MigrationAvisToEpisodeLivres()

        # Mock des DB vars
        mock_get_db_vars.return_value = ("localhost", "test_db", "port")

        # Mock de la collection MongoDB
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection

        # Mock des méthodes collection
        mock_collection.count_documents.return_value = 150
        mock_collection.distinct.side_effect = lambda field: {
            "episode_id": ["ep1", "ep2", "ep3"],
            "livre_titre": ["livre1", "livre2", "livre3", "livre4"],
            "auteur_nom": ["auteur1", "auteur2"],
        }[field]

        # Mock des exemples
        mock_collection.find.return_value.sort.return_value.limit.return_value = [
            {
                "livre_titre": "Exemple Livre",
                "auteur_nom": "Exemple Auteur",
                "episode_titre": "Exemple Episode",
            }
        ]

        validation = migration.validate_migration()

        # Vérifications
        self.assertEqual(validation["total_episode_livres"], 150)
        self.assertEqual(validation["episodes_uniques"], 3)
        self.assertEqual(validation["livres_uniques"], 4)
        self.assertEqual(validation["auteurs_uniques"], 2)
        self.assertTrue(validation["coherence_ok"])
        self.assertEqual(len(validation["exemples"]), 1)

    @patch("migrate_avis_to_episode_livres.Episodes")
    def test_migrate_all_episodes_avec_limite(self, mock_episodes_class):
        """Test de migration avec limite d'épisodes"""
        migration = MigrationAvisToEpisodeLivres(dry_run=True)

        # Mock Episodes manager
        mock_episodes_manager = Mock()
        mock_episodes_manager.oid_episodes = ["oid1", "oid2", "oid3"]
        mock_episodes_class.return_value = mock_episodes_manager

        # Mock des épisodes
        mock_episodes = [Mock() for _ in range(3)]
        for i, ep in enumerate(mock_episodes):
            ep.get_id.return_value = f"episode_{i}"
            ep.get_field.return_value = None  # Pas d'avis pour simplifier

        self.mock_episode.from_oid.side_effect = mock_episodes

        stats = migration.migrate_all_episodes(limit=3)

        # Vérifications
        mock_episodes_class.assert_called_once()
        mock_episodes_manager.get_entries.assert_called_once_with(limit=3)
        self.assertEqual(stats.episodes_traites, 3)

    def test_gestion_erreur_episode(self):
        """Test de gestion d'erreur lors de migration d'un épisode"""
        migration = MigrationAvisToEpisodeLivres(dry_run=True)

        # Mock épisode qui lève une exception
        mock_episode = Mock()
        mock_episode.get_oid.side_effect = Exception("Erreur test")
        mock_episode.titre = "episode_error"

        migration._migrate_episode(mock_episode)

        # Vérifications
        self.assertEqual(migration.stats.erreurs, 1)
        self.assertEqual(len(migration.stats.erreurs_details), 1)
        self.assertIn(
            "Erreur épisode episode_error", migration.stats.erreurs_details[0]
        )


class TestMainFunction(unittest.TestCase):
    """Tests pour la fonction main()"""

    @patch("migrate_avis_to_episode_livres.MigrationAvisToEpisodeLivres")
    @patch("sys.argv", ["migrate_avis_to_episode_livres.py", "--dry-run"])
    def test_main_dry_run(self, mock_migration_class):
        """Test de main() en mode dry-run"""
        mock_migration = Mock()
        mock_migration_class.return_value = mock_migration
        mock_migration.migrate_all_episodes.return_value = MigrationStats()

        result = main()

        self.assertEqual(result, 0)
        mock_migration_class.assert_called_once_with(dry_run=True)
        mock_migration.migrate_all_episodes.assert_called_once_with(limit=None)

    @patch("migrate_avis_to_episode_livres.MigrationAvisToEpisodeLivres")
    @patch("sys.argv", ["migrate_avis_to_episode_livres.py", "--limit", "10"])
    def test_main_avec_limite(self, mock_migration_class):
        """Test de main() avec limite"""
        mock_migration = Mock()
        mock_migration_class.return_value = mock_migration
        mock_migration.migrate_all_episodes.return_value = MigrationStats()
        mock_migration.validate_migration.return_value = {"total_episode_livres": 10}

        result = main()

        self.assertEqual(result, 0)
        mock_migration_class.assert_called_once_with(dry_run=False)
        mock_migration.migrate_all_episodes.assert_called_once_with(limit=10)
        mock_migration.validate_migration.assert_called_once()

    @patch("migrate_avis_to_episode_livres.MigrationAvisToEpisodeLivres")
    @patch("sys.argv", ["migrate_avis_to_episode_livres.py", "--validate-only"])
    def test_main_validation_seulement(self, mock_migration_class):
        """Test de main() en mode validation seulement"""
        mock_migration = Mock()
        mock_migration_class.return_value = mock_migration
        mock_migration.validate_migration.return_value = {"total_episode_livres": 50}

        result = main()

        self.assertEqual(result, 0)
        mock_migration_class.assert_called_once_with(dry_run=False)
        mock_migration.migrate_all_episodes.assert_not_called()
        mock_migration.validate_migration.assert_called_once()


if __name__ == "__main__":
    # Configuration logging pour tests
    import logging

    logging.getLogger("migration_avis").setLevel(logging.CRITICAL)

    unittest.main(verbosity=2)
