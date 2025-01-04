# AUTOGENERATED! DO NOT EDIT! File to edit: mongo helper.ipynb.

# %% auto 0
__all__ = ["get_DB_VARS", "mongolog", "print_logs", "Auteur"]

# %% mongo helper.ipynb 2
from dotenv import load_dotenv, find_dotenv
from helper import load_env
import os


def get_DB_VARS():
    load_env()
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    DB_LOGS = os.getenv("DB_LOGS")
    return DB_HOST, DB_NAME, DB_LOGS


# %% mongo helper.ipynb 4
from connection import get_collection
from datetime import datetime
import pymongo


def mongolog(operation: str, entite: str, desc: str):
    DB_HOST, DB_NAME, DB_LOGS = get_DB_VARS()
    if DB_LOGS == "true" or "True":
        coll_logs = get_collection(DB_HOST, DB_NAME, "logs")
        coll_logs.insert_one(
            {
                "operation": operation,
                "entite": entite,
                "desc": desc,
                "date": datetime.now(),
            }
        )


def print_logs(n: int = 10):
    """
    Print the last n logs
    """
    DB_HOST, DB_NAME, DB_LOGS = get_DB_VARS()
    coll_logs = get_collection(DB_HOST, DB_NAME, "logs")
    for log in coll_logs.find().sort("date", pymongo.DESCENDING):
        print(log)


# %% mongo helper.ipynb 6
from bson import ObjectId
from connection import get_collection


class Auteur:
    def __init__(self, nom: str):
        """
        Auteur is a class that represents an author in the database auteurs.
        :param nom: The name of the author.
        """
        DB_HOST, DB_NAME, _ = get_DB_VARS()
        self.collection = get_collection(
            target_db=DB_HOST, client_name=DB_NAME, collection_name="auteurs"
        )
        self.nom = nom

    def exists(self) -> bool:
        """
        Check if the author exists in the database.
        :return: True if the author exists, False otherwise.
        """

        return self.collection.find_one({"nom": self.nom}) is not None

    def keep(self):
        """
        Keep the author in the database.
        """

        if not self.exists():
            mongolog("insert", "auteur", self.nom)
            self.collection.insert_one({"nom": self.nom})
        else:
            mongolog("update", "auteur", self.nom)

    def remove(self):
        """
        Remove the author in the database.
        """
        # remove from database

        self.collection.delete_one({"nom": self.nom})
        mongolog("delete", "auteur", self.nom)

    def get_oid(self) -> ObjectId:
        """
        Get the object id of the author.
        :return: The object id of the author. (bson.ObjectId)
        None if does not exist.
        """

        document = self.collection.find_one({"nom": self.nom})
        if document:
            return document["_id"]
        else:
            return None
