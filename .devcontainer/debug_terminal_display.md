# Diagnostic : problème d'affichage terminal lors du build devcontainer

## Symptôme

Pendant le `postCreateCommand`, le terminal VS Code ("show log") cesse de scroller.
Seules 2 lignes se mettent à jour :
- la barre de progression (au centre de l'écran)
- la dernière ligne

À partir de ce moment, l'installation semble bloquée mais tourne en réalité en arrière-plan.

## Cause racine

Les programmes qui utilisent des séquences ANSI / `\r` (carriage return) pour mettre à jour
leur barre de progression "en place" cassent l'affichage du viewer de log VS Code, qui n'est
pas un vrai TTY.

Coupables identifiés dans l'ordre d'exécution :

1. **`apt-get upgrade`** dans `update_system()` → barre `Progress: [XX%] [###...]`
2. **`uv sync`** dans `create_python_environment()` → barre de progression uv

## Ce qui a été corrigé

### Session précédente
- `install_locales()` : ajout de `-o Dpkg::Use-Pty=0` sur les `apt install`

### Cette session (2026-04-03)
- `update_system()` : ajout de `-o Dpkg::Use-Pty=0` sur le `apt-get upgrade`

```diff
 sudo apt-get -y -qq -o Dpkg::Options::="--force-confdef" \
     -o Dpkg::Options::="--force-confnew" \
     -o Dpkg::Options::="--force-unsafe-io" \
+    -o Dpkg::Use-Pty=0 upgrade || {
```

## Ce qui reste à tester / corriger

- **`uv sync`** dans `create_python_environment()` : ajouter `--no-progress`
  ou positionner `UV_NO_PROGRESS=1` dans `containerEnv` du `devcontainer.json`

```bash
# Option A : dans le script
uv sync --active --all-extras --no-progress

# Option B : dans devcontainer.json containerEnv
"UV_NO_PROGRESS": "1"
```

## Note sur gh auth login

`gh auth login` n'est **pas** la cause du blocage — c'est juste là que le terminal
était déjà cassé et rendait l'interaction impossible. Le call a été remplacé par un
simple message demandant à l'utilisateur de le faire manuellement après le build.
