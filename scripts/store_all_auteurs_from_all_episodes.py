import sys
import os
import argparse
import datetime
import pandas as pd

# Ajouter le chemin du répertoire 'nbs' à sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../nbs")))

from mongo_episode import Episode, Episodes
from mongo_auteur import Auteur, AuthorChecker
from rich import print as rprint
from rich.table import Table

# il faudra executer ce script dans le repo (utilisation de la lib git)
# et avec le devcontainer du repo lmelp

cache_filename = "store_all_auteurs_from_all_episodes.txt"


def prettyprint(auteur_traitement_df, date: datetime.datetime = None):
    table = Table(
        title=(
            f"Table des auteurs {date.strftime('%d %b %Y')}"
            if date
            else "Table des auteurs"
        )
    )
    # Ajout d'une colonne pour l'index (par exemple "Auteur" si l'index correspond au nom)
    table.add_column("Auteur", justify="center", style="bold")
    # Ajout des colonnes du DataFrame
    for column in auteur_traitement_df.columns:
        table.add_column(column, justify="center")
    # Ajout des lignes, incluant l'index en première colonne
    for idx, row in auteur_traitement_df.iterrows():
        table.add_row(str(idx), *[str(item) for item in row])
    rprint(table)


def ajoute_auteurs(episode: Episode, verbose=False):
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
    prettyprint(auteur_traitement_df, date=episode.date)
    if len(analyse_dict) > 0:
        print("\nAnalyse des anomalies\n")
    for auteur, details in analyse_dict.items():
        print(f"{auteur} -> {details['analyse']} (score: {details['score']})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="store_all_auteurs_from_all_episodes.py",
        description=(
            "Ce programme récupère les épisodes d'une base de données pour une date donnée, "
            "extrait les auteurs de chaque épisode, vérifie et met à jour ces auteurs dans "
            "la base de données, puis affiche un rapport du traitement effectué."
            "Si une date est fournie, seuls les episodes posterieurs à cette date seront traités."
            "Si mode verbose, affiche les détails de chaque auteur."
            "si le fichier `store_all_auteurs_from_all_episodes.txt` existe et contient une date, on reprend de cette date"
        ),
    )
    parser.add_argument(
        "-d",
        "--date",
        type=str,
        required=False,
        help="Date of the episode au format francais dd/mm/year",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose mode if you want additional infos",
    )
    args = parser.parse_args()
    if args.date is not None:
        try:
            date = datetime.datetime.strptime(args.date, "%d/%m/%Y")
        except ValueError:
            print(f"Format de date invalide {args.date}. Utiliser le format dd/mm/yyyy")
            sys.exit(1)
    else:
        date = datetime.datetime(1950, 1, 1)

    # lis le contenu du fichier cache_filename s'il existe
    if os.path.exists(cache_filename):
        with open(cache_filename, "r") as f:
            date_cache = datetime.datetime.strptime(f.read(), "%d/%m/%Y")
            print(f"Reprise du traitement à partir de la date {date_cache}")
    else:
        # 1er episode date de 1958
        print(f"Pas de fichier cache")
        date_cache = datetime.datetime(1950, 1, 1)

    # on prend la date la plus recente entre date et date_cache
    date = date if date > date_cache else date_cache
    episodes = Episodes()
    episodes.get_entries({"date": {"$gte": date}})
    for oid_episode in episodes:
        episode = Episode.from_oid(oid_episode)
        if episode.date > date:
            ajoute_auteurs(episode, verbose=args.verbose)
            # on sauvegarde la date de traitement
            # le cache ne contient que cette date, rien d'autre
            with open(cache_filename, "w") as f:
                f.write(episode.date.strftime("%d/%m/%Y"))
    print("Fin du traitement")
