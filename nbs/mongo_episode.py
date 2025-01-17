# AUTOGENERATED! DO NOT EDIT! File to edit: py mongo helper episodes.ipynb.

# %% auto 0
__all__ = [
    "AUDIO_PATH",
    "DATE_FORMAT",
    "LOG_DATE_FORMAT",
    "RSS_DUREE_MINI_MINUTES",
    "RSS_DATE_FORMAT",
    "get_audio_path",
    "extract_whisper",
    "Episode",
    "RSS_episode",
]

# %% py mongo helper episodes.ipynb 3
import os
from git import Repo

AUDIO_PATH = "audios"


def get_audio_path(audio_path=AUDIO_PATH, year: str = "2024"):
    """
    audio_path: str
        relative path to audio files
    will add year as subdirectory
    return full audio path and create dir if it doesn t exist
    """

    def get_git_root(path):
        git_repo = Repo(path, search_parent_directories=True)
        return git_repo.git.rev_parse("--show-toplevel")

    project_root = get_git_root(os.getcwd())
    full_audio_path = os.path.join(project_root, audio_path, year)

    # create dir if it doesn t exist
    if not os.path.exists(full_audio_path):
        os.makedirs(full_audio_path)

    return full_audio_path


# %% py mongo helper episodes.ipynb 6
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset


def extract_whisper(mp3_filename):

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = "openai/whisper-large-v3-turbo"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device,
    )

    dataset = load_dataset(
        "distil-whisper/librispeech_long", "clean", split="validation"
    )
    sample = dataset[0]["audio"]

    result = pipe(
        mp3_filename,
        return_timestamps=True,
    )

    return result["text"]


# %% py mongo helper episodes.ipynb 7
from bson import ObjectId
from mongo import get_collection, get_DB_VARS, mongolog
from datetime import datetime
import requests

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
LOG_DATE_FORMAT = "%d %b %Y %H:%M"


class Episode:
    def __init__(self, date: str, titre: str, collection_name: str = "episodes"):
        """
        Episode is a class that represents a generic Episode entity in the database.
        :param date: The date for this episode at the format "2024-12-22T09:59:39.000+00:00" parsed by "%Y-%m-%dT%H:%M:%S.%f%z".
        :param titre: The title of this episode.
        :param collection_name: The name of the collection. default: "episodes".

        if this episode already exists in DB, loads it
        """
        DB_HOST, DB_NAME, _ = get_DB_VARS()
        self.collection = get_collection(
            target_db=DB_HOST, client_name=DB_NAME, collection_name=collection_name
        )
        self.date = Episode.get_date_from_string(date)
        self.titre = titre

        if self.exists():
            episode = self.collection.find_one({"titre": self.titre, "date": self.date})
            self.description = episode.get("description")
            self.url_telechargement = episode.get("url")
            self.audio_rel_filename = episode.get("audio_rel_filename")
            self.transcription = episode.get("transcription")
            self.type = episode.get("type")
            self.duree = episode.get("duree")
        else:
            self.description = None
            self.url_telechargement = None
            self.audio_rel_filename = None
            self.transcription = None
            self.type = None
            self.duree = -1  # in seconds

    def exists(self) -> bool:
        """
        Check if the episode exists in the database.
        :return: True if the episode exists, False otherwise.
        """
        return (
            self.collection.find_one({"titre": self.titre, "date": self.date})
            is not None
        )

    def keep(self) -> int:
        """
        download the audio file if needed
        Keep the episode in the database

        retourne 1 si 1 entree est creee en base
        0 sinon
        """
        message_log = f"{Episode.get_string_from_date(self.date, format=LOG_DATE_FORMAT)} - {self.titre}"
        if not self.exists():
            print(
                f"Episode du {Episode.get_string_from_date(self.date, format=LOG_DATE_FORMAT)} nouveau: Duree: {self.duree}, Type: {self.type}"
            )
            mongolog("insert", self.collection.name, message_log)
            self.download_audio(verbose=True)
            self.collection.insert_one(
                {
                    "titre": self.titre,
                    "date": self.date,
                    "description": self.description,
                    "url": self.url_telechargement,
                    "audio_rel_filename": self.audio_rel_filename,
                    "transcription": self.transcription,
                    "type": self.type,
                    "duree": self.duree,
                }
            )
            return 1
        else:
            print(
                f"Episode du {Episode.get_string_from_date(self.date, format=LOG_DATE_FORMAT)} deja existant"
            )
            mongolog("update", self.collection.name, message_log)
            return 0

    def remove(self):
        """
        Remove the episode from the database.
        """
        message_log = f"{Episode.get_string_from_date(self.date, format=LOG_DATE_FORMAT)} - {self.titre}"
        self.collection.delete_one({"titre": self.titre, "date": self.date})
        mongolog("delete", self.collection.name, message_log)

    def get_oid(self) -> ObjectId:
        """
        Get the object id of the episode.
        :return: The object id of the episode. (bson.ObjectId)
        None if does not exist.
        """
        document = self.collection.find_one({"titre": self.titre, "date": self.date})
        if document:
            return document["_id"]
        else:
            return None

    @staticmethod
    def get_date_from_string(date: str) -> datetime:
        """
        Get the datetime object from a string.
        :param date: The date string.
        :return: The datetime object.
        """
        return datetime.strptime(date, DATE_FORMAT)

    @staticmethod
    def get_string_from_date(date: datetime, format: str = None) -> str:
        """
        Get the string from a datetime object.
        :param date: The datetime object.
        :param format: The format of the string. default: None and DATE_FORMAT will be used.
        :return: The date string.
        """
        if format is not None:
            return date.strftime(format)
        else:
            return date.strftime(DATE_FORMAT)

    def __str__(self):
        return f"""
        _oid: {self.get_oid()}
        Date: {Episode.get_string_from_date(self.date, format=LOG_DATE_FORMAT)}
        Titre: {self.titre}
        Description: {self.description}
        URL de téléchargement: {self.url_telechargement}
        Fichier audio: {self.audio_rel_filename}
        Duree: {self.duree} en secondes 
        Transcription: {self.transcription[:100] if self.transcription else 'No transcription yet available'}...
        """

    def __repr__(self):
        return self.__str__()

    def download_audio(self, verbose=False):
        """
        based on url_telechargement
        will download audio file and store in AUDIO_PATH/year
        """
        if self.url_telechargement is None:
            return
        year = str(self.date.year)
        full_audio_path = get_audio_path(AUDIO_PATH, year)
        full_filename = os.path.join(
            full_audio_path, os.path.basename(self.url_telechargement)
        )
        self.audio_rel_filename = os.path.relpath(
            full_filename, get_audio_path(AUDIO_PATH, year="")
        )
        # Vérification si le fichier existe déjà
        if not os.path.exists(full_filename):
            if verbose:
                print(
                    f"Téléchargement de {self.url_telechargement} vers {full_filename}"
                )
            response = requests.get(self.url_telechargement)
            with open(full_filename, "wb") as file:
                file.write(response.content)
        else:
            if verbose:
                print(f"Le fichier {full_filename} existe déjà. Ignoré.")

    def set_transcription(self, verbose=False):
        """
        based on audio file, use whisper model to get transcription
        if transcription already exists, do nothing
        if audio file does not exist, do nothing
        save transcription in DB
        """
        if self.transcription is not None:
            if verbose:
                print("Transcription existe deja")
            return
        mp3_fullfilename = get_audio_path(AUDIO_PATH, year="") + self.audio_rel_filename
        self.transcription = extract_whisper(mp3_fullfilename)
        self.collection.update_one(
            {"_id": self.get_oid()}, {"$set": {"transcription": self.transcription}}
        )


# %% py mongo helper episodes.ipynb 9
from feedparser.util import FeedParserDict
from transformers import pipeline

RSS_DUREE_MINI_MINUTES = 15
RSS_DATE_FORMAT = "%a, %d %b %Y %H:%M:%S %z"  # "Sun, 29 Dec 2024 10:59:39 +0100"


class RSS_episode(Episode):
    def __init__(self, date: str, titre: str):
        """
        RSS_episode is a class that represents an RSS episode in the database episodes.
        :param date: The date for this episode at the format "2024-12-22T09:59:39.000+00:00" parsed by "%Y-%m-%dT%H:%M:%S.%f%z".
        :param titre: The title of this episode.
        """
        super().__init__(date, titre)

    @classmethod
    def from_feed_entry(cls, feed_entry: FeedParserDict) -> "RSS_episode":
        """
        Create an RSS episode from a feed entry.
        :param feed_entry: The feed entry.
        :return: The RSS episode.
        """

        date_rss = datetime.strptime(feed_entry.published, RSS_DATE_FORMAT)
        date_rss_str = cls.get_string_from_date(date_rss, DATE_FORMAT)
        inst = cls(
            date=date_rss_str,
            titre=feed_entry.title,
        )
        inst.description = feed_entry.summary

        for link in feed_entry.links:
            if link.type == "audio/mpeg":
                inst.url_telechargement = link.href
                break

        # self.audio_rel_filename = None
        # self.transcription = None
        inst.type = cls.set_titre(inst.titre + " " + inst.description)
        inst.duree = cls.get_duree_in_seconds(feed_entry.itunes_duration)  # in seconds

        return inst

    @staticmethod
    def get_duree_in_seconds(duree: str) -> int:
        """
        Get the duration in seconds from a string.
        :param duree: The duration string at the format "HH:MM:SS" or "HH:MM".
        :return: The duration in seconds.
        """
        duree = duree.split(":")
        if len(duree) == 3:
            return int(duree[0]) * 3600 + int(duree[1]) * 60 + int(duree[2])
        elif len(duree) == 2:
            return int(duree[0]) * 60 + int(duree[1])
        else:
            return int(duree[0])

    def keep(self) -> int:
        """
        Keep the episode in the database.
        only if duration > RSS_DUREE_MINI_MINUTES * 60
        only if type == livres

        retourne 1 si 1 entree est creee en base
        0 sinon
        """
        if (self.duree > RSS_DUREE_MINI_MINUTES * 60) & (self.type == "livres"):
            return super().keep()
        else:
            print(
                f"Episode du {Episode.get_string_from_date(self.date, format=LOG_DATE_FORMAT)} ignored: Duree: {self.duree}, Type: {self.type}"
            )
            return 0

    @staticmethod
    def set_titre(description: str) -> str:
        """
        use bart meta model from huggingface to classify episodes from
        ["livres", "films", "pièces de théâtre"]
        """
        # Charger le pipeline de classification de texte
        classifier = pipeline(
            "zero-shot-classification", model="facebook/bart-large-mnli"
        )
        # Labels possibles
        labels = ["livres", "films", "pièces de théâtre"]

        result = classifier(description, labels)
        return result["labels"][0]
