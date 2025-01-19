import sys
import os

# Ajouter le chemin du répertoire 'nbs' à sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../nbs")))

# il faudra executer ce script dans le repo (utilisation de la lib git)
# et avec l'interpreter python whisper

from mongo_episode import WEB_episode, Episodes
from web import WebPage


def main():
    legacy_episodes = WebPage()
    for episode in legacy_episodes:
        vieil_episode = WEB_episode.from_webpage_entry(episode)
        vieil_episode.keep()
        print(vieil_episode)

    episodes = Episodes()
    print(episodes)


if __name__ == "__main__":
    main()
