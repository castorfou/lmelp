# Changelog - Tests Unitaires

## 2025-07-13

### [T001] DONE - Configuration pytest de base
- **Fichier créé** : `pytest.ini`
- **Contenu** : Configuration pytest avec testpaths=tests, mode verbose, filterwarnings
- **Impact** : Aucun - fichier de configuration uniquement
- **Régression** : Aucune - imports existants fonctionnent
- **Rollback** : `git rm pytest.ini`

### [T002] DONE - Dépendances de test intégrées
- **Fichier modifié** : `.devcontainer/requirements.txt`
- **Ajouté** : pytest>=7.0, pytest-mock>=3.10, pytest-env>=0.8, pytest-cov>=4.0
- **Stratégie** : Intégration dans requirements existant (cohérent avec workflow uv)
- **Impact** : Aucun - dépendances ajoutées uniquement  
### [T003] DONE - Package tests créé
- **Fichier créé** : `tests/__init__.py`
- **Contenu** : Commentaire descriptif pour package Python
- **Impact** : Aucun - infrastructure de tests uniquement
- **Test** : Import du package tests réussi
- **Rollback** : `rm -rf tests/`

### [T004] DONE - Configuration pytest globale
- **Fichier créé** : `tests/conftest.py`
- **Contenu** : Fixtures globales (test_environment, mock_mongodb, test_config)
- **Correction** : Mock MongoDB complet (pas de connexion réseau), Azure OpenAI uniquement
- **Sécurité** : Isolation complète, aucun appel API/DB réel
- **Impact** : Aucun - configuration pytest uniquement
- **Test** : Import conftest réussi, pytest collecte OK, pas de régression
- **Rollback** : `rm tests/conftest.py`

### [T005] DONE - Structure tests unitaires
- **Fichier créé** : `tests/unit/__init__.py`
- **Contenu** : Package pour tests de fonctions individuelles
- **Structure** : Organisation claire tests unitaires vs intégration
- **Impact** : Aucun - infrastructure de tests uniquement
- **Test** : Import tests.unit réussi, structure tree propre
- **Rollback** : `rm -rf tests/unit/`

### [T006] DONE - Premier test unitaire concret !
- **Fichier créé** : `tests/unit/test_config.py` (renommé depuis test_simple.py)
- **Contenu** : 3 tests pour `get_RSS_URL()` de nbs/config.py
- **Tests** : env var définie, env var absente, type de retour + validation URL
- **Pattern** : ARRANGE-ACT-ASSERT avec monkeypatch
- **Traçabilité** : Convention test_config.py ↔ nbs/config.py
- **Résultat** : ✅ 3/3 tests PASSED en 0.16s 
- **Impact** : Premier code de test fonctionnel avec traçabilité claire !
- **Test** : `pytest tests/unit/test_config.py -v`
- **Rollback** : `rm tests/unit/test_config.py`
