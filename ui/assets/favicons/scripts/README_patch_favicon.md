# Streamlit Favicon Patch

## Problème

Streamlit affiche brièvement son favicon par défaut (couronne blanche sur fond noir) avant de charger le favicon personnalisé configuré via `st.set_page_config()`. Ce "flash" est particulièrement visible lors du chargement initial et du rafraîchissement de la page.

Ce comportement est un **problème connu de Streamlit** sans solution officielle (voir [GitHub issue #9058](https://github.com/streamlit/streamlit/issues/9058) et [discussions communautaires](https://discuss.streamlit.io/t/favicon-and-title-change-during-refresh/74003)).

## Cause

Le favicon par défaut est codé en dur dans les fichiers statiques de Streamlit et est chargé dans le HTML initial avant que JavaScript n'exécute `st.set_page_config()`.

## Solution

Le seul workaround fiable (recommandé par la communauté Streamlit) est de **patcher directement l'installation de Streamlit** en remplaçant son favicon par défaut par notre favicon personnalisé.

## Utilisation

### Appliquer le patch

```bash
python scripts/patch_streamlit_favicon.py
```

Ce script :
1. Sauvegarde le favicon original de Streamlit (si pas déjà fait)
2. Remplace le favicon par défaut par notre favicon personnalisé
3. Affiche un message de confirmation

### Restaurer l'original

```bash
python scripts/patch_streamlit_favicon.py --restore
```

### Quand l'exécuter ?

Le patch doit être appliqué dans ces situations :
- ✅ Après l'installation initiale de Streamlit
- ✅ Après la mise à jour de Streamlit (`pip install --upgrade streamlit`)
- ✅ Après la création d'un nouvel environnement virtuel
- ✅ Lors de la configuration d'un nouveau devcontainer
- ✅ Quand vous voyez le flash du favicon couronne

### Automatisation

Pour automatiser l'application du patch, ajoutez-le au `postCreateCommand` de votre devcontainer :

```json
"postCreateCommand": "pip install -r requirements.txt && python scripts/patch_streamlit_favicon.py"
```

## Tests

Des tests automatisés vérifient que le patch a été correctement appliqué :

```bash
pytest tests/integration/test_streamlit_patch.py -v
```

Ces tests vérifient :
- ✅ Le favicon de Streamlit existe
- ✅ Notre favicon personnalisé existe
- ✅ Une sauvegarde de l'original a été créée
- ✅ Le favicon de Streamlit correspond à notre favicon personnalisé
- ✅ La sauvegarde est différente de notre favicon (preuve qu'un remplacement a eu lieu)

## Fichiers concernés

- **Script** : `scripts/patch_streamlit_favicon.py`
- **Tests** : `tests/integration/test_streamlit_patch.py`
- **Favicon source** : `ui/assets/favicons/favicon-32x32.png`
- **Cible Streamlit** : `.venv/lib/python3.11/site-packages/streamlit/static/favicon.png`
- **Backup** : `.venv/lib/python3.11/site-packages/streamlit/static/favicon.png.original`

## Notes importantes

⚠️ **Le patch est spécifique à l'environnement virtuel** : Si vous créez un nouveau venv ou mettez à jour Streamlit, vous devrez réappliquer le patch.

✅ **Sûr et réversible** : Le script sauvegarde toujours l'original avant de le remplacer. Vous pouvez restaurer à tout moment avec `--restore`.

📦 **Non invasif** : Le patch ne modifie que les fichiers statiques de Streamlit, pas le code source de l'application.

## Références

- [Streamlit GitHub Issue #9058](https://github.com/streamlit/streamlit/issues/9058) - Change page title and favicon in the initial HTML
- [Discussion : Favicon and title change during refresh](https://discuss.streamlit.io/t/favicon-and-title-change-during-refresh/74003)
- [Discussion : Page Title & Icon Flicker](https://discuss.streamlit.io/t/page-title-icon-flicker-before-override/30884)
