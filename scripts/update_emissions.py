import sys
import os

# Ajouter le chemin du répertoire 'nbs' à sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../nbs")))

# il faudra executer ce script dans le repo (utilisation de la lib git)
# et avec l'interpreter python whisper

from mongo_episode import Episode
from rss import Podcast


def main():
    podcast = Podcast()
    podcast.store_last_large_episodes()


if __name__ == "__main__":
    main()
