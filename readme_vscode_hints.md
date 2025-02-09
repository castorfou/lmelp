- [multicurseur pour remplacer des variables par ex](#multicurseur-pour-remplacer-des-variables-par-ex) 💡
- [multicurseur sur chaque ligne d'un texte (pour insérer un \> par ex en debut de ligne)](#multicurseur-sur-chaque-ligne-dun-texte-pour-insérer-un--par-ex-en-debut-de-ligne) ✏️
- [cacher un repertoire du workspace (par exemple __pycache__)](#cacher-un-repertoire-du-workspace-par-exemple-pycache) 🔒
- [ajouter des sources pour pylance](#ajouter-des-sources-pour-pylance) 📦
- [editer des fichiers markdown](#editer-des-fichiers-markdown) 📝

# multicurseur pour remplacer des variables par ex 🔄

sur le mot `Ctrl-d` autant de fois que le nombre de variable à remplacer 💻

# multicurseur sur chaque ligne d'un texte (pour insérer un > par ex en debut de ligne) 📋

selection du texte puis `Shift-Alt-i` 👉

# cacher un repertoire du workspace (par exemple __pycache__) 🙈

ouvrir settings.json : `Ctrl-Shift-p` et taper Preferences: Open Settings (JSON) ⚙️

ajouter une entree dans __`files.exclude`__ ➕

```
    "files.exclude": {
        "**/.ipynb_checkpoints": true
    },v
```

# ajouter des sources pour pylance 🔌

ouvrir settings.json : `Ctrl-Shift-p` et taper Preferences: Open Settings (JSON) ⚙️

ajouter une entree dans __`python.analysis.extraPaths`__ ➕

```
    "python.analysis.extraPaths": [
        "/home/guillaume/miniforge3/envs/gemini/lib/python3.11/site-packages",
        "/home/guillaume/miniforge3/envs/whisper/lib/python3.11/site-packages"
    ],
```

# editer des fichiers markdown ✏️

[readme_markdown](readme_markdown.md)s 📄
