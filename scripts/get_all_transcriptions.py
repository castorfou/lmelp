import sys
import os
import dbus
import time
import warnings

# Ajouter le chemin du répertoire 'nbs' à sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../nbs")))

# il faudra executer ce script dans le repo (utilisation de la lib git)
# et avec l'interpreter python whisper

from mongo_episode import Episodes, Episode


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

    # Connexion au bus D-Bus
    bus = dbus.SessionBus()
    proxy = bus.get_object(
        "org.freedesktop.ScreenSaver", "/org/freedesktop/ScreenSaver"
    )
    interface = dbus.Interface(proxy, "org.freedesktop.ScreenSaver")

    episodes = Episodes()
    episodes.get_missing_transcriptions()

    for oid_episode in reversed(episodes):
        episode = Episode.from_oid(oid_episode)
        # Prévenir la mise en veille
        cookie = interface.Inhibit("my_script", "Long running process")
        print("Mise en veille deactivee")
        print("On va recuperer la transcription de l'episode \n")
        print(episode)
        try:
            # Votre traitement long ici
            start_time = time.time()
            episode.set_transcription(verbose=True)
            end_time = time.time()
            print_duree_traitement(start_time=start_time, end_time=end_time)

        finally:
            # Réactiver la mise en veille normale
            print("Mise en veille normale reactivee")
            interface.UnInhibit(cookie)
        print(episodes)


if __name__ == "__main__":
    # Ignorer les warnings
    warnings.filterwarnings("ignore")
    main()
