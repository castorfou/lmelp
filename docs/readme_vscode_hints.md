- [Vscode hints](#vscode-hints) 💡
    - [multicurseur pour remplacer des variables par ex🔄](#multicurseur-pour-remplacer-des-variables-par-ex)
    - [multicurseur sur chaque ligne d'un texte📋](#multicurseur-sur-chaque-ligne-dun-texte)
    - [cacher un repertoire du workspace (par exemple __pycache__)🙈](#cacher-un-repertoire-du-workspace-par-exemple-pycache)
    - [ajouter des sources pour pylance🔌](#ajouter-des-sources-pour-pylance)
    - [tester un petit code python en REPL](#tester-un-petit-code-python-en-repl) 🐍
    - [editer des fichiers markdown](#editer-des-fichiers-markdown) 📝

# Vscode hints

## multicurseur pour remplacer des variables par ex🔄

sur le mot `Ctrl-d` autant de fois que le nombre de variable à remplacer 💻

## multicurseur sur chaque ligne d'un texte📋

(pour inserer un > par ex en debut de ligne) ➡️

selection du texte puis `Shift-Alt-i` 👉

## cacher un repertoire du workspace (par exemple __pycache__)🙈

ouvrir settings.json : `Ctrl-Shift-p` et taper Preferences: Open Settings (JSON) ⚙️

ajouter une entree dans __`files.exclude`__ ➕

```
        "files.exclude": {
                "**/.ipynb_checkpoints": true
        },v
```

## ajouter des sources pour pylance🔌

ouvrir settings.json : `Ctrl-Shift-p` et taper Preferences: Open Settings (JSON) ⚙️

ajouter une entree dans __`python.analysis.extraPaths`__ ➕

```
        "python.analysis.extraPaths": [
                "/home/guillaume/miniforge3/envs/gemini/lib/python3.11/site-packages",
                "/home/guillaume/miniforge3/envs/whisper/lib/python3.11/site-packages"
        ],
```

## tester un petit code python en REPL 🐍

https://code.visualstudio.com/docs/python/run#_native-repl

> You can open the Native REPL via the Command Palette (Ctrl+Shift+P) by searching for Python: **Start Native REPL**. Furthermore, you can send code to the Native REPL via **Smart Send** (Shift+Enter) and Run Selection/Line in Python REPL by setting `"python.REPL.sendToNativeREPL": true` in your settings.json file. 🚀

ca fait tourner un unkonwn.ipnb juste a cote. 🔍

## editer des fichiers markdown 📝

[readme_markdown](readme_markdown.md) 📄
