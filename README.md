- [pour developper 💻](#pour-developper-)
  - [environnements de dev python 🐍](#environnements-de-dev-python-)
  - [pre-commit ⏱️](#pre-commit-️)
  - [config vscode 🖥️](#config-vscode-️)
- [pour utiliser 🚀](#pour-utiliser-)
  - [ffmpeg 🎞️](#ffmpeg-️)
  - [locale FR 🇫🇷](#locale-fr-)
  - [ulimit ⚙️](#ulimit-️)
  - [`.env` 🌐](#env-)
    - [rss info 🎙️](#rss-info-️)
    - [web info 🌍](#web-info-)
    - [db info 🗄️](#db-info-️)
    - [llm, llamaindex 🤖](#llm-llamaindex-)
    - [SerpApi 🔍](#serpapi-)
  - [streamlit 🖱️](#streamlit-️)


# pour developper 💻

## environnements de dev python 🐍

vscode utilisera automatiquement le devcontainer definit dans le repo sous `.devcontainer`

je garde quand meme le script de creation d'environnement whisper depuis `envs/whisper.txt` ✨  qui contient ce qu il faut pour whisper, feedparser, transformers (huggingface), dotenv, mongo, streamlit 🛠️

## pre-commit ⏱️

dans devcontainer, pre-commit est deja configure sinon

`pre-commit install` ✅

## config vscode 🖥️

en cas de message `"Visual Studio Code is unable to watch for file changes in this large workspace" (error ENOSPC)` [see vscode linux page](https://code.visualstudio.com/docs/setup/linux#_visual-studio-code-is-unable-to-watch-for-file-changes-in-this-large-workspace-error-enospc) ⚠️

```bash
# add fs.inotify.max_user_watches=524288 to /etc/sysctl.conf
sudo sysctl -p # to apply directly
cat /proc/sys/fs/inotify/max_user_watches # to control it is applied
```
  
or add `files.watcherExclude` directive in `.vscode/settings.json` 📁

# pour utiliser 🚀

## ffmpeg 🎞️

ffmpeg is required to load audio files from filename for whisper use (transcription d'un mp3) 🎧

install, it is available in snap (4.3.1) 📦

## locale FR 🇫🇷

en cas d'erreur de type `locale.Error: unsupported locale setting` ❗

verifier avec `locale -a` que `fr_FR.UTF-8` soit installée. 🔍

Sinon le faire avec 

```bash
sudo apt-get install language-pack-fr-base
locale -a
```

## ulimit ⚙️

j'ai du augmenter l'ulimit de mon systeme pour utiliser whisper pour eviter l'erreur `Too many open files` 🚫

Avec ce parametre je n'ai plus le probleme: `ulimit -n 4096` ✔️  
Je l'ai ajoute dans `.zshrc` 📝

## `.env` 🌐

https://pypi.org/project/python-dotenv/ 💡

> Python-dotenv reads key-value pairs from a .env file and can set them as environment variables. It helps in the development of applications following the 12-factor principles. 📋

creer `.env` à la racine du repo avec 🏗️

### rss info 🎙️

L'adresse du flux RSS du podcast du Masque et la Plume 🎧

si absent `https://radiofrance-podcast.net/podcast09/rss_14007.xml` est utilisé par defaut 🔄  

```
RSS_LMELP_URL=https://radiofrance-podcast.net/podcast09/rss_14007.xml
```

### web info 🌍

Le lien vers la page web stockee du masque listant les episodes "legacy" historiques 📜

si absent `db/À écouter plus tard I Radio France/À écouter plus tard I Radio France.html` est utilisé par defaut 🔄  

```
WEB_LMELP_FILENAME=db/À écouter plus tard I Radio France/À écouter plus tard I Radio France.html
```

### db info 🗄️

pour tout ce qui concerne la base mongo 🛢️

```
DB_HOST=localhost # à changer avec nas923 par exemple
DB_NAME="masque_et_la_plume"
DB_LOGS=true # si présent et valant true, va enregistrer toutes les operations dans la collection logs
```

### llm, llamaindex 🤖

```
# gemini 
GEMINI_API_KEY=
# gemini vertex
GOOGLE_PROJECT_ID=
GOOGLE_AUTH_FILE=

# openai
OPENAI_API_KEY=

# azure openai
AZURE_API_KEY=
AZURE_ENDPOINT=
AZURE_API_VERSION=
```

gemini llm, GEMINI_API_KEY dispo à 🚀

from https://console.cloud.google.com/apis/credentials 🔑

gemini vertex (llamaindex), GOOGLE_PROJECT_ID 🧭

from https://console.cloud.google.com 🌐

gemini vertex (llamaindex), GOOGLE_AUTH_FILE 📂

follow instructions at https://stackoverflow.com/a/69941050 📘

### SerpApi 🔍

to request search engines 🌟

with

```text
SERP_API_KEY
```

## streamlit 🖱️

from vscode: palette > run task > run streamlit 🚀

or from terminal: `ui/lmelp_ui.sh` ⚡
