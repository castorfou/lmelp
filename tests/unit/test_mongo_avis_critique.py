"""
Tests unitaires pour le module mongo_avis_critique

Ce module contient tous les tests pour la classe AvisCritique et ses méthodes.
Suit les patterns de test établis dans le projet.
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import TypeVar
from bson import ObjectId
import json
import os


# Import des fixtures de données
@pytest.fixture
def avis_critique_fixture_data():
    """Fixture pour charger les données de test des avis critiques"""
    fixture_path = "/workspaces/lmelp/tests/fixtures/data/avis_critique_data.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


@pytest.fixture
def mock_mongo_dependencies():
    """Fixture pour mocker les dépendances MongoDB et config"""
    # Mock pour config
    mock_config = MagicMock()
    mock_config.get_DB_VARS.return_value = ("localhost", "test_db", "logs")

    # Mock pour mongo
    mock_mongo = MagicMock()

    # Mock pour BaseEntity
    class MockBaseEntity:
        def __init__(self, nom, collection=None):
            self.nom = nom
            self.collection = collection

        def exists(self):
            return False

        def keep(self):
            pass

        def remove(self):
            pass

        def get_oid(self):
            return ObjectId()

        def to_dict(self):
            return {}

    mock_mongo.BaseEntity = MockBaseEntity
    mock_mongo.get_collection = MagicMock()

    with patch.dict(
        "sys.modules",
        {
            "mongo": mock_mongo,
            "config": mock_config,
        },
    ):
        yield


@pytest.fixture
def sample_avis_data(avis_critique_fixture_data):
    """Fixture pour un avis critique valide"""
    return avis_critique_fixture_data["valid_avis"][0]


@pytest.fixture
def truncated_avis_data(avis_critique_fixture_data):
    """Fixture pour un avis critique tronqué"""
    return avis_critique_fixture_data["truncated_avis"][0]


@pytest.fixture
def edge_case_avis_data(avis_critique_fixture_data):
    """Fixture pour un cas limite"""
    return avis_critique_fixture_data["edge_cases"][0]


class TestModuleConstants:
    """Tests pour les constantes et exports du module"""

    def test_module_exports(self):
        """Test des exports __all__ du module"""
        from nbs import mongo_avis_critique

        expected_exports = ["T", "AvisCritique"]

        # Assert
        assert mongo_avis_critique.__all__ == expected_exports

        # Verify all exports exist
        for export in expected_exports:
            assert hasattr(mongo_avis_critique, export), f"Missing export: {export}"

    def test_typevar_t(self):
        """Test du TypeVar T"""
        from nbs.mongo_avis_critique import T

        # Assert
        assert isinstance(T, type(TypeVar("test")))
        # Vérifier que T est bien bound à "AvisCritique" (en string ou ForwardRef)
        assert T.__bound__ is not None


@patch(
    "nbs.mongo_avis_critique.get_DB_VARS", return_value=("localhost", "test_db", "logs")
)
class TestAvisCritiqueClass:
    """Tests pour la classe AvisCritique"""

    def test_avis_critique_initialization(self, mock_get_db_vars, sample_avis_data):
        """Test d'initialisation d'un avis critique"""
        mock_collection = MagicMock()

        with patch(
            "nbs.mongo_avis_critique.get_collection", return_value=mock_collection
        ):
            from nbs.mongo_avis_critique import AvisCritique

            avis = AvisCritique(
                episode_id=sample_avis_data["episode_id"],
                entity_type=sample_avis_data["entity_type"],
                entity_name=sample_avis_data["entity_name"],
            )

            # Assert
            assert avis.episode_id == sample_avis_data["episode_id"]
            assert avis.entity_type == sample_avis_data["entity_type"]
            assert avis.entity_name == sample_avis_data["entity_name"]
            assert avis.summary_text is None
            assert avis.created_at is not None
            assert avis.updated_at is not None
            # Vérifier que l'objet a les attributs attendus
            assert hasattr(avis, "collection")
            assert hasattr(avis, "nom")  # Hérité de BaseEntity

    def test_avis_critique_with_summary(self, mock_get_db_vars, sample_avis_data):
        """Test d'initialisation avec summary_text"""
        mock_collection = MagicMock()

        with patch(
            "nbs.mongo_avis_critique.get_collection", return_value=mock_collection
        ):
            from nbs.mongo_avis_critique import AvisCritique

            avis = AvisCritique(
                episode_id=sample_avis_data["episode_id"],
                entity_type=sample_avis_data["entity_type"],
                entity_name=sample_avis_data["entity_name"],
                summary_text=sample_avis_data["summary_text"],
            )

            # Assert
            assert avis.summary_text == sample_avis_data["summary_text"]

    def test_avis_critique_nom_property(self, mock_get_db_vars, sample_avis_data):
        """Test que la propriété nom est correctement définie"""
        mock_collection = MagicMock()

        with patch(
            "nbs.mongo_avis_critique.get_collection", return_value=mock_collection
        ):
            from nbs.mongo_avis_critique import AvisCritique

            avis = AvisCritique(
                episode_id=sample_avis_data["episode_id"],
                entity_type=sample_avis_data["entity_type"],
                entity_name=sample_avis_data["entity_name"],
            )

            expected_nom = f"{sample_avis_data['entity_type']}_{sample_avis_data['entity_name']}_{sample_avis_data['episode_id']}"
            assert avis.nom == expected_nom


class TestAvisCritiqueValidation:
    """Tests pour les méthodes de validation d'AvisCritique"""

    @patch(
        "nbs.mongo_avis_critique.get_DB_VARS",
        return_value=("localhost", "test_db", "logs"),
    )
    def test_is_summary_truncated_valid(self, mock_get_db_vars, sample_avis_data):
        """Test détection d'un résumé non tronqué"""
        mock_collection = MagicMock()

        with patch(
            "nbs.mongo_avis_critique.get_collection", return_value=mock_collection
        ):
            from nbs.mongo_avis_critique import AvisCritique

            avis = AvisCritique(
                episode_id=sample_avis_data["episode_id"],
                entity_type=sample_avis_data["entity_type"],
                entity_name=sample_avis_data["entity_name"],
                summary_text=sample_avis_data["summary_text"],
            )

            # Assert
            assert not avis.is_summary_truncated()

    @patch(
        "nbs.mongo_avis_critique.get_DB_VARS",
        return_value=("localhost", "test_db", "logs"),
    )
    def test_is_summary_truncated_truncated(
        self, mock_get_db_vars, truncated_avis_data
    ):
        """Test détection d'un résumé tronqué"""
        mock_collection = MagicMock()

        with patch(
            "nbs.mongo_avis_critique.get_collection", return_value=mock_collection
        ):
            from nbs.mongo_avis_critique import AvisCritique

            avis = AvisCritique(
                episode_id=truncated_avis_data["episode_id"],
                entity_type=truncated_avis_data["entity_type"],
                entity_name=truncated_avis_data["entity_name"],
                summary_text=truncated_avis_data["summary_text"],
            )

            # Assert
            assert avis.is_summary_truncated()

    @patch(
        "nbs.mongo_avis_critique.get_DB_VARS",
        return_value=("localhost", "test_db", "logs"),
    )
    def test_is_summary_truncated_no_summary(self, mock_get_db_vars, sample_avis_data):
        """Test détection avec summary_text None"""
        mock_collection = MagicMock()

        with patch(
            "nbs.mongo_avis_critique.get_collection", return_value=mock_collection
        ):
            from nbs.mongo_avis_critique import AvisCritique

            avis = AvisCritique(
                episode_id=sample_avis_data["episode_id"],
                entity_type=sample_avis_data["entity_type"],
                entity_name=sample_avis_data["entity_name"],
            )

            # Assert - pas de summary text, donc pas tronqué
            assert not avis.is_summary_truncated()

    @patch(
        "nbs.mongo_avis_critique.get_DB_VARS",
        return_value=("localhost", "test_db", "logs"),
    )
    def test_debug_truncation_detection(self, mock_get_db_vars, truncated_avis_data):
        """Test des informations de debug pour la détection de troncature"""
        mock_collection = MagicMock()

        with patch(
            "nbs.mongo_avis_critique.get_collection", return_value=mock_collection
        ):
            from nbs.mongo_avis_critique import AvisCritique

            avis = AvisCritique(
                episode_id=truncated_avis_data["episode_id"],
                entity_type=truncated_avis_data["entity_type"],
                entity_name=truncated_avis_data["entity_name"],
                summary_text=truncated_avis_data["summary_text"],
            )

            debug_info = avis.debug_truncation_detection()

            # Assert
            assert "text_length" in debug_info
            assert "ends_with_truncation_pattern" in debug_info
            assert "truncation_patterns_found" in debug_info
            assert "is_truncated" in debug_info
            assert debug_info["is_truncated"] is True


class TestAvisCritiqueClassMethods:
    """Tests pour les méthodes de classe d'AvisCritique"""

    @patch(
        "nbs.mongo_avis_critique.get_DB_VARS",
        return_value=("localhost", "test_db", "logs"),
    )
    def test_from_oid_success(self, mock_get_db_vars, sample_avis_data):
        """Test from_oid() trouve un avis critique"""
        test_oid = ObjectId()
        mock_collection = MagicMock()

        mock_document = {
            "episode_id": sample_avis_data["episode_id"],
            "entity_type": sample_avis_data["entity_type"],
            "entity_name": sample_avis_data["entity_name"],
            "summary_text": sample_avis_data["summary_text"],
            "created_at": sample_avis_data["created_at"],
            "updated_at": sample_avis_data["updated_at"],
        }
        mock_collection.find_one.return_value = mock_document

        with patch(
            "nbs.mongo_avis_critique.get_collection", return_value=mock_collection
        ):
            from nbs.mongo_avis_critique import AvisCritique

            result = AvisCritique.from_oid(test_oid)

            # Assert
            assert result is not None
            assert result.episode_id == sample_avis_data["episode_id"]
            assert result.entity_type == sample_avis_data["entity_type"]
            assert result.entity_name == sample_avis_data["entity_name"]
            assert result.summary_text == sample_avis_data["summary_text"]
            mock_collection.find_one.assert_called_once_with({"_id": test_oid})

    @patch(
        "nbs.mongo_avis_critique.get_DB_VARS",
        return_value=("localhost", "test_db", "logs"),
    )
    def test_from_oid_not_found(self, mock_get_db_vars):
        """Test from_oid() ne trouve pas d'avis critique"""
        test_oid = ObjectId()
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None

        with patch(
            "nbs.mongo_avis_critique.get_collection", return_value=mock_collection
        ):
            from nbs.mongo_avis_critique import AvisCritique

            result = AvisCritique.from_oid(test_oid)

            # Assert
            assert result is None

    def test_from_oid_none_input(self):
        """Test from_oid() avec ObjectId None"""
        from nbs.mongo_avis_critique import AvisCritique

        result = AvisCritique.from_oid(None)

        # Assert
        assert result is None

    @patch(
        "nbs.mongo_avis_critique.get_DB_VARS",
        return_value=("localhost", "test_db", "logs"),
    )
    def test_find_by_episode_and_entity(self, mock_get_db_vars, sample_avis_data):
        """Test de recherche par episode_id et entité"""
        mock_collection = MagicMock()
        mock_documents = [
            {
                "episode_id": sample_avis_data["episode_id"],
                "entity_type": sample_avis_data["entity_type"],
                "entity_name": sample_avis_data["entity_name"],
                "summary_text": sample_avis_data["summary_text"],
                "created_at": sample_avis_data["created_at"],
                "updated_at": sample_avis_data["updated_at"],
            }
        ]
        mock_collection.find.return_value = mock_documents

        with patch(
            "nbs.mongo_avis_critique.get_collection", return_value=mock_collection
        ):
            from nbs.mongo_avis_critique import AvisCritique

            results = AvisCritique.find_by_episode_and_entity(
                episode_id=sample_avis_data["episode_id"],
                entity_type=sample_avis_data["entity_type"],
                entity_name=sample_avis_data["entity_name"],
            )

            # Assert
            assert len(results) == 1
            assert results[0].episode_id == sample_avis_data["episode_id"]
            assert results[0].entity_type == sample_avis_data["entity_type"]
            assert results[0].entity_name == sample_avis_data["entity_name"]

    @patch(
        "nbs.mongo_avis_critique.get_DB_VARS",
        return_value=("localhost", "test_db", "logs"),
    )
    def test_find_by_episode_id(self, mock_get_db_vars, sample_avis_data):
        """Test de recherche par episode_id seulement"""
        mock_collection = MagicMock()
        mock_documents = [
            {
                "episode_id": sample_avis_data["episode_id"],
                "entity_type": sample_avis_data["entity_type"],
                "entity_name": sample_avis_data["entity_name"],
                "summary_text": sample_avis_data["summary_text"],
                "created_at": sample_avis_data["created_at"],
                "updated_at": sample_avis_data["updated_at"],
            }
        ]
        mock_collection.find.return_value = mock_documents

        with patch(
            "nbs.mongo_avis_critique.get_collection", return_value=mock_collection
        ):
            from nbs.mongo_avis_critique import AvisCritique

            results = AvisCritique.find_by_episode_id(sample_avis_data["episode_id"])

            # Assert
            assert len(results) == 1
            assert results[0].episode_id == sample_avis_data["episode_id"]
            mock_collection.find.assert_called_once_with(
                {"episode_id": sample_avis_data["episode_id"]}
            )


class TestAvisCritiqueStringRepresentation:
    """Tests pour la représentation string d'AvisCritique"""

    @patch(
        "nbs.mongo_avis_critique.get_DB_VARS",
        return_value=("localhost", "test_db", "logs"),
    )
    def test_str_representation_with_summary(self, mock_get_db_vars, sample_avis_data):
        """Test __str__ avec summary_text"""
        mock_collection = MagicMock()

        with patch(
            "nbs.mongo_avis_critique.get_collection", return_value=mock_collection
        ):
            from nbs.mongo_avis_critique import AvisCritique

            avis = AvisCritique(
                episode_id=sample_avis_data["episode_id"],
                entity_type=sample_avis_data["entity_type"],
                entity_name=sample_avis_data["entity_name"],
                summary_text=sample_avis_data["summary_text"],
            )

            result = str(avis)

            # Assert
            assert sample_avis_data["entity_name"] in result
            assert sample_avis_data["entity_type"] in result
            assert sample_avis_data["episode_id"] in result
            assert "Episode:" in result
            assert "Entity:" in result
            assert "Summary:" in result

    @patch(
        "nbs.mongo_avis_critique.get_DB_VARS",
        return_value=("localhost", "test_db", "logs"),
    )
    def test_str_representation_without_summary(
        self, mock_get_db_vars, sample_avis_data
    ):
        """Test __str__ sans summary_text"""
        mock_collection = MagicMock()

        with patch(
            "nbs.mongo_avis_critique.get_collection", return_value=mock_collection
        ):
            from nbs.mongo_avis_critique import AvisCritique

            avis = AvisCritique(
                episode_id=sample_avis_data["episode_id"],
                entity_type=sample_avis_data["entity_type"],
                entity_name=sample_avis_data["entity_name"],
            )

            result = str(avis)

            # Assert
            assert sample_avis_data["entity_name"] in result
            assert sample_avis_data["entity_type"] in result
            assert sample_avis_data["episode_id"] in result
            assert "Summary: None" in result


class TestAvisCritiqueInheritedMethods:
    """Tests pour les méthodes héritées de BaseEntity"""

    @patch(
        "nbs.mongo_avis_critique.get_DB_VARS",
        return_value=("localhost", "test_db", "logs"),
    )
    def test_avis_critique_inherits_base_methods(
        self, mock_get_db_vars, sample_avis_data
    ):
        """Test qu'AvisCritique hérite correctement des méthodes de BaseEntity"""
        mock_collection = MagicMock()

        with patch(
            "nbs.mongo_avis_critique.get_collection", return_value=mock_collection
        ):
            from nbs.mongo_avis_critique import AvisCritique

            avis = AvisCritique(
                episode_id=sample_avis_data["episode_id"],
                entity_type=sample_avis_data["entity_type"],
                entity_name=sample_avis_data["entity_name"],
            )

            # Assert que les méthodes héritées existent
            assert hasattr(avis, "exists")
            assert hasattr(avis, "keep")
            assert hasattr(avis, "remove")
            assert hasattr(avis, "get_oid")
            assert hasattr(avis, "to_dict")

            # Assert que nom est hérité et correctement défini
            assert hasattr(avis, "nom")
            expected_nom = f"{sample_avis_data['entity_type']}_{sample_avis_data['entity_name']}_{sample_avis_data['episode_id']}"
            assert avis.nom == expected_nom


class TestAvisCritiqueEdgeCases:
    """Tests pour les cas limites d'AvisCritique"""

    @patch(
        "nbs.mongo_avis_critique.get_DB_VARS",
        return_value=("localhost", "test_db", "logs"),
    )
    def test_edge_case_empty_strings(self, mock_get_db_vars):
        """Test avec des chaînes vides"""
        mock_collection = MagicMock()

        with patch(
            "nbs.mongo_avis_critique.get_collection", return_value=mock_collection
        ):
            from nbs.mongo_avis_critique import AvisCritique

            avis = AvisCritique(episode_id="", entity_type="", entity_name="")

            # Assert
            assert avis.episode_id == ""
            assert avis.entity_type == ""
            assert avis.entity_name == ""
            assert avis.nom == "__"

    @patch(
        "nbs.mongo_avis_critique.get_DB_VARS",
        return_value=("localhost", "test_db", "logs"),
    )
    def test_edge_case_special_characters(self, mock_get_db_vars, edge_case_avis_data):
        """Test avec des caractères spéciaux"""
        mock_collection = MagicMock()

        with patch(
            "nbs.mongo_avis_critique.get_collection", return_value=mock_collection
        ):
            from nbs.mongo_avis_critique import AvisCritique

            avis = AvisCritique(
                episode_id=edge_case_avis_data["episode_id"],
                entity_type=edge_case_avis_data["entity_type"],
                entity_name=edge_case_avis_data["entity_name"],
                summary_text=edge_case_avis_data["summary_text"],
            )

            # Assert
            assert avis.episode_id == edge_case_avis_data["episode_id"]
            assert avis.entity_type == edge_case_avis_data["entity_type"]
            assert avis.entity_name == edge_case_avis_data["entity_name"]
            assert avis.summary_text == edge_case_avis_data["summary_text"]

    @patch(
        "nbs.mongo_avis_critique.get_DB_VARS",
        return_value=("localhost", "test_db", "logs"),
    )
    def test_update_summary_text(self, mock_get_db_vars, sample_avis_data):
        """Test de mise à jour du summary_text"""
        mock_collection = MagicMock()

        with patch(
            "nbs.mongo_avis_critique.get_collection", return_value=mock_collection
        ):
            from nbs.mongo_avis_critique import AvisCritique

            avis = AvisCritique(
                episode_id=sample_avis_data["episode_id"],
                entity_type=sample_avis_data["entity_type"],
                entity_name=sample_avis_data["entity_name"],
            )

            # Initial state
            assert avis.summary_text is None

            # Update
            new_summary = "Nouveau résumé de critique"
            avis.update_summary_text(new_summary)

            # Assert
            assert avis.summary_text == new_summary
            assert avis.updated_at is not None
