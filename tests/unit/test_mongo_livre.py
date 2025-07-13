"""
Tests pour le module nbs.mongo_livre.

Ce module teste les fonctionnalités de gestion des livres incluant :
- Classe Livre (hérite de BaseEntity)
- Méthodes CRUD (create, read, update, delete)
- Relations avec Auteur et Editeur
- Constructeurs alternatifs (with_details, from_oid)
- Représentation string
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
from typing import Type, TypeVar
from bson import ObjectId

# Configuration des variables d'environnement pour éviter les erreurs
import os

os.environ.setdefault("AUDIO_PATH", "/tmp/test_audio")


@pytest.fixture(autouse=True)
def mock_mongo_livre_dependencies():
    """Mock toutes les dépendances externes pour mongo_livre automatiquement"""
    # Configuration du mock config pour être compatible
    mock_config = MagicMock()
    mock_config.get_DB_VARS.return_value = ("localhost", "test_db", "true")

    # Mock pour les autres modules
    mock_mongo = MagicMock()
    mock_mongo_auteur = MagicMock()

    # Mock pour BaseEntity (classe parent) - plus simple
    class MockBaseEntity:
        def __init__(self, nom: str, collection_name: str):
            self.nom = nom
            self.collection = MagicMock()
            self.collection.name = collection_name

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

    # Mock pour Auteur et Editeur
    mock_auteur_class = MagicMock()
    mock_editeur_class = MagicMock()

    mock_mongo.BaseEntity = MockBaseEntity
    mock_mongo.Editeur = mock_editeur_class
    mock_mongo.get_collection = MagicMock()
    mock_mongo_auteur.Auteur = mock_auteur_class

    with patch.dict(
        "sys.modules",
        {
            "mongo": mock_mongo,
            "config": mock_config,
            "mongo_auteur": mock_mongo_auteur,
        },
    ):
        yield


@pytest.fixture
def sample_livre_data():
    """Fixture pour les données de livre de test"""
    return {
        "titre": "Les Misérables",
        "auteur_nom": "Victor Hugo",
        "editeur_nom": "Gallimard",
    }


@pytest.fixture
def mock_auteur():
    """Fixture pour un auteur mocké"""
    auteur = MagicMock()
    auteur.get_oid.return_value = ObjectId()
    auteur.nom = "Victor Hugo"
    return auteur


@pytest.fixture
def mock_editeur():
    """Fixture pour un éditeur mocké"""
    editeur = MagicMock()
    editeur.get_oid.return_value = ObjectId()
    editeur.nom = "Gallimard"
    return editeur


class TestModuleConstants:
    """Tests pour les constantes et exports du module"""

    def test_module_exports(self):
        """Test des exports __all__ du module"""
        from nbs import mongo_livre

        expected_exports = ["T", "Livre"]

        # Assert
        assert mongo_livre.__all__ == expected_exports

        # Verify all exports exist
        for export in expected_exports:
            assert hasattr(mongo_livre, export), f"Missing export: {export}"

    def test_typevar_t(self):
        """Test du TypeVar T"""
        from nbs.mongo_livre import T

        # Assert
        assert isinstance(T, type(TypeVar("test")))
        # Vérifier que T est bien bound à "Livre" (en string ou ForwardRef)
        assert T.__bound__ is not None


@patch("nbs.mongo_livre.get_DB_VARS", return_value=("localhost", "test_db", "logs"))
class TestLivreClass:
    """Tests pour la classe Livre"""

    def test_livre_initialization(self, mock_get_db_vars, sample_livre_data):
        """Test d'initialisation d'un livre"""
        mock_collection = MagicMock()

        with patch("nbs.mongo_livre.get_collection", return_value=mock_collection):
            from nbs.mongo_livre import Livre

            livre = Livre(sample_livre_data["titre"])

            # Assert
            assert livre.titre == sample_livre_data["titre"]
            assert livre.auteur is None
            assert livre.editeur is None
            # Vérifier que l'objet a les attributs attendus
            assert hasattr(livre, "collection")
            assert hasattr(livre, "nom")  # Hérité de BaseEntity
            assert livre.nom == sample_livre_data["titre"]

    def test_livre_add_auteur(self, mock_get_db_vars, sample_livre_data, mock_auteur):
        """Test d'ajout d'un auteur à un livre"""
        mock_collection = MagicMock()
        test_oid = ObjectId()
        mock_auteur.get_oid.return_value = test_oid

        with patch("nbs.mongo_livre.get_collection", return_value=mock_collection):
            from nbs.mongo_livre import Livre

            livre = Livre(sample_livre_data["titre"])
            livre.add_auteur(mock_auteur)

            # Assert
            assert livre.auteur == test_oid
            assert mock_auteur.get_oid.called  # Vérifie qu'il a été appelé

    def test_livre_add_auteur_none(self, mock_get_db_vars, sample_livre_data):
        """Test d'ajout d'un auteur None à un livre"""
        mock_collection = MagicMock()

        with patch("nbs.mongo_livre.get_collection", return_value=mock_collection):
            from nbs.mongo_livre import Livre

            livre = Livre(sample_livre_data["titre"])
            livre.add_auteur(None)

            # Assert
            assert livre.auteur is None

    def test_livre_add_editeur(self, mock_get_db_vars, sample_livre_data, mock_editeur):
        """Test d'ajout d'un éditeur à un livre"""
        mock_collection = MagicMock()
        test_oid = ObjectId()
        mock_editeur.get_oid.return_value = test_oid

        with patch("nbs.mongo_livre.get_collection", return_value=mock_collection):
            from nbs.mongo_livre import Livre

            livre = Livre(sample_livre_data["titre"])
            livre.add_editeur(mock_editeur)

            # Assert
            assert livre.editeur == test_oid
            assert mock_editeur.get_oid.called  # Vérifie qu'il a été appelé

    def test_livre_add_editeur_none(self, mock_get_db_vars, sample_livre_data):
        """Test d'ajout d'un éditeur None à un livre"""
        mock_collection = MagicMock()

        with patch("nbs.mongo_livre.get_collection", return_value=mock_collection):
            from nbs.mongo_livre import Livre

            livre = Livre(sample_livre_data["titre"])
            livre.add_editeur(None)

            # Assert
            assert livre.editeur is None


class TestLivreClassMethods:
    """Tests pour les méthodes de classe de Livre"""

    @patch("nbs.mongo_livre.get_DB_VARS", return_value=("localhost", "test_db", "logs"))
    def test_with_details(
        self, mock_get_db_vars, sample_livre_data, mock_auteur, mock_editeur
    ):
        """Test du constructeur alternatif with_details"""
        mock_collection = MagicMock()

        with patch("nbs.mongo_livre.get_collection", return_value=mock_collection):
            from nbs.mongo_livre import Livre

            livre = Livre.with_details(
                sample_livre_data["titre"], mock_auteur, mock_editeur
            )

            # Assert
            assert livre.titre == sample_livre_data["titre"]
            assert livre.auteur == mock_auteur.get_oid()
            assert livre.editeur == mock_editeur.get_oid()

    @patch("nbs.mongo_livre.get_DB_VARS", return_value=("localhost", "test_db", "logs"))
    def test_from_oid_success(self, mock_get_db_vars, sample_livre_data):
        """Test from_oid() trouve un livre"""
        test_oid = ObjectId()
        mock_collection = MagicMock()
        mock_auteur_oid = ObjectId()
        mock_editeur_oid = ObjectId()

        mock_document = {
            "titre": sample_livre_data["titre"],
            "auteur": mock_auteur_oid,
            "editeur": mock_editeur_oid,
        }
        mock_collection.find_one.return_value = mock_document

        # Mock des instances Auteur et Editeur retournées par from_oid
        mock_auteur = MagicMock()
        mock_editeur = MagicMock()

        with patch(
            "nbs.mongo_livre.get_collection", return_value=mock_collection
        ), patch("nbs.mongo_livre.Auteur") as MockAuteur, patch(
            "nbs.mongo_livre.Editeur"
        ) as MockEditeur:

            MockAuteur.from_oid.return_value = mock_auteur
            MockEditeur.from_oid.return_value = mock_editeur

            from nbs.mongo_livre import Livre

            result = Livre.from_oid(test_oid)

            # Assert
            assert result is not None
            assert result.titre == sample_livre_data["titre"]
            mock_collection.find_one.assert_called_once_with({"_id": test_oid})
            MockAuteur.from_oid.assert_called_once_with(mock_auteur_oid)
            MockEditeur.from_oid.assert_called_once_with(mock_editeur_oid)

    @patch("nbs.mongo_livre.get_DB_VARS", return_value=("localhost", "test_db", "logs"))
    def test_from_oid_not_found(self, mock_get_db_vars):
        """Test from_oid() ne trouve pas de livre"""
        test_oid = ObjectId()
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None

        with patch("nbs.mongo_livre.get_collection", return_value=mock_collection):
            from nbs.mongo_livre import Livre

            result = Livre.from_oid(test_oid)

            # Assert
            assert result is None

    def test_from_oid_none_input(self):
        """Test from_oid() avec ObjectId None"""
        from nbs.mongo_livre import Livre

        result = Livre.from_oid(None)

        # Assert
        assert result is None


class TestLivreStringRepresentation:
    """Tests pour la représentation string de Livre"""

    @patch("nbs.mongo_livre.get_DB_VARS", return_value=("localhost", "test_db", "logs"))
    def test_str_representation_with_auteur_editeur(
        self, mock_get_db_vars, sample_livre_data
    ):
        """Test __str__ avec auteur et éditeur"""
        mock_collection = MagicMock()
        mock_auteur_oid = ObjectId()
        mock_editeur_oid = ObjectId()

        # Mock des objets Auteur et Editeur retournés
        mock_auteur_obj = MagicMock()
        mock_auteur_obj.__str__ = MagicMock(return_value="Victor Hugo")
        mock_editeur_obj = MagicMock()
        mock_editeur_obj.__str__ = MagicMock(return_value="Gallimard")

        with patch(
            "nbs.mongo_livre.get_collection", return_value=mock_collection
        ), patch("nbs.mongo_livre.Auteur") as MockAuteur, patch(
            "nbs.mongo_livre.Editeur"
        ) as MockEditeur:

            MockAuteur.from_oid.return_value = mock_auteur_obj
            MockEditeur.from_oid.return_value = mock_editeur_obj

            from nbs.mongo_livre import Livre

            livre = Livre(sample_livre_data["titre"])
            livre.auteur = mock_auteur_oid
            livre.editeur = mock_editeur_oid

            result = str(livre)

            # Assert
            assert sample_livre_data["titre"] in result
            assert "Titre:" in result
            assert "Auteur:" in result
            assert "Editeur:" in result

    @patch("nbs.mongo_livre.get_DB_VARS", return_value=("localhost", "test_db", "logs"))
    def test_str_representation_without_auteur_editeur(
        self, mock_get_db_vars, sample_livre_data
    ):
        """Test __str__ sans auteur ni éditeur"""
        mock_collection = MagicMock()

        with patch("nbs.mongo_livre.get_collection", return_value=mock_collection):
            from nbs.mongo_livre import Livre

            livre = Livre(sample_livre_data["titre"])

            result = str(livre)

            # Assert
            assert sample_livre_data["titre"] in result
            assert "Titre:" in result
            assert "Auteur: None" in result
            assert "Editeur: None" in result


class TestLivreInheritedMethods:
    """Tests pour les méthodes héritées de BaseEntity"""

    @patch("nbs.mongo_livre.get_DB_VARS", return_value=("localhost", "test_db", "logs"))
    def test_livre_inherits_base_methods(self, mock_get_db_vars, sample_livre_data):
        """Test que Livre hérite correctement des méthodes de BaseEntity"""
        mock_collection = MagicMock()

        with patch("nbs.mongo_livre.get_collection", return_value=mock_collection):
            from nbs.mongo_livre import Livre

            livre = Livre(sample_livre_data["titre"])

            # Assert que les méthodes héritées existent
            assert hasattr(livre, "exists")
            assert hasattr(livre, "keep")
            assert hasattr(livre, "remove")
            assert hasattr(livre, "get_oid")
            assert hasattr(livre, "to_dict")

            # Assert que nom est hérité et égal au titre
            assert hasattr(livre, "nom")
            assert livre.nom == sample_livre_data["titre"]
