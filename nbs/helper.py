# AUTOGENERATED! DO NOT EDIT! File to edit: helper.ipynb.

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
    "get_gemini_llamaindex_llm",
    "get_vertex_llm",
]

# %% helper.ipynb 1
from dotenv import load_dotenv, find_dotenv
import os


def load_env():
    _ = load_dotenv(find_dotenv())


def get_gemini_api_key():
    load_env()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    return gemini_api_key


def get_openai_api_key():
    load_env()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    return openai_api_key


def get_google_projectID():
    load_env()
    google_projectID = os.getenv("GOOGLE_PROJECT_ID")
    return google_projectID


def get_google_auth_file():
    load_env()
    google_auth_file = os.getenv("GOOGLE_AUTH_FILE")
    return google_auth_file


def get_azure_openai_keys():
    load_env()
    azure_api_key = os.getenv("AZURE_API_KEY")
    azure_endpoint = os.getenv("AZURE_ENDPOINT")
    azure_api_version = os.getenv("AZURE_API_VERSION")
    return azure_api_key, azure_endpoint, azure_api_version


# %% helper.ipynb 5
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core import Settings


def get_azure_llm(engine="gpt-4o"):
    AZURE_API_KEY, AZURE_ENDPOINT, AZURE_API_VERSION = get_azure_openai_keys()
    llm = AzureOpenAI(
        engine=engine,
        api_key=AZURE_API_KEY,
        azure_endpoint=AZURE_ENDPOINT,
        api_version=AZURE_API_VERSION,
    )
    Settings.llm = llm
    return llm


# %% helper.ipynb 8
import google.generativeai as genai


def get_gemini_llm(model="gemini-1.5-flash"):
    genai.configure(api_key=get_gemini_api_key())
    llm = genai.GenerativeModel(model)
    return llm


# %% helper.ipynb 11
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings


def get_gemini_llamaindex_llm(model="models/gemini-1.5-flash"):
    genai.configure(api_key=get_gemini_api_key())
    llm = Gemini(model=model, api_key=get_gemini_api_key())
    Settings.llm = llm
    return llm


# %% helper.ipynb 14
from llama_index.core import Settings
from llama_index.llms.vertex import Vertex
from google.oauth2 import service_account


def get_vertex_llm(model="gemini-1.5-flash-001"):

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
