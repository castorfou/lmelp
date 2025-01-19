import streamlit as st
from git import Repo
import os


def get_git_root(path):
    git_repo = Repo(path, search_parent_directories=True)
    return git_repo.git.rev_parse("--show-toplevel")


project_root = get_git_root(os.getcwd())


def afficher_episodes():
    st.write("### Épisodes")
    st.write("Liste des épisodes du Masque et la Plume.")
    # Ajoutez ici le code pour afficher les épisodes


afficher_episodes()

st.write(project_root)
