# Spécification des changements - Tests Unitaires

## Vue d'ensemble

L'objectif est d'implémenter une infrastructure de tests unitaires robuste pour le projet LMELP afin de permettre des modifications plus sereines du code. Cette implémentation suivra une approche progressive en commençant par les modules les plus critiques.

## Composants à tester

### 1. Modules Python critiques (Priorité 1)
- **`nbs/mongo.py`** : Module de gestion MongoDB
- **`nbs/llm.py`** : Module d'intégration LLM
- **`nbs/rss.py`** : Module de collecte RSS
- **`nbs/config.py`** : Module de configuration

### 2. Scripts utilitaires (Priorité 2)
- **`scripts/*.py`** : Scripts de migration et traitements one-shot
- Tests unitaires pour les fonctions utilitaires
- Tests d'intégration pour les workflows complets

### 3. Interface Streamlit (Priorité 3)
- **`ui/*.py`** : Applications Streamlit
- Tests de la logique métier
- Tests d'interface utilisateur basiques

## Infrastructure de tests

### Framework de test
- **pytest** : Framework principal (plus adapté pour ce type de projet)
- **pytest-mock** : Pour le mocking des APIs externes
- **pytest-cov** : Pour la couverture de code (optionnelle)

### Gestion des dépendances externes
- **APIs (Google Gemini, Azure OpenAI)** : Mocking complet en CI/CD, tests d'intégration en local
- **MongoDB** : Utilisation de `pymongo-inmemory` ou mocking pour les tests unitaires
- **Fichiers audio** : Données générées ou petits échantillons de test

### Structure des tests
```
tests/
├── __init__.py
├── conftest.py              # Configuration globale pytest
├── fixtures/                # Données de test
│   ├── audio_samples/       # Petits fichiers audio de test
│   ├── rss_feeds/          # Exemples de flux RSS
│   └── transcriptions/     # Exemples de transcriptions
├── unit/
│   ├── test_mongo.py       # Tests du module mongo
│   ├── test_llm.py         # Tests du module LLM
│   ├── test_rss.py         # Tests du module RSS
│   └── test_config.py      # Tests de configuration
├── integration/
│   ├── test_scripts.py     # Tests des scripts
│   └── test_workflows.py   # Tests de workflows complets
└── ui/
    └── test_streamlit.py   # Tests interface Streamlit
```

## Exclusions

### Notebooks expérimentaux
- Tous les notebooks commençant par des chiffres : `nbs/[0-9]*.ipynb`
- Exception : Si un notebook contient de la logique critique, extraire cette logique dans un module .py testable

### Données sensibles
- Pas de données réelles dans les tests
- Utilisation de données synthétiques ou anonymisées

## Configuration CI/CD

### GitHub Actions
- Déclenchement sur tous les push (toutes branches)
- Déclenchement sur les pull requests
- Tests bloquants pour les merges
- Exécution sur Python 3.11 uniquement

### Workflow de test
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-mock pytest-cov
      - name: Run tests
        run: pytest tests/ --verbose
```

## Documentation

### README.md
Ajout d'une section "Tests" sous "Pour développer" expliquant :
- Comment lancer les tests localement
- Structure des tests
- Bonnes pratiques

### docs/readme_unit_test.md
Documentation détaillée incluant :
- Guide complet des tests
- Exemples de tests
- Gestion des mocks
- Données de test
- Ajout dans `mkdocs.yml`

### docs/readme_github.md
Mise à jour pour expliquer :
- Nouveau workflow CI/CD
- Tests automatiques
- Politique de merge

## Migration progressive

### Phase 1 : Infrastructure de base
1. Configuration pytest
2. Tests pour `mongo.py`
3. Tests pour `config.py`
4. CI/CD basique

### Phase 2 : Modules critiques
1. Tests pour `llm.py`
2. Tests pour `rss.py`
3. Amélioration des fixtures

### Phase 3 : Scripts et intégration
1. Tests des scripts principaux
2. Tests d'intégration
3. Tests Streamlit

## Critères de réussite

### Tests unitaires
- ✅ Modules critiques couverts
- ✅ Mocking des APIs externes
- ✅ Tests rapides (< 30 secondes)
- ✅ Tests déterministes

### CI/CD
- ✅ Tests automatiques sur tous les push
- ✅ Blocage des merges en cas d'échec
- ✅ Feedback rapide (< 5 minutes)

### Documentation
- ✅ Guide utilisateur complet
- ✅ Exemples pratiques
- ✅ Intégration dans la doc existante

## Configuration recommandée

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
filterwarnings = ignore::DeprecationWarning
```

### .gitignore (ajouts)
```
# Tests
.pytest_cache/
htmlcov/
.coverage
test_*.db
```

Cette spécification permettra d'implémenter une infrastructure de tests solide tout en respectant les contraintes existantes et en suivant une approche progressive.
