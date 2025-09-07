# Checklist de Migration : Refactorisation Avis Critiques

## Phase Préparatoire

### Backup et Environnement
- [ ] **Backup complet du projet**
  ```bash
  git add -A
  git commit -m "Backup avant refactorisation avis critiques"
  git tag backup-before-avis-critique-refactor
  ```
- [ ] **Vérification environnement de développement**
  - [ ] MongoDB accessible et fonctionnel
  - [ ] Python environment activé avec toutes les dépendances
  - [ ] Jupyter Lab/Notebook accessible pour nbdev
  - [ ] Streamlit fonctionnel (`streamlit run ui/lmelp.py`)

### Tests Baseline
- [ ] **Exécution suite de tests complète AVANT modification**
  ```bash
  pytest tests/ -v --tb=short
  # Noter tous les tests qui passent actuellement
  ```
- [ ] **Capture état actuel interface utilisateur**
  - [ ] Screenshots page avis critiques
  - [ ] Test manuel génération avis critique
  - [ ] Vérification messages d'erreur avec résumé tronqué

## BOUCLE 1 : Foundation avec Tests Simples (T001-T012)

### Création Fixtures et Tests
- [ ] **T001 : Fixtures avis critique** ✅ `tests/fixtures/data/avis_critique_data.json`
  - [ ] Exemples avis critiques valides (≥3 cas)
  - [ ] Exemples avis critiques tronqués (≥5 cas différents)
  - [ ] Structure JSON compatible collection MongoDB
  - [ ] Validation format dates cohérent

- [ ] **T002 : Tests unitaires AvisCritique** ✅ `tests/unit/test_mongo_avis_critique.py`
  - [ ] Structure suivant pattern `test_mongo_livre.py`
  - [ ] Mocks appropriés (MongoDB, config)
  - [ ] Tests classe AvisCritique (init, propriétés)
  - [ ] Tests méthodes validation (is_summary_truncated, etc.)
  - [ ] Tests constructeurs alternatifs (from_oid, from_episode_oid)
  - [ ] Tests méthodes CRUD (save_if_valid, update, delete)
  - [ ] Couverture ≥80% prévue

- [ ] **T003 : Tests unitaires date_utils** ✅ `tests/unit/test_date_utils.py`
  - [ ] Tests fonction format_episode_date() 
  - [ ] Tests constante DATE_FORMAT
  - [ ] Tests cas limites (dates invalides, formats différents)
  - [ ] Tests compatibilité formats existants projet

### Implémentation et Refactorisation Date Utils
- [ ] **T004 : Implémentation date_utils** ✅ `nbs/date_utils.py`
  - [ ] Constante DATE_FORMAT centralisée
  - [ ] Fonction format_episode_date() robuste
  - [ ] Implémentation pour passer tous tests T003
  - [ ] Import sans erreur

- [ ] **T005 : Migration 4_avis_critiques.py** 
  - [ ] Backup automatique avant modification
  - [ ] Remplacement DATE_FORMAT hardcodé
  - [ ] Import date_utils ajouté
  - [ ] Aucune régression fonctionnelle

- [ ] **T006 : Recherche exhaustive usages dates**
  ```bash
  grep -r "DATE_FORMAT\|%d %b %Y\|strftime.*%d.*%b.*%Y" --include="*.py" .
  ```
  - [ ] Inventaire complet fichiers utilisant formatage dates
  - [ ] Documentation des patterns trouvés

- [ ] **T007 : Refactorisation globale dates**
  - [ ] Migration de tous les fichiers identifiés en T006
  - [ ] Remplacement formats hardcodés par date_utils
  - [ ] Tests de non-régression après chaque fichier

- [ ] **T008 : Validation tests date_utils**
  ```bash
  pytest tests/unit/test_date_utils.py -v
  ```
  - [ ] Tous tests date_utils passent (100%)
  - [ ] Aucune régression dans autres tests
  - [ ] Performance maintenue

### Modules Core AvisCritique
- [ ] **T009 : Notebook principal** ✅ `nbs/py mongo helper avis_critiques.ipynb`
  - [ ] Structure identique à `py mongo helper livres.ipynb`
  - [ ] Commentaire `# |default_exp mongo_avis_critique`
  - [ ] Classe AvisCritique héritant BaseEntity
  - [ ] Toutes méthodes spécifiées (validation, CRUD, constructeurs)
  - [ ] Utilisation date_utils pour formatage
  - [ ] Documentation et exemples inclus
  - [ ] Compatible nbdev

- [ ] **T010 : Génération module** ✅ `nbs/mongo_avis_critique.py`
  ```bash
  cd nbs/
  jupyter nbconvert --to python "py mongo helper avis_critiques.ipynb" --output mongo_avis_critique
  ```
  - [ ] Module généré sans erreur
  - [ ] Import `from mongo_avis_critique import AvisCritique` fonctionne
  - [ ] Aucune erreur de syntaxe

### Validation Foundation
- [ ] **T011 : Tests foundation passent**
  ```bash
  pytest tests/unit/test_mongo_avis_critique.py -v
  ```
  - [ ] Tous les tests unitaires passent (100%)
  - [ ] Aucune erreur d'import ou de dépendance
  - [ ] Coverage ≥80% sur nouveau module
  - [ ] Aucune régression tests existants

- [ ] **T012 : Backup UI** ✅ `ui/pages/4_avis_critiques.py.backup`
  ```bash
  cp ui/pages/4_avis_critiques.py ui/pages/4_avis_critiques.py.backup.$(date +%Y%m%d_%H%M%S)
  ```

**CHECKPOINT BOUCLE 1** : ✅ Foundation solide, utilitaires dates centralisés, tests passent, module fonctionnel

## BOUCLE 2 : Refactorisation Interface Utilisateur (T013-T020)

### Refactorisation Progressive
- [ ] **T013 : Refactor get_summary_from_cache()** 
  - [ ] Remplacement logique MongoDB directe par AvisCritique.from_episode_oid()
  - [ ] Préservation signature de fonction
  - [ ] Préservation gestion d'erreur exacte
  - [ ] Test manuel : récupération cache fonctionne

- [ ] **T014 : Refactor save_summary_to_cache()**
  - [ ] Remplacement logique validation par avis_critique.is_valid_for_saving()
  - [ ] Utilisation avis_critique.get_truncation_debug_info()
  - [ ] Préservation EXACTE messages UI (warnings, success, info)
  - [ ] Test manuel : sauvegarde fonctionne identiquement

- [ ] **T015 : Refactor check_existing_summaries()**
  - [ ] Remplacement accès MongoDB direct par méthodes AvisCritique
  - [ ] Préservation logique de filtrage
  - [ ] Test manuel : indicateurs résumés existants corrects

### Nettoyage Code
- [ ] **T016 : Suppression is_summary_truncated()**
  - [ ] Fonction supprimée (~45 lignes)
  - [ ] Aucune référence restante dans le code
  
- [ ] **T017 : Suppression debug_truncation_detection()**
  - [ ] Fonction supprimée (~55 lignes)
  - [ ] Aucune référence restante dans le code

### Mise à jour Imports
- [ ] **T018 : Ajout imports nouveaux modules**
  ```python
  from mongo_avis_critique import AvisCritique
  from date_utils import DATE_FORMAT, format_episode_date
  ```
  - [ ] Imports ajoutés sans conflit
  - [ ] Aucune erreur d'import au lancement

- [ ] **T019 : Remplacement constante DATE_FORMAT**
  - [ ] Suppression `DATE_FORMAT = "%d %b %Y"` hardcodée
  - [ ] Utilisation `date_utils.DATE_FORMAT`
  - [ ] Formatage dates reste identique

### Validation Refactorisation
- [ ] **T020 : Tests régression UI**
  ```bash
  pytest tests/ui/test_4_avis_critiques.py -v
  ```
  - [ ] Tous tests UI passent
  - [ ] Mise à jour mocks si nécessaire
  - [ ] Interface streamlit lance sans erreur

**CHECKPOINT BOUCLE 2** : ✅ Interface refactorisée, comportement identique

## BOUCLE 3 : Tests d'Intégration et Validation (T021-T024)

### Tests d'Intégration
- [ ] **T021 : Tests intégration MongoDB** ✅ `tests/integration/test_avis_critique_integration.py`
  - [ ] Tests avec vraie base MongoDB
  - [ ] Pattern suivant tests/integration/ existants
  - [ ] Tests persistence complète (save, retrieve, update, delete)
  - [ ] Tests cas limites (données manquantes, format incorrect)

- [ ] **T022 : Validation tests intégration**
  ```bash
  pytest tests/integration/test_avis_critique_integration.py -v
  ```
  - [ ] Tous tests intégration passent
  - [ ] Aucune erreur de connexion MongoDB
  - [ ] Données test nettoyées après exécution

### Finalisation Intégration
- [ ] **T023 : Update imports globaux**
  ```python
  # nbs/__init__.py
  from .mongo_avis_critique import AvisCritique
  ```
  - [ ] Import global ajouté
  - [ ] Module accessible depuis autres parties projet

- [ ] **T024 : Validation manuelle complète**
  ```bash
  streamlit run ui/lmelp.py
  ```
  **CHECKLIST VALIDATION MANUELLE** :
  - [ ] Page avis critiques charge sans erreur
  - [ ] Sélection épisode avec transcription fonctionne
  - [ ] Génération nouvel avis critique fonctionne
  - [ ] Récupération avis critique existant fonctionne
  - [ ] Détection résumé tronqué fonctionne (avec debug info)
  - [ ] Messages UI identiques (success, warning, info, error)
  - [ ] Performance subjective maintenue
  - [ ] Aucune erreur console/logs
  - [ ] Navigation entre pages fluide

**CHECKPOINT BOUCLE 3** : ✅ Intégration validée, comportement préservé

## BOUCLE 4 : Documentation et Finalisation (T025-T026)

### Documentation
- [ ] **T025 : Documentation module** ✅ `docs/mongo_avis_critique.md`
  - [ ] Guide utilisation AvisCritique
  - [ ] Exemples code pratiques
  - [ ] Migration depuis ancienne approche
  - [ ] API reference principale

### Finalisation Notebook
- [ ] **T026 : Finalisation notebook**
  - [ ] Nettoyage cellules développement temporaires
  - [ ] Documentation complète et claire
  - [ ] Exemples fonctionnels
  - [ ] Génération nbdev propre

## Tests de Régression Finaux

### Suite Complète
- [ ] **Tests unitaires complets**
  ```bash
  pytest tests/unit/ -v --cov=nbs/mongo_avis_critique.py --cov-report=html
  ```
  - [ ] Couverture ≥90% nouveau module
  - [ ] Tous tests existants passent
  - [ ] Aucune régression détectée

- [ ] **Tests intégration complets**
  ```bash
  pytest tests/integration/ -v
  ```
  - [ ] Tous tests passent
  - [ ] Aucun impact sur autres modules

- [ ] **Tests interface utilisateur**
  ```bash
  pytest tests/ui/ -v
  ```
  - [ ] Tous tests UI passent
  - [ ] Mocks mis à jour correctement

## Validation Déploiement

### Préparation Production
- [ ] **Code review interne**
  - [ ] Respect conventions projet
  - [ ] Qualité code maintenue
  - [ ] Documentation suffisante
  - [ ] Tests complets

- [ ] **Validation environnement**
  - [ ] Tests sur environnement similaire production
  - [ ] Dépendances correctes
  - [ ] Configuration appropriée

### Go/No-Go Déploiement
- [ ] **Critères techniques** ✅
  - [ ] Tous tests passent
  - [ ] Aucune régression détectée
  - [ ] Documentation complète

- [ ] **Critères fonctionnels** ✅
  - [ ] Interface utilisateur identique
  - [ ] Toutes fonctionnalités préservées
  - [ ] Gestion erreur robuste
  - [ ] Rollback testé et fonctionnel

**VALIDATION FINALE** : ✅ Refactorisation réussie, déploiement approuvé

## Plan de Rollback d'Urgence

### Rollback Rapide (< 5 minutes)
```bash
# 1. Restauration fichier UI
cp ui/pages/4_avis_critiques.py.backup ui/pages/4_avis_critiques.py

# 2. Suppression nouveaux modules
rm -f nbs/mongo_avis_critique.py
rm -f nbs/date_utils.py

# 3. Redémarrage service
systemctl restart streamlit  # ou processus équivalent

# 4. Validation rapide
curl -f http://localhost:8501/health || echo "ÉCHEC"
```

### Rollback Complet (< 15 minutes)
```bash
# 1. Retour version git
git checkout backup-before-avis-critique-refactor

# 2. Nettoyage fichiers résiduels
rm -f nbs/py\ mongo\ helper\ avis_critiques.ipynb
rm -f tests/unit/test_mongo_avis_critique.py
rm -f tests/unit/test_date_utils.py
rm -f tests/fixtures/data/avis_critique_data.json
rm -f tests/integration/test_avis_critique_integration.py
rm -f nbs/date_utils.py

# 3. Tests validation rollback
pytest tests/ui/test_4_avis_critiques.py -v

# 4. Validation manuelle
streamlit run ui/lmelp.py
```

---

**Date de création** : _____________  
**Responsable technique** : _____________  
**Validateur** : _____________
