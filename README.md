- [pour developper 💻](#pour-developper-)
  - [environnements de dev python 🐍](#environnements-de-dev-python-)
  - [pre-commit ⏱️](#pre-commit-️)
  - [config vscode 🖥️](#config-vscode-️)
  - [tests unitaires 🧪](#tests-unitaires-)
- [😀 à propos de la doc](#-à-propos-de-la-doc)
- [pour utiliser 🚀](#pour-utiliser-)
  - [💾 base de données mongodb](#-base-de-données-mongodb)
  - [ffmpeg 🎞️](#ffmpeg-️)
  - [locale FR 🇫🇷](#locale-fr-)
  - [ulimit ⚙️](#ulimit-️)
  - [`.env` 🌐](#env-)
    - [rss info 🎙️](#rss-info-️)
    - [web info 🌍](#web-info-)
    - [db info 🗄️](#db-info-️)
    - [llm, llamaindex, litellm 🤖](#llm-llamaindex-litellm-)
    - [websearch](#websearch)
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
# add fs.inotify.max_user_watches=524288 to /etc/sysctl.d/99-custom-inotify.conf
sudo sysctl -p # to apply directly
cat /proc/sys/fs/inotify/max_user_watches # to control it is applied
```
  
or add `files.watcherExclude` directive in `.vscode/settings.json` 📁

pour quelques astuces liées à vscode : [Vscode hints (sur github pages)](https://castorfou.github.io/lmelp/readme_vscode_hints/)

## tests unitaires 🧪

Le projet utilise **pytest** pour les tests unitaires avec une couverture de code élevée.

**Infrastructure CI/CD :**
- ✅ **GitHub Actions** : Tests automatiques sur chaque push/PR
- ✅ **Dépendances optimisées** : `tests/requirements.txt` (sans PyTorch/ML)
- ✅ **Mocking avancé** : torch, transformers, dbus mockés pour CI/CD
- ✅ **Coverage 72%+** : Couverture actuelle avec 214 tests
- ✅ **Linting automatique** : flake8, black, isort

```bash
# Lancer tous les tests
pytest

# Tests avec couverture 
pytest --cov=nbs --cov-report=term-missing

# Tests spécifiques
pytest tests/unit/test_config.py -v
```

**Structure des tests :**
- `tests/unit/` : Tests unitaires par module
- `tests/fixtures/` : Données de test et utilitaires
- `tests/requirements.txt` : **Dépendances minimales pour tests**
- `tests/conftest.py` : Configuration et fixtures globales
- `.env.test` : Variables d'environnement de test
- `.github/workflows/tests.yml` : **CI/CD GitHub Actions**

**Documentation complète :** [Guide des tests unitaires](https://castorfou.github.io/lmelp/readme_unit_test/) 📋

# 😀 à propos de la doc

on change la doc depuis `docs` (génie) 😊

- APIs 🚀
- Quelques astuces ou choix de conception 🔍

Mkdocs+github actions ramasse tout cela (branche main uniquement) et publie sur le [github pages du projet](https://castorfou.github.io/lmelp/) 📦

Expliqué à https://castorfou.github.io/lmelp/readme_doc/ 👍


# pour utiliser 🚀

## 💾 base de données mongodb

mongodb est utilisée pour conserver toutes les données de l'application ([voir schéma](https://castorfou.github.io/lmelp/readme_data_model/)). 📊  
pour conserver une sauvegarde de la base, lancer depuis devcontainer `scripts/backup_mongodb.sh` 🚀

si les liens ont été faits dans `~/bin/lmelp`, alors lancer depuis host `~/bin/lmelp/backup_mongodb.sh`

penser à le faire réguiliérement, il n'y a aucun rappel.

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

### llm, llamaindex, litellm 🤖

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

Et pour les modeles locaux **LiteLLM**
```
LITELLM_API_KEY
```

### websearch

We need these 2 keys.

```GOOGLE_CUSTOM_SEARCH_API_KEY

SEARCH_ENGINE_ID
```

more details at [readme Google](docs/readme_google.md)

## streamlit 🖱️

3 ways to run it: from vscode, from devcontainer, from host

from **vscode**: palette > run task > run streamlit 🚀

from **devcontainer** terminal: `ui/lmelp_ui.sh` ⚡

from **host** terminal: 

```bash
#!/bin/bash 

source ~/git/lmelp/scripts/from_host/get_container.sh

container=$(get_container)
echo "Using container: $container"

# Execute the UI script in the found container as the user vscode.
docker exec -u vscode "$container" /workspaces/lmelp/ui/lmelp_ui.sh
```