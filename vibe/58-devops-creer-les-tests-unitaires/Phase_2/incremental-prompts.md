# Prompts incrémentaux pour l'implémentation des tests unitaires

## BOUCLE 1 : Boucle complète avec test minimal (T001-T011)

### Objectif
Valider la boucle complète **environnement → test simple → CI/CD → documentation** le plus rapidement possible.

### Prompt BOUCLE 1 : Implémentation complète minimale

```
Contexte : Je travaille sur le projet LMELP qui traite des podcasts avec transcription et analyse par LLM.
Structure actuelle : nbs/ contient les modules Python, ui/ contient Streamlit, scripts/ contient les utilitaires.

Je veux implémenter les tâches T001 à T011 pour valider la boucle complète de tests avec un cas ultra-simple.

IMPLÉMENTATION T001-T011 :

T001 - pytest.ini :
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
filterwarnings = ignore::DeprecationWarning
```

T002 - requirements-test.txt :
```
pytest>=7.0
pytest-mock>=3.10
pytest-env>=0.8
```

T003-T005 - Structure tests/ avec __init__.py vides

T006 - tests/unit/test_simple.py :
```python
"""Test ultra-simple pour valider la boucle complète"""
import pytest

def test_import_config():
    """Test que les imports de base fonctionnent"""
    try:
        import nbs.config
        assert True
    except ImportError:
        pytest.fail("Impossible d'importer nbs.config")

def test_basic_math():
    """Test trivial pour vérifier pytest"""
    assert 1 + 1 == 2

def test_environment():
    """Test que l'environnement de test est isolé"""
    import os
    # Ce test doit passer même sans vraie configuration
    assert os.environ.get('TEST_MODE', 'true') == 'true'
```

T007 - .github/workflows/tests.yml :
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt || echo "requirements.txt not found"
          pip install -r requirements-test.txt
      - name: Run tests
        env:
          TEST_MODE: true
        run: pytest tests/ --verbose --tb=short
```

T008 - .gitignore (ajouter) :
```
# Tests
.pytest_cache/
htmlcov/
.coverage
test_*.db
```

T009 - README.md (ajouter dans "Pour développer") :
```markdown
## Tests

Pour lancer les tests localement :
```bash
pip install -r requirements-test.txt
pytest tests/ -v
```

Structure des tests :
- `tests/unit/` : Tests unitaires des modules
- Tests d'intégration et documentation à venir
```

T010 - docs/readme_unit_test.md (guide basique) :
```markdown
# Tests Unitaires

## Lancer les tests
```bash
pytest tests/ -v
```

## Ajouter un test
Créer un fichier `test_*.py` dans `tests/unit/` avec des fonctions `test_*()`.

Guide complet à venir.
```

T011 - mkdocs.yml (ajouter l'entrée) :
```yaml
nav:
  # ... entrées existantes ...
  - Tests: readme_unit_test.md
```

VALIDATION BOUCLE 1 :
1. `pytest tests/` doit passer (3 tests)
2. CI/CD GitHub Actions doit réussir  
3. Documentation doit se générer avec `mkdocs serve`
4. Aucun impact sur le code existant

Préserver : Tout le code existant intact
Compatibilité : Notebooks et Streamlit inchangés
Test de régression : `python -c "import nbs.config"` doit fonctionner
```

## BOUCLE 2 : Tests config.py réels (T012-T015)

### Prompt BOUCLE 2 : Tests du module config

```
Contexte : BOUCLE 1 validée, boucle complète opérationnelle.
Maintenant implémenter les tests réels du module nbs/config.py.

IMPLÉMENTATION T012-T015 :

T012 - tests/unit/test_config.py (remplacer test_simple.py) :
```python
"""Tests du module nbs/config.py"""
import pytest
import os
from unittest.mock import patch, mock_open

def test_config_import():
    """Test basique d'import du module config"""
    import nbs.config
    assert nbs.config is not None

@patch.dict(os.environ, {'TEST_VAR': 'test_value'})
def test_environment_variable_loading():
    """Test du chargement des variables d'environnement"""
    # Tester la logique de configuration si elle existe
    test_var = os.environ.get('TEST_VAR')
    assert test_var == 'test_value'

def test_config_structure():
    """Test de la structure de configuration attendue"""
    # Adapter selon la vraie structure de nbs/config.py
    import nbs.config
    # Test minimal - adapter selon l'API réelle
    assert hasattr(nbs.config, '__file__')

# Ajouter d'autres tests selon l'API réelle de config.py
```

T013-T014 - Fixtures de base pour les tests config

T015 - .env.test pour isoler l'environnement de test

VALIDATION BOUCLE 2 :
1. Tests config.py passent
2. CI/CD continue de fonctionner
3. Aucune régression sur BOUCLE 1

Préserver : Code config.py inchangé
Test de régression : Import config.py depuis notebooks fonctionne
```

## BOUCLE 3 : Tests mongo.py (T016-T017)

### Prompt BOUCLE 3 : Tests MongoDB avec mocking

```
Contexte : Tests config.py opérationnels.
Implémenter tests du module critique nbs/mongo.py avec mocking complet.

IMPLÉMENTATION T016-T017 :

T016 - tests/unit/test_mongo.py avec mocking MongoDB complet
T017 - Fixture episode.json basée sur le schéma réel

Préserver : Module mongo.py inchangé, pas d'appel à la vraie DB
Mocking : Complet de pymongo.MongoClient
Test de régression : Notebooks utilisant mongo.py inchangés
```

## BOUCLE 4 : Tests llm.py (T018-T019)

### Prompt BOUCLE 4 : Tests LLM avec mocking APIs

```
Contexte : Tests mongo.py opérationnels.
Implémenter tests du module nbs/llm.py avec mocking des APIs externes.

IMPLÉMENTATION T018-T019 :

T018 - tests/unit/test_llm.py avec mocking Gemini/OpenAI
T019 - Fixture transcription.txt réaliste

Préserver : Module llm.py inchangé, pas d'appel aux vraies APIs
Mocking : google.generativeai et openai
Test de régression : Pipeline LLM existant fonctionnel
```

## BOUCLE 5 : Tests rss.py (T020-T021)

### Prompt BOUCLE 5 : Tests RSS avec mocking HTTP

```
Contexte : Tests LLM opérationnels.
Implémenter tests du module nbs/rss.py avec mocking des requêtes HTTP.

IMPLÉMENTATION T020-T021 :

T020 - tests/unit/test_rss.py avec mocking requests
T021 - Fixture rss_feed.xml du vrai format

Préserver : Module rss.py inchangé, pas de requête réseau
Mocking : requests.get avec différents codes de statut
Test de régression : Collection RSS automatique fonctionne
```

## BOUCLE 6 : Tests d'intégration (T022-T023)

### Prompt BOUCLE 6 : Tests d'intégration workflows

```
Contexte : Tous les tests unitaires opérationnels.
Implémenter tests d'intégration des workflows principaux.

IMPLÉMENTATION T022-T023 :

T022-T023 - Tests end-to-end avec mocking sélectif des APIs externes
Combiner les modules avec vraies données de test

Préserver : Workflows existants dans notebooks
Test de régression : Scripts de production opérationnels
```

## BOUCLE 7 : Tests Streamlit et finalisation (T024-T026)

### Prompt BOUCLE 7 : Tests UI et documentation finale

```
Contexte : Infrastructure complète opérationnelle.
Finaliser avec tests Streamlit et documentation complète.

IMPLÉMENTATION T024-T026 :

T024-T025 - Tests basiques interface Streamlit
T026 - Documentation finale readme_github.md

Préserver : Interface Streamlit inchangée
Test de régression : Application web opérationnelle
```

## Principes pour tous les prompts

### Validation à chaque boucle
1. **Tests passent** : `pytest tests/ -v` 
2. **CI/CD fonctionne** : GitHub Actions en vert
3. **Documentation générée** : `mkdocs serve` 
4. **Aucune régression** : Code existant inchangé

### Stratégie de rollback par boucle
- **BOUCLE 1** : `rm -rf tests/ pytest.ini requirements-test.txt`
- **BOUCLE 2+** : `git reset --hard boucle-1-complete`

### Points de contrôle
- Après chaque boucle : `git tag boucle-X-complete`
- Test de non-régression : Notebooks principaux s'exécutent
- Performance : Tests < 30s par boucle
