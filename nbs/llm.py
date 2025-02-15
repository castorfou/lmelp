# AUTOGENERATED! DO NOT EDIT! File to edit: py llm helper.ipynb.

# %% auto 0
__all__ = [
    "load_env",
    "get_gemini_api_key",
    "get_openai_api_key",
    "get_google_projectID",
    "get_google_auth_file",
    "get_azure_openai_keys",
    "get_azure_llm",
    "get_gemini_llm",
    "get_vertex_llm",
]

# %% py llm helper.ipynb 1
from dotenv import load_dotenv, find_dotenv
import os


def load_env():
    """
    Load environment variables from a .env file.

    This function uses `dotenv` to find and load environment variables
    from a .env file into the environment.
    """
    _ = load_dotenv(find_dotenv())


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


# %% py llm helper.ipynb 5
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core import Settings


def get_azure_llm(engine="gpt-4o") -> AzureOpenAI:
    """
    Get the Azure OpenAI language model.

    Args:
        engine (str): The engine to use for the Azure OpenAI model. Default is "gpt-4o".

    Returns:
        AzureOpenAI: An instance of the AzureOpenAI language model.
    """
    AZURE_API_KEY, AZURE_ENDPOINT, AZURE_API_VERSION = get_azure_openai_keys()
    llm = AzureOpenAI(
        engine=engine,
        api_key=AZURE_API_KEY,
        azure_endpoint=AZURE_ENDPOINT,
        api_version=AZURE_API_VERSION,
        # increase timeout to 120 seconds to avoid timeout on scripts/store_all_auteurs_from_all_episodes.py
        timeout=120.0,
    )
    Settings.llm = llm
    return llm


# %% py llm helper.ipynb 8
import google.generativeai as genai


def get_gemini_llm(model="gemini-1.5-flash") -> genai.GenerativeModel:
    """
    Get the Gemini language model.

    This function configures the Gemini API using the API key obtained from the environment variables
    and returns an instance of the GenerativeModel.

    Args:
        model (str): The model to use for the Gemini language model. Default is "gemini-1.5-flash".

    Returns:
        GenerativeModel: An instance of the GenerativeModel.
    """
    genai.configure(api_key=get_gemini_api_key())
    llm = genai.GenerativeModel(model)
    return llm


# %% py llm helper.ipynb 11
# from llama_index.llms.gemini import Gemini
# from llama_index.core import Settings


# def get_gemini_llamaindex_llm(model="models/gemini-1.5-flash") -> Gemini:
#     """
#     Get the Gemini language model for LlamaIndex.

#     This function configures the Gemini API using the API key obtained from the environment variables
#     and returns an instance of the Gemini model for LlamaIndex.

#     Args:
#         model (str): The model to use for the Gemini language model. Default is "models/gemini-1.5-flash".

#     Returns:
#         Gemini: An instance of the Gemini language model.
#     """
#     genai.configure(api_key=get_gemini_api_key())
#     llm = Gemini(model=model, api_key=get_gemini_api_key())
#     Settings.llm = llm
#     return llm

# %% py llm helper.ipynb 14
from llama_index.core import Settings
from llama_index.llms.vertex import Vertex
from google.oauth2 import service_account


def get_vertex_llm(model="gemini-1.5-flash-001") -> Vertex:
    """
    Get the Vertex language model.

    This function configures the Vertex API using the project ID and API key obtained from the environment variables
    and returns an instance of the Vertex model.

    Args:
        model (str): The model to use for the Vertex language model. Default is "gemini-1.5-flash-001".

    Returns:
        Vertex: An instance of the Vertex language model.
    """
    # Set up necessary variables
    credentials = {
        "project_id": get_google_projectID(),
        "api_key": get_gemini_api_key(),
    }

    # filename = get_google_auth_file()
    # credentials_service: service_account.Credentials = (
    #     service_account.Credentials.from_service_account_file(filename)
    # )

    # Create an instance of the Vertex class
    llm = Vertex(
        model=model,
        project=credentials["project_id"],
        credentials=credentials,
        context_window=100000,
    )
    # llm = Vertex(
    #     model=model,
    #     project=credentials_service.project_id,
    #     credentials=credentials_service,
    #     context_window=100000,    )
    Settings.llm = llm
    return llm
