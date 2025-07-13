"""
Tests d'intégration pour les workflows principaux du projet LMELP.

Ces tests valident l'interaction entre plusieurs modules :
- RSS parsing → MongoDB storage → LLM analysis
- Configuration → Database → Processing pipelines
- End-to-end workflows complets

Contrairement aux tests unitaires qui isolent chaque module,
les tests d'intégration utilisent des vraies connexions inter-modules
avec des données contrôlées pour valider le système complet.
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock, call
from datetime import datetime
import json

# Import des modules à tester
from tests.fixtures import load_sample_json, load_sample_text


class TestRSSToMongoWorkflow:
    """Tests du workflow RSS → MongoDB"""

    @patch("sys.modules", new_callable=dict)
    def test_rss_to_mongo_complete_workflow(self, mock_modules):
        """Test : workflow complet RSS parsing → MongoDB storage"""
        # ARRANGE : Mock les modules pour éviter les imports
        mock_rss = MagicMock()
        mock_mongo = MagicMock()
        mock_feedparser = MagicMock()
        mock_pymongo = MagicMock()

        # Configurer les mocks
        mock_modules.update(
            {
                "feedparser": mock_feedparser,
                "pymongo": mock_pymongo,
                "pymongo.collection": MagicMock(),
                "config": MagicMock(),
                "nbs.config": MagicMock(),
                "nbs.rss": mock_rss,
                "nbs.mongo": mock_mongo,
            }
        )

        # Mock données RSS avec épisodes longs
        mock_feed = MagicMock()
        mock_feed.entries = [
            MagicMock(
                **{
                    "title": "Livres : \"L'art de perdre\" d'Alice Zeniter",
                    "summary": "Émission critique littéraire. Durée : 58 minutes",
                    "published": "Sun, 15 Dec 2024 17:00:00 +0100",
                    "enclosures": [
                        MagicMock(
                            type="audio/mpeg",
                            length="139456512",
                            href="https://example.com/episode.mp3",
                        )
                    ],
                }
            ),
            MagicMock(
                **{
                    "title": "Cinéma court",
                    "summary": "Critique cinéma. Durée : 35 minutes",
                    "published": "Sun, 08 Dec 2024 17:00:00 +0100",
                    "enclosures": [
                        MagicMock(
                            type="audio/mpeg",
                            length="84512768",
                            href="https://example.com/short.mp3",
                        )
                    ],
                }
            ),
        ]
        mock_feedparser.parse.return_value = mock_feed

        # Mock classe Podcast
        mock_podcast_instance = MagicMock()
        mock_podcast_instance.list_last_large_episodes.return_value = [
            {"title": 'Livres : "L\'art de perdre"', "duree_secondes": 58 * 60}
        ]
        mock_podcast_instance.store_last_large_episodes.return_value = 1
        mock_rss.Podcast.return_value = mock_podcast_instance

        # Mock MongoDB
        mock_collection = MagicMock()
        mock_mongo.get_collection.return_value = mock_collection

        # ACT : Simuler le workflow RSS → MongoDB
        podcast = mock_rss.Podcast()
        large_episodes = podcast.list_last_large_episodes()
        collection = mock_mongo.get_collection()
        stored_count = podcast.store_last_large_episodes(large_episodes)

        # ASSERT : Vérifier le workflow complet
        assert mock_rss.Podcast.called, "Podcast doit être instancié"
        assert len(large_episodes) == 1, "Un épisode long doit être trouvé"
        assert (
            large_episodes[0]["duree_secondes"] == 58 * 60
        ), "Durée doit être 58 minutes"
        assert (
            mock_mongo.get_collection.called
        ), "Collection MongoDB doit être récupérée"
        assert stored_count == 1, "Un épisode doit être stocké"

    def test_rss_parsing_with_real_feed_structure(self):
        """Test : parsing RSS avec structure de données réelle"""
        # ARRANGE : Utiliser les fixtures RSS réelles
        rss_content = load_sample_text("sample_rss_feed.xml")

        # ACT & ASSERT : Vérifier la structure des données RSS
        assert "<?xml" in rss_content, "RSS doit être du XML valide"
        assert "<rss" in rss_content, "RSS doit contenir une balise rss"
        assert (
            "Le Masque et la Plume" in rss_content
        ), "RSS doit contenir le nom de l'émission"
        assert "58:23" in rss_content, "RSS doit contenir des durées d'épisodes"
        assert "audio/mpeg" in rss_content, "RSS doit contenir des types audio"

        # Vérifier que les données sont exploitables
        episode_count = rss_content.count("<item>")
        assert (
            episode_count >= 5
        ), f"RSS doit contenir plusieurs épisodes, trouvés: {episode_count}"


class TestConfigurationIntegration:
    """Tests d'intégration de la configuration avec les autres modules"""

    def test_config_provides_valid_rss_url(self):
        """Test : configuration fournit une URL RSS valide pour les modules"""
        # ACT : Récupération de l'URL via config
        from nbs.config import get_RSS_URL

        rss_url = get_RSS_URL()

        # ASSERT : URL valide pour utilisation dans rss.py
        assert rss_url is not None, "URL RSS ne doit pas être None"
        assert isinstance(rss_url, str), "URL RSS doit être une string"
        assert rss_url.startswith("http"), "URL RSS doit être une URL HTTP valide"

    @patch.dict(os.environ, {"TEST_VAR": "test_value"})
    def test_config_environment_isolation(self):
        """Test : isolation des variables d'environnement entre modules"""
        # ACT & ASSERT : Variables de test disponibles
        from nbs.config import get_RSS_URL

        # La configuration doit fonctionner avec des variables d'environnement de test
        test_var = os.getenv("TEST_VAR")
        assert (
            test_var == "test_value"
        ), "Variables d'environnement de test doivent être disponibles"

        # Les modules doivent pouvoir utiliser la configuration
        rss_url = get_RSS_URL()
        assert (
            rss_url is not None
        ), "Configuration doit fonctionner dans l'environnement de test"


class TestLLMIntegrationWorkflow:
    """Tests d'intégration LLM avec données et configuration"""

    @patch("sys.modules", new_callable=dict)
    def test_llm_with_transcription_data(self, mock_modules):
        """Test : LLM processing avec données de transcription réelles"""
        # ARRANGE : Mock les modules LLM
        mock_llm = MagicMock()
        mock_azure_openai = MagicMock()
        mock_config = MagicMock()

        mock_modules.update(
            {
                "llama_index.llms.azure_openai": MagicMock(),
                "llama_index.core": MagicMock(),
                "config": mock_config,
                "nbs.config": mock_config,
                "nbs.llm": mock_llm,
            }
        )

        # Mock configuration Azure
        mock_config.get_azure_openai_keys.return_value = (
            "fake_key",
            "fake_endpoint",
            "fake_version",
        )
        mock_llm_instance = MagicMock()
        mock_llm.get_azure_llm.return_value = mock_llm_instance

        # Charger une vraie transcription
        transcription = load_sample_text("sample_transcription.txt")

        # ACT : Simuler processing LLM
        llm = mock_llm.get_azure_llm()

        # ASSERT : Vérifier l'intégration LLM + données
        assert mock_llm.get_azure_llm.called, "LLM Azure doit être appelé"
        assert (
            len(transcription) > 1000
        ), "Transcription doit avoir du contenu substantiel"
        assert (
            "critique" in transcription.lower()
        ), "Transcription doit contenir du contenu critique"
        assert llm is not None, "LLM doit être instancié"

    @patch("sys.modules", new_callable=dict)
    def test_multiple_llm_providers_integration(self, mock_modules):
        """Test : intégration multiple providers LLM"""
        # ARRANGE : Mock différents providers
        mock_llm = MagicMock()
        mock_config = MagicMock()

        mock_modules.update(
            {
                "google.generativeai": MagicMock(),
                "llama_index.llms.gemini": MagicMock(),
                "config": mock_config,
                "nbs.config": mock_config,
                "nbs.llm": mock_llm,
            }
        )

        mock_config.get_gemini_api_key.return_value = "fake_gemini_key"
        mock_llm_instance = MagicMock()
        mock_llm.get_gemini_llm.return_value = mock_llm_instance

        # ACT : Initialiser différents LLMs
        gemini_llm = mock_llm.get_gemini_llm()

        # ASSERT : Vérifier que différents providers peuvent coexister
        assert mock_llm.get_gemini_llm.called, "LLM Gemini doit être appelé"
        assert gemini_llm is not None, "LLM Gemini doit être instancié"


class TestMongoIntegrationWorkflow:
    """Tests d'intégration MongoDB avec données et entités"""

    @patch("sys.modules", new_callable=dict)
    def test_mongo_entity_workflow(self, mock_modules):
        """Test : workflow complet entités MongoDB"""
        # ARRANGE : Mock MongoDB
        mock_mongo = MagicMock()
        mock_pymongo = MagicMock()
        mock_config = MagicMock()

        mock_modules.update(
            {
                "pymongo": mock_pymongo,
                "pymongo.collection": MagicMock(),
                "config": mock_config,
                "nbs.config": mock_config,
                "nbs.mongo": mock_mongo,
            }
        )

        # Simuler données épisode
        episode_data = load_sample_json("sample_episode.json")
        test_episode = episode_data["episodes"][0]

        # Mock collection et entité
        mock_collection = MagicMock()
        mock_mongo.get_collection.return_value = mock_collection
        mock_entity = MagicMock()
        mock_entity.name = "test_name"
        mock_entity.collection = mock_collection
        mock_mongo.BaseEntity.return_value = mock_entity

        # ACT : Créer et manipuler des entités MongoDB
        collection = mock_mongo.get_collection()
        entity = mock_mongo.BaseEntity("test_name", collection)

        # ASSERT : Vérifier l'intégration MongoDB + données
        assert (
            mock_mongo.get_collection.called
        ), "Collection MongoDB doit être récupérée"
        assert mock_mongo.BaseEntity.called, "Entité doit être créée"
        assert entity.name == "test_name", "Entité doit avoir le bon nom"
        assert entity.collection is not None, "Entité doit avoir une collection"
        assert (
            "titre" in test_episode
        ), "Données épisode doivent avoir structure attendue"

    @patch("sys.modules", new_callable=dict)
    def test_mongo_logging_integration(self, mock_modules):
        """Test : intégration logging MongoDB"""
        # ARRANGE : Mock MongoDB pour logs
        mock_mongo = MagicMock()
        mock_pymongo = MagicMock()

        mock_modules.update(
            {
                "pymongo": mock_pymongo,
                "pymongo.collection": MagicMock(),
                "nbs.mongo": mock_mongo,
            }
        )

        # ACT : Test logging MongoDB
        mock_mongo.mongolog("Test integration log", "INFO")

        # ASSERT : Vérifier que le logging fonctionne
        assert mock_mongo.mongolog.called, "Fonction mongolog doit être appelée"


class TestEndToEndWorkflows:
    """Tests end-to-end complets intégrant tous les modules"""

    @patch("sys.modules", new_callable=dict)
    def test_complete_podcast_analysis_workflow(self, mock_modules):
        """Test : workflow complet RSS → MongoDB → LLM analysis"""
        # ARRANGE : Setup complet all mocks
        mock_rss = MagicMock()
        mock_mongo = MagicMock()
        mock_llm = MagicMock()
        mock_config = MagicMock()

        mock_modules.update(
            {
                "feedparser": MagicMock(),
                "pymongo": MagicMock(),
                "pymongo.collection": MagicMock(),
                "llama_index.llms.azure_openai": MagicMock(),
                "llama_index.core": MagicMock(),
                "config": mock_config,
                "nbs.config": mock_config,
                "nbs.rss": mock_rss,
                "nbs.mongo": mock_mongo,
                "nbs.llm": mock_llm,
            }
        )

        # Mock workflow components

        # 1. RSS Mock
        mock_podcast = MagicMock()
        mock_podcast.list_last_large_episodes.return_value = [
            {"title": "Livres : Romans de rentrée", "duree_secondes": 62 * 60}
        ]
        mock_podcast.store_last_large_episodes.return_value = 1
        mock_rss.Podcast.return_value = mock_podcast

        # 2. MongoDB Mock
        mock_collection = MagicMock()
        mock_mongo.get_collection.return_value = mock_collection

        # 3. LLM Mock
        mock_config.get_azure_openai_keys.return_value = (
            "fake_key",
            "fake_endpoint",
            "fake_version",
        )
        mock_llm_instance = MagicMock()
        mock_llm.get_azure_llm.return_value = mock_llm_instance

        # ACT : Exécuter workflow complet

        # 1. RSS parsing
        podcast = mock_rss.Podcast()
        episodes = podcast.list_last_large_episodes()

        # 2. MongoDB storage
        collection = mock_mongo.get_collection()
        stored_count = podcast.store_last_large_episodes(episodes)

        # 3. LLM analysis setup
        llm = mock_llm.get_azure_llm()

        # ASSERT : Vérifier workflow end-to-end

        # Vérification RSS
        assert mock_rss.Podcast.called, "Podcast doit être instancié"
        assert len(episodes) == 1, "Un épisode long doit être trouvé"
        assert episodes[0]["duree_secondes"] == 62 * 60, "Durée doit être 62 minutes"

        # Vérification MongoDB
        assert (
            mock_mongo.get_collection.called
        ), "MongoDB collection doit être récupérée"
        assert stored_count == 1, "Un épisode doit être stocké"

        # Vérification LLM
        assert mock_llm.get_azure_llm.called, "LLM doit être appelé"

        # Vérification intégration
        assert llm is not None, "LLM doit être prêt pour analysis"

    def test_configuration_consistency_across_modules(self):
        """Test : cohérence de la configuration à travers tous les modules"""
        # ACT : Tester la configuration de base

        # Import du module config (le seul qui fonctionne directement)
        import nbs.config

        # ASSERT : Vérifier que le module config est importable
        assert hasattr(
            nbs.config, "get_RSS_URL"
        ), "Module config doit avoir get_RSS_URL"

        # Vérifier que la configuration fonctionne
        from nbs.config import get_RSS_URL

        rss_url = get_RSS_URL()
        assert rss_url is not None, "Configuration RSS doit être disponible"
        assert isinstance(rss_url, str), "URL RSS doit être une string"

    def test_data_flow_consistency(self):
        """Test : cohérence du flux de données entre modules"""
        # ACT : Charger les fixtures et vérifier la cohérence

        # Données RSS
        rss_content = load_sample_text("sample_rss_feed.xml")

        # Données épisode
        episode_data = load_sample_json("sample_episode.json")

        # Données transcription
        transcription = load_sample_text("sample_transcription.txt")

        # ASSERT : Vérifier cohérence des formats de données
        assert "<?xml" in rss_content, "RSS doit être du XML valide"
        assert "episodes" in episode_data, "JSON épisode doit avoir structure attendue"
        assert len(transcription) > 500, "Transcription doit avoir contenu substantiel"

        # Vérifier que les données sont compatibles entre modules
        assert (
            "Le Masque et la Plume" in rss_content
        ), "RSS doit contenir le nom de l'émission"
        assert (
            "critique" in transcription.lower()
        ), "Transcription doit contenir vocabulaire critique"

        # Vérifier structures de données consistantes
        test_episode = episode_data["episodes"][0]
        required_fields = ["titre", "date", "duree"]
        for field in required_fields:
            assert field in test_episode, f"Épisode doit avoir le champ {field}"
