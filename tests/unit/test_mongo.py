"""Tests pour nbs/mongo.py - Interactions avec MongoDB"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from bson import ObjectId
from datetime import datetime
from nbs.mongo import (
    get_collection,
    mongolog,
    print_logs,
    BaseEntity,
    Editeur,
    Critique,
)


class TestGetCollection:
    """Tests pour la fonction get_collection"""

    @patch("nbs.mongo.pymongo.MongoClient")
    def test_get_collection_default_params(self, mock_client):
        """Test get_collection avec paramètres par défaut"""
        # ARRANGE
        mock_db = Mock()
        mock_collection = Mock()
        mock_client.return_value = {"masque_et_la_plume": mock_db}
        mock_db.__getitem__.return_value = mock_collection

        # ACT
        result = get_collection()

        # ASSERT
        mock_client.assert_called_once_with("mongodb://localhost:27017/")
        assert result == mock_collection

    @patch("nbs.mongo.pymongo.MongoClient")
    def test_get_collection_custom_params(self, mock_client):
        """Test get_collection avec paramètres personnalisés"""
        # ARRANGE
        mock_db = Mock()
        mock_collection = Mock()
        mock_client.return_value = {"test_db": mock_db}
        mock_db.__getitem__.return_value = mock_collection

        # ACT
        result = get_collection(
            target_db="nas923", client_name="test_db", collection_name="test_collection"
        )

        # ASSERT
        mock_client.assert_called_once_with("mongodb://nas923:27017/")
        assert result == mock_collection


class TestMongolog:
    """Tests pour la fonction mongolog"""

    @patch("nbs.mongo.get_DB_VARS")
    @patch("nbs.mongo.get_collection")
    def test_mongolog_enabled(self, mock_get_collection, mock_get_db_vars):
        """Test mongolog quand les logs sont activés"""
        # ARRANGE
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection

        # ACT
        mongolog("insert", "episodes", "Test episode")

        # ASSERT
        mock_get_collection.assert_called_once_with("localhost", "test_db", "logs")
        mock_collection.insert_one.assert_called_once()

        # Vérifier la structure du document inséré
        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args["operation"] == "insert"
        assert call_args["entite"] == "episodes"
        assert call_args["desc"] == "Test episode"
        assert isinstance(call_args["date"], datetime)

    @patch("nbs.mongo.get_DB_VARS")
    @patch("nbs.mongo.get_collection")
    def test_mongolog_disabled(self, mock_get_collection, mock_get_db_vars):
        """Test mongolog quand les logs sont désactivés"""
        # ARRANGE
        mock_get_db_vars.return_value = ("localhost", "test_db", "false")

        # ACT
        mongolog("insert", "episodes", "Test episode")

        # ASSERT
        mock_get_collection.assert_not_called()

    @patch("nbs.mongo.get_DB_VARS")
    @patch("nbs.mongo.get_collection")
    def test_mongolog_true_uppercase(self, mock_get_collection, mock_get_db_vars):
        """Test mongolog avec 'True' en majuscules"""
        # ARRANGE
        mock_get_db_vars.return_value = ("localhost", "test_db", "True")
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection

        # ACT
        mongolog("update", "auteurs", "Test author")

        # ASSERT
        mock_get_collection.assert_called_once()
        mock_collection.insert_one.assert_called_once()


class TestPrintLogs:
    """Tests pour la fonction print_logs"""

    @patch("nbs.mongo.get_DB_VARS")
    @patch("nbs.mongo.get_collection")
    @patch("builtins.print")
    def test_print_logs_default_limit(
        self, mock_print, mock_get_collection, mock_get_db_vars
    ):
        """Test print_logs avec limite par défaut"""
        # ARRANGE
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection

        # Simuler 5 logs dans la base
        fake_logs = [
            {"_id": ObjectId(), "operation": "insert", "date": datetime.now()},
            {"_id": ObjectId(), "operation": "update", "date": datetime.now()},
            {"_id": ObjectId(), "operation": "delete", "date": datetime.now()},
            {"_id": ObjectId(), "operation": "insert", "date": datetime.now()},
            {"_id": ObjectId(), "operation": "update", "date": datetime.now()},
        ]
        mock_collection.find.return_value.sort.return_value = fake_logs

        # ACT
        print_logs()

        # ASSERT
        mock_get_collection.assert_called_once_with("localhost", "test_db", "logs")
        assert mock_print.call_count == 5

    @patch("nbs.mongo.get_DB_VARS")
    @patch("nbs.mongo.get_collection")
    @patch("builtins.print")
    def test_print_logs_custom_limit(
        self, mock_print, mock_get_collection, mock_get_db_vars
    ):
        """Test print_logs avec limite personnalisée"""
        # ARRANGE
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection

        # Simuler 10 logs mais on veut seulement 3
        fake_logs = [{"_id": ObjectId(), "operation": f"op_{i}"} for i in range(10)]
        mock_collection.find.return_value.sort.return_value = fake_logs

        # ACT
        print_logs(n=3)

        # ASSERT
        assert mock_print.call_count == 3


class TestBaseEntity:
    """Tests pour la classe BaseEntity"""

    @patch("nbs.mongo.get_DB_VARS")
    @patch("nbs.mongo.get_collection")
    def test_base_entity_init(self, mock_get_collection, mock_get_db_vars):
        """Test initialisation de BaseEntity"""
        # ARRANGE
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection

        # ACT
        entity = BaseEntity("test_name", "test_collection")

        # ASSERT
        assert entity.nom == "test_name"
        assert entity.collection == mock_collection
        mock_get_collection.assert_called_once_with(
            target_db="localhost",
            client_name="test_db",
            collection_name="test_collection",
        )

    @patch("nbs.mongo.get_DB_VARS")
    @patch("nbs.mongo.get_collection")
    def test_exists_true(self, mock_get_collection, mock_get_db_vars):
        """Test exists() quand l'entité existe"""
        # ARRANGE
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        mock_collection = Mock()
        mock_collection.find_one.return_value = {"nom": "test_name", "_id": ObjectId()}
        mock_get_collection.return_value = mock_collection

        entity = BaseEntity("test_name", "test_collection")

        # ACT
        result = entity.exists()

        # ASSERT
        assert result is True
        mock_collection.find_one.assert_called_once_with({"nom": "test_name"})

    @patch("nbs.mongo.get_DB_VARS")
    @patch("nbs.mongo.get_collection")
    def test_exists_false(self, mock_get_collection, mock_get_db_vars):
        """Test exists() quand l'entité n'existe pas"""
        # ARRANGE
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        mock_collection = Mock()
        mock_collection.find_one.return_value = None
        mock_get_collection.return_value = mock_collection

        entity = BaseEntity("test_name", "test_collection")

        # ACT
        result = entity.exists()

        # ASSERT
        assert result is False

    @patch("nbs.mongo.get_DB_VARS")
    @patch("nbs.mongo.get_collection")
    def test_to_dict(self, mock_get_collection, mock_get_db_vars):
        """Test to_dict() exclut les attributs non sérialisables"""
        # ARRANGE
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection

        entity = BaseEntity("test_name", "test_collection")
        entity.custom_attr = "test_value"

        # ACT
        result = entity.to_dict()

        # ASSERT
        assert "nom" in result
        assert "custom_attr" in result
        assert "collection" not in result  # Exclu comme prévu
        assert result["nom"] == "test_name"
        assert result["custom_attr"] == "test_value"

    @patch("nbs.mongo.mongolog")
    @patch("nbs.mongo.get_DB_VARS")
    @patch("nbs.mongo.get_collection")
    def test_keep_insert_new_entity(
        self, mock_get_collection, mock_get_db_vars, mock_mongolog
    ):
        """Test keep() pour une nouvelle entité (insert)"""
        # ARRANGE
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        mock_collection = Mock()
        mock_collection.find_one.return_value = None  # Entity doesn't exist
        mock_get_collection.return_value = mock_collection

        entity = BaseEntity("new_entity", "test_collection")

        # ACT
        entity.keep()

        # ASSERT
        mock_collection.insert_one.assert_called_once()
        mock_mongolog.assert_called_once_with("insert", "test_collection", "new_entity")

    @patch("nbs.mongo.mongolog")
    @patch("nbs.mongo.get_DB_VARS")
    @patch("nbs.mongo.get_collection")
    def test_keep_update_existing_entity(
        self, mock_get_collection, mock_get_db_vars, mock_mongolog
    ):
        """Test keep() pour une entité existante (update)"""
        # ARRANGE
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        mock_collection = Mock()
        mock_collection.find_one.return_value = {
            "nom": "existing_entity"
        }  # Entity exists
        mock_get_collection.return_value = mock_collection

        entity = BaseEntity("existing_entity", "test_collection")

        # ACT
        entity.keep()

        # ASSERT
        mock_collection.replace_one.assert_called_once()
        mock_mongolog.assert_called_once_with(
            "update", "test_collection", "existing_entity"
        )

    @patch("nbs.mongo.mongolog")
    @patch("nbs.mongo.get_DB_VARS")
    @patch("nbs.mongo.get_collection")
    def test_remove(self, mock_get_collection, mock_get_db_vars, mock_mongolog):
        """Test remove() supprime l'entité"""
        # ARRANGE
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection

        entity = BaseEntity("to_remove", "test_collection")

        # ACT
        entity.remove()

        # ASSERT
        mock_collection.delete_one.assert_called_once_with({"nom": "to_remove"})
        mock_mongolog.assert_called_once_with("delete", "test_collection", "to_remove")

    @patch("nbs.mongo.get_DB_VARS")
    @patch("nbs.mongo.get_collection")
    def test_get_oid_exists(self, mock_get_collection, mock_get_db_vars):
        """Test get_oid() quand l'entité existe"""
        # ARRANGE
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        test_oid = ObjectId()
        mock_collection = Mock()
        mock_collection.find_one.return_value = {"nom": "test_entity", "_id": test_oid}
        mock_get_collection.return_value = mock_collection

        entity = BaseEntity("test_entity", "test_collection")

        # ACT
        result = entity.get_oid()

        # ASSERT
        assert result == test_oid

    @patch("nbs.mongo.get_DB_VARS")
    @patch("nbs.mongo.get_collection")
    def test_get_oid_not_exists(self, mock_get_collection, mock_get_db_vars):
        """Test get_oid() quand l'entité n'existe pas"""
        # ARRANGE
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        mock_collection = Mock()
        mock_collection.find_one.return_value = None
        mock_get_collection.return_value = mock_collection

        entity = BaseEntity("test_entity", "test_collection")

        # ACT
        result = entity.get_oid()

        # ASSERT
        assert result is None

    def test_str_and_repr(self):
        """Test __str__ et __repr__"""
        # ARRANGE
        with patch("nbs.mongo.get_DB_VARS") as mock_get_db_vars, patch(
            "nbs.mongo.get_collection"
        ) as mock_get_collection:

            mock_get_db_vars.return_value = ("localhost", "test_db", "true")
            mock_get_collection.return_value = Mock()

            entity = BaseEntity("test_name", "test_collection")

            # ACT & ASSERT
            assert str(entity) == "test_name"
            assert repr(entity) == "test_name"


class TestEditeur:
    """Tests pour la classe Editeur"""

    @patch("nbs.mongo.get_DB_VARS")
    @patch("nbs.mongo.get_collection")
    def test_editeur_init(self, mock_get_collection, mock_get_db_vars):
        """Test initialisation d'Editeur"""
        # ARRANGE
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection

        # ACT
        editeur = Editeur("Gallimard")

        # ASSERT
        assert editeur.nom == "Gallimard"
        assert editeur.collection == mock_collection
        mock_get_collection.assert_called_once_with(
            target_db="localhost", client_name="test_db", collection_name="editeurs"
        )

    def test_editeur_collection_name(self):
        """Test que la collection est bien 'editeurs'"""
        assert Editeur.collection == "editeurs"


class TestCritique:
    """Tests pour la classe Critique"""

    @patch("nbs.mongo.get_DB_VARS")
    @patch("nbs.mongo.get_collection")
    def test_critique_init(self, mock_get_collection, mock_get_db_vars):
        """Test initialisation de Critique"""
        # ARRANGE
        mock_get_db_vars.return_value = ("localhost", "test_db", "true")
        mock_collection = Mock()
        mock_get_collection.return_value = mock_collection

        # ACT
        critique = Critique("Critique de Roman")

        # ASSERT
        assert critique.nom == "Critique de Roman"
        assert critique.collection == mock_collection
        mock_get_collection.assert_called_once_with(
            target_db="localhost", client_name="test_db", collection_name="critiques"
        )

    def test_critique_collection_name(self):
        """Test que la collection est bien 'critiques'"""
        assert Critique.collection == "critiques"
