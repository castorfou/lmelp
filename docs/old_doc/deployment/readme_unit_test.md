# Guide des Tests Unitaires 🧪

## Vue d'ensemble

Le projet LMELP utilise **pytest** comme framework de tests avec une approche de **mocking complet** pour isoler les tests de l'environnement extérieur (MongoDB, APIs, système de fichiers).

## Architecture des Tests

### Structure des Dossiers

```
tests/
├── __init__.py                 # Package principal
├── conftest.py                # Configuration globale et fixtures
├── requirements.txt           # 🆕 Dépendances minimales pour tests
├── fixtures/                  # 🆕 Données de test et utilitaires
│   ├── __init__.py           #     Fonctions load_sample_json/text
│   └── data/                 #     Données d'exemple
│       └── sample_config.json
└── unit/                      # Tests unitaires
    ├── __init__.py
    ├── test_config.py         # Tests du module nbs/config.py
    ├── test_fixtures.py       # 🆕 Tests infrastructure fixtures
    └── test_mongo.py          # Tests du module nbs/mongo.py (à venir)

# Infrastructure CI/CD
.env.test                      # 🆕 Variables d'environnement de test
.github/workflows/tests.yml    # 🆕 GitHub Actions pour CI/CD
```

### Configuration

- **pytest.ini** : Configuration principale avec chemins et options + pytest-env
- **.env.test** : **Variables d'environnement isolées pour tests**
- **tests/requirements.txt** : **Dépendances optimisées (sans PyTorch/ML)**
- **conftest.py** : Fixtures globales et fonction `load_env_test()`

## Infrastructure CI/CD 🚀

### GitHub Actions

Le projet utilise **GitHub Actions** pour l'intégration continue avec un workflow optimisé :

```yaml
# .github/workflows/tests.yml
name: Tests Unitaires
on:
  push:
    branches: [ main, develop, "**devops**", "**test**" ]
  pull_request:
    branches: [ main, develop ]
```

**Optimisations clés :**
- ✅ **Dépendances minimales** : `pip install -r tests/requirements.txt` (30s vs 2m30s)
- ✅ **Coverage ciblée** : `--cov=nbs.config` (97% sur module testé)
- ✅ **Chemins portables** : Fonction `get_project_root()` pour dev/CI
- ✅ **Tests robustesse** : Validation CI/CD depuis `/tmp`

### Performance

| Avant | Après | Gain |
|-------|-------|------|
| 2m30s installation | 30s installation | **5x plus rapide** |
| Tests sur tout `nbs/` | Tests sur `nbs.config` | **Focus ciblé** |
| Chemins absolus | Chemins relatifs | **Portable** |

## Frameworks et Outils

### Dépendances

```txt
# tests/requirements.txt - Dépendances minimales optimisées
pytest>=7.0           # Framework de tests
pytest-mock>=3.10     # Mocking avancé
pytest-env>=0.8       # Variables d'environnement
pytest-cov>=4.0       # Couverture de code
python-dotenv>=1.0.0  # Gestion .env
PyYAML>=6.0           # Parsing YAML (workflow tests)
requests>=2.25.0      # HTTP (tests futurs)
```

### Patterns de Test

#### 1. Structure ARRANGE-ACT-ASSERT

```python
def test_example_function(self, monkeypatch):
    # ARRANGE : Préparer les données et mocks
    test_value = "example"
    monkeypatch.setenv("TEST_VAR", test_value)

    # ACT : Exécuter la fonction à tester
    result = function_to_test()

    # ASSERT : Vérifier les résultats
    assert result == expected_value
```

#### 2. Mocking avec Monkeypatch

```python
# Variables d'environnement
monkeypatch.setenv("API_KEY", "fake_key")
monkeypatch.delenv("OPTIONAL_VAR", raising=False)

# Fonctions et méthodes
def mock_function():
    return "fake_result"

monkeypatch.setattr("module.real_function", mock_function)
```

#### 3. Organisation en Classes

```python
class TestConfigModule:
    """Tests pour le module de configuration"""

    def test_specific_feature(self, monkeypatch):
        # Test spécifique
        pass
```

## Stratégies de Mocking

### 1. Isolation Complète

**Principe** : Aucun test ne doit dépendre de ressources externes.

```python
# ❌ Mauvais : Test dépend de MongoDB réel
def test_save_entity():
    entity = Entity("test")
    entity.save()  # Sauvegarde dans la vraie DB

# ✅ Bon : Test avec MongoDB mocké
@patch('module.get_collection')
def test_save_entity(mock_get_collection):
    mock_collection = Mock()
    mock_get_collection.return_value = mock_collection

    entity = Entity("test")
    entity.save()

    mock_collection.insert_one.assert_called_once()
```

### 1.1. Mocking des Dépendances Lourdes (ML/IA) 🤖

**Problème** : Les dépendances ML comme PyTorch, transformers, llama_index sont lourdes et causent des échecs en CI/CD.

**Solution** : Mock précoce au niveau `sys.modules` avant tout import.

```python
import sys
from unittest.mock import Mock

# 🔥 CRITIQUE : Mocking AVANT les imports
# Mock des modules ML lourds
sys.modules['torch'] = Mock()
sys.modules['transformers'] = Mock()
sys.modules['datasets'] = Mock()

# Mock des modules système problématiques
sys.modules['dbus'] = Mock()
sys.modules['dbus.mainloop'] = Mock()
sys.modules['dbus.mainloop.glib'] = Mock()

# Mock des modules LlamaIndex et sous-modules
sys.modules['llama_index'] = Mock()
sys.modules['llama_index.core'] = Mock()
sys.modules['llama_index.core.base'] = Mock()
sys.modules['llama_index.core.base.embeddings'] = Mock()
sys.modules['llama_index.embeddings'] = Mock()
sys.modules['llama_index.embeddings.azure_openai'] = Mock()

# Mock des modules Google AI
sys.modules['google'] = Mock()
sys.modules['google.generativeai'] = Mock()
sys.modules['google.oauth2'] = Mock()
sys.modules['google.oauth2.service_account'] = Mock()

# PUIS seulement après, importer le module à tester
from nbs.mongo_episode import MongoEpisode
```

**Cas d'Usage Typiques :**

```python
class TestMongoEpisodeWithML:
    """Tests nécessitant du mocking ML complet"""

    def setup_method(self):
        """Mocking précoce pour chaque test"""
        # Déjà fait au niveau module, mais on peut renforcer
        pass

    def test_transcription_without_torch(self):
        """Test de transcription sans installer PyTorch"""
        # Le module est déjà mocké, on peut tester la logique
        episode = MongoEpisode()
        # Test de la logique métier sans dépendances ML
        assert episode.collection_name == "episodes"
```

**⚠️ Points Critiques :**
- Le mocking doit être fait **AVANT** tout import du module testé
- Utiliser `sys.modules` plutôt que `@patch` pour les dépendances transversales
- Mocker les **sous-modules** également (ex: `llama_index.core.base`)
- Tester en environnement **propre** (ex: nouveau terminal) pour valider

### 2. Variables d'Environnement

```python
def test_config_with_env(self, monkeypatch):
    # Test avec variable définie
    monkeypatch.setenv("API_KEY", "test_key")
    result = get_api_key()
    assert result == "test_key"

def test_config_without_env(self, monkeypatch):
    # Test sans variable (valeur par défaut)
    monkeypatch.delenv("API_KEY", raising=False)
    result = get_api_key()
    assert result is None  # ou valeur par défaut
```

### 3. Mocking de Classes et Méthodes

```python
@patch('nbs.mongo.pymongo.MongoClient')
def test_database_connection(mock_client):
    mock_db = Mock()
    mock_client.return_value = {"test_db": mock_db}

    collection = get_collection("localhost", "test_db", "test_coll")

    mock_client.assert_called_once_with("mongodb://localhost:27017/")
```

## Fixtures Globales

### Fixtures Disponibles (conftest.py)

```python
@pytest.fixture
def test_environment():
    """Environnement de test isolé"""

@pytest.fixture
def mock_mongodb():
    """Mock complet de MongoDB"""

@pytest.fixture
def test_config():
    """Configuration de test standard"""
```

### Utilisation des Fixtures

```python
def test_with_fixtures(self, test_environment, mock_mongodb):
    # Les fixtures sont automatiquement injectées
    # test_environment et mock_mongodb sont disponibles
    pass
```

## Couverture de Code

### Mesurer la Couverture

```bash
# Couverture pour un module
pytest tests/unit/test_config.py --cov=nbs.config --cov-report=term-missing

# Couverture globale
pytest --cov=nbs --cov-report=html

# Couverture avec seuil minimum
pytest --cov=nbs --cov-fail-under=90
```

### Interpréter les Résultats

```
Name            Stmts   Miss  Cover   Missing
---------------------------------------------
nbs/config.py      60      2    97%   43, 154
---------------------------------------------
TOTAL              60      2    97%
```

- **Stmts** : Nombre total de lignes de code
- **Miss** : Lignes non testées
- **Cover** : Pourcentage de couverture
- **Missing** : Numéros de lignes manquantes

### Objectifs de Couverture

- **Minimum acceptable** : 80%
- **Objectif** : 90%+
- **Excellence** : 95%+

## Commandes Principales

### Exécution des Tests

```bash
# Tous les tests
pytest

# Tests avec verbosité
pytest -v

# Tests spécifiques
pytest tests/unit/test_config.py
pytest tests/unit/test_config.py::TestConfig::test_specific

# Tests avec pattern
pytest -k "test_config"
```

### Debug et Développement

```bash
# Arrêter au premier échec
pytest -x

# Mode debug avec pdb
pytest --pdb

# Afficher les print()
pytest -s

# Tests en parallèle (avec pytest-xdist)
pytest -n auto
```

### Rapports

```bash
# Rapport HTML de couverture
pytest --cov=nbs --cov-report=html
# Voir tests/htmlcov/index.html

# Rapport XML (pour CI/CD)
pytest --cov=nbs --cov-report=xml

# Rapport JUnit
pytest --junit-xml=tests/results.xml
```

## Bonnes Pratiques

### 1. Nommage

- **Fichiers** : `test_module_name.py`
- **Classes** : `TestModuleName`
- **Fonctions** : `test_specific_behavior`

### 2. Documentation

```python
def test_function_behavior(self, monkeypatch):
    """Test que la fonction retourne la valeur attendue quand X"""
    # Commentaires expliquant les étapes complexes
```

### 3. Isolation

- Chaque test doit être **indépendant**
- Utiliser des **mocks** pour les dépendances externes
- **Nettoyer** après chaque test (automatique avec fixtures)

### 4. Lisibilité

- **Un test = Un comportement**
- **Arrange-Act-Assert** clairement séparés
- **Noms explicites** pour les variables de test

### 5. Mocking des Dépendances Lourdes (Leçons GitHub Actions) 🚀

**Problème Résolu** : Import failures en CI/CD avec dépendances ML/IA

**Stratégie Gagnante** :
1. **Mock précoce** : `sys.modules` avant imports
2. **Mock exhaustif** : Inclure tous les sous-modules
3. **Test isolated** : Valider en environnement propre
4. **Requirements split** : `tests/requirements.txt` minimal

```python
# Pattern éprouvé pour nouveaux tests ML
import sys
from unittest.mock import Mock

# Mock AVANT imports (dans l'ordre de découverte des erreurs)
sys.modules['torch'] = Mock()
sys.modules['transformers'] = Mock()
sys.modules['dbus'] = Mock()
sys.modules['llama_index'] = Mock()
sys.modules['google.generativeai'] = Mock()

# Puis import du module
from nbs.module_with_ml import ModuleToTest
```

**Métriques de Succès** :
- ✅ 214 tests passent en GitHub Actions
- ✅ Installation CI : 30s (vs 2m30s avant)
- ✅ Couverture maintenue : 72.72%
- ✅ Zéro dépendance ML en tests

## Patterns Avancés

### 1. Mocking de Hiérarchies Complexes

```python
class MockRepo:
    def __init__(self, path, search_parent_directories=True):
        self.git = MockGit()

class MockGit:
    def rev_parse(self, option):
        return "/fake/git/root"

monkeypatch.setattr("nbs.config.Repo", MockRepo)
```

### 2. Tests Paramétrés

```python
@pytest.mark.parametrize("input,expected", [
    ("test1", "result1"),
    ("test2", "result2"),
    ("test3", "result3"),
])
def test_multiple_cases(input, expected):
    assert function(input) == expected
```

### 3. Tests d'Exception

```python
def test_function_raises_error():
    with pytest.raises(ValueError, match="Expected error message"):
        function_that_should_fail()
```

## Dépannage

### Problèmes Courants

#### Variables d'Environnement Persistantes

```python
# ❌ Les vraies variables interfèrent
def test_without_env():
    result = get_env_var()  # Utilise la vraie variable !

# ✅ Mock complet
def test_without_env(self, monkeypatch):
    def mock_getenv(key, default=None):
        return None
    monkeypatch.setattr(os, "getenv", mock_getenv)
```

#### Imports et Paths

```python
# ✅ Imports explicites pour les tests
from nbs.config import function_to_test

# ✅ Mocking avec le path complet
monkeypatch.setattr("nbs.config.function", mock_function)
```

### Debug des Tests

```python
# Afficher les valeurs pour debug
def test_debug(self, monkeypatch):
    result = function()
    print(f"Debug: result = {result}")  # Visible avec pytest -s
    assert result == expected
```

## Évolution et Maintenance

### Ajout de Nouveaux Tests

1. **Identifier** le module à tester
2. **Créer** le fichier `test_module.py`
3. **Définir** les classes et méthodes de test
4. **Implémenter** les mocks nécessaires
5. **Vérifier** la couverture

### Refactoring

- **Maintenir** la couverture lors des changements
- **Adapter** les mocks aux nouvelles signatures
- **Regrouper** les fixtures communes

---

*Ce guide évolue avec le projet. N'hésitez pas à l'enrichir !* 🚀
