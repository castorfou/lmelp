import sys
import os
import argparse
import datetime
import pandas as pd

# Ajouter le chemin du répertoire 'nbs' à sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../nbs")))

from mongo_episode import Episode, Episodes
from mongo_auteur import Auteur, AuthorChecker

# il faudra executer ce script dans le repo (utilisation de la lib git)
# et avec l'interpreter python whisper


def ajoute_auteurs(episode: Episode):
    affiche_episode = f"""
    Date: {episode.date.strftime("%d %b %Y")}
    Titre: {episode.titre}
    Description: {episode.description}

    """
    print(affiche_episode)

    auteurs = episode.get_all_auteurs()
    print(f"La liste des auteurs : {auteurs}\n")

    ac = AuthorChecker(episode)
    auteur_traitement_df = pd.DataFrame(
        columns=["auteur_corrige", "detection", "existait_en_base", "anomalie"]
    )
    verbose = False
    analyse_dict = {}

    for auteur in auteurs:
        auteur_corrige_dict = ac.check_author(
            auteur, return_details=True, verbose=verbose
        )
        if verbose:
            print(auteur_corrige_dict)
        # check_author retourne None dans author_corrected si le process via rss:metadata, db, llm, web search n'a rien renvoye
        # c'est donc une anomalie
        anomalie = True if auteur_corrige_dict["author_corrected"] is None else False
        # dans auteur_corrige c'est le nom de l'auteur si il est different de l'original sinon None
        auteur_corrige = (
            auteur_corrige_dict["author_corrected"]
            if auteur_corrige_dict["author_corrected"]
            != auteur_corrige_dict["author_original"]
            else None
        )
        nom_auteur = auteur_corrige_dict["author_corrected"] if not None else auteur
        # a quel endroit a ete detecte l'auteur (rss:metadata, db, llm, web search)
        detection = auteur_corrige_dict["source"]
        existait_en_base = False if anomalie else Auteur(nom_auteur).exists()
        auteur_traitement_df.loc[auteur] = [
            auteur_corrige,
            detection,
            existait_en_base,
            anomalie,
        ]
        if not anomalie:
            aut = Auteur(nom_auteur)
            aut.keep()
        else:
            analyse_dict[auteur] = {
                "analyse": auteur_corrige_dict["analyse"],
                "score": auteur_corrige_dict["score"],
            }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="store_all_auteurs_from_all_episodes.py",
        description=(
            "Ce programme récupère les épisodes d'une base de données pour une date donnée, "
            "extrait les auteurs de chaque épisode, vérifie et met à jour ces auteurs dans "
            "la base de données, puis affiche un rapport du traitement effectué."
            "Si une date est fournie, seuls les episodes anterieurs à cette date seront traités."
        ),
    )
    parser.add_argument(
        "-d",
        "--date",
        type=str,
        required=False,
        help="Date of the episode au format francais dd/mm/year",
    )
    args = parser.parse_args()
    if args.date is not None:
        try:
            date = datetime.datetime.strptime(args.date, "%d/%m/%Y")
        except ValueError:
            print(f"Format de date invalide {args.date}. Utiliser le format dd/mm/yyyy")
            sys.exit(1)
    else:
        date = datetime.datetime.now()
    episodes = Episodes().get_entries()
    for episode in episodes:
        if episode.date < date:
            ajoute_auteurs(episode)
