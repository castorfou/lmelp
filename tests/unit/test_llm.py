"""
Tests pour le module nbs/llm.py (T018)
Testing complet des fonctions LLM avec mocking des APIs externes
"""

import pytest
from unittest.mock import patch, MagicMock, call
import sys
import os


# Mock all external dependencies at module level
@pytest.fixture(autouse=True)
def mock_external_imports():
    """Mock toutes les dépendances externes automatiquement pour tous les tests"""
    with patch.dict(
        "sys.modules",
        {
            "google": MagicMock(),
            "google.generativeai": MagicMock(),
            "google.oauth2": MagicMock(),
            "google.oauth2.service_account": MagicMock(),
            "llama_index": MagicMock(),
            "llama_index.llms": MagicMock(),
            "llama_index.llms.azure_openai": MagicMock(),
            "llama_index.llms.vertex": MagicMock(),
            "llama_index.core": MagicMock(),
        },
    ):
        yield


# Configuration du path pour importer nos modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../nbs"))


class TestAzureLLM:
    """Tests pour la fonction get_azure_llm"""

    @patch("llm.Settings")
    @patch("llm.AzureOpenAI")
    @patch("llm.get_azure_openai_keys")
    def test_get_azure_llm_default_engine(
        self, mock_get_keys, mock_azure_openai, mock_settings
    ):
        """Test get_azure_llm avec engine par défaut"""
        # Import du module après le mocking
        from llm import get_azure_llm

        # Arrange
        mock_get_keys.return_value = (
            "test-key",
            "https://test.openai.azure.com",
            "2024-02-15-preview",
        )
        mock_llm_instance = MagicMock()
        mock_azure_openai.return_value = mock_llm_instance

        # Act
        result = get_azure_llm()

        # Assert
        assert result == mock_llm_instance
        mock_get_keys.assert_called_once()
        mock_azure_openai.assert_called_once_with(
            engine="gpt-4o",
            api_key="test-key",
            azure_endpoint="https://test.openai.azure.com",
            api_version="2024-02-15-preview",
            timeout=300.0,
        )
        assert mock_settings.llm == mock_llm_instance

    @patch("llm.Settings")
    @patch("llm.AzureOpenAI")
    @patch("llm.get_azure_openai_keys")
    def test_get_azure_llm_custom_engine(
        self, mock_get_keys, mock_azure_openai, mock_settings
    ):
        """Test get_azure_llm avec engine personnalisé"""
        # Import du module après le mocking
        from llm import get_azure_llm

        # Arrange
        mock_get_keys.return_value = (
            "test-key",
            "https://test.openai.azure.com",
            "2024-02-15-preview",
        )
        mock_llm_instance = MagicMock()
        mock_azure_openai.return_value = mock_llm_instance

        # Act
        result = get_azure_llm(engine="gpt-3.5-turbo")

        # Assert
        assert result == mock_llm_instance
        mock_azure_openai.assert_called_once_with(
            engine="gpt-3.5-turbo",
            api_key="test-key",
            azure_endpoint="https://test.openai.azure.com",
            api_version="2024-02-15-preview",
            timeout=300.0,
        )

    @patch("llm.Settings")
    @patch("llm.AzureOpenAI")
    @patch("llm.get_azure_openai_keys")
    def test_get_azure_llm_with_error(
        self, mock_get_keys, mock_azure_openai, mock_settings
    ):
        """Test get_azure_llm avec erreur lors de la configuration"""
        # Import du module après le mocking
        from llm import get_azure_llm

        # Arrange
        mock_get_keys.side_effect = Exception("Configuration error")

        # Act & Assert
        with pytest.raises(Exception, match="Configuration error"):
            get_azure_llm()

    @patch("llm.Settings")
    @patch("llm.AzureOpenAI")
    @patch("llm.get_azure_openai_keys")
    def test_get_azure_llm_sets_global_settings(
        self, mock_get_keys, mock_azure_openai, mock_settings
    ):
        """Test que get_azure_llm configure Settings.llm globalement"""
        # Import du module après le mocking
        from llm import get_azure_llm

        # Arrange
        mock_get_keys.return_value = (
            "test-key",
            "https://test.openai.azure.com",
            "2024-02-15-preview",
        )
        mock_llm_instance = MagicMock()
        mock_azure_openai.return_value = mock_llm_instance

        # Act
        result = get_azure_llm()

        # Assert
        assert mock_settings.llm == mock_llm_instance


class TestGeminiLLM:
    """Tests pour la fonction get_gemini_llm"""

    @patch("llm.genai.GenerativeModel")
    @patch("llm.genai.configure")
    @patch("llm.get_gemini_api_key")
    def test_get_gemini_llm_default_model(
        self, mock_get_key, mock_configure, mock_model_class
    ):
        """Test get_gemini_llm avec modèle par défaut"""
        # Import du module après le mocking
        from llm import get_gemini_llm

        # Arrange
        mock_get_key.return_value = "test-gemini-key"
        mock_model_instance = MagicMock()
        mock_model_class.return_value = mock_model_instance

        # Act
        result = get_gemini_llm()

        # Assert
        assert result == mock_model_instance
        mock_get_key.assert_called_once()
        mock_configure.assert_called_once_with(api_key="test-gemini-key")
        mock_model_class.assert_called_once_with("gemini-1.5-flash")

    @patch("llm.genai.GenerativeModel")
    @patch("llm.genai.configure")
    @patch("llm.get_gemini_api_key")
    def test_get_gemini_llm_custom_model(
        self, mock_get_key, mock_configure, mock_model_class
    ):
        """Test get_gemini_llm avec modèle personnalisé"""
        # Import du module après le mocking
        from llm import get_gemini_llm

        # Arrange
        mock_get_key.return_value = "test-gemini-key"
        mock_model_instance = MagicMock()
        mock_model_class.return_value = mock_model_instance

        # Act
        result = get_gemini_llm(model="gemini-1.5-pro")

        # Assert
        assert result == mock_model_instance
        mock_configure.assert_called_once_with(api_key="test-gemini-key")
        mock_model_class.assert_called_once_with("gemini-1.5-pro")

    @patch("llm.genai.GenerativeModel")
    @patch("llm.genai.configure")
    @patch("llm.get_gemini_api_key")
    def test_get_gemini_llm_with_error(
        self, mock_get_key, mock_configure, mock_model_class
    ):
        """Test get_gemini_llm avec erreur lors de la configuration"""
        # Import du module après le mocking
        from llm import get_gemini_llm

        # Arrange
        mock_get_key.side_effect = Exception("API key error")

        # Act & Assert
        with pytest.raises(Exception, match="API key error"):
            get_gemini_llm()

    @patch("llm.genai.GenerativeModel")
    @patch("llm.genai.configure")
    @patch("llm.get_gemini_api_key")
    def test_get_gemini_llm_configure_called_first(
        self, mock_get_key, mock_configure, mock_model_class
    ):
        """Test que genai.configure est appelé avant GenerativeModel"""
        # Import du module après le mocking
        from llm import get_gemini_llm

        # Arrange
        mock_get_key.return_value = "test-gemini-key"
        mock_model_instance = MagicMock()
        mock_model_class.return_value = mock_model_instance

        # Track call order
        call_order = []
        mock_configure.side_effect = lambda **kwargs: call_order.append("configure")
        mock_model_class.side_effect = lambda model: (
            call_order.append("model"),
            mock_model_instance,
        )[1]

        # Act
        result = get_gemini_llm()

        # Assert
        assert call_order == ["configure", "model"]


class TestVertexLLM:
    """Tests pour la fonction get_vertex_llm"""

    @patch("llm.Settings")
    @patch("llm.Vertex")
    @patch("llm.get_google_projectID")
    @patch("llm.get_gemini_api_key")
    def test_get_vertex_llm_default_model(
        self, mock_get_key, mock_get_project, mock_vertex, mock_settings
    ):
        """Test get_vertex_llm avec modèle par défaut"""
        # Import du module après le mocking
        from llm import get_vertex_llm

        # Arrange
        mock_get_key.return_value = "test-gemini-key"
        mock_get_project.return_value = "test-project-id"
        mock_llm_instance = MagicMock()
        mock_vertex.return_value = mock_llm_instance

        # Act
        result = get_vertex_llm()

        # Assert
        assert result == mock_llm_instance
        mock_get_key.assert_called_once()
        mock_get_project.assert_called_once()
        mock_vertex.assert_called_once_with(
            model="gemini-1.5-flash-001",
            project="test-project-id",
            credentials={"project_id": "test-project-id", "api_key": "test-gemini-key"},
            context_window=100000,
        )
        assert mock_settings.llm == mock_llm_instance

    @patch("llm.Settings")
    @patch("llm.Vertex")
    @patch("llm.get_google_projectID")
    @patch("llm.get_gemini_api_key")
    def test_get_vertex_llm_custom_model(
        self, mock_get_key, mock_get_project, mock_vertex, mock_settings
    ):
        """Test get_vertex_llm avec modèle personnalisé"""
        # Import du module après le mocking
        from llm import get_vertex_llm

        # Arrange
        mock_get_key.return_value = "test-gemini-key"
        mock_get_project.return_value = "test-project-id"
        mock_llm_instance = MagicMock()
        mock_vertex.return_value = mock_llm_instance

        # Act
        result = get_vertex_llm(model="gemini-1.5-pro-001")

        # Assert
        assert result == mock_llm_instance
        mock_vertex.assert_called_once_with(
            model="gemini-1.5-pro-001",
            project="test-project-id",
            credentials={"project_id": "test-project-id", "api_key": "test-gemini-key"},
            context_window=100000,
        )

    @patch("llm.Settings")
    @patch("llm.Vertex")
    @patch("llm.get_google_projectID")
    @patch("llm.get_gemini_api_key")
    def test_get_vertex_llm_with_error(
        self, mock_get_key, mock_get_project, mock_vertex, mock_settings
    ):
        """Test get_vertex_llm avec erreur lors de la configuration"""
        # Import du module après le mocking
        from llm import get_vertex_llm

        # Arrange
        mock_get_project.side_effect = Exception("Project ID error")

        # Act & Assert
        with pytest.raises(Exception, match="Project ID error"):
            get_vertex_llm()

    @patch("llm.Settings")
    @patch("llm.Vertex")
    @patch("llm.get_google_projectID")
    @patch("llm.get_gemini_api_key")
    def test_get_vertex_llm_credentials_structure(
        self, mock_get_key, mock_get_project, mock_vertex, mock_settings
    ):
        """Test que get_vertex_llm construit correctement la structure credentials"""
        # Import du module après le mocking
        from llm import get_vertex_llm

        # Arrange
        mock_get_key.return_value = "specific-api-key"
        mock_get_project.return_value = "specific-project"
        mock_llm_instance = MagicMock()
        mock_vertex.return_value = mock_llm_instance

        # Act
        result = get_vertex_llm()

        # Assert
        call_args = mock_vertex.call_args
        credentials = call_args[1]["credentials"]
        assert credentials["project_id"] == "specific-project"
        assert credentials["api_key"] == "specific-api-key"
        assert call_args[1]["context_window"] == 100000


class TestLLMIntegration:
    """Tests d'intégration pour les fonctions LLM"""

    @patch("llm.Settings")
    @patch("llm.AzureOpenAI")
    @patch("llm.get_azure_openai_keys")
    @patch("llm.genai.GenerativeModel")
    @patch("llm.genai.configure")
    @patch("llm.get_gemini_api_key")
    @patch("llm.Vertex")
    @patch("llm.get_google_projectID")
    def test_all_llm_functions_can_be_called(
        self,
        mock_get_project,
        mock_vertex,
        mock_get_gemini_key,
        mock_configure,
        mock_gemini_model,
        mock_get_azure_keys,
        mock_azure_openai,
        mock_settings,
    ):
        """Test que toutes les fonctions LLM peuvent être appelées sans erreur"""
        # Import du module après le mocking
        from llm import get_azure_llm, get_gemini_llm, get_vertex_llm

        # Arrange
        mock_get_azure_keys.return_value = (
            "azure-key",
            "https://azure.com",
            "2024-02-15",
        )
        mock_get_gemini_key.return_value = "gemini-key"
        mock_get_project.return_value = "project-id"

        mock_azure_instance = MagicMock()
        mock_gemini_instance = MagicMock()
        mock_vertex_instance = MagicMock()

        mock_azure_openai.return_value = mock_azure_instance
        mock_gemini_model.return_value = mock_gemini_instance
        mock_vertex.return_value = mock_vertex_instance

        # Act
        azure_result = get_azure_llm()
        gemini_result = get_gemini_llm()
        vertex_result = get_vertex_llm()

        # Assert
        assert azure_result == mock_azure_instance
        assert gemini_result == mock_gemini_instance
        assert vertex_result == mock_vertex_instance

        # Verify all functions were called
        mock_azure_openai.assert_called_once()
        mock_gemini_model.assert_called_once()
        mock_vertex.assert_called_once()

    @patch("llm.Settings")
    def test_azure_and_vertex_set_global_settings(self, mock_settings):
        """Test que Azure et Vertex LLM configurent Settings.llm mais pas Gemini"""
        # Import du module après le mocking
        from llm import get_azure_llm, get_gemini_llm, get_vertex_llm

        with patch("llm.AzureOpenAI") as mock_azure, patch(
            "llm.get_azure_openai_keys"
        ) as mock_azure_keys, patch("llm.genai.GenerativeModel") as mock_gemini, patch(
            "llm.genai.configure"
        ) as mock_configure, patch(
            "llm.get_gemini_api_key"
        ) as mock_gemini_key, patch(
            "llm.Vertex"
        ) as mock_vertex, patch(
            "llm.get_google_projectID"
        ) as mock_project:

            # Arrange
            mock_azure_keys.return_value = ("key", "endpoint", "version")
            mock_gemini_key.return_value = "gemini-key"
            mock_project.return_value = "project"

            mock_azure_instance = MagicMock()
            mock_gemini_instance = MagicMock()
            mock_vertex_instance = MagicMock()

            mock_azure.return_value = mock_azure_instance
            mock_gemini.return_value = mock_gemini_instance
            mock_vertex.return_value = mock_vertex_instance

            # Act
            get_azure_llm()
            # Vérifier que Settings.llm est défini pour Azure
            assert mock_settings.llm == mock_azure_instance

            get_gemini_llm()
            # Gemini ne change pas Settings.llm, donc toujours l'instance Azure
            assert mock_settings.llm == mock_azure_instance

            get_vertex_llm()
            # Vertex change Settings.llm
            assert mock_settings.llm == mock_vertex_instance


class TestLLMErrorHandling:
    """Tests de gestion d'erreurs pour les fonctions LLM"""

    @patch("llm.get_azure_openai_keys")
    def test_azure_llm_missing_config(self, mock_get_keys):
        """Test get_azure_llm avec configuration manquante"""
        # Import du module après le mocking
        from llm import get_azure_llm

        # Arrange
        mock_get_keys.return_value = (None, None, None)

        # Act & Assert
        with patch("llm.AzureOpenAI") as mock_azure:
            mock_azure.side_effect = Exception("Missing credentials")
            with pytest.raises(Exception, match="Missing credentials"):
                get_azure_llm()

    @patch("llm.get_gemini_api_key")
    def test_gemini_llm_missing_api_key(self, mock_get_key):
        """Test get_gemini_llm avec clé API manquante"""
        # Import du module après le mocking
        from llm import get_gemini_llm

        # Arrange
        mock_get_key.return_value = None

        # Act & Assert
        with patch("llm.genai.configure") as mock_configure:
            mock_configure.side_effect = Exception("Invalid API key")
            with pytest.raises(Exception, match="Invalid API key"):
                get_gemini_llm()

    @patch("llm.get_google_projectID")
    @patch("llm.get_gemini_api_key")
    def test_vertex_llm_missing_project(self, mock_get_key, mock_get_project):
        """Test get_vertex_llm avec project ID manquant"""
        # Import du module après le mocking
        from llm import get_vertex_llm

        # Arrange
        mock_get_key.return_value = "valid-key"
        mock_get_project.return_value = None

        # Act & Assert
        with patch("llm.Vertex") as mock_vertex:
            mock_vertex.side_effect = Exception("Missing project ID")
            with pytest.raises(Exception, match="Missing project ID"):
                get_vertex_llm()
