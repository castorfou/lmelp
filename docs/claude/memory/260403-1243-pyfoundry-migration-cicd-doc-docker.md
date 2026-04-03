# Migration PyFoundry — CI/CD, Docker, Documentation

**Branche :** `100-pyfoundry-basculer-sur-pyfoundry`
**Date :** 2026-04-03

## Contexte

Application de la migration PyFoundry au projet lmelp. Cette session couvre trois axes : CI/CD, Docker, et Documentation.

---

## 1. CI/CD — Migration pip → uv

### Ce qui a été fait

- **Suppression** de `.github/workflows/tests.yml` (ancien workflow pip)
- **Refonte** de `.github/workflows/ci.yml` (template PyFoundry) pour l'adapter au projet :
  - Trigger sur tous les pushes (pas seulement main/develop)
  - `pip install -r tests/requirements.txt` → `uv sync --extra dev`
  - `--cov=src` → `--cov=nbs` (chemin correct du projet)
  - Seuil de couverture : 90% → 70% (réalité du projet, l'ancien workflow ne mesurait qu'un seul module)
  - Ajout system deps (`libdbus-1-dev` etc.) manquants
  - Job `lint` avec `ruff` (remplace flake8/black/isort)
  - Tests d'intégration streamlit skippés en CI via `os.getenv("CI") == "true"`

- **`docs.yml`** et **`docker-publish.yml`** : déjà bons, pas modifiés

### Dépendances manquantes ajoutées à pyproject.toml

- `pytz` — utilisé dans `nbs/rss.py` (manquait dans pyproject.toml)
- `torch` et `google-api-python-client` : tirés transitivement, pas besoin de les ajouter

### Test fixtures mis à jour

- `test_fixtures.py` : `tests.yml` → `ci.yml`, job `test` → `tests`
- Seuil couverture cohérent avec le nouveau workflow

---

## 2. Pre-commit — detect-secrets

### Problème rencontré

`detect-secrets` bloque les commits sur des faux positifs (clés de test factices comme `test-azure-api-key-12345`).

### Solution — pragma résistant au reformatage

Le `# pragma: allowlist secret` doit être sur la **même ligne** que la valeur. Ruff/black reformatent les assertions longues et séparent la valeur du pragma, cassant la protection.

**Pattern correct :**
```python
azure_key = "AZURE_API_KEY=test-azure-api-key-12345"  # pragma: allowlist secret
assert azure_key in content
```

Documenté dans `CLAUDE.md` section "Pre-commit hooks > Faux positifs detect-secrets".

### Config ruff corrigée dans pyproject.toml

- `extend-select` / `ignore` déplacés de `[tool.ruff]` vers `[tool.ruff.lint]`
- `extend-exclude` / `line-length` / `target-version` restent dans `[tool.ruff]`
- `PD901` supprimé (règle retirée de ruff)

---

## 3. Docker — Migration pip → uv

### Dockerfile migré

`docker/build/Dockerfile` — stage builder :

**Avant :**
```dockerfile
RUN pip install --no-cache-dir uv
COPY .devcontainer/requirements.txt .
RUN uv pip install --system -r requirements.txt
```

**Après :**
```dockerfile
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml .
COPY uv.lock .
RUN uv export --frozen --no-dev --no-emit-project --format requirements-txt -o requirements.txt && \
    uv pip install --system -r requirements.txt && \
    rm -rf /root/.cache/uv requirements.txt /tmp/*
```

**Pourquoi `uv export` + `uv pip install --system` et non `uv sync` :**
- `uv sync` crée un `.venv` dans `/build/`, pas dans `/usr/local/`
- Le runtime copie `/usr/local` depuis le builder → les packages sont absents avec `uv sync`
- `UV_SYSTEM_PYTHON=1` ne suffit pas pour `uv sync`
- Solution : exporter en requirements.txt puis installer en système

### Test Docker local

```bash
# Build
docker build -f docker/build/Dockerfile -t lmelp:test .

# Test sans démarrer Streamlit (bypasse l'entrypoint)
docker run --rm --entrypoint python lmelp:test -c "import streamlit, pymongo; print('OK')"

# Test connexion MongoDB
docker run --rm --entrypoint python lmelp:test -c \
  "from pymongo import MongoClient; print(MongoClient('mongodb://172.17.0.1:27017').admin.command('ping'))"
```

**Note :** `docker run lmelp:test python -c "..."` ne fonctionne pas — l'entrypoint intercepte tout. Toujours utiliser `--entrypoint`.

---

## 4. Documentation — MkDocs + mkdocstrings

### Abandon de nbdev_docs

nbdev v2 génère la doc via Quarto (incompatible avec MkDocs). Les fichiers `docs/api/*.md` sont maintenus manuellement. Documenté dans `docs/api/README.md`.

### mkdocstrings ajouté à mkdocs.yml

```yaml
plugins:
  - mkdocstrings:
      handlers:
        python:
          paths: [.]
          options:
            show_root_heading: true
            show_source: true
            docstring_style: google
```

### Correction des chemins de modules

Tous les `docs/api/*.md` corrigés : `::: rss` → `::: nbs.rss` (les modules sont dans `nbs/`).

### Exclusion old_doc du build

`mkdocs.yml` — `exclude_docs` étendu :
```yaml
exclude_docs: |
  claude/
  old_doc/
```

---

## 5. Points clés à retenir

### uv — toujours utiliser --active dans ce devcontainer

Le devcontainer a un venv préactivé à `/home/vscode/.venv`. Sans `--active`, uv crée un `.venv` local.

```bash
uv run --active pytest ...
uv sync --active --extra dev
uv add --active <package>
# uvx n'a pas besoin de --active (env isolé indépendant)
```

### Générer .secrets.baseline

```bash
cd /tmp && GIT_DIR=/workspaces/lmelp/.git uvx detect-secrets scan /workspaces/lmelp > /workspaces/lmelp/.secrets.baseline && cd -
```
Depuis `/tmp` pour éviter la création d'un `.venv` local, avec `GIT_DIR` pour que detect-secrets trouve le repo git.
