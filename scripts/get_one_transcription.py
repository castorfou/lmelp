import sys
import os
import dbus

# Ajouter le chemin du répertoire 'nbs' à sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../nbs")))

# il faudra executer ce script dans le repo (utilisation de la lib git)
# et avec l'interpreter python whisper

from mongo_episode import Episodes


def main():

    # Connexion au bus D-Bus
    bus = dbus.SessionBus()
    proxy = bus.get_object(
        "org.freedesktop.ScreenSaver", "/org/freedesktop/ScreenSaver"
    )
    interface = dbus.Interface(proxy, "org.freedesktop.ScreenSaver")

    # Prévenir la mise en veille
    cookie = interface.Inhibit("my_script", "Long running process")

    episodes = Episodes()
    print(episodes)
    miss_transcriptions = episodes.get_missing_transcriptions()
    if len(miss_transcriptions) > 0:
        # on prend le dernier
        miss_transcription = miss_transcriptions[-1]
        try:
            # Votre traitement long ici
            miss_transcription.set_transcription(verbose=True)
        finally:
            # Réactiver la mise en veille normale
            interface.UnInhibit(cookie)
    print(episodes)


if __name__ == "__main__":
    main()
