- [Étapes à suivre](#étapes-à-suivre) 📋
  - [Installer les dépendances](#installer-les-dependances) 🔧
  - [Initialiser le projet MkDocs](#initialiser-le-projet-mkdocs) 🚀
  - [Configurer le fichier `mkdocs.yml`](#configurer-le-fichier-mkdocsyml) ⚙️
  - [Créer les pages Markdown pour intégrer la doc extraite](#créer-les-pages-markdown-pour-intégrer-la-doc-extraite) 📝
  - [Modifier les docstrings](#modifier-les-docstrings) ✏️
  - [Lancer le serveur de développement](#lancer-le-serveur-de-développement) 🖥️
  - [Générer la documentation statique](#générer-la-documentation-statique) 🏗️
  - [Pousser sous github pages](#pousser-sous-github-pages) 🚢

Voici une solution complète pour créer une documentation avec MkDocs et le thème Material, en incluant l'extraction automatique de la doc de vos fichiers .py grâce à l'extension mkdocstrings. ℹ️

# Étapes à suivre 🔍

## Installer les dépendances 🛠️

Créez (optionnellement) un environnement virtuel et installez MkDocs, le thème Material et l'extension mkdocstrings : 💻

```bash
# ajouter a mon env python
pip install mkdocs mkdocs-material "mkdocstrings[python]"
```

## Initialiser le projet MkDocs 🚀

Dans la racine de votre repo, initialisez MkDocs (si vous n’avez pas déjà de fichier mkdocs.yml) : 📁

```bash
mkdocs new .
```

Cela crée un fichier `mkdocs.yml` et un dossier `docs/`. 📂

## Configurer le fichier `mkdocs.yml` ⚙️

Modifiez le fichier mkdocs.yml pour définir le nom du site, la navigation, le thème et la configuration de mkdocstrings. Par exemple : 📝

```yaml
site_name: Documentation des APIs du repo lmelp
nav:
  - Accueil: index.md
  - Modules:
      - Module llm: llm.md
      - Module whisper: whisper.md
      - Module web: web.md
      - Module rss: rss.md
      - Module mongo: mongo.md
      - Module mongo_episode: mongo_episode.md
      - Module mongo_auteur: mongo_auteur.md
  - Other kind of docs:
      - To manage doc: readme_doc.md
      - To write markdown: readme_markdown.md
      - some vs_code hints: readme_vscode_hints.md
      - about Google services: readme_google.md
theme:
  name: material

# Configuration de mkdocstrings pour extraire la documentation de vos .py
markdown_extensions:
  - toc:
      permalink: true

plugins:
  - search
  - mkdocstrings:
      default_handler: python
      handlers:
        python:
          paths: [nbs]  
```

Quelques points à noter : ℹ️

- Vous pouvez organiser votre navigation comme vous le souhaitez. ✅
- La section `plugins` avec mkdocstrings permet d'extraire la doc des fichiers Python. 🔍

## Créer les pages Markdown pour intégrer la doc extraite 📝

Dans le dossier `docs/`, créez par exemple un fichier `mongo_auteur.md` pour documenter le module `mongo_auteur.py` : 📄

```markdown
# Module mongo_auteur

::: mongo_auteur
    rendering:
      show_root_full_path: false
```

De même, créez un fichier `mongo_episode.md` pour documenter `mongo_episode.py` : 📄

```markdown
# Module mongo_episode

::: mongo_episode
    rendering:
      show_root_full_path: false
```

L'opérateur `:::` indique à mkdocstrings (via la syntaxe Python) d'extraire automatiquement les docstrings du module nommé (`mongo_auteur` ou `mongo_episode`). 🔍  
Assurez-vous que ces modules soient dans votre `PYTHONPATH` ou que vous spécifiiez leur chemin relatif si besoin. ⚠️

## Modifier les docstrings ✏️

J'utilise copilot avec le prompt suivant : 💡

```text
peux-tu ajouter des docstrings au format Google style utilisables par mkdocs ou les modifier pour qu'ils soient utilisables par mkdocs et t'assurer qu'ils soient au format Google style ?
precise egalement les bons types dans la signature des methodes/fonctions ainsi que le type de sortie s'il y a lieu.
```

## Lancer le serveur de développement 🖥️

Pour visualiser la documentation, exécutez : 👀

```bash
mkdocs serve
```

Vous pourrez alors accéder à l’interface web sur http://127.0.0.1:8000. 🌐

## Générer la documentation statique 🏗️

Quand vous êtes satisfait, générez le site statique : 🏁

```bash
mkdocs build
```

Le site sera créé dans le dossier `site/`, prêt à être déployé. 🚀

## Pousser sous github pages 🚢

```bash
mkdocs gh-deploy
```

**Résumé** 📝

- Vous installez MkDocs, Material, et mkdocstrings. ✅
- Vous configurez `mkdocs.yml` pour intégrer mkdocstrings et vous indiquez dans la navigation les pages souhaitées. 🗂️
- Dans vos pages Markdown, vous utilisez la syntaxe `:::` pour extraire automatiquement la doc de vos fichiers Python. 🔍
- Vous lancez le serveur MkDocs pour vérifier l'interface web moderne et bien organisée. 👓

Cette approche vous permettra d'avoir une documentation conviviale et rapidement mise à jour à partir de vos docstrings. 👍
