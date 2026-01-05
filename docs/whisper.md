# Module whisper

::: whisper
    rendering:
      show_root_full_path: false

## whisper.cpp (Docker)

- Script: `scripts/whisper.cpp/whisper.sh` exécute `whisper-cli` via `ghcr.io/ggml-org/whisper.cpp`.
- Pré-requis: Docker actif, modèle `models/ggml-large-v3.bin`, audio stocké dans `audios/`.
- Variables optionnelles: `MODELS_DIR`, `AUDIO_ROOT`, `WHISPER_LOG_DIR`, `WHISPER_DOCKER_IMAGE`, `WHISPER_MODEL_FILENAME`, `WHISPER_THREADS`, `WHISPER_ENTRYPOINT`, `WHISPER_CPP_SCRIPT` (chemin du script custom).
- Journalisation: chaque exécution crée `logs/whisper_<chemin>_<timestamp>.log` et le script affiche `LOG_FILE=...` pour consultation rapide.
- Exécution manuelle: `bash scripts/whisper.cpp/whisper.sh audios/1992/episode.mp3` confirme la transcription (`audios/.../episode.txt`).

## Intégration Python

- `extract_whisper_cpp()` vérifie Docker + modèle, lance le script, lit le `.txt` généré et retourne `(texte, chemin_log)`.
- `Episode.set_transcription()` tente whisper.cpp en priorité (message + lien log si `verbose`), puis bascule sur `extract_whisper_long()` de Hugging Face si l'étape Docker échoue.
- Le cache `.txt` dans `audios/...` reste inchangé : supprimer le fichier rejouera la chaîne whisper.cpp → fallback HF.
- Option `keep_cache=True` continue à alimenter MongoDB et le cache disque une fois la transcription consolidée.

## Dépannage

- `Erreur: Docker est requis` → installer/configurer Docker ou exécuter dans un environnement compatible.
- `Le modèle Whisper ... est introuvable` → déposer `ggml-large-v3.bin` dans `models/` (ou redéfinir `MODELS_DIR`).
- `whisper.cpp indisponible ... fallback Hugging Face` → voir le fichier de log indiqué pour diagnostiquer (mémoire, threads, etc.).