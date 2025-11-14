# CLAUDE.md - Le Masque et la Plume

## Vue d'ensemble du projet

**lmelp** (Le Masque et la Plume) est un système d'analyse et de gestion d'épisodes de podcast pour l'émission de radio culturelle française "Le Masque et la Plume". Le projet automatise la récupération, la transcription et l'analyse structurée des épisodes pour extraire des critiques littéraires et culturelles.

### Fonctionnalités principales

- **Récupération automatique** des épisodes depuis les flux RSS
- **Téléchargement et transcription** audio avec Whisper (OpenAI)
- **Extraction structurée** d'informations (auteurs, livres, critiques, avis) via LLMs
- **Interface web Streamlit** pour parcourir et gérer le contenu
- **Base de données MongoDB** avec modèle de données bien défini
- **Couverture de tests** de 72%+ avec 214 tests

## Architecture technique

### Stack technologique

**Core:**
- Python 3.11-3.12
- MongoDB (base de données principale)
- Streamlit (interface web)
- nbdev (programmation littéraire - notebooks Jupyter → modules Python)

**IA/ML:**
- Whisper (OpenAI) - Transcription audio
- LlamaIndex - Framework d'orchestration LLM
- Azure OpenAI (GPT-4o) - LLM principal
- Google Gemini - LLM alternatif
- Google Vertex AI - Plateforme AI entreprise
- Hugging Face Transformers - Classification zero-shot
- LiteLLM - Support modèles locaux

**Traitement de données:**
- feedparser - Parsing RSS
- BeautifulSoup4 - Web scraping
- PyMongo - Interface MongoDB
- thefuzz - Fuzzy matching pour noms d'auteurs

## Structure du projet

```
/home/user/lmelp/
├── nbs/                          # Modules Python (générés depuis notebooks)
│   ├── config.py                 # Configuration environnement
│   ├── mongo.py                  # Utilitaires MongoDB de base
│   ├── mongo_episode.py          # Entité Episode (933 lignes)
│   ├── mongo_auteur.py           # Entité Auteur
│   ├── mongo_livre.py            # Entité Livre
│   ├── mongo_avis_critique.py    # Entité Avis Critique
│   ├── rss.py                    # Traitement flux RSS
│   ├── web.py                    # Web scraping
│   ├── whisper.py                # Transcription audio
│   ├── llm.py                    # Utilitaires LLM
│   ├── date_utils.py             # Formatage dates
│   └── *.ipynb                   # Notebooks sources (30+ fichiers)
│
├── ui/                           # Interface web Streamlit
│   ├── lmelp.py                  # Page principale
│   └── pages/                    # Application multi-pages
│       ├── 1_episodes.py         # Gestion des épisodes
│       ├── 2_auteurs.py          # Gestion des auteurs
│       ├── 3_livres.py           # Gestion des livres
│       └── 4_avis_critiques.py   # Gestion des avis critiques
│
├── tests/                        # Suite de tests (72%+ couverture)
│   ├── unit/                     # Tests unitaires (14 fichiers)
│   ├── integration/              # Tests d'intégration
│   ├── fixtures/                 # Données de test
│   ├── conftest.py               # Configuration pytest
│   └── requirements.txt          # Dépendances minimales pour tests
│
├── scripts/                      # Scripts utilitaires
│   ├── backup_mongodb.sh         # Sauvegarde base de données
│   ├── update_emissions.py       # Synchronisation RSS → DB
│   ├── get_one_transcription.py  # Transcription épisode unique
│   ├── get_all_transcriptions.py # Transcription en masse
│   └── store_all_auteurs_from_all_episodes.py  # Extraction auteurs
│
├── docs/                         # Documentation MkDocs
│   ├── *.md                      # Documentation modules
│   └── readme_*.md               # Guides (tests, GitHub, Google APIs)
│
├── vibe/                         # Système de workflow développement
│   └── [BRANCH-NAME]/            # Développement assisté LLM en 4 phases
│       ├── Phase_0/              # Contexte & analyse
│       ├── Phase_1/              # Spécifications
│       ├── Phase_2/              # Planification
│       ├── Phase_3/              # Exécution
│       └── Phase_4/              # Documentation
│
├── .devcontainer/                # Environnement Docker
│   ├── linux/devcontainer.json   # Configuration conteneur
│   ├── requirements.txt          # ~45 dépendances
│   └── postCommand.sh            # Script post-création
│
├── .github/workflows/            # CI/CD
│   ├── tests.yml                 # Tests unitaires + linting
│   └── ci.yml                    # Déploiement documentation
│
├── db/                           # Sauvegardes DB & archives web
├── audios/                       # Fichiers audio téléchargés (par année)
└── site/                         # Site documentation généré
```

## Modèle de données (MongoDB)

### Entités principales

**Episode** - Entité centrale
- `episode_id`: Identifiant unique
- `date`: Date de diffusion
- `duration`: Durée en minutes
- `type`: livres/films/théâtre/spéciale
- `transcription`: Texte transcrit
- `audio_file`: Chemin fichier audio
- `title`, `summary`, `url`

**RSS_episode** - Épisodes RSS
- Hérite de `Episode`
- Classification automatique du type
- `enclosure`: URL audio

**WEB_episode** - Épisodes web (legacy)
- Hérite de `Episode`
- Données scrapées du site web

**Auteur** - Auteurs d'œuvres
- `nom`: Nom de l'auteur
- Fuzzy matching pour déduplication
- Validation Google Search

**Livre** - Ouvrages critiqués
- `titre`: Titre du livre
- `auteur_id`: Référence à Auteur
- `editeur_id`: Référence à Éditeur
- `annee_parution`: Année de publication

**Avis_Critique** - Critiques/avis
- `episode_id`: Référence à Episode
- `livre_id`: Référence à Livre
- `critique_id`: Référence à Critique
- `avis`: Texte de l'avis
- `sentiment`: positif/négatif/neutre

**Critique** - Critiques (personnes)
- `nom`: Nom du critique

**Editeur** - Maisons d'édition
- `nom`: Nom de l'éditeur

## Points d'entrée et commandes importantes

### Interface web
```bash
./ui/lmelp_ui.sh          # Lance l'interface Streamlit
# Accessible sur http://localhost:8501
```

### Scripts de traitement
```bash
# Synchroniser les épisodes depuis RSS
python scripts/update_emissions.py

# Transcrire un épisode spécifique
python scripts/get_one_transcription.py <episode_id>

# Transcrire tous les épisodes manquants
python scripts/get_all_transcriptions.py

# Extraire tous les auteurs des épisodes
python scripts/store_all_auteurs_from_all_episodes.py
```

### Tests
```bash
# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=nbs --cov-report=html

# Tests d'un module spécifique
pytest tests/unit/test_mongo_episode.py
```

### Documentation
```bash
# Générer la documentation
nbdev_docs

# Servir localement
mkdocs serve
```

## Configuration et environnement

### Variables d'environnement (.env)

**Obligatoires:**
```bash
# Flux RSS
RSS_LMELP_URL=https://radiofrance-podcast.net/podcast09/rss_14007.xml

# Base de données
DB_HOST=localhost
DB_NAME=masque_et_la_plume
DB_LOGS=true

# LLM APIs (au moins une)
AZURE_API_KEY=...
AZURE_ENDPOINT=...
# OU
GEMINI_API_KEY=...
# OU
OPENAI_API_KEY=...
```

**Optionnelles:**
```bash
# Google Services
GOOGLE_PROJECT_ID=...
GOOGLE_CUSTOM_SEARCH_API_KEY=...
SEARCH_ENGINE_ID=...

# Chemins
AUDIO_BASE_PATH=./audios
```

### Environnement de développement

Le projet utilise **devcontainer** pour un environnement cohérent:
- Python 3.11
- MongoDB préconfiguré
- Toutes les dépendances installées
- Port 8501 auto-forwarded pour Streamlit

```bash
# Ouvrir dans devcontainer (VS Code)
# Ou installer manuellement:
pip install -r .devcontainer/requirements.txt
```

## Workflow de développement

### Programmation littéraire avec nbdev

**Important:** Les modules Python dans `nbs/` sont **générés automatiquement** depuis les notebooks Jupyter.

```bash
# Workflow de modification:
1. Éditer le notebook: nbs/XX_module.ipynb
2. Générer le module Python: nbdev_export
3. Tester: pytest tests/unit/test_module.py
4. Documenter: nbdev_docs
```

**Ne jamais éditer directement les fichiers .py dans nbs/** - vos modifications seront écrasées!

### Pre-commit hooks

Le projet utilise des hooks pre-commit:
- `nbdev_clean` - Nettoie les outputs des notebooks
- `black` - Formatage Python
- `black-jupyter` - Formatage notebooks

```bash
# Installer les hooks
pre-commit install

# Lancer manuellement
pre-commit run --all-files
```

### Système Vibe (développement assisté LLM)

Le répertoire `vibe/` contient un workflow structuré en 4 phases pour le développement assisté par LLM:

**Phase 0 - Contexte:** Analyse et compréhension
**Phase 1 - Spécifications:** Définition des exigences
**Phase 2 - Planification:** Plan d'implémentation
**Phase 3 - Exécution:** Développement
**Phase 4 - Documentation:** Finalisation

Chaque branche de feature a son propre dossier `vibe/[BRANCH-NAME]/`.

## Tests et qualité

### Stratégie de test

- **214 tests** avec **72%+ de couverture**
- Tests unitaires pour chaque module
- Tests d'intégration pour workflows complets
- Tests UI pour composants Streamlit
- Mocking des dépendances lourdes (torch, transformers)

### CI/CD

**GitHub Actions** (.github/workflows/):
- `tests.yml` - Exécute tests + linting sur chaque push/PR
- `ci.yml` - Déploie la documentation sur GitHub Pages

### Couverture par module

Les modules critiques visent 90%+ de couverture:
- `mongo_episode.py` - Entité centrale
- `rss.py` - Parsing RSS
- `whisper.py` - Transcription
- `llm.py` - Extraction LLM

## Conventions et bonnes pratiques

### Conventions de code

1. **PEP 8** - Style Python standard (appliqué par black)
2. **Type hints** - Fortement encouragés
3. **Docstrings** - Format Google style
4. **Imports** - Organisés par stdlib, third-party, local
5. **Logging** - Utiliser le système de logs MongoDB intégré

### Logging MongoDB

Le projet utilise un système de logs centralisé dans MongoDB:

```python
from nbs.mongo import log_to_mongodb

log_to_mongodb("INFO", "Module", "Message de log")
```

Niveaux: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Gestion des erreurs

- Toujours logger les erreurs avec contexte
- Utiliser des exceptions custom pour les cas métier
- Nettoyer les ressources (fichiers, connexions DB)

### Dates et locale française

Le projet gère spécifiquement les dates françaises:

```python
from nbs.date_utils import format_date_french

# Convertit "20 janv. 2024" → "2024-01-20"
date = format_date_french(french_date_string)
```

## Dépendances et versions

### Dépendances principales (~45 packages)

**ML/AI:**
- transformers, torch, accelerate
- llama-index-core, llama-index-llms-*
- google-generativeai, smolagents

**Data:**
- pymongo, feedparser, beautifulsoup4
- requests, thefuzz

**UI:**
- streamlit, streamlit-extras

**Dev:**
- nbdev, pytest, black, mkdocs

### Installation

```bash
# Via devcontainer (recommandé)
# Ou manuel:
pip install -r .devcontainer/requirements.txt

# Tests uniquement:
pip install -r tests/requirements.txt
```

## Ressources et documentation

- **Documentation:** Générée via nbdev et MkDocs
- **Site web:** Déployé sur GitHub Pages
- **Tests:** Rapport de couverture dans `htmlcov/`
- **Logs:** Collection MongoDB `logs`

## Points d'attention pour les assistants IA

### Modifications de code

1. **Toujours modifier les notebooks (.ipynb), jamais les .py dans nbs/**
2. Exécuter `nbdev_export` après modification d'un notebook
3. Lancer les tests pertinents avant de commiter
4. Les pre-commit hooks nettoient automatiquement les notebooks

### Ajout de fonctionnalités

1. Créer un nouveau notebook ou modifier un existant
2. Ajouter des tests dans `tests/unit/`
3. Documenter dans le notebook (sera exporté vers docs/)
4. Mettre à jour `.env.example` si nouvelles variables
5. Suivre le workflow Vibe si développement complexe

### Debugging

- Logs MongoDB: Collection `logs` avec horodatage et contexte
- Tests: `pytest -v -s` pour output verbose
- Streamlit: Logs dans console, mode debug avec `--logger.level=debug`

### Performance

- Les transcriptions Whisper sont **coûteuses** (CPU/GPU)
- Cache des transcriptions dans MongoDB
- LLM calls peuvent être lents - utiliser caching LlamaIndex
- Fuzzy matching auteurs peut être optimisé si trop lent

## Commandes rapides

```bash
# Développement
./ui/lmelp_ui.sh                    # Interface web
nbdev_export                        # Notebooks → Python
nbdev_docs                          # Générer docs

# Tests
pytest                              # Tous les tests
pytest -v --cov=nbs                 # Avec couverture

# Qualité
pre-commit run --all-files          # Linting
black nbs/ tests/                   # Formatage

# Base de données
./scripts/backup_mongodb.sh         # Backup MongoDB
mongo masque_et_la_plume            # Shell MongoDB

# Production
python scripts/update_emissions.py  # Sync RSS
python scripts/get_all_transcriptions.py  # Transcriptions
```

## Contact et contribution

Le projet utilise des branches feature avec préfixe `claude/` pour le développement assisté par IA.

**Workflow Git:**
1. Créer une branche: `claude/feature-name-[SESSION-ID]`
2. Développer et tester
3. Commit avec messages clairs
4. Push avec: `git push -u origin <branch-name>`
5. Créer PR vers branche principale

---

*Ce fichier est maintenu pour aider les assistants IA à comprendre et contribuer au projet lmelp.*
