# pour developper

## envs python

creer l'environnement whisper depuis `envs/whisper.txt`
qui contient ce qu il faut pour whisper, feedparser, transformers (huggingface)

creer l'environnement whisper depuis `envs/gemini.txt`
qui contient ce qu il faut pour gemini, dotenv, llamaindex

## pre-commit

`pre-commit install`


## ffmpeg

ffmpeg is required to load audio files from filename

available in snap (4.3.1)

## gemini api key

creer .env a la racine du repo avec
GEMINI_API_KEY=<your api key>

from https://console.cloud.google.com/apis/credentials

et pour gemini llamaindex

GOOGLE_PROJECT_ID

from https://console.cloud.google.com

## db host, db name

creer .env a la racine du repo avec
DB_HOST=localhost # à changer avec nas923 par exemple
DB_NAME="masque_et_la_plume"
DB_LOGS=true # va enregistrer toutes les operations dans la collection logs