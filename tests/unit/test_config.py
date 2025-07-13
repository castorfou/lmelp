"""Tests pour nbs/config.py - Configuration et variables d'environnement"""

import pytest
import os
from nbs.config import get_RSS_URL


class TestConfig:
    """Tests pour les fonctions de nbs/config.py"""

    def test_get_RSS_URL_with_env_var(self, monkeypatch):
        """Test get_RSS_URL() quand RSS_LMELP_URL est définie"""
        # ARRANGE : Préparer
        test_url = "https://example.com/test-rss.xml"
        monkeypatch.setenv("RSS_LMELP_URL", test_url)

        # ACT : Exécuter
        result = get_RSS_URL()

        # ASSERT : Vérifier
        assert result == test_url

    def test_get_RSS_URL_without_env_var(self, monkeypatch):
        """Test get_RSS_URL() quand RSS_LMELP_URL n'est pas définie (valeur par défaut)"""
        # ARRANGE : Préparer (supprimer la variable si elle existe)
        monkeypatch.delenv("RSS_LMELP_URL", raising=False)

        # ACT : Exécuter
        result = get_RSS_URL()

        # ASSERT : Vérifier qu'on obtient l'URL par défaut
        expected_default = "https://radiofrance-podcast.net/podcast09/rss_14007.xml"
        assert result == expected_default

    def test_get_RSS_URL_returns_string(self):
        """Test que get_RSS_URL() retourne toujours une string non-vide"""
        # ACT : Exécuter
        result = get_RSS_URL()

        # ASSERT : Vérifier le type et la longueur
        assert isinstance(result, str)
        assert len(result) > 0
        assert result.startswith("https://")  # doit être une URL HTTPS
