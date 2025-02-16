import sys
import os
import dbus
import time
import warnings

# Ajouter le chemin du répertoire 'nbs' à sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../nbs")))

# il faudra executer ce script dans le repo (utilisation de la lib git)
# et avec l'interpreter python whisper

from mongo_episode import Episodes


def print_duree_traitement(start_time, end_time):
    # Calculer la durée
    duration = end_time - start_time

    # Convertir la durée en heures, minutes et secondes
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Afficher la durée formatée
    if hours > 0:
        print(
            f"Le traitement a pris {int(hours)} heures, {int(minutes)} minutes et {int(seconds)} secondes."
        )
    else:
        print(
            f"Le traitement a pris {int(minutes)} minutes et {int(seconds)} secondes."
        )


def main():

    episodes = Episodes()
    episodes.get_missing_transcriptions()
    if len(episodes) > 0:
        # on prend le dernier
        episode = episodes[-1]
        print("On va recuperer la transcription de l'episode \n")
        print(episode)
        start_time = time.time()
        episode.set_transcription(verbose=True)
        end_time = time.time()
        print_duree_traitement(start_time=start_time, end_time=end_time)
    else:
        print("Il n'y a pas d'episodes sans transcriptions")


if __name__ == "__main__":
    # Ignorer les warnings
    warnings.filterwarnings("ignore")
    main()
