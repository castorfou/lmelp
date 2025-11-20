# Fix du Flash du Favicon Streamlit - Issue #76

**Date**: 2025-11-20 23:42
**Issue**: #76 - Bug favicon (flash de la couronne blanche)
**Branche**: `76-bug-favicon`
**Commit**: `6530621`

## Problème

Après l'implémentation du favicon personnalisé (issue #74), un bug persistait :
- Le favicon par défaut de Streamlit (couronne blanche/fond noir) s'affiche brièvement avant le favicon personnalisé (masque de théâtre/fond vert)
- Les bookmarks capturent l'ancien favicon au lieu du nouveau
- L'expérience utilisateur est dégradée par ce "flash"

## Cause Racine

**Limitation connue de Streamlit** (GitHub issue #9058) :
- Le favicon par défaut est hardcodé dans `streamlit/static/favicon.png`
- Il est chargé dans le HTML initial **avant** que JavaScript n'exécute `st.set_page_config()`
- Aucune option de configuration officielle (`server.favIconPath` n'existe pas dans Streamlit 1.51.0)

**Consensus communautaire** : La seule solution fiable est de **patcher directement l'installation Streamlit**.

## Solution Implémentée

### Script de Patch Automatisé

**Fichier** : `ui/assets/favicons/scripts/patch_streamlit_favicon.py` (144 lignes)

**Fonctionnement** :
1. Détecte automatiquement le chemin d'installation de Streamlit
2. Sauvegarde l'original (`favicon.png.original`)
3. Remplace par notre favicon personnalisé (`favicon-32x32.png`)
4. Support multi-environnement (dev + Docker)

```bash
# Appliquer le patch
python ui/assets/favicons/scripts/patch_streamlit_favicon.py

# Restaurer l'original
python ui/assets/favicons/scripts/patch_streamlit_favicon.py --restore
```

### Automatisation : Deux Contextes

#### 1. Devcontainer (`.devcontainer/postCreateCommand.sh`)

Ajout d'une fonction `patch_streamlit_favicon()` exécutée après l'installation des dépendances :

```bash
patch_streamlit_favicon() {
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        python ui/assets/favicons/scripts/patch_streamlit_favicon.py
    fi
}
```

**Trigger** : À chaque reconstruction du devcontainer

#### 2. Docker (`docker/build/Dockerfile`)

Intégration dans le stage `builder` après l'installation de Streamlit :

```dockerfile
# Patch Streamlit favicon to prevent default crown icon flash
COPY ui/assets/favicons/favicon-32x32.png /tmp/custom-favicon.png
COPY ui/assets/favicons/scripts/patch_streamlit_favicon.py /tmp/patch_streamlit_favicon.py
RUN python /tmp/patch_streamlit_favicon.py && \
    rm /tmp/custom-favicon.png /tmp/patch_streamlit_favicon.py
```

**Avantage** : Le favicon patché est copié dans l'image runtime avec `/usr/local`

## Tests (TDD)

**Fichier** : `tests/integration/test_streamlit_patch.py` (98 lignes, 5 tests)

### Stratégie de Test

Utilisation de **hash MD5** pour comparer les fichiers binaires (images PNG) :

```python
1. test_streamlit_favicon_exists
   → Vérifie existence du favicon Streamlit

2. test_custom_favicon_exists
   → Vérifie existence de notre favicon

3. test_backup_exists_after_patch
   → Vérifie que le backup a été créé

4. test_streamlit_favicon_matches_custom
   → Compare MD5 : Streamlit = notre favicon

5. test_backup_different_from_custom
   → Compare MD5 : backup ≠ notre favicon (preuve du patch)
```

**Résultat** : ✅ 5/5 tests passent

## Documentation

### Fichiers Créés

1. **`ui/assets/favicons/scripts/patch_streamlit_favicon.py`** (144 lignes)
   - Script de patch avec backup automatique
   - Support dev + Docker
   - Messages clairs avec emojis
   - Réversible

2. **`ui/assets/favicons/scripts/README_patch_favicon.md`** (88 lignes)
   - Explication du problème
   - Instructions d'utilisation
   - Quand exécuter le patch
   - Références aux issues Streamlit

3. **`tests/integration/test_streamlit_patch.py`** (98 lignes)
   - 5 tests de validation
   - Vérification par hash MD5

### Fichiers Modifiés

1. **`.devcontainer/postCreateCommand.sh`** (+19 lignes)
   - Fonction `patch_streamlit_favicon()`
   - Appelée après `setup_git`

2. **`docker/build/Dockerfile`** (+7 lignes)
   - Patch dans stage `builder`
   - Cleanup des fichiers temporaires

3. **`ui/assets/favicons/README.md`** (+34 lignes, -5 lignes)
   - Nouvelle section "Patch Streamlit"
   - Documentation de l'automatisation
   - Lien vers README_patch_favicon.md

## Statistiques

- **Total lignes ajoutées** : 390
- **Total lignes supprimées** : 5
- **Fichiers créés** : 3
- **Fichiers modifiés** : 3
- **Tests** : 5 (100% pass)
- **Temps de patch** : < 1 seconde

## Apprentissages Clés

### 1. Problème Non Résolu dans Streamlit

Ce n'est **pas un bug** mais une **limitation d'architecture** :
- Le HTML initial contient le favicon par défaut
- JavaScript (st.set_page_config) s'exécute après
- Streamlit n'a pas d'option pour changer le favicon dans l'HTML initial

### 2. Solution "Hacky" Mais Officiellement Recommandée

La communauté Streamlit recommande explicitement cette approche :
> "I do not believe there is an easy fix for this unless you go directly into root folder of streamlit and edit the title/favicon there"

Références :
- GitHub issue #9058 (ouvert depuis 2023, toujours ouvert)
- Discussion #74003 (juillet 2024)
- Discussion #30884 (septembre 2022)

### 3. Automatisation Critique

Le patch doit être appliqué **automatiquement** car il est perdu à chaque :
- Mise à jour de Streamlit (`pip install --upgrade streamlit`)
- Reconstruction du devcontainer
- Build de l'image Docker
- Création d'un nouvel environnement virtuel

**Notre solution** : Intégrer dans les scripts d'installation (devcontainer + Docker)

### 4. Tests de Modifications Système

Les tests vérifient une modification dans `site-packages` (hors du code du projet).

**Technique** : Utilisation de hash MD5 pour comparer des images binaires :
```python
with open(favicon_path, 'rb') as f:
    file_hash = hashlib.md5(f.read()).hexdigest()
```

### 5. Support Multi-Environnement dans un Seul Script

Le script détecte automatiquement son contexte :
- **Développement** : `project_root/ui/assets/favicons/favicon-32x32.png`
- **Docker** : `/tmp/custom-favicon.png` (copié par Dockerfile)

Cela évite de dupliquer la logique entre dev et prod.

## Impact

### Avant
- ❌ Flash visible du favicon par défaut
- ❌ Bookmarks capturent le mauvais favicon
- ❌ Expérience utilisateur dégradée

### Après
- ✅ Aucun flash, favicon personnalisé dès le début
- ✅ Bookmarks capturent le bon favicon
- ✅ Automatisation complète (dev + prod)
- ✅ Tests garantissent le bon fonctionnement
- ✅ Documentation exhaustive

## Commandes Utiles

```bash
# Appliquer le patch manuellement
python ui/assets/favicons/scripts/patch_streamlit_favicon.py

# Restaurer l'original
python ui/assets/favicons/scripts/patch_streamlit_favicon.py --restore

# Tester le patch
pytest tests/integration/test_streamlit_patch.py -v

# Vérifier l'état du patch
ls -la .venv/lib/python*/site-packages/streamlit/static/favicon.*
```

## Références

- **Streamlit Issue #9058** : https://github.com/streamlit/streamlit/issues/9058
- **Discussion #74003** : https://discuss.streamlit.io/t/favicon-and-title-change-during-refresh/74003
- **Discussion #30884** : https://discuss.streamlit.io/t/page-title-icon-flicker-before-override/30884
- **Issue #76** : https://github.com/castorfou/lmelp/issues/76
- **PR** : (à compléter après création de la PR)

## À Retenir pour le Futur

1. **Streamlit 1.51.0** n'a pas d'option de configuration pour le favicon initial
2. **Le patch est nécessaire** tant que Streamlit n'implémente pas #9058
3. **Automatisation essentielle** : intégrer dans postCreateCommand + Dockerfile
4. **Tests MD5** : bonne approche pour vérifier des modifications de fichiers binaires
5. **Script réversible** : toujours backup avant de patcher
6. **Multi-environnement** : un seul script pour dev + Docker grâce à la détection de contexte

## Conclusion

Cette solution résout **définitivement** le problème du flash du favicon en :
1. **Patchant** directement l'installation Streamlit (seule solution viable)
2. **Automatisant** le patch pour qu'il survive aux reconstructions
3. **Testant** avec validation MD5 du patch
4. **Documentant** pour la maintenabilité future

C'est une approche "hacky" mais c'est la **seule solution recommandée par la communauté** en attendant une implémentation officielle dans Streamlit.
