# Vue d'ensemble du projet : LMELP

## 1. Architecture Actuelle

Le projet "Le Masque et la Plume" (LMELP) est une application web de traitement et d'analyse de données audio, spécifiquement conçue pour les épisodes de l'émission de radio. L'architecture est multi-couches et orientée données, combinant des notebooks pour le développement et l'expérimentation, des scripts pour l'automatisation, et une interface utilisateur web pour la visualisation.

L'architecture peut être décomposée comme suit :

- **Couche d'Ingestion de Données** :
  - **Flux RSS** : Le système ingère les données des épisodes depuis un flux RSS de Radio France. Le module `nbs/rss.py` et les notebooks associés (`20 workflow sur flux RSS.ipynb`) sont responsables du parsing et de l'extraction des métadonnées des épisodes.
  - **Fichiers Audio** : Les fichiers audio (MP3, M4A) des épisodes sont téléchargés et stockés localement dans le répertoire `audios/`.

- **Couche de Traitement et d'Analyse** :
  - **Transcription Audio** : Le service **Whisper** est utilisé pour transcrire les fichiers audio en texte. Le module `nbs/whisper.py` et les notebooks (`09 whisper mp3.ipynb`, `10 update whisper.ipynb`) gèrent ce processus.
  - **Analyse par LLM** : Le projet utilise des modèles de langage (LLM) via **Azure OpenAI** et **Gemini** pour analyser les transcriptions. Le module `nbs/llm.py` et les notebooks (`11 gemini on transcription.ipynb`, `33 add Auteurs.ipynb`) gèrent l'extraction d'entités (auteurs, livres), la génération de synthèses et d'autres tâches NLP. La bibliothèque `llama_index` est utilisée pour orchestrer les interactions avec les LLM.

- **Couche de Persistance des Données** :
  - **MongoDB** : Une base de données **MongoDB** est utilisée pour stocker toutes les données structurées, incluant les épisodes, les auteurs, les livres, les critiques, et les transcriptions. Les modules `nbs/mongo.py`, `nbs/mongo_episode.py`, `nbs/mongo_auteur.py`, et `nbs/mongo_livre.py` définissent les schémas et les interactions avec la base de données.

- **Couche de Logique Métier et d'Automatisation** :
  - **Notebooks Jupyter** (`nbs/`) : Une grande partie de la logique métier est développée et testée dans des notebooks Jupyter. Ils couvrent l'ensemble du workflow, du téléchargement des données à l'analyse par LLM.
  - **Scripts** (`scripts/`) : Des scripts Python et shell sont utilisés pour automatiser les tâches récurrentes comme les sauvegardes de la base de données (`backup_mongodb.sh`), la mise à jour des transcriptions (`lmelp_get_one_transcription.sh`), et le stockage des entités (`store_all_auteurs_from_all_episodes.py`).

- **Couche de Présentation (UI)** :
  - **Streamlit** (`ui/`) : Une application web multi-pages construite avec **Streamlit** sert d'interface utilisateur. Elle permet de visualiser les données, de suivre l'état du système (nombre d'épisodes, transcriptions manquantes), et d'interagir avec les fonctionnalités du back-office.

## 2. Technologies Utilisées

- **Langage de Programmation** : **Python 3**
- **Base de Données** : **MongoDB** (avec `pymongo`)
- **Interface Utilisateur** : **Streamlit**
- **Analyse de Données et Machine Learning** :
  - **Transcription Audio** : **Whisper** (via `transformers`)
  - **LLM** : **Azure OpenAI**, **Google Gemini** (via `llama_index`, `google-generativeai`)
  - **Bibliothèques NLP** : `thefuzz` pour la correspondance de chaînes de caractères.
- **Développement et Expérimentation** : **Jupyter Notebooks**
- **Tests** :
  - **Framework** : **pytest**
  - **Utilitaires** : `pytest-mock`, `pytest-cov` pour la couverture de code.
- **Gestion des Dépendances** : `requirements.txt`
- **Parsing de Données** : `feedparser` pour les flux RSS, `BeautifulSoup4` pour le HTML.
- **Gestion de l'Environnement** : `python-dotenv` pour les variables d'environnement.

## 3. Structure des Fichiers

La structure du projet est organisée par fonctionnalité, avec une séparation claire entre les différentes couches de l'application.

- `nbs/` : Le cœur du projet, contenant les **notebooks Jupyter** pour le développement des workflows et les **modules Python** (`.py`) qui encapsulent la logique réutilisable (configuration, accès à la base de données, interaction avec les LLM).
- `scripts/` : Contient les **scripts d'automatisation** pour les tâches de maintenance et de traitement en batch.
- `ui/` : Contient l'application **Streamlit**, avec une page principale (`lmelp.py`) et des sous-pages dans `ui/pages/` pour chaque fonctionnalité majeure (épisodes, auteurs, livres, etc.).
- `tests/` : Un répertoire de tests très complet, avec une séparation entre les **tests unitaires** (`tests/unit`), les **tests d'intégration** (`tests/integration`), et les **tests d'interface utilisateur** (`tests/ui`). Il contient également des **fixtures** (`tests/fixtures`) pour les données de test.
- `docs/` : Contient la **documentation** du projet au format Markdown.
- `db/` : Semble contenir des **artefacts de base de données** et des schémas (`.drawio`).
- `audios/` : Le répertoire de stockage pour les **fichiers audio** téléchargés, organisés par année.
- `.env.test` : Fichier de configuration pour l'environnement de **test**.
- `pytest.ini`, `.coveragerc` : Fichiers de configuration pour **pytest** et la **couverture de code**.

## 4. Patterns Identifiés

- **Modularité et Séparation des Préoccupations** : La logique de bas niveau (configuration, accès à la base de données, appels LLM) est isolée dans des modules Python dédiés dans `nbs/`, ce qui permet de la réutiliser facilement dans les notebooks et les scripts.
- **Développement Orienté Notebook (Notebook-Driven Development)** : Les notebooks sont utilisés comme outil principal pour développer, tester et documenter les workflows de traitement de données.
- **Tests Complets** : Le projet suit des pratiques de test robustes, avec une suite de tests complète qui couvre les unités, les intégrations et l'interface utilisateur.
- **Utilisation de Fixtures de Test** : Le répertoire `tests/fixtures/` contient des données d'exemple (JSON, XML, texte) qui sont utilisées pour rendre les tests déterministes et indépendants des services externes.
- **Mocking et Isolation** : `pytest-mock` et `monkeypatch` sont utilisés de manière extensive dans les tests pour isoler les composants et simuler les dépendances externes (API, base de données), ce qui est une bonne pratique pour les tests unitaires.
- **Configuration via Variables d'Environnement** : Le module `nbs/config.py` centralise la gestion de la configuration et utilise `python-dotenv` pour charger les variables d'environnement, ce qui permet de séparer la configuration du code.
- **Modèle de Données Orienté Entité** : Les interactions avec MongoDB sont structurées autour de classes d'entités (`Episode`, `Auteur`, `Livre`, etc.), ce qui fournit une abstraction claire sur la base de données.
