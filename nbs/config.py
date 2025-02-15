# AUTOGENERATED! DO NOT EDIT! File to edit: py config.ipynb.

# %% auto 0
__all__ = [
    "AUDIO_PATH",
    "load_env",
    "get_RSS_URL",
    "get_gemini_api_key",
    "get_openai_api_key",
    "get_google_projectID",
    "get_google_auth_file",
    "get_azure_openai_keys",
    "get_git_root",
    "get_audio_path",
    "get_DB_VARS",
]

# %% py config.ipynb 1
from dotenv import load_dotenv, find_dotenv
import os


def load_env() -> None:
    """
    Charge les variables d'environnement à partir d'un fichier .env.
    """
    _ = load_dotenv(find_dotenv())


# %% py config.ipynb 3
def get_RSS_URL() -> str:
    """
    Récupère l'URL du flux RSS à partir des variables d'environnement.

    Returns:
        str: L'URL du flux RSS. Si la variable d'environnement `RSS_LMELP_URL` n'est pas définie,
        retourne une URL par défaut.
    """
    load_env()
    RSS_LMELP_URL = os.getenv("RSS_LMELP_URL")
    if RSS_LMELP_URL is None:
        RSS_LMELP_URL = "https://radiofrance-podcast.net/podcast09/rss_14007.xml"
    return RSS_LMELP_URL


# %% py config.ipynb 6
def get_gemini_api_key() -> str:
    """
    Get the Gemini API key from environment variables.

    Returns:
        str: The Gemini API key.
    """
    load_env()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    return gemini_api_key


def get_openai_api_key() -> str:
    """
    Get the OpenAI API key from environment variables.

    Returns:
        str: The OpenAI API key.
    """
    load_env()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    return openai_api_key


def get_google_projectID() -> str:
    """
    Get the Google Project ID from environment variables.

    Returns:
        str: The Google Project ID.
    """
    load_env()
    google_projectID = os.getenv("GOOGLE_PROJECT_ID")
    return google_projectID


def get_google_auth_file() -> str:
    """
    Get the Google authentication file path from environment variables.

    Returns:
        str: The path to the Google authentication file.
    """
    load_env()
    google_auth_file = os.getenv("GOOGLE_AUTH_FILE")
    return google_auth_file


def get_azure_openai_keys() -> tuple[str, str, str]:
    """
    Get the Azure OpenAI keys from environment variables.

    Returns:
        tuple: A tuple containing the Azure API key, endpoint, and API version.
    """
    load_env()
    azure_api_key = os.getenv("AZURE_API_KEY")
    azure_endpoint = os.getenv("AZURE_ENDPOINT")
    azure_api_version = os.getenv("AZURE_API_VERSION")
    return azure_api_key, azure_endpoint, azure_api_version


# %% py config.ipynb 8
from git import Repo


def get_git_root(path: str) -> str:
    """Retrieves the root directory of the Git repository.

    Args:
        path (str): The current working directory.

    Returns:
        str: The root directory of the Git repository.
    """
    git_repo = Repo(path, search_parent_directories=True)
    return git_repo.git.rev_parse("--show-toplevel")


# %% py config.ipynb 10
import os

AUDIO_PATH: str = "audios"


def get_audio_path(audio_path: str = AUDIO_PATH, year: str = "2024") -> str:
    """Returns the full path to the audio files by appending the year as a subdirectory.

    If the directory does not exist, it is created.

    Args:
        audio_path (str): Relative path to the audio files.
        year (str): The year used as a subdirectory (default "2024").

    Returns:
        str: The full path to the corresponding audio directory.

    Example:
        >>> path = get_audio_path("audios", "2024")
    """

    project_root: str = get_git_root(os.getcwd())
    full_audio_path: str = os.path.join(project_root, audio_path, year)

    # Create the directory if it does not exist
    if not os.path.exists(full_audio_path):
        os.makedirs(full_audio_path)

    return full_audio_path


# %% py config.ipynb 13
import os
from typing import Tuple, Optional


def get_DB_VARS() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Retrieve the database configuration variables from the environment.

    This function loads the environment variables and retrieves the following
    database configuration variables:
        - DB_HOST: The hostname for the database.
        - DB_NAME: The name of the database.
        - DB_LOGS: A flag indicating if logging is enabled.

    Returns:
        Tuple[Optional[str], Optional[str], Optional[str]]:
            A tuple containing (DB_HOST, DB_NAME, DB_LOGS).
    """
    load_env()
    DB_HOST: Optional[str] = os.getenv("DB_HOST")
    DB_NAME: Optional[str] = os.getenv("DB_NAME")
    DB_LOGS: Optional[str] = os.getenv("DB_LOGS")
    return DB_HOST, DB_NAME, DB_LOGS
