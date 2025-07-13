# Stratégie d'intégration - Tests Unitaires

## Approche générale

L'intégration des tests unitaires suivra une approche **progressive et non-disruptive** pour minimiser les risques et permettre un retour en arrière facile. L'objectif est d'ajouter une couche de tests sans modifier le code existant.

## Plan d'intégration en 4 phases

### Phase 1 : Fondation (Semaine 1)
**Objectif** : Mettre en place l'infrastructure de base

#### Étapes
1. **Configuration pytest**
   - Création de `pytest.ini`
   - Structure des répertoires de test
   - Configuration de base

2. **Premier module critique : config.py**
   - Tests simples de configuration
   - Validation de l'approche
   - Mise au point des fixtures

3. **CI/CD basique**
   - Workflow GitHub Actions minimal
   - Tests non-bloquants (warning only)
   - Feedback de validation

#### Critères de validation
- [ ] Tests s'exécutent localement
- [ ] CI/CD fonctionne sans erreur
- [ ] Aucun impact sur le code existant

### Phase 2 : Modules critiques (Semaine 2)
**Objectif** : Tester les modules MongoDB et LLM

#### Étapes
1. **Tests mongo.py**
   - Mocking de MongoDB
   - Tests des opérations CRUD
   - Tests de gestion d'erreurs

2. **Tests llm.py**
   - Mocking des APIs (Gemini, OpenAI)
   - Tests des transformations
   - Tests de configuration LLM

3. **Amélioration des fixtures**
   - Données de test réalistes
   - Helpers de test communs

#### Critères de validation
- [ ] Tests des modules critiques passent
- [ ] Couverture des fonctions principales
- [ ] Performance acceptable (< 30s total)

### Phase 3 : Extension (Semaine 3)
**Objectif** : Couvrir les scripts et l'intégration

#### Étapes
1. **Tests rss.py**
   - Mocking des requêtes HTTP
   - Tests de parsing RSS
   - Gestion des erreurs réseau

2. **Tests des scripts principaux**
   - Scripts de migration
   - Scripts de traitement
   - Tests d'intégration basiques

3. **Tests bloquants en CI/CD**
   - Activation des tests bloquants
   - Monitoring des échecs
   - Ajustements si nécessaire

#### Critères de validation
- [ ] Scripts principaux testés
- [ ] CI/CD bloque les merges défaillants
- [ ] Aucune régression détectée

### Phase 4 : Interface et finalisation (Semaine 4)
**Objectif** : Compléter avec Streamlit et documentation

#### Étapes
1. **Tests Streamlit basiques**
   - Tests de logique métier
   - Tests d'interface simples
   - Mocking des données

2. **Documentation complète**
   - Guide développeur
   - Exemples de tests
   - Mise à jour README

3. **Optimisation et nettoyage**
   - Performance des tests
   - Refactoring si nécessaire
   - Validation finale

## Stratégies techniques

### Gestion des dépendances externes

#### MongoDB
```python
# Approche 1: Mocking avec pytest-mock
@pytest.fixture
def mock_mongo(mocker):
    return mocker.patch('nbs.mongo.MongoClient')

# Approche 2: Base en mémoire pour tests d'intégration
@pytest.fixture
def test_db():
    from pymongo_inmemory import MongoClient
    client = MongoClient()
    yield client.test_db
    client.close()
```

#### APIs externes (Gemini, OpenAI)
```python
@pytest.fixture
def mock_gemini_api(mocker):
    mock_response = {
        'candidates': [{'content': {'parts': [{'text': 'Test response'}]}}]
    }
    return mocker.patch('google.generativeai.generate_text', 
                       return_value=mock_response)
```

#### Fichiers audio
```python
@pytest.fixture
def sample_audio_file(tmp_path):
    # Génère un fichier audio minimal pour les tests
    audio_file = tmp_path / "test.mp3"
    # Contenu minimal ou fichier pré-enregistré court
    return audio_file
```

### Isolation des tests

#### Variables d'environnement
```python
# conftest.py
@pytest.fixture(autouse=True)
def test_env(monkeypatch):
    """Isole l'environnement de test"""
    monkeypatch.setenv("MONGODB_URI", "mongodb://test:27017/test")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
```

#### Configuration de test
```python
# tests/conftest.py
@pytest.fixture
def test_config():
    return {
        'mongodb': {'uri': 'mongodb://test:27017/test'},
        'gemini': {'api_key': 'test-key'},
        'paths': {'audio': '/tmp/test_audio'}
    }
```

### Données de test

#### Structure des fixtures
```
tests/fixtures/
├── episodes/
│   ├── complete_episode.json     # Épisode complet
│   ├── minimal_episode.json      # Épisode minimal
│   └── invalid_episode.json      # Cas d'erreur
├── rss/
│   ├── valid_feed.xml           # Flux RSS valide
│   └── invalid_feed.xml         # Flux RSS malformé
├── transcriptions/
│   ├── short_transcript.txt     # Transcription courte
│   └── long_transcript.txt      # Transcription longue
└── audio/
    └── test_5s.mp3             # Audio test 5 secondes
```

## Intégration CI/CD

### Configuration GitHub Actions

#### Workflow complet
```yaml
name: Tests et Qualité

on:
  push:
    branches: [ "main", "develop" ]
  pull_request:
    branches: [ "main" ]

jobs:
  tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
        
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-test.txt
        
    - name: Run tests
      run: |
        pytest tests/ -v --tb=short
        
    - name: Check code quality (optional)
      run: |
        flake8 nbs/ --max-line-length=100
```

#### Progression des tests bloquants
1. **Semaines 1-2** : Tests en mode `continue-on-error: true`
2. **Semaine 3** : Tests bloquants sur nouvelles PRs
3. **Semaine 4** : Tests bloquants sur toutes les branches

## Rollback et récupération

### Points de rollback
1. **Après Phase 1** : Suppression des tests, retour état initial
2. **Après Phase 2** : Désactivation CI/CD, conservation des tests
3. **Après Phase 3** : Désactivation blocage, tests en warning
4. **Phase 4** : Rollback partiel possible (documentation)

### Procédure de rollback
```bash
# Rollback complet
git revert <commit-tests>
rm -rf tests/
git checkout .github/workflows/ci.yml~

# Rollback partiel (désactivation CI/CD)
# Modifier .github/workflows/tests.yml
# continue-on-error: true
```

### Indicateurs de réussite

#### Métriques de validation
- **Temps d'exécution** : < 2 minutes CI/CD total
- **Taux de réussite** : > 95% des tests passent
- **Couverture** : Modules critiques couverts à 80%+
- **Adoption** : Développeurs utilisent les tests localement

#### Signaux d'alerte nécessitant rollback
- Temps CI/CD > 10 minutes
- Tests instables (< 90% de réussite)
- Blocage récurrent des développeurs
- Régression fonctionnelle détectée

## Formation et adoption

### Guide développeur
- Documentation claire des conventions de test
- Exemples concrets pour chaque type de test
- Intégration dans l'IDE (VS Code)

### Processus de développement
1. **Nouveau code** : Tests obligatoires
2. **Modification existante** : Tests de non-régression
3. **Bug fix** : Test reproduisant le bug

### Support continu
- Templates de tests pour nouveaux modules
- Assistance pour cas complexes
- Révision des tests en code review

Cette stratégie assure une intégration progressive, sécurisée et réversible des tests unitaires dans le projet.
