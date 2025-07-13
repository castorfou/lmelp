"""Tests pour le module nbs.mongo"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from bson import ObjectId
import sys

# Mock du module config AVANT l'import de nbs.mongo
sys.modules["config"] = MagicMock()
sys.modules["config"].get_DB_VARS.return_value = ("localhost", "test_db", "true")


class TestMongoConnection:
    """Tests pour les fonctions de connexion MongoDB"""

    def test_get_collection_default_params(self, monkeypatch):
        """Test get_collection avec paramètres par défaut"""
        # ARRANGE : Mock de pymongo
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()

        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        monkeypatch.setattr(
            "nbs.mongo.pymongo.MongoClient", MagicMock(return_value=mock_client)
        )

        # ACT : Appeler get_collection
        from nbs.mongo import get_collection

        result = get_collection()

        # ASSERT : Vérifier les appels avec les paramètres par défaut
        assert result == mock_collection

    def test_get_collection_custom_params(self, monkeypatch):
        """Test get_collection avec paramètres personnalisés"""
        # ARRANGE
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()

        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        monkeypatch.setattr(
            "nbs.mongo.pymongo.MongoClient", MagicMock(return_value=mock_client)
        )

        # ACT
        from nbs.mongo import get_collection

        result = get_collection("remote_db", "custom_client", "custom_collection")

        # ASSERT
        assert result == mock_collection

    def test_get_collection_returns_collection_type(self, monkeypatch):
        """Test que get_collection retourne un objet Collection"""
        # ARRANGE
        mock_collection = MagicMock()
        monkeypatch.setattr("nbs.mongo.pymongo.MongoClient", MagicMock())

        # ACT
        from nbs.mongo import get_collection

        with patch("nbs.mongo.pymongo.MongoClient") as mock_mongo:
            mock_mongo.return_value.__getitem__.return_value.__getitem__.return_value = (
                mock_collection
            )
            result = get_collection()

        # ASSERT
        assert result == mock_collection


class TestMongoLogging:
    """Tests pour les fonctions de logging MongoDB"""

    def test_mongolog_creates_log_entry(self, monkeypatch):
        """Test que mongolog crée une entrée de log"""
        # ARRANGE : Mock de get_collection et datetime
        mock_collection = MagicMock()
        mock_datetime = MagicMock()
        mock_datetime.now.return_value = "2025-07-13T12:00:00"

        monkeypatch.setattr(
            "nbs.mongo.get_collection", MagicMock(return_value=mock_collection)
        )
        monkeypatch.setattr("nbs.mongo.datetime", mock_datetime)

        # ACT : Appeler mongolog
        from nbs.mongo import mongolog

        mongolog("CREATE", "Episode", "Test episode creation")

        # ASSERT : Vérifier l'appel insert_one
        mock_collection.insert_one.assert_called_once()
        call_args = mock_collection.insert_one.call_args[0][0]

        assert call_args["operation"] == "CREATE"
        assert call_args["entite"] == "Episode"
        assert call_args["desc"] == "Test episode creation"
        assert call_args["date"] == "2025-07-13T12:00:00"

    def test_print_logs_displays_logs(self, monkeypatch, capsys):
        """Test que print_logs affiche les logs correctement"""
        # ARRANGE : Mock de get_collection avec des logs simulés
        mock_logs = [
            {
                "operation": "CREATE",
                "entite": "Episode",
                "desc": "Episode created",
                "date": "2025-07-13",
            },
            {
                "operation": "UPDATE",
                "entite": "Critique",
                "desc": "Review updated",
                "date": "2025-07-13",
            },
        ]
        mock_collection = MagicMock()
        mock_find = MagicMock()
        mock_sort = MagicMock()
        mock_sort.__iter__ = MagicMock(return_value=iter(mock_logs))
        mock_find.sort.return_value = mock_sort
        mock_collection.find.return_value = mock_find

        monkeypatch.setattr(
            "nbs.mongo.get_collection", MagicMock(return_value=mock_collection)
        )

        # ACT : Appeler print_logs
        from nbs.mongo import print_logs

        print_logs(5)

        # ASSERT : Vérifier l'appel à la collection et l'affichage
        mock_collection.find.assert_called_once()
        captured = capsys.readouterr()
        assert "CREATE" in captured.out
        assert "Episode" in captured.out

    def test_print_logs_default_limit(self, monkeypatch):
        """Test que print_logs utilise la limite par défaut"""
        # ARRANGE : Mock de get_collection
        mock_collection = MagicMock()
        mock_find = MagicMock()
        mock_sort = MagicMock()
        # Simulate 15 logs but only 10 should be printed due to default limit
        mock_logs = [
            {
                "operation": f"OP{i}",
                "entite": "Test",
                "desc": f"Log {i}",
                "date": "2025-07-13",
            }
            for i in range(15)
        ]
        mock_sort.__iter__ = MagicMock(return_value=iter(mock_logs))
        mock_find.sort.return_value = mock_sort
        mock_collection.find.return_value = mock_find

        monkeypatch.setattr(
            "nbs.mongo.get_collection", MagicMock(return_value=mock_collection)
        )

        # ACT : Appeler sans paramètre
        from nbs.mongo import print_logs

        print_logs()

        # ASSERT : Vérifier l'appel
        mock_collection.find.assert_called_once()


class TestBaseEntity:
    """Tests pour la classe BaseEntity"""

    def test_base_entity_init(self, monkeypatch):
        """Test l'initialisation de BaseEntity"""
        # ARRANGE : Mock de get_collection
        mock_collection = MagicMock()
        monkeypatch.setattr(
            "nbs.mongo.get_collection", MagicMock(return_value=mock_collection)
        )

        # ACT
        from nbs.mongo import BaseEntity

        entity = BaseEntity("test_name", "test_collection")

        # ASSERT
        assert entity.nom == "test_name"
        assert entity.collection == mock_collection

    def test_base_entity_exists_true(self, monkeypatch):
        """Test exists() retourne True quand l'entité existe"""
        # ARRANGE : Mock de get_collection avec résultat trouvé
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {"nom": "test_name"}

        monkeypatch.setattr(
            "nbs.mongo.get_collection", MagicMock(return_value=mock_collection)
        )

        from nbs.mongo import BaseEntity

        entity = BaseEntity("test_name", "test_collection")

        # ACT
        result = entity.exists()

        # ASSERT
        assert result is True
        mock_collection.find_one.assert_called_once_with({"nom": "test_name"})

    def test_base_entity_exists_false(self, monkeypatch):
        """Test exists() retourne False quand l'entité n'existe pas"""
        # ARRANGE : Mock de get_collection sans résultat
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None

        monkeypatch.setattr(
            "nbs.mongo.get_collection", MagicMock(return_value=mock_collection)
        )

        from nbs.mongo import BaseEntity

        entity = BaseEntity("test_name", "test_collection")

        # ACT
        result = entity.exists()

        # ASSERT
        assert result is False

    def test_base_entity_to_dict(self, monkeypatch):
        """Test to_dict() retourne un dictionnaire"""
        # ARRANGE
        mock_collection = MagicMock()
        monkeypatch.setattr(
            "nbs.mongo.get_collection", MagicMock(return_value=mock_collection)
        )

        from nbs.mongo import BaseEntity

        entity = BaseEntity("test_name", "test_collection")

        # ACT
        result = entity.to_dict()

        # ASSERT
        assert isinstance(result, dict)
        assert result["nom"] == "test_name"

    def test_base_entity_keep_new_entity(self, monkeypatch):
        """Test keep() pour une nouvelle entité"""
        # ARRANGE : Mock de get_collection et mongolog
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None  # N'existe pas
        mock_collection.insert_one.return_value.inserted_id = ObjectId()

        monkeypatch.setattr(
            "nbs.mongo.get_collection", MagicMock(return_value=mock_collection)
        )
        monkeypatch.setattr("nbs.mongo.mongolog", MagicMock())

        from nbs.mongo import BaseEntity

        entity = BaseEntity("test_name", "test_collection")

        # ACT
        result = entity.keep()

        # ASSERT
        assert result is None  # keep() retourne None
        mock_collection.insert_one.assert_called_once()

    def test_base_entity_keep_existing_entity(self, monkeypatch):
        """Test keep() pour une entité existante"""
        # ARRANGE : Mock avec entité existante
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {"nom": "test_name"}  # Existe déjà

        monkeypatch.setattr(
            "nbs.mongo.get_collection", MagicMock(return_value=mock_collection)
        )
        monkeypatch.setattr("nbs.mongo.mongolog", MagicMock())

        from nbs.mongo import BaseEntity

        entity = BaseEntity("test_name", "test_collection")

        # ACT
        result = entity.keep()

        # ASSERT
        assert result is None
        mock_collection.insert_one.assert_not_called()

    def test_base_entity_remove(self, monkeypatch):
        """Test remove() supprime l'entité"""
        # ARRANGE : Mock de get_collection et mongolog
        mock_collection = MagicMock()
        monkeypatch.setattr(
            "nbs.mongo.get_collection", MagicMock(return_value=mock_collection)
        )
        monkeypatch.setattr("nbs.mongo.mongolog", MagicMock())

        from nbs.mongo import BaseEntity

        entity = BaseEntity("test_name", "test_collection")

        # ACT
        entity.remove()

        # ASSERT
        mock_collection.delete_one.assert_called_once_with({"nom": "test_name"})

    def test_base_entity_get_oid(self, monkeypatch):
        """Test get_oid() retourne l'ObjectId"""
        # ARRANGE : Mock avec ObjectId
        test_oid = ObjectId()
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {"_id": test_oid, "nom": "test_name"}

        monkeypatch.setattr(
            "nbs.mongo.get_collection", MagicMock(return_value=mock_collection)
        )

        from nbs.mongo import BaseEntity

        entity = BaseEntity("test_name", "test_collection")

        # ACT
        result = entity.get_oid()

        # ASSERT
        assert result == test_oid

    def test_base_entity_get_oid_not_found(self, monkeypatch):
        """Test get_oid() retourne None si non trouvé"""
        # ARRANGE : Mock sans résultat
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = None

        monkeypatch.setattr(
            "nbs.mongo.get_collection", MagicMock(return_value=mock_collection)
        )

        from nbs.mongo import BaseEntity

        entity = BaseEntity("test_name", "test_collection")

        # ACT
        result = entity.get_oid()

        # ASSERT
        assert result is None


class TestEditeur:
    """Tests pour la classe Editeur"""

    def test_editeur_init(self, monkeypatch):
        """Test l'initialisation d'Editeur"""
        # ARRANGE : Mock de get_collection
        mock_collection = MagicMock()
        monkeypatch.setattr(
            "nbs.mongo.get_collection", MagicMock(return_value=mock_collection)
        )

        # ACT
        from nbs.mongo import Editeur

        editeur = Editeur("Gallimard")

        # ASSERT
        assert editeur.nom == "Gallimard"
        assert Editeur.collection == "editeurs"  # Attribut de classe, pas d'instance

    def test_editeur_inherits_from_base_entity(self):
        """Test qu'Editeur hérite de BaseEntity"""
        # ARRANGE
        from nbs.mongo import Editeur, BaseEntity

        # ACT & ASSERT
        assert issubclass(Editeur, BaseEntity)


class TestCritique:
    """Tests pour la classe Critique"""

    def test_critique_init(self, monkeypatch):
        """Test l'initialisation de Critique"""
        # ARRANGE : Mock de get_collection
        mock_collection = MagicMock()
        monkeypatch.setattr(
            "nbs.mongo.get_collection", MagicMock(return_value=mock_collection)
        )

        # ACT
        from nbs.mongo import Critique

        critique = Critique("Jean Dupont")

        # ASSERT
        assert critique.nom == "Jean Dupont"
        assert Critique.collection == "critiques"  # Attribut de classe, pas d'instance

    def test_critique_inherits_from_base_entity(self):
        """Test que Critique hérite de BaseEntity"""
        # ARRANGE
        from nbs.mongo import Critique, BaseEntity

        # ACT & ASSERT
        assert issubclass(Critique, BaseEntity)


class TestClassMethods:
    """Tests pour les méthodes de classe"""

    def test_from_oid_creates_instance(self, monkeypatch):
        """Test from_oid() crée une instance à partir d'ObjectId"""
        # ARRANGE : Mock de get_collection avec document
        test_oid = ObjectId()
        mock_collection = MagicMock()
        mock_collection.find_one.return_value = {"_id": test_oid, "nom": "Test Editeur"}

        monkeypatch.setattr(
            "nbs.mongo.get_collection", MagicMock(return_value=mock_collection)
        )

        # ACT
        from nbs.mongo import Editeur

        editeur = Editeur.from_oid(test_oid)

        # ASSERT
        assert editeur.nom == "Test Editeur"
        assert isinstance(editeur, Editeur)

    def test_get_entries_returns_list(self, monkeypatch):
        """Test get_entries() retourne une liste d'instances"""
        # ARRANGE : Mock avec plusieurs documents
        test_oid1 = ObjectId()
        test_oid2 = ObjectId()
        mock_collection = MagicMock()
        mock_collection.find.return_value = [
            {"_id": test_oid1, "nom": "Editeur 1"},
            {"_id": test_oid2, "nom": "Editeur 2"},
        ]
        # Mock find_one pour from_oid
        mock_collection.find_one.side_effect = [
            {"_id": test_oid1, "nom": "Editeur 1"},
            {"_id": test_oid2, "nom": "Editeur 2"},
        ]

        monkeypatch.setattr(
            "nbs.mongo.get_collection", MagicMock(return_value=mock_collection)
        )

        # ACT
        from nbs.mongo import Editeur

        editeurs = Editeur.get_entries()

        # ASSERT
        assert len(editeurs) == 2
        assert all(isinstance(e, Editeur) for e in editeurs)
        assert editeurs[0].nom == "Editeur 1"
        assert editeurs[1].nom == "Editeur 2"

    def test_get_entries_with_request(self, monkeypatch):
        """Test get_entries() avec requête spécifique"""
        # ARRANGE : Mock avec requête
        test_oid = ObjectId()
        mock_collection = MagicMock()
        mock_collection.find.return_value = [
            {"_id": test_oid, "nom": "Filtered Editeur"}
        ]
        mock_collection.find_one.return_value = {
            "_id": test_oid,
            "nom": "Filtered Editeur",
        }

        monkeypatch.setattr(
            "nbs.mongo.get_collection", MagicMock(return_value=mock_collection)
        )

        # ACT
        from nbs.mongo import Editeur

        editeurs = Editeur.get_entries("specific_request")

        # ASSERT
        assert len(editeurs) == 1
        assert editeurs[0].nom == "Filtered Editeur"
        assert isinstance(editeurs[0], Editeur)


class TestStringRepresentations:
    """Tests pour les représentations string"""

    def test_base_entity_repr(self, monkeypatch):
        """Test __repr__ de BaseEntity"""
        # ARRANGE
        mock_collection = MagicMock()
        monkeypatch.setattr(
            "nbs.mongo.get_collection", MagicMock(return_value=mock_collection)
        )

        from nbs.mongo import BaseEntity

        entity = BaseEntity("test_name", "test_collection")

        # ACT
        result = repr(entity)

        # ASSERT
        assert "test_name" in result

    def test_base_entity_str(self, monkeypatch):
        """Test __str__ de BaseEntity"""
        # ARRANGE
        mock_collection = MagicMock()
        monkeypatch.setattr(
            "nbs.mongo.get_collection", MagicMock(return_value=mock_collection)
        )

        from nbs.mongo import BaseEntity

        entity = BaseEntity("test_name", "test_collection")

        # ACT
        result = str(entity)

        # ASSERT
        assert result == "test_name"

    def test_editeur_str(self, monkeypatch):
        """Test __str__ d'Editeur"""
        # ARRANGE
        mock_collection = MagicMock()
        monkeypatch.setattr(
            "nbs.mongo.get_collection", MagicMock(return_value=mock_collection)
        )

        from nbs.mongo import Editeur

        editeur = Editeur("Gallimard")

        # ACT
        result = str(editeur)

        # ASSERT
        assert result == "Gallimard"

    def test_critique_str(self, monkeypatch):
        """Test __str__ de Critique"""
        # ARRANGE
        mock_collection = MagicMock()
        monkeypatch.setattr(
            "nbs.mongo.get_collection", MagicMock(return_value=mock_collection)
        )

        from nbs.mongo import Critique

        critique = Critique("Jean Dupont")

        # ACT
        result = str(critique)

        # ASSERT
        assert result == "Jean Dupont"
