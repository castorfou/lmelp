# Favicons pour l'interface Streamlit

Ce répertoire contient tous les fichiers favicon pour l'application web lmelp.

## Structure des fichiers

- `favicon.png` - Image source haute résolution (1327x1328)
- `favicon.ico` - Fichier ICO multi-taille (16x16, 32x32, 48x48)
- `favicon-16x16.png` - Format 16x16 pixels
- `favicon-32x32.png` - Format 32x32 pixels
- `favicon-48x48.png` - Format 48x48 pixels
- `apple-touch-icon.png` - Icône Apple (180x180)
- `android-chrome-192x192.png` - Icône Android/PWA (192x192)
- `android-chrome-512x512.png` - Icône Android/PWA (512x512)
- `scripts/generate_favicons.py` - Script de génération multi-formats
- `scripts/patch_streamlit_favicon.py` - Script de patch Streamlit (fix le flash de la couronne)
- `scripts/README_patch_favicon.md` - Documentation complète du patch Streamlit

## Génération des favicons

Pour régénérer tous les favicons à partir de l'image source :

```bash
# Depuis la racine du projet
python ui/assets/favicons/scripts/generate_favicons.py
```

Le script :
1. Charge l'image source `favicon.png`
2. Génère tous les formats requis avec redimensionnement LANCZOS
3. Crée un fichier ICO multi-taille

## Utilisation dans Streamlit

### Configuration du favicon personnalisé

Les favicons sont configurés dans le fichier UI principal avec PIL.Image :

```python
from pathlib import Path
from PIL import Image

# Load favicon
favicon_path = Path(__file__).parent / "assets" / "favicons" / "favicon-32x32.png"
favicon = Image.open(favicon_path)

st.set_page_config(
    page_title="le masque et la plume",
    page_icon=favicon,  # Objet PIL.Image
    layout="wide",
)
```

### Patch Streamlit (fix du flash de couronne)

**Problème** : Streamlit affiche brièvement son favicon par défaut (couronne blanche) avant de charger notre favicon personnalisé.

**Solution** : Patcher l'installation Streamlit pour remplacer le favicon par défaut.

```bash
# Appliquer le patch
python ui/assets/favicons/scripts/patch_streamlit_favicon.py

# Restaurer l'original
python ui/assets/favicons/scripts/patch_streamlit_favicon.py --restore
```

**Automatisation** : Le patch est appliqué automatiquement lors de :
- La création du devcontainer (`.devcontainer/postCreateCommand.sh`)
- La construction de l'image Docker (`docker/build/Dockerfile`)

📖 Voir [`scripts/README_patch_favicon.md`](scripts/README_patch_favicon.md) pour la documentation complète

## Source

Image originale provenant du projet back-office-lmelp :
https://github.com/castorfou/back-office-lmelp/blob/main/frontend/public/gimp_favicon/favicon.png

## Dépendances

- Python 3.11+
- Pillow (PIL) pour le traitement d'images

## Notes

- L'image source doit être au format PNG avec transparence (RGBA)
- La résolution recommandée : > 512x512 pixels
- Le script utilise LANCZOS pour un redimensionnement de haute qualité
