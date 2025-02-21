# AUTOGENERATED! DO NOT EDIT! File to edit: py mongo helper.ipynb.

# %% auto 0
__all__ = [
    "T",
    "get_collection",
    "mongolog",
    "print_logs",
    "BaseEntity",
    "Editeur",
    "Critique",
]

# %% py mongo helper.ipynb 2
import pymongo
from pymongo.collection import Collection


def get_collection(
    target_db: str = "localhost",
    client_name: str = "masque_et_la_plume",
    collection_name: str = "episodes",
) -> Collection:
    """Retrieve a MongoDB collection.

    This function connects to a MongoDB database using the provided database host,
    client name (database name), and collection name, and returns the collection object.

    Args:
        target_db (str): The database host address (e.g., "localhost" or "nas923").
        client_name (str): The name of the MongoDB client/database.
        collection_name (str): The name of the collection to retrieve.

    Returns:
        Collection: The MongoDB collection object.
    """
    client = pymongo.MongoClient(f"mongodb://{target_db}:27017/")
    db = client[client_name]
    collection = db[collection_name]
    return collection


# %% py mongo helper.ipynb 4
from datetime import datetime
import pymongo
from config import get_DB_VARS


def mongolog(operation: str, entite: str, desc: str) -> None:
    """Enregistre une opération de log dans la collection 'logs' si la configuration autorise les logs.

    Args:
        operation (str): L'opération effectuée (par exemple, "insert", "update", "delete").
        entite (str): Le nom de l'entité concernée.
        desc (str): Une description détaillée de l'opération.
    """
    DB_HOST, DB_NAME, DB_LOGS = get_DB_VARS()
    if DB_LOGS in ["true", "True"]:
        coll_logs = get_collection(DB_HOST, DB_NAME, "logs")
        coll_logs.insert_one(
            {
                "operation": operation,
                "entite": entite,
                "desc": desc,
                "date": datetime.now(),
            }
        )


def print_logs(n: int = 10) -> None:
    """Affiche les n derniers logs de la collection 'logs', triés par date décroissante.

    Args:
        n (int, optional): Le nombre maximum de logs à afficher. Par défaut à 10.
    """
    DB_HOST, DB_NAME, DB_LOGS = get_DB_VARS()
    coll_logs = get_collection(DB_HOST, DB_NAME, "logs")
    for i, log in enumerate(coll_logs.find().sort("date", pymongo.DESCENDING)):
        if i == n:
            break
        print(log)


# %% py mongo helper.ipynb 8
from bson import ObjectId
from typing import List, Optional, Type, TypeVar

T = TypeVar("T", bound="BaseEntity")


class BaseEntity:
    def __init__(self, nom: str, collection_name: str) -> None:
        """Initializes a new BaseEntity instance.

        Args:
            nom (str): The name of the entity.
            collection_name (str): The name of the collection.
        """
        DB_HOST, DB_NAME, _ = get_DB_VARS()
        self.collection = get_collection(
            target_db=DB_HOST, client_name=DB_NAME, collection_name=collection_name
        )
        self.nom = nom

    def exists(self) -> bool:
        """Checks if the entity exists in the database.

        Returns:
            bool: True if the entity exists, False otherwise.
        """
        return self.collection.find_one({"nom": self.nom}) is not None

    def to_dict(self) -> dict:
        """
        Sérialise l'instance en dictionnaire en excluant les attributs non désirés.
        On exclut ici 'collection' par exemple.
        """
        # On récupère l'ensemble des attributs de l'objet
        data = self.__dict__.copy()
        # On retire attributes non serialisables
        data.pop("collection", None)
        return data

    def keep(self) -> None:
        """
        Insert ou met à jour l'entité dans la base.
        Utilise la sérialisation via to_dict() pour conserver tous les attributs serialisables.
        """
        data = self.to_dict()
        if not self.exists():
            mongolog("insert", self.collection.name, self.nom)
            self.collection.insert_one(data)
        else:
            mongolog("update", self.collection.name, self.nom)
            self.collection.replace_one({"nom": self.nom}, data)

    def remove(self) -> None:
        """Removes the entity from the database."""
        self.collection.delete_one({"nom": self.nom})
        mongolog("delete", self.collection.name, self.nom)

    def get_oid(self) -> Optional[ObjectId]:
        """Retrieves the ObjectId of the entity from the database.

        Returns:
            Optional[ObjectId]: The ObjectId of the entity if found, otherwise None.
        """
        document = self.collection.find_one({"nom": self.nom})
        if document:
            return document["_id"]
        else:
            return None

    @classmethod
    def from_oid(cls: Type[T], oid: ObjectId) -> T:
        """Creates an instance of the derived class from a MongoDB ObjectId.

        Args:
            oid (ObjectId): The MongoDB ObjectId.

        Returns:
            T: An instance of the derived class.
        """
        DB_HOST, DB_NAME, _ = get_DB_VARS()
        collection = get_collection(
            target_db=DB_HOST, client_name=DB_NAME, collection_name=cls.collection
        )
        document = collection.find_one({"_id": oid})
        inst = cls(document.get("nom"))
        return inst

    @classmethod
    def get_entries(cls: Type[T], request: str = "") -> List[T]:
        """Retrieves a list of entries matching the query.

        Args:
            request (str, optional): A substring of the name to filter results
                (case-insensitive). Defaults to an empty string.

        Returns:
            List[T]: A list of instances of the derived class.
        """
        DB_HOST, DB_NAME, _ = get_DB_VARS()
        collection = get_collection(
            target_db=DB_HOST, client_name=DB_NAME, collection_name=cls.collection
        )
        query = {
            "nom": {
                "$regex": request,
                "$options": "i",
            }
        }
        result = collection.find(query)
        list_baseentity = [cls.from_oid(entry.get("_id")) for entry in result]
        return list_baseentity

    def __repr__(self) -> str:
        """Official string representation of the entity.

        Returns:
            str: The name of the entity.
        """
        return self.nom

    def __str__(self) -> str:
        """Informal string representation of the entity.

        Returns:
            str: The name of the entity.
        """
        return self.nom


# %% py mongo helper.ipynb 10
class Editeur(BaseEntity):
    """
    Represents a publisher stored in the 'editeurs' MongoDB collection.

    Attributes:
        collection (str): The name of the MongoDB collection.
    """

    collection: str = "editeurs"

    def __init__(self, nom: str) -> None:
        """
        Initialize an Editeur instance.

        Args:
            nom (str): The name of the publisher.
        """
        super().__init__(nom, self.collection)


# %% py mongo helper.ipynb 15
class Critique(BaseEntity):
    """
    Class representing a review (Critique) entity stored in the 'critiques' MongoDB collection.

    Attributes:
        collection (str): MongoDB collection name used to store critiques.
    """

    collection: str = "critiques"

    def __init__(self, nom: str) -> None:
        """
        Initializes a Critique instance.

        Args:
            nom (str): Name of the critique.
        """
        super().__init__(nom, self.collection)
