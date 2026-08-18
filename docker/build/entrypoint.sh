#!/bin/bash
# Entrypoint script for lmelp Docker container
# Supports multiple modes: web (Streamlit) or batch (scripts)

set -e

# Le conteneur démarre en root pour pouvoir remapper l'utilisateur non-root
# "appuser" vers l'UID/GID de l'hôte (PUID/PGID, cf. issue #105 : l'UID
# cible diffère selon la machine, ex. 1000 sur laptop vs 1027 sur NAS) et
# chowner les volumes bind-mountés en conséquence, avant de dropper les
# privilèges via gosu. Ce bloc ne s'exécute donc qu'à la première passe
# (root) ; après le "exec gosu appuser", "id -u" ne vaut plus 0 et ce bloc
# est sauté.
if [ "$(id -u)" = "0" ]; then
    PUID=${PUID:-1000}
    PGID=${PGID:-1000}

    CURRENT_UID=$(id -u appuser)
    CURRENT_GID=$(id -g appuser)

    if [ "$PUID" != "$CURRENT_UID" ] || [ "$PGID" != "$CURRENT_GID" ]; then
        groupmod -o -g "$PGID" appuser
        usermod -o -u "$PUID" appuser
    fi

    # chown -R inconditionnel à chaque démarrage : corrige automatiquement
    # les fichiers déjà root:root d'avant ce fix (migration transparente au
    # premier redémarrage du conteneur). Un chown conditionné à la
    # propriété du répertoire racine seul serait trompeur : ce répertoire
    # peut déjà appartenir à PUID:PGID (bind mount créé par l'hôte) alors
    # que des fichiers à l'intérieur sont encore root:root.
    chown -R "$PUID:$PGID" /app/audios /app/db /app/logs

    exec gosu appuser "$0" "$@"
fi

# Mode d'execution : web (Streamlit) ou batch (scripts)
MODE=${LMELP_MODE:-web}

echo "[lmelp] Starting in $MODE mode..."

if [ "$MODE" = "web" ]; then
    exec streamlit run ui/lmelp.py \
        --server.port=8501 \
        --server.address=0.0.0.0 \
        --server.headless=true \
        --logger.level=info

elif [ "$MODE" = "batch-update" ]; then
    echo "Running RSS update script..."
    exec python scripts/update_emissions.py

elif [ "$MODE" = "batch-transcribe" ]; then
    echo "Running transcription script..."
    if [ -n "$EPISODE_ID" ]; then
        echo "Transcribing episode: $EPISODE_ID"
        exec python scripts/get_one_transcription.py "$EPISODE_ID"
    else
        echo "Transcribing all episodes without transcription..."
        exec python scripts/get_all_transcriptions.py
    fi

elif [ "$MODE" = "batch-authors" ]; then
    echo "Running author extraction script..."
    if [ -n "$EPISODE_ID" ]; then
        echo "Extracting authors from episode: $EPISODE_ID"
        exec python scripts/store_all_auteurs_from_episode.py "$EPISODE_ID"
    else
        echo "Extracting authors from all episodes..."
        exec python scripts/store_all_auteurs_from_all_episodes.py
    fi

else
    echo "ERROR: Unknown mode: $MODE"
    echo ""
    echo "Available modes:"
    echo "  web              - Start Streamlit web interface (default)"
    echo "  batch-update     - Update episodes from RSS feed"
    echo "  batch-transcribe - Transcribe episodes (set EPISODE_ID for specific episode)"
    echo "  batch-authors    - Extract authors from episodes (set EPISODE_ID for specific episode)"
    echo ""
    echo "Usage:"
    echo "  docker run -e LMELP_MODE=web lmelp"
    echo "  docker run -e LMELP_MODE=batch-update lmelp"
    echo "  docker run -e LMELP_MODE=batch-transcribe -e EPISODE_ID=123 lmelp"
    exit 1
fi
