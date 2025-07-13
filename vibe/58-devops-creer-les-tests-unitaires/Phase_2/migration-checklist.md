# Checklist de migration - Tests Unitaires (Approche boucle rapide)

## Phase préparatoire

### Backup du code actuel
- [ ] Créer une branche de sauvegarde : `git checkout -b backup-before-tests`
- [ ] Vérifier que tous les fichiers sont commités : `git status`
- [ ] Créer un tag de référence : `git tag v-before-tests`
- [ ] Documenter l'état actuel du projet dans `vibe/58-devops-creer-les-tests-unitaires/Phase_4/baseline-state.md`

### Validation de l'environnement de base
- [ ] Environnement de développement fonctionnel (Dev Container)
- [ ] MongoDB accessible et opérationnel
- [ ] Application Streamlit se lance correctement : `streamlit run ui/lmelp.py`
- [ ] Documentation se génère : `mkdocs serve`
- [ ] CI/CD existant passe : vérifier dernière exécution GitHub Actions

## BOUCLE 1 : Boucle complète minimale (T001-T011) ⚡

**Objectif** : Valider la boucle complète environnement → test → CI/CD → doc en < 2h

### Infrastructure de base (T001-T006)
- [ ] **T001** : Créer `pytest.ini` avec configuration de base
- [ ] **T002** : Créer `requirements-test.txt` (pytest, pytest-mock, pytest-env)
- [ ] **T003** : Créer `tests/__init__.py`
- [ ] **T004** : Créer `tests/conftest.py` avec fixtures basiques
- [ ] **T005** : Créer `tests/unit/__init__.py`
- [ ] **T006** : Créer `tests/unit/test_simple.py` (3 tests ultra-simples)

### CI/CD et documentation (T007-T011)
- [ ] **T007** : Créer `.github/workflows/tests.yml` 
- [ ] **T008** : Modifier `.gitignore` (ajout exclusions tests)
- [ ] **T009** : Modifier `README.md` (section Tests basique)
- [ ] **T010** : Créer `docs/readme_unit_test.md` (guide minimal)
- [ ] **T011** : Modifier `mkdocs.yml` (ajout entrée tests)

### Validation BOUCLE 1 🎯
- [ ] **Tests locaux** : `pytest tests/ -v` → 3 tests passent
- [ ] **CI/CD** : Push → GitHub Actions en vert ✅
- [ ] **Documentation** : `mkdocs serve` → page Tests accessible
- [ ] **Non-régression** : `python -c "import nbs.config"` fonctionne
- [ ] **Point de rollback** : `git tag boucle-1-complete`

## BOUCLE 2 : Tests config.py réels (T012-T015)

**Objectif** : Premier vrai test sur module critique

### Tests configuration (T012-T015)
- [ ] **T012** : Créer `tests/unit/test_config.py` (remplace test_simple.py)
- [ ] **T013** : Créer `tests/fixtures/__init__.py`
- [ ] **T014** : Créer `tests/fixtures/sample_config.json`
- [ ] **T015** : Créer `.env.test` pour isolation environnement

### Validation BOUCLE 2
- [ ] Tests config.py passent : module importé et testé
- [ ] CI/CD continue de fonctionner
- [ ] **Point de rollback** : `git tag boucle-2-complete`

## BOUCLE 3 : Tests mongo.py avec mocking (T016-T017)

**Objectif** : Valider mocking des dépendances externes

### Tests MongoDB (T016-T017)
- [ ] **T016** : Créer `tests/unit/test_mongo.py` avec mocking complet pymongo
- [ ] **T017** : Créer `tests/fixtures/sample_episode.json` basé sur schéma réel

### Validation BOUCLE 3
- [ ] Tests mongo.py passent avec mocking
- [ ] Aucun appel à la vraie base MongoDB
- [ ] **Point de rollback** : `git tag boucle-3-complete`

## BOUCLE 4 : Tests llm.py avec mocking APIs (T018-T019)

**Objectif** : Valider mocking des APIs externes

### Tests LLM (T018-T019)
- [ ] **T018** : Créer `tests/unit/test_llm.py` avec mocking Gemini/OpenAI
- [ ] **T019** : Créer `tests/fixtures/sample_transcription.txt`

### Validation BOUCLE 4
- [ ] Tests llm.py passent avec mocking
- [ ] Aucun appel aux vraies APIs (Gemini, OpenAI)
- [ ] **Point de rollback** : `git tag boucle-4-complete`

## BOUCLE 5 : Tests rss.py avec mocking HTTP (T020-T021)

**Objectif** : Compléter les modules critiques

### Tests RSS (T020-T021)
- [ ] **T020** : Créer `tests/unit/test_rss.py` avec mocking requests
- [ ] **T021** : Créer `tests/fixtures/sample_rss_feed.xml`

### Validation BOUCLE 5
- [ ] Tests rss.py passent avec mocking HTTP
- [ ] Aucune requête réseau réelle
- [ ] **Point de rollback** : `git tag boucle-5-complete`

## BOUCLE 6 : Tests d'intégration (T022-T023)

**Objectif** : Valider les workflows complets

### Intégration (T022-T023)
- [ ] **T022** : Créer `tests/integration/__init__.py`
- [ ] **T023** : Créer `tests/integration/test_workflows.py`

### Validation BOUCLE 6
- [ ] Tests d'intégration passent
- [ ] Workflows end-to-end validés
- [ ] **Point de rollback** : `git tag boucle-6-complete`

## BOUCLE 7 : Tests UI et finalisation (T024-T026)

**Objectif** : Compléter avec Streamlit et doc finale

### Interface et documentation (T024-T026)
- [ ] **T024** : Créer `tests/ui/__init__.py`
- [ ] **T025** : Créer `tests/ui/test_streamlit.py`
- [ ] **T026** : Modifier `docs/readme_github.md` (doc CI/CD finale)

### Validation BOUCLE 7
- [ ] Tests Streamlit basiques passent
- [ ] Documentation complète et cohérente
- [ ] **Point de rollback** : `git tag boucle-7-complete`

## Validation finale

### Tests de non-régression complets
- [ ] Tous les notebooks critiques s'exécutent sans erreur
- [ ] Application Streamlit fonctionne entièrement
- [ ] Collection automatique RSS opérationnelle  
- [ ] Pipeline LLM de production fonctionnel
- [ ] Documentation complète se génère

### Performance et stabilité
- [ ] **PHASE 1** : < 30 secondes (tests simples)
- [ ] **PHASE 2-3** : < 1 minute (tests config + mongo)
- [ ] **PHASE 4-5** : < 2 minutes (tous tests unitaires)
- [ ] **PHASE 6-7** : < 3 minutes (tests complets)
- [ ] **CI/CD total** : < 5 minutes
- [ ] Taux de réussite > 95% sur 10 exécutions

### Nouvelles fonctionnalités implémentées ✅
- [x] Infrastructure pytest opérationnelle dès BOUCLE 1
- [x] CI/CD automatique validé dès BOUCLE 1  
- [x] Documentation intégrée dès BOUCLE 1
- [x] Tests modules critiques : config, mongo, llm, rss
- [x] Tests d'intégration workflows
- [x] Tests interface Streamlit basiques

## Métriques de succès par boucle

### BOUCLE 1 (Critique - Boucle complète)
- Temps implémentation : ≤ 2 heures ⚡
- Tests passent : 3/3 ✓
- CI/CD fonctionne : ✓
- Documentation accessible : ✓

### BOUCLE 2-7 (Extension progressive)
- 1 boucle par jour maximum
- Aucune régression détectée
- Performance maintenue
- Rollback possible à tout moment

## Stratégies de rollback par boucle

### Rollback BOUCLE 1 (si problème)
```bash
rm -rf tests/
git rm pytest.ini requirements-test.txt
git checkout README.md mkdocs.yml .gitignore
git rm .github/workflows/tests.yml docs/readme_unit_test.md
```

### Rollback BOUCLE 2+ (retour boucle précédente)
```bash
git reset --hard boucle-X-complete  # X = boucle précédente
```

### Rollback urgence (état initial)
```bash
git reset --hard v-before-tests
```

Cette approche garantit une validation de la boucle complète dès la BOUCLE 1 ! 🚀
