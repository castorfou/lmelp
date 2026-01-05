#!/bin/bash

# Vérification du nombre d'arguments
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <fichier_mp3>"
    echo "Exemple: $0 audios/extrait_5min.mp3"
    exit 1
fi

# Récupération du chemin du fichier MP3
mp3_file="$1"

# Vérification que le fichier existe
if [ ! -f "$mp3_file" ]; then
    echo "Erreur: Le fichier '$mp3_file' n'existe pas."
    exit 1
fi

# Extraction du nom de base (sans extension)
base_name=$(basename "$mp3_file" .mp3)
dir_name=$(dirname "$mp3_file")

# Construction du chemin de sortie SANS .txt (le conteneur l'ajoute automatiquement)
output_txt="${dir_name}/${base_name}"

# Exécution de la commande Docker
docker run --rm \
  -v "$(pwd)/models:/models" \
  -v "$(pwd)/audios:/audios" \
  --entrypoint /bin/sh \
  ghcr.io/ggerganov/whisper.cpp:main \
  -c "/app/build/bin/whisper-cli --model /models/ggml-large-v3.bin --file /audios/$(basename "$mp3_file") --language fr --output-txt --output-file /audios/$(basename "$output_txt")" > logs.txt 2>&1

# Message de confirmation
echo "Transcription terminée. Résultat dans : ${output_txt}.txt"

