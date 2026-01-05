#!/bin/bash

set -euo pipefail

usage() {
  echo "Usage: $0 <fichier_mp3>"
  echo "Exemple: $0 audios/1992/episode.mp3"
}

if [ "$#" -ne 1 ]; then
  usage
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "Erreur: Docker est requis pour exécuter whisper.cpp" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

MODELS_DIR="${MODELS_DIR:-${REPO_ROOT}/models}"
AUDIO_ROOT="${AUDIO_ROOT:-${REPO_ROOT}/audios}"
LOG_DIR="${WHISPER_LOG_DIR:-${REPO_ROOT}/logs}"
DOCKER_IMAGE="${WHISPER_DOCKER_IMAGE:-ghcr.io/ggml-org/whisper.cpp:main-cuda}"
MODEL_FILENAME="${WHISPER_MODEL_FILENAME:-ggml-large-v3.bin}"
MODEL_URL="${WHISPER_MODEL_URL:-https://huggingface.co/ggerganov/whisper.cpp/resolve/main/${MODEL_FILENAME}?download=1}"
WHISPER_THREADS="${WHISPER_THREADS:-}"
WHISPER_BINARY="${WHISPER_ENTRYPOINT:-/app/build/bin/whisper-cli}"

mkdir -p "$LOG_DIR"
mkdir -p "$MODELS_DIR"

download_model() {
  local tmp_file
  echo "Modèle introuvable, téléchargement depuis $MODEL_URL ..."
  tmp_file="$(mktemp "${MODELS_DIR}/.${MODEL_FILENAME}.XXXX")"
  if command -v curl >/dev/null 2>&1; then
    curl -L --fail --progress-bar "$MODEL_URL" -o "$tmp_file"
  elif command -v wget >/dev/null 2>&1; then
    wget -O "$tmp_file" "$MODEL_URL"
  else
    echo "Erreur: ni curl ni wget n'est disponible pour télécharger le modèle." >&2
    exit 1
  fi
  mv "$tmp_file" "$model_path"
}

mp3_file="$1"
mp3_abs="$(realpath "$mp3_file")"

if [ ! -f "$mp3_abs" ]; then
  echo "Erreur: Le fichier '$mp3_file' n'existe pas." >&2
  exit 1
fi

if [[ "$mp3_abs" != "$AUDIO_ROOT"/* ]]; then
  echo "Erreur: Le fichier audio doit se trouver dans '$AUDIO_ROOT'." >&2
  exit 1
fi

model_path="$MODELS_DIR/$MODEL_FILENAME"
if [ ! -f "$model_path" ]; then
  download_model
fi

rel_path="${mp3_abs#${AUDIO_ROOT}/}"
rel_dir="$(dirname "$rel_path")"
rel_stem="${rel_path%.*}"

cleanup_tmp_audio=""

convert_to_wav() {
  if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "Erreur: ffmpeg est requis pour convertir les fichiers audio." >&2
    exit 1
  fi

  local input_path="$1"
  local target_dir="$(dirname "$input_path")"
  local tmp_file
  tmp_file="$(mktemp -p "$target_dir" .whisper_tmp_XXXXXX.wav)"
  ffmpeg -hide_banner -loglevel error -y -i "$input_path" -ar 16000 -ac 1 "$tmp_file"
  cleanup_tmp_audio="$tmp_file"
  mp3_abs="$tmp_file"
}

input_ext="${mp3_abs##*.}"
input_ext="${input_ext,,}"
if [ "$input_ext" != "wav" ]; then
  convert_to_wav "$mp3_abs"
fi

trap 'if [ -n "$cleanup_tmp_audio" ] && [ -f "$cleanup_tmp_audio" ]; then rm -f "$cleanup_tmp_audio"; fi' EXIT

working_rel_path="${mp3_abs#${AUDIO_ROOT}/}"

timestamp="$(date +%Y%m%dT%H%M%S)"
safe_name="$(echo "$rel_stem" | tr '/ ' '__')"
log_file="${LOG_DIR}/whisper_${safe_name}_${timestamp}.log"

output_rel="/audios/${rel_stem}"
mp3_rel="/audios/${working_rel_path}"

docker_cmd=(
    "--model" "/models/${MODEL_FILENAME}"
    "--file" "$mp3_rel"
    "--language" "fr"
    "--output-txt"
    "--output-file" "$output_rel"
)

if [ -n "$WHISPER_THREADS" ]; then
    docker_cmd+=("--threads" "$WHISPER_THREADS")
fi

docker run --rm \
  -v "${MODELS_DIR}:/models" \
  -v "${AUDIO_ROOT}:/audios" \
  --entrypoint "$WHISPER_BINARY" \
  "$DOCKER_IMAGE" \
  "${docker_cmd[@]}" \
  >"$log_file" 2>&1

result_path="${AUDIO_ROOT}/${rel_stem}.txt"

if [ ! -f "$result_path" ]; then
  echo "Erreur: le fichier de transcription attendu '$result_path' est introuvable." >&2
  exit 1
fi

echo "Transcription terminée. Résultat dans : ${result_path}"
echo "LOG_FILE=${log_file}"

