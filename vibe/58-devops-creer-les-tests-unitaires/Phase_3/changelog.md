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
- **Rollback** : `git checkout .devcontainer/requirements.txt`
