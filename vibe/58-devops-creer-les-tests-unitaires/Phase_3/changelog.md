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
