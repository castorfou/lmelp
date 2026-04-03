# Documentation MkDocs — Guide

- [Dépendances](#dependances)
- [Configuration mkdocs.yml](#configuration-mkdocsyml)
- [Fichiers de doc API](#fichiers-de-doc-api)
- [Modifier les docstrings](#modifier-les-docstrings)
- [Lancer le serveur de développement](#lancer-le-serveur-de-developpement)
- [Générer la documentation statique](#generer-la-documentation-statique)
- [Déploiement automatique GitHub Actions](#deploiement-automatique-github-actions)

## Dependances

Les dépendances de documentation sont dans `pyproject.toml` sous `[project.optional-dependencies] dev` :

```toml
mkdocs>=1.5.0
mkdocs-material>=9.4.0
mkdocstrings[python]
mkdocs-include-markdown-plugin
mkdocs-awesome-nav
mkdocs-git-revision-date-localized-plugin
```

Installation :
```bash
uv sync --active --all-extras
```

## Configuration mkdocsyml

Le fichier `mkdocs.yml` à la racine du projet configure MkDocs. Points clés :

```yaml
plugins:
  - search
  - awesome-nav          # navigation auto depuis .nav.yml
  - include-markdown
  - git-revision-date-localized:
      enable_creation_date: true
  - mkdocstrings:
      handlers:
        python:
          paths: [.]     # chemin depuis la racine du projet
          options:
            show_root_heading: true
            show_source: true
            docstring_style: google

exclude_docs: |
  claude/
  old_doc/
```

La navigation est gérée automatiquement par `awesome-nav` via des fichiers `.nav.yml` dans chaque sous-répertoire de `docs/`.

## Fichiers de doc API

Les modules Python sont dans `nbs/` et documentés dans `docs/api/`. Chaque fichier utilise la directive mkdocstrings avec le chemin complet du module :

```markdown
# Module rss

::: nbs.rss
    rendering:
      show_root_full_path: false
```

**Note :** nbdev_docs a été abandonné (il repose sur Quarto, incompatible avec MkDocs). Les fichiers `docs/api/*.md` sont maintenus manuellement. Voir `docs/api/README.md` pour le workflow d'ajout d'un nouveau module.

## Modifier les docstrings

Prompt utile pour générer des docstrings Google style :

```text
peux-tu ajouter des docstrings au format Google style utilisables par mkdocs ou les modifier
pour qu'ils soient utilisables par mkdocs et t'assurer qu'ils soient au format Google style ?
Précise également les bons types dans la signature des méthodes/fonctions ainsi que le type
de sortie s'il y a lieu.
```

**Important :** les modules Python dans `nbs/` sont générés depuis les notebooks Jupyter via `nbdev_export`. Ne jamais éditer les `.py` directement — éditer le notebook correspondant puis lancer `nbdev_export`.

## Lancer le serveur de developpement

```bash
uv run --active mkdocs serve
```

Accessible sur http://127.0.0.1:8000.

## Generer la documentation statique

```bash
uv run --active mkdocs build
```

Le site est généré dans `site/`.

## Deploiement automatique GitHub Actions

Le workflow `.github/workflows/docs.yml` se déclenche automatiquement à chaque push sur `main` si des fichiers dans `docs/**` ou `mkdocs.yml` changent.

Il build la doc et la déploie via GitHub Actions artifacts sur [https://castorfou.github.io/lmelp](https://castorfou.github.io/lmelp).

### Configuration GitHub Pages requise

1. Aller dans **Settings > Pages** du repo
2. Dans **Source**, sélectionner **"GitHub Actions"** (pas "Deploy from a branch")
3. Le lien apparaît dans `About` : `Edit repository details` > ✓ `Use your GitHub Pages website`
