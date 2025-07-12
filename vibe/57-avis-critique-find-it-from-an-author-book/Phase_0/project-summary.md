# Vue d'ensemble du projet

Ce document fournit une vue d'ensemble de l'architecture, des technologies, de la structure des fichiers et des patterns de conception identifiés dans le projet.

## Architecture actuelle

Le projet est architecturé comme un pipeline de traitement de données, depuis la collecte jusqu'à la présentation, avec plusieurs composants clés :

1.  **Ingestion de Données** : Des scripts et des notebooks collectent des données à partir de sources externes. Principalement des flux RSS de podcasts (`rss.py`, notebook `20`) et potentiellement des pages web (`web.py`) pour des données historiques.

2.  **Pipeline de Traitement** : Le cœur du projet réside dans une série de notebooks Jupyter (`nbs/`) qui orchestrent le traitement :
    *   Téléchargement des fichiers audio (MP3, M4A) des épisodes.
    *   Transcription des fichiers audio en texte à l'aide du modèle **Whisper**.
    *   Analyse du texte transcrit par des modèles de langage (LLM) comme **Gemini** et **Azure OpenAI** via **LlamaIndex** pour extraire des entités (auteurs, livres, critiques).
    *   Stockage des métadonnées et des résultats dans une base de données.

3.  **Stockage** :
    *   **MongoDB** : Utilisé comme base de données principale pour stocker les informations structurées sur les épisodes, les auteurs, les livres, les critiques, etc. Le schéma est visible dans `db/lmelp.drawio`.
    *   **Système de fichiers** : Les fichiers audio téléchargés sont stockés localement.

4.  **Interface Utilisateur (UI)** : Une application web développée avec **Streamlit** (`ui/`) permet de visualiser et d'interagir avec les données traitées (parcourir les épisodes, les auteurs, les livres).

5.  **Documentation** : Un site de documentation statique est généré avec **MkDocs** (`docs/`, `site/`), fournissant des informations sur les modules et la configuration du projet.

6.  **Automatisation et Opérations (DevOps)** :
    *   Des scripts shell (`scripts/`) sont utilisés pour automatiser des tâches récurrentes comme les sauvegardes MongoDB et le lancement des pipelines de traitement.
    *   L'environnement de développement est standardisé grâce à **Dev Containers** (`.devcontainer/`).
    *   L'intégration continue est configurée avec **GitHub Actions** (`.github/workflows/ci.yml`).

## Technologies utilisées

*   **Langage de programmation** : Python
*   **IA & Machine Learning** :
    *   Transcription Audio : **Whisper** (via Hugging Face Transformers)
    *   LLM & Analyse de texte : **Google Gemini**, **Azure OpenAI**, **LlamaIndex**, **smolagents**
    *   Frameworks ML : **PyTorch**, **Accelerate**
*   **Base de données** : **MongoDB** (avec `pymongo`)
*   **Interface Utilisateur** : **Streamlit**
*   **Data Science & Notebooks** : **Jupyter**, **Pandas**
*   **Documentation** : **MkDocs** avec le thème Material for MkDocs
*   **DevOps & Outillage** : **Git**, **GitHub Actions**, **Docker (Dev Containers)**, **Pre-commit**
*   **Librairies Python clés** : `feedparser`, `requests`, `beautifulsoup4`, `streamlit`, `pandas`, `transformers`, `torch`, `google-generativeai`, `llama-index`, `pymongo`.

## Structure des fichiers

La structure du projet est modulaire et bien organisée :

```
.
├── .devcontainer/      # Configuration pour les environnements de développement Docker
├── .github/            # Workflows pour l'intégration continue (CI)
├── db/                 # Schéma de la base de données (diagramme Draw.io)
├── docs/               # Fichiers source Markdown pour la documentation
├── env/                # Scripts et listes de dépendances pour l'environnement
├── nbs/                # Notebooks Jupyter pour l'expérimentation et le traitement de données
├── scripts/            # Scripts d'automatisation (shell, Python)
├── site/               # Site de documentation HTML généré par MkDocs
├── ui/                 # Application UI développée avec Streamlit
├── .pre-commit-config.yaml # Configuration des hooks de pre-commit pour la qualité du code
├── mkdocs.yml          # Fichier de configuration pour MkDocs
└── README.md           # README principal du projet
```

## Patterns identifiés

*   **Pipeline de Données** : Le projet suit un modèle de pipeline clair : Collecte -> Traitement -> Stockage -> Présentation.
*   **Développement piloté par les notebooks (Notebook-Driven Development)** : Les notebooks sont massivement utilisés pour l'expérimentation, le prototypage et l'orchestration du pipeline de traitement.
*   **Code Modulaire** : La logique métier est encapsulée dans des modules Python (`mongo.py`, `llm.py`, `rss.py`, etc.) qui sont ensuite utilisés par les notebooks et l'application Streamlit, favorisant la réutilisation.
*   **Infrastructure as Code (IaC)** : L'utilisation de Dev Containers permet de définir l'environnement de développement de manière déclarative et reproductible.
*   **Configuration par variables d'environnement** : La documentation mentionne l'utilisation d'un fichier `.env` pour gérer les clés d'API, ce qui est une bonne pratique pour séparer la configuration du code.
*   **Documentation as Code** : La documentation est écrite en Markdown et versionnée avec le code, puis générée automatiquement en un site statique.
