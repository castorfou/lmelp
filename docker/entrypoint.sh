#!/bin/bash
# Entrypoint script for lmelp Docker container
# Supports multiple modes: web (Streamlit) or batch (scripts)

set -e

# Mode d'exécution : web (Streamlit) ou batch (scripts)
MODE=${LMELP_MODE:-web}

echo "=================================="
echo "lmelp - Le Masque et la Plume"
echo "Mode: $MODE"
echo "=================================="

if [ "$MODE" = "web" ]; then
    echo "Starting Streamlit web interface..."
    exec streamlit run ui/lmelp.py \
        --server.port=8501 \
        --server.address=0.0.0.0 \
        --server.headless=true

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
