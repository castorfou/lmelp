# Stratégie d'imports - Projet LMELP

## Vue d'ensemble

Le projet LMELP utilise différentes stratégies d'imports selon le contexte, optimisées pour chaque usage.

## Stratégies par contexte

### 📁 `nbs/` - Modules principaux
**Pattern** : Imports directs (même dossier)
```python
# ✅ Dans nbs/mongo.py
from config import get_DB_VARS
```
**Justification** : Modules dans le même dossier, imports simples et directs.

### 📁 `scripts/` - Scripts utilitaires
**Pattern** : Ajout explicite au sys.path
```python
# ✅ Dans scripts/*.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../nbs")))
from config import get_RSS_URL
```
**Justification** : Scripts ponctuels exécutés depuis différents endroits, besoin de chemin absolu.

### 📁 `ui/` - Interface Streamlit
**Pattern** : Fonction centralisée add_to_sys_path()
```python
# ✅ Dans ui/pages/*.py  
from ui_tools import add_to_sys_path
add_to_sys_path()
from mongo_episode import Episodes
```
**Justification** : Apps Streamlit avec logique réutilisable, fonction centralisée dans ui_tools.py.

### 📁 `tests/` - Tests unitaires
**Pattern** : Imports explicites avec chemin complet
```python
# ✅ Dans tests/unit/*.py
from nbs.config import get_RSS_URL
from nbs.mongo import get_collection
```
**Justification** : Isolation maximale, traçabilité claire, pas de modification sys.path.

## Avantages de cette approche

| **Contexte** | **Avantage** |
|-------------|-------------|
| `nbs/` | Simple, pas de configuration |
| `scripts/` | Portable, fonctionne de partout |
| `ui/` | Centralisé, facile à maintenir |
| `tests/` | Isolé, explicite, pas d'effets de bord |

## Convention de nommage des tests

```
tests/unit/test_config.py     ← teste nbs/config.py
tests/unit/test_mongo.py      ← teste nbs/mongo.py  
tests/unit/test_llm.py        ← teste nbs/llm.py
```

**Pattern** : `test_<module>.py` teste `nbs/<module>.py`

## Exemples concrets

### Import dans un test
```python
# tests/unit/test_config.py
from nbs.config import get_RSS_URL  # ✅ Explicite et clair

def test_get_RSS_URL_with_env_var():
    # Test code...
```

### Import dans un script
```python
# scripts/get_transcription.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../nbs")))
from config import get_RSS_URL  # ✅ Après modification sys.path
```

### Import dans Streamlit
```python
# ui/pages/episodes.py
from ui_tools import add_to_sys_path
add_to_sys_path()
from mongo_episode import Episodes  # ✅ Après add_to_sys_path()
```

## Évolutions futures

Si le projet grandit, considérer :
- **Package Python installable** : `pip install -e .` pour développement
- **Imports absolus partout** : `from lmelp.config import get_RSS_URL`
- **Structure package standard** : `src/lmelp/` layout

Pour l'instant, le status quo fonctionne bien et respecte les contraintes de chaque contexte.
