"""Tests pour le module nbs.llm"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys

# Mock des modules externes AVANT l'import de nbs.llm
sys.modules["config"] = MagicMock()
sys.modules["config"].get_azure_openai_keys.return_value = (
    "test-key",
    "test-endpoint",
    "test-version",
)
sys.modules["config"].get_gemini_api_key.return_value = "test-gemini-key"
sys.modules["config"].get_google_projectID.return_value = "test-project-id"
sys.modules["config"].get_google_auth_file.return_value = "/path/to/auth.json"

sys.modules["llama_index.llms.azure_openai"] = MagicMock()
sys.modules["llama_index.core"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()
sys.modules["llama_index.llms.vertex"] = MagicMock()
sys.modules["google.oauth2.service_account"] = MagicMock()


class TestAzureLLM:
    """Tests pour la fonction get_azure_llm"""

    def test_get_azure_llm_default_engine(self, monkeypatch):
        """Test get_azure_llm avec moteur par défaut"""
        # ARRANGE : Mock des dépendances
        mock_azure_openai = MagicMock()
        mock_azure_instance = MagicMock()
        mock_azure_openai.return_value = mock_azure_instance
        mock_settings = MagicMock()
        mock_get_keys = MagicMock()
        mock_get_keys.return_value = ("test-key", "test-endpoint", "test-version")

        monkeypatch.setattr("nbs.llm.AzureOpenAI", mock_azure_openai)
        monkeypatch.setattr("nbs.llm.Settings", mock_settings)
        monkeypatch.setattr("nbs.llm.get_azure_openai_keys", mock_get_keys)

        # ACT : Appeler get_azure_llm
        from nbs.llm import get_azure_llm

        result = get_azure_llm()

        # ASSERT : Vérifier la configuration Azure OpenAI
        mock_azure_openai.assert_called_once_with(
            engine="gpt-4o",
            api_key="test-key",
            azure_endpoint="test-endpoint",
            api_version="test-version",
            timeout=300.0,
        )
        assert mock_settings.llm == mock_azure_instance
        assert result == mock_azure_instance

    def test_get_azure_llm_custom_engine(self, monkeypatch):
        """Test get_azure_llm avec moteur personnalisé"""
        # ARRANGE
        mock_azure_openai = MagicMock()
        mock_azure_instance = MagicMock()
        mock_azure_openai.return_value = mock_azure_instance
        mock_settings = MagicMock()
        mock_get_keys = MagicMock()
        mock_get_keys.return_value = ("test-key", "test-endpoint", "test-version")

        monkeypatch.setattr("nbs.llm.AzureOpenAI", mock_azure_openai)
        monkeypatch.setattr("nbs.llm.Settings", mock_settings)
        monkeypatch.setattr("nbs.llm.get_azure_openai_keys", mock_get_keys)

        # ACT
        from nbs.llm import get_azure_llm

        result = get_azure_llm("gpt-3.5-turbo")

        # ASSERT
        mock_azure_openai.assert_called_once_with(
            engine="gpt-3.5-turbo",
            api_key="test-key",
            azure_endpoint="test-endpoint",
            api_version="test-version",
            timeout=300.0,
        )
        assert result == mock_azure_instance

    def test_get_azure_llm_config_keys_called(self, monkeypatch):
        """Test que get_azure_openai_keys est appelé"""
        # ARRANGE
        mock_get_keys = MagicMock()
        mock_get_keys.return_value = ("custom-key", "custom-endpoint", "custom-version")
        mock_azure_openai = MagicMock()
        mock_settings = MagicMock()

        monkeypatch.setattr("nbs.llm.get_azure_openai_keys", mock_get_keys)
        monkeypatch.setattr("nbs.llm.AzureOpenAI", mock_azure_openai)
        monkeypatch.setattr("nbs.llm.Settings", mock_settings)

        # ACT
        from nbs.llm import get_azure_llm

        get_azure_llm()

        # ASSERT
        mock_get_keys.assert_called_once()

    def test_get_azure_llm_returns_azure_openai_instance(self, monkeypatch):
        """Test que get_azure_llm retourne une instance AzureOpenAI"""
        # ARRANGE
        mock_azure_openai = MagicMock()
        mock_instance = MagicMock()
        mock_azure_openai.return_value = mock_instance
        mock_settings = MagicMock()
        mock_get_keys = MagicMock()
        mock_get_keys.return_value = ("test-key", "test-endpoint", "test-version")

        monkeypatch.setattr("nbs.llm.AzureOpenAI", mock_azure_openai)
        monkeypatch.setattr("nbs.llm.Settings", mock_settings)
        monkeypatch.setattr("nbs.llm.get_azure_openai_keys", mock_get_keys)

        # ACT
        from nbs.llm import get_azure_llm

        result = get_azure_llm()

        # ASSERT
        assert result == mock_instance

    def test_get_azure_llm_timeout_configuration(self, monkeypatch):
        """Test que le timeout est configuré à 300 secondes"""
        # ARRANGE
        mock_azure_openai = MagicMock()
        mock_settings = MagicMock()
        mock_get_keys = MagicMock()
        mock_get_keys.return_value = ("test-key", "test-endpoint", "test-version")

        monkeypatch.setattr("nbs.llm.AzureOpenAI", mock_azure_openai)
        monkeypatch.setattr("nbs.llm.Settings", mock_settings)
        monkeypatch.setattr("nbs.llm.get_azure_openai_keys", mock_get_keys)

        # ACT
        from nbs.llm import get_azure_llm

        get_azure_llm()

        # ASSERT
        call_args = mock_azure_openai.call_args[1]
        assert call_args["timeout"] == 300.0


class TestGeminiLLM:
    """Tests pour la fonction get_gemini_llm"""

    def test_get_gemini_llm_default_model(self, monkeypatch):
        """Test get_gemini_llm avec modèle par défaut"""
        # ARRANGE : Mock des dépendances
        mock_genai = MagicMock()
        mock_generative_model = MagicMock()
        mock_model_instance = MagicMock()
        mock_generative_model.return_value = mock_model_instance
        mock_get_gemini_key = MagicMock()
        mock_get_gemini_key.return_value = "test-gemini-key"

        monkeypatch.setattr("nbs.llm.genai", mock_genai)
        monkeypatch.setattr("nbs.llm.genai.GenerativeModel", mock_generative_model)
        monkeypatch.setattr("nbs.llm.get_gemini_api_key", mock_get_gemini_key)

        # ACT : Appeler get_gemini_llm
        from nbs.llm import get_gemini_llm

        result = get_gemini_llm()

        # ASSERT : Vérifier la configuration Gemini
        mock_genai.configure.assert_called_once_with(api_key="test-gemini-key")
        mock_generative_model.assert_called_once_with("gemini-1.5-flash")
        assert result == mock_model_instance

    def test_get_gemini_llm_custom_model(self, monkeypatch):
        """Test get_gemini_llm avec modèle personnalisé"""
        # ARRANGE
        mock_genai = MagicMock()
        mock_generative_model = MagicMock()
        mock_model_instance = MagicMock()
        mock_generative_model.return_value = mock_model_instance
        mock_get_gemini_key = MagicMock()
        mock_get_gemini_key.return_value = "test-gemini-key"

        monkeypatch.setattr("nbs.llm.genai", mock_genai)
        monkeypatch.setattr("nbs.llm.genai.GenerativeModel", mock_generative_model)
        monkeypatch.setattr("nbs.llm.get_gemini_api_key", mock_get_gemini_key)

        # ACT
        from nbs.llm import get_gemini_llm

        result = get_gemini_llm("gemini-1.5-pro")

        # ASSERT
        mock_generative_model.assert_called_once_with("gemini-1.5-pro")
        assert result == mock_model_instance

    def test_get_gemini_llm_api_key_called(self, monkeypatch):
        """Test que get_gemini_api_key est appelé"""
        # ARRANGE
        mock_genai = MagicMock()
        mock_generative_model = MagicMock()
        mock_get_gemini_key = MagicMock()
        mock_get_gemini_key.return_value = "custom-gemini-key"

        monkeypatch.setattr("nbs.llm.genai", mock_genai)
        monkeypatch.setattr("nbs.llm.genai.GenerativeModel", mock_generative_model)
        monkeypatch.setattr("nbs.llm.get_gemini_api_key", mock_get_gemini_key)

        # ACT
        from nbs.llm import get_gemini_llm

        get_gemini_llm()

        # ASSERT
        mock_get_gemini_key.assert_called_once()
        mock_genai.configure.assert_called_once_with(api_key="custom-gemini-key")

    def test_get_gemini_llm_returns_generative_model(self, monkeypatch):
        """Test que get_gemini_llm retourne une instance GenerativeModel"""
        # ARRANGE
        mock_genai = MagicMock()
        mock_generative_model = MagicMock()
        mock_instance = MagicMock()
        mock_generative_model.return_value = mock_instance
        mock_get_gemini_key = MagicMock()

        monkeypatch.setattr("nbs.llm.genai", mock_genai)
        monkeypatch.setattr("nbs.llm.genai.GenerativeModel", mock_generative_model)
        monkeypatch.setattr("nbs.llm.get_gemini_api_key", mock_get_gemini_key)

        # ACT
        from nbs.llm import get_gemini_llm

        result = get_gemini_llm()

        # ASSERT
        assert result == mock_instance

    def test_get_gemini_llm_configure_before_model_creation(self, monkeypatch):
        """Test que genai.configure est appelé avant la création du modèle"""
        # ARRANGE
        mock_genai = MagicMock()
        mock_generative_model = MagicMock()
        mock_get_gemini_key = MagicMock()
        mock_get_gemini_key.return_value = "test-key"

        # Utilisation d'un gestionnaire d'appels pour vérifier l'ordre
        call_order = []

        def configure_side_effect(*args, **kwargs):
            call_order.append("configure")

        def model_side_effect(*args, **kwargs):
            call_order.append("model")
            return MagicMock()

        mock_genai.configure.side_effect = configure_side_effect
        mock_generative_model.side_effect = model_side_effect

        monkeypatch.setattr("nbs.llm.genai", mock_genai)
        monkeypatch.setattr("nbs.llm.genai.GenerativeModel", mock_generative_model)
        monkeypatch.setattr("nbs.llm.get_gemini_api_key", mock_get_gemini_key)

        # ACT
        from nbs.llm import get_gemini_llm

        get_gemini_llm()

        # ASSERT
        assert call_order == ["configure", "model"]


class TestVertexLLM:
    """Tests pour la fonction get_vertex_llm"""

    def test_get_vertex_llm_default_model(self, monkeypatch):
        """Test get_vertex_llm avec modèle par défaut"""
        # ARRANGE : Mock des dépendances
        mock_vertex = MagicMock()
        mock_vertex_instance = MagicMock()
        mock_vertex.return_value = mock_vertex_instance
        mock_settings = MagicMock()
        mock_get_project_id = MagicMock()
        mock_get_project_id.return_value = "test-project"
        mock_get_gemini_key = MagicMock()
        mock_get_gemini_key.return_value = "test-api-key"

        monkeypatch.setattr("nbs.llm.Vertex", mock_vertex)
        monkeypatch.setattr("nbs.llm.Settings", mock_settings)
        monkeypatch.setattr("nbs.llm.get_google_projectID", mock_get_project_id)
        monkeypatch.setattr("nbs.llm.get_gemini_api_key", mock_get_gemini_key)

        # ACT : Appeler get_vertex_llm
        from nbs.llm import get_vertex_llm

        result = get_vertex_llm()

        # ASSERT : Vérifier la configuration Vertex AI
        expected_credentials = {
            "project_id": "test-project",
            "api_key": "test-api-key",
        }
        mock_vertex.assert_called_once_with(
            model="gemini-1.5-flash-001",
            project="test-project",
            credentials=expected_credentials,
            context_window=100000,
        )
        assert mock_settings.llm == mock_vertex_instance
        assert result == mock_vertex_instance

    def test_get_vertex_llm_custom_model(self, monkeypatch):
        """Test get_vertex_llm avec modèle personnalisé"""
        # ARRANGE
        mock_vertex = MagicMock()
        mock_vertex_instance = MagicMock()
        mock_vertex.return_value = mock_vertex_instance
        mock_settings = MagicMock()
        mock_get_project_id = MagicMock()
        mock_get_project_id.return_value = "test-project"
        mock_get_gemini_key = MagicMock()
        mock_get_gemini_key.return_value = "test-api-key"

        monkeypatch.setattr("nbs.llm.Vertex", mock_vertex)
        monkeypatch.setattr("nbs.llm.Settings", mock_settings)
        monkeypatch.setattr("nbs.llm.get_google_projectID", mock_get_project_id)
        monkeypatch.setattr("nbs.llm.get_gemini_api_key", mock_get_gemini_key)

        # ACT
        from nbs.llm import get_vertex_llm

        result = get_vertex_llm("gemini-1.5-pro-001")

        # ASSERT
        call_args = mock_vertex.call_args[1]
        assert call_args["model"] == "gemini-1.5-pro-001"
        assert result == mock_vertex_instance

    def test_get_vertex_llm_credentials_structure(self, monkeypatch):
        """Test que les credentials sont structurés correctement"""
        # ARRANGE
        mock_vertex = MagicMock()
        mock_settings = MagicMock()
        mock_get_project_id = MagicMock()
        mock_get_project_id.return_value = "custom-project-id"
        mock_get_gemini_key = MagicMock()
        mock_get_gemini_key.return_value = "custom-api-key"

        monkeypatch.setattr("nbs.llm.Vertex", mock_vertex)
        monkeypatch.setattr("nbs.llm.Settings", mock_settings)
        monkeypatch.setattr("nbs.llm.get_google_projectID", mock_get_project_id)
        monkeypatch.setattr("nbs.llm.get_gemini_api_key", mock_get_gemini_key)

        # ACT
        from nbs.llm import get_vertex_llm

        get_vertex_llm()

        # ASSERT
        call_args = mock_vertex.call_args[1]
        expected_credentials = {
            "project_id": "custom-project-id",
            "api_key": "custom-api-key",
        }
        assert call_args["credentials"] == expected_credentials
        assert call_args["project"] == "custom-project-id"

    def test_get_vertex_llm_context_window_configuration(self, monkeypatch):
        """Test que le context_window est configuré à 100000"""
        # ARRANGE
        mock_vertex = MagicMock()
        mock_settings = MagicMock()
        mock_get_project_id = MagicMock()
        mock_get_gemini_key = MagicMock()

        monkeypatch.setattr("nbs.llm.Vertex", mock_vertex)
        monkeypatch.setattr("nbs.llm.Settings", mock_settings)
        monkeypatch.setattr("nbs.llm.get_google_projectID", mock_get_project_id)
        monkeypatch.setattr("nbs.llm.get_gemini_api_key", mock_get_gemini_key)

        # ACT
        from nbs.llm import get_vertex_llm

        get_vertex_llm()

        # ASSERT
        call_args = mock_vertex.call_args[1]
        assert call_args["context_window"] == 100000

    def test_get_vertex_llm_config_functions_called(self, monkeypatch):
        """Test que les fonctions de configuration sont appelées"""
        # ARRANGE
        mock_vertex = MagicMock()
        mock_settings = MagicMock()
        mock_get_project_id = MagicMock()
        mock_get_project_id.return_value = "test-project"
        mock_get_gemini_key = MagicMock()
        mock_get_gemini_key.return_value = "test-key"

        monkeypatch.setattr("nbs.llm.Vertex", mock_vertex)
        monkeypatch.setattr("nbs.llm.Settings", mock_settings)
        monkeypatch.setattr("nbs.llm.get_google_projectID", mock_get_project_id)
        monkeypatch.setattr("nbs.llm.get_gemini_api_key", mock_get_gemini_key)

        # ACT
        from nbs.llm import get_vertex_llm

        get_vertex_llm()

        # ASSERT
        mock_get_project_id.assert_called_once()
        mock_get_gemini_key.assert_called_once()

    def test_get_vertex_llm_returns_vertex_instance(self, monkeypatch):
        """Test que get_vertex_llm retourne une instance Vertex"""
        # ARRANGE
        mock_vertex = MagicMock()
        mock_instance = MagicMock()
        mock_vertex.return_value = mock_instance
        mock_settings = MagicMock()
        mock_get_project_id = MagicMock()
        mock_get_gemini_key = MagicMock()

        monkeypatch.setattr("nbs.llm.Vertex", mock_vertex)
        monkeypatch.setattr("nbs.llm.Settings", mock_settings)
        monkeypatch.setattr("nbs.llm.get_google_projectID", mock_get_project_id)
        monkeypatch.setattr("nbs.llm.get_gemini_api_key", mock_get_gemini_key)

        # ACT
        from nbs.llm import get_vertex_llm

        result = get_vertex_llm()

        # ASSERT
        assert result == mock_instance


class TestLLMModuleIntegration:
    """Tests d'intégration pour le module LLM"""

    def test_all_functions_available_in_module(self):
        """Test que toutes les fonctions publiques sont disponibles"""
        # ACT
        from nbs import llm

        # ASSERT
        assert hasattr(llm, "get_azure_llm")
        assert hasattr(llm, "get_gemini_llm")
        assert hasattr(llm, "get_vertex_llm")

    def test_module_all_exports(self):
        """Test que __all__ contient les bonnes exportations"""
        # ACT
        from nbs import llm

        # ASSERT
        expected_exports = ["get_azure_llm", "get_gemini_llm", "get_vertex_llm"]
        assert llm.__all__ == expected_exports

    def test_functions_are_callable(self, monkeypatch):
        """Test que toutes les fonctions sont appelables"""
        # ARRANGE : Mock minimal pour éviter les erreurs d'import
        monkeypatch.setattr("nbs.llm.AzureOpenAI", MagicMock())
        monkeypatch.setattr("nbs.llm.Settings", MagicMock())
        monkeypatch.setattr("nbs.llm.genai", MagicMock())
        monkeypatch.setattr("nbs.llm.genai.GenerativeModel", MagicMock())
        monkeypatch.setattr("nbs.llm.Vertex", MagicMock())
        monkeypatch.setattr(
            "nbs.llm.get_azure_openai_keys",
            MagicMock(return_value=("key", "endpoint", "version")),
        )
        monkeypatch.setattr("nbs.llm.get_gemini_api_key", MagicMock(return_value="key"))
        monkeypatch.setattr(
            "nbs.llm.get_google_projectID", MagicMock(return_value="project")
        )

        # ACT & ASSERT
        from nbs.llm import get_azure_llm, get_gemini_llm, get_vertex_llm

        assert callable(get_azure_llm)
        assert callable(get_gemini_llm)
        assert callable(get_vertex_llm)


class TestLLMErrorHandling:
    """Tests de gestion d'erreur pour le module LLM"""

    def test_azure_llm_with_missing_config(self, monkeypatch):
        """Test que get_azure_llm gère les erreurs de configuration"""
        # ARRANGE : Mock qui lève une exception
        mock_get_keys = MagicMock()
        mock_get_keys.side_effect = Exception("Configuration manquante")

        monkeypatch.setattr("nbs.llm.get_azure_openai_keys", mock_get_keys)

        # ACT & ASSERT
        from nbs.llm import get_azure_llm

        with pytest.raises(Exception, match="Configuration manquante"):
            get_azure_llm()

    def test_gemini_llm_with_missing_api_key(self, monkeypatch):
        """Test que get_gemini_llm gère les erreurs de clé API"""
        # ARRANGE : Mock qui lève une exception
        mock_get_key = MagicMock()
        mock_get_key.side_effect = Exception("Clé API manquante")

        monkeypatch.setattr("nbs.llm.get_gemini_api_key", mock_get_key)

        # ACT & ASSERT
        from nbs.llm import get_gemini_llm

        with pytest.raises(Exception, match="Clé API manquante"):
            get_gemini_llm()

    def test_vertex_llm_with_missing_project_id(self, monkeypatch):
        """Test que get_vertex_llm gère les erreurs de projet ID"""
        # ARRANGE : Mock qui lève une exception
        mock_get_project = MagicMock()
        mock_get_project.side_effect = Exception("Project ID manquant")
        mock_get_key = MagicMock()
        mock_get_key.return_value = "test-key"

        monkeypatch.setattr("nbs.llm.get_google_projectID", mock_get_project)
        monkeypatch.setattr("nbs.llm.get_gemini_api_key", mock_get_key)

        # ACT & ASSERT
        from nbs.llm import get_vertex_llm

        with pytest.raises(Exception, match="Project ID manquant"):
            get_vertex_llm()
