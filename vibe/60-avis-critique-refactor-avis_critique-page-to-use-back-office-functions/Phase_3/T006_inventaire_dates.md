## T006 - Inventaire complet des patterns de dates

### 📋 Fichiers analysés

**Date de recherche :** 14/07/2025  
**Commande utilisée :** `grep -r "DATE_FORMAT|%d %b %Y|%d %B %Y|strftime" --include="*.py"`

### 🎯 Patterns identifiés

#### 1. **Constante DATE_FORMAT hardcodée (À REFACTORER)**

| Fichier | Ligne | Pattern | Status |
|---------|-------|---------|---------|
| `ui/lmelp.py` | 110 | `DATE_FORMAT = "%d %b %Y"` | ❌ TODO T007 |
| `ui/pages/1_episodes.py` | 26 | `DATE_FORMAT = "%d %b %Y"` | ❌ TODO T007 |
| `ui/pages/4_avis_critiques.py` | - | **MIGRÉ** | ✅ DONE T005 |

#### 2. **Usages strftime() hardcodés (À REFACTORER)**

| Fichier | Ligne | Pattern | Contexte |
|---------|-------|---------|----------|
| `ui/lmelp.py` | 117 | `.strftime(DATE_FORMAT)` | UI principale |
| `ui/pages/1_episodes.py` | 49 | `.strftime(DATE_FORMAT)` (×2) | Plage dates |
| `ui/pages/1_episodes.py` | 65 | `.strftime(DATE_FORMAT)` | Apply sur DataFrame |
| `ui/pages/1_episodes.py` | 72 | `.strftime(DATE_FORMAT)` | Apply sur DataFrame |
| `ui/pages/1_episodes.py` | 98 | `.strftime(DATE_FORMAT)` | Apply sur DataFrame |
| `scripts/store_all_auteurs_from_episode.py` | 22 | `.strftime('%d %b %Y')` | Titre table |
| `scripts/store_all_auteurs_from_episode.py` | 40 | `.strftime("%d %b %Y")` | Description |
| `scripts/store_all_auteurs_from_episode.py` | 122 | `.strftime('%d/%m/%Y')` | Message erreur |
| `scripts/store_all_auteurs_from_all_episodes.py` | 24 | `.strftime('%d %b %Y')` | Titre table |
| `scripts/store_all_auteurs_from_all_episodes.py` | 42 | `.strftime("%d %b %Y")` | Description |
| `scripts/store_all_auteurs_from_all_episodes.py` | 156 | `.strftime("%d/%m/%Y")` | Fichier sortie |
| `nbs/mongo_auteur.py` | 166 | `.strftime("%Y/%m/%d")` | Format date |

#### 3. **Module mongo_episode.py - Formats spécialisés**

| Constante | Valeur | Usage | Action |
|-----------|--------|-------|--------|
| `DATE_FORMAT` | `"%Y-%m-%dT%H:%M:%S"` | Format MongoDB Episodes | ⚠️ À ne **PAS** toucher |
| `LOG_DATE_FORMAT` | `"%d %b %Y %H:%M"` | Logs et messages | ⚠️ **Spécifique** - garder |
| `RSS_DATE_FORMAT` | `"%a, %d %b %Y %H:%M:%S %z"` | Parsing RSS feeds | ⚠️ **Spécifique** - garder |
| `WEB_DATE_FORMAT` | `"%d %b %Y"` | Parsing web | ⚠️ **Spécifique** - garder |

#### 4. **Module nbs/rss.py - Format RSS**

| Fichier | Ligne | Pattern | Action |
|---------|-------|---------|---------|
| `nbs/rss.py` | 69 | `RSS_DATE_FORMAT = "%a, %d %b %Y %H:%M:%S %z"` | ⚠️ **Spécifique** - garder |

### 📈 Analyse des résultats

#### ✅ **DÉJÀ MIGRÉ** (T005)
- `ui/pages/4_avis_critiques.py` : Utilise maintenant `from date_utils import DATE_FORMAT, format_date`

#### 🎯 **CANDIDATS pour T007** (Migration vers date_utils)
1. **`ui/lmelp.py`** : Page principale UI - **PRIORITÉ 1**
2. **`ui/pages/1_episodes.py`** : Page épisodes - **PRIORITÉ 1** 
3. **Scripts auteurs** : Formatage dates utilisateur - **PRIORITÉ 2**
4. **`nbs/mongo_auteur.py`** : 1 occurence - **PRIORITÉ 3**

#### ⚠️ **À NE PAS TOUCHER** (Formats spécialisés)
- **`nbs/mongo_episode.py`** : Formats spécifiques (MongoDB, RSS, Web parsing)
- **`nbs/rss.py`** : Format RSS standard

### 🚀 Recommandations T007

#### Phase 1 - UI Principal (BOUCLE1)
1. **`ui/lmelp.py`** - 2 changements
   - Remplacer `DATE_FORMAT = "%d %b %Y"` → `from date_utils import DATE_FORMAT`
   - Remplacer `.strftime(DATE_FORMAT)` → `format_date(date_obj)`

2. **`ui/pages/1_episodes.py`** - 6 changements
   - Remplacer `DATE_FORMAT = "%d %b %Y"` → `from date_utils import DATE_FORMAT, format_date`
   - Remplacer tous les `.strftime(DATE_FORMAT)` → `format_date(date_obj)`

#### Phase 2 - Scripts (BOUCLE2)  
3. **Scripts auteurs** - Patterns divers à harmoniser
4. **`nbs/mongo_auteur.py`** - 1 occurrence à évaluer

### 🔍 Validation aucune régression

#### Tests existants : ✅ PASSENT
- `tests/unit/test_date_utils.py` : 31/31 tests PASS
- Autres modules : 245/260 tests PASS (échecs attendus T009-T010)

#### Tests à ajouter pour T007
- Tests UI avec nouveaux imports
- Tests scripts avec date_utils
- Tests de régression formatage dates

### 📝 Conclusion T006

**Fichiers identifiés pour migration :** 4 fichiers principaux  
**Patterns à migrer :** ~12 occurrences  
**Formats spécialisés à préserver :** 4 modules (mongo_episode, rss)  
**Impact estimé :** Faible - changements localisés dans UI/scripts
