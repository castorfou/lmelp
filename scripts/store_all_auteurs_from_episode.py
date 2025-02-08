import sys
import os
import argparse
import datetime

# Ajouter le chemin du répertoire 'nbs' à sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../nbs")))

from mongo_episode import Episode
from mongo_auteur import Auteur, AuthorChecker

# il faudra executer ce script dans le repo (utilisation de la lib git)
# et avec l'interpreter python whisper


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--date",
        type=str,
        required=True,
        help="Date of the episode au format francais dd/mm/year",
    )
    args = parser.parse_args()
    try:
        date = datetime.datetime.strptime(args.date, "%d/%m/%Y")
    except ValueError:
        print(f"Format de date invalide {args.date}. Utiliser le format dd/mm/yyyy")
        sys.exit(1)

    episode = Episode.from_date(date=date)
    if not episode:
        print(f"Episode du {date.strftime('%d/%m/%Y')} n'existe pas")
        sys.exit(1)

    print(episode)

    auteurs = episode.get_all_auteurs()
    print(auteurs)

    ac = AuthorChecker(episode)

    for auteur in auteurs:
        auteur_corrige = ac.check_author(auteur)
        if auteur_corrige is not None:
            print(f"{auteur} -> {auteur_corrige}")
            aut = Auteur(auteur_corrige)
            print(f"Est-ce que {aut.nom} existe ? {aut.exists()}")
            aut.keep()
