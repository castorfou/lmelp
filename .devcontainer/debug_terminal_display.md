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

## Cette session (2026-04-03, suite)

Problèmes constatés après les corrections précédentes :
- Le script allait jusqu'au bout, mais l'affichage était très moche
- Impossible de configurer `gh` (authentification GitHub)

### Fix 1 — affichage moche : suppression du wrapper awk

`exec > >(awk '{ print strftime("[%H:%M:%S]"), $0; fflush() }' | tee ...)` remplacé par
`exec > >(tee /tmp/postCreate_full.log) 2>&1`

L'`awk` ajoutait `[HH:MM:SS]` sur chaque ligne et cassait les séquences ANSI
(output de `zsh-in-docker`, emojis, couleurs). Le log reste capturé dans
`/tmp/postCreate_full.log`, sans dénaturer l'affichage.

```diff
-exec > >(awk '{ print strftime("[%H:%M:%S]"), $0; fflush() }' | tee /tmp/postCreate_full.log) 2>&1
+exec > >(tee /tmp/postCreate_full.log) 2>&1
```

### Fix 2 — gh auth : montage de ~/.config/gh depuis le host

`postCreateCommand` et `postStartCommand` sont non-interactifs dans VS Code —
`gh auth login` (qui nécessite un navigateur ou un prompt) ne peut pas y fonctionner.

Solution : monter `~/.config/gh` depuis le host dans `devcontainer.json`, identique
aux montages `.gitconfig` et `.ssh` déjà en place.

```diff
+        "source=${localEnv:HOME}/.config/gh,target=/home/vscode/.config/gh,type=bind,consistency=cached"
```

Le container hérite ainsi automatiquement de l'authentification GitHub du host.

**Prérequis :** être authentifié sur le host (`gh auth login`) avant le rebuild.

## État après rebuild

### Diagnostic (2026-04-03)

Le montage `~/.config/gh` fonctionne bien (bind sur `/dev/nvme0n1p2`, même partition).
Le `hosts.yml` est bien synchronisé host ↔ container.

Mais le token stocké dans `hosts.yml` était invalide (OAuth token révoqué ou expiré côté GitHub).

**Fix immédiat :** relancer `gh auth login --git-protocol https --web` dans le terminal du container.
Comme c'est un bind mount, le nouveau token est automatiquement partagé avec le host.

### Fix 3 — postStartCommand avec vérification gh auth

Le `postStartCommand` est maintenant un script `.devcontainer/scripts/post_start.sh` qui :
- Affiche le message de bienvenue
- Vérifie `gh auth status` et affiche clairement le statut
- Si non authentifié, indique la commande à lancer

```diff
-    "postStartCommand": "echo '🚀 lmelp - Environnement prêt!'"
+    "postStartCommand": "bash .devcontainer/scripts/post_start.sh"
```

**Prérequis :** avoir un token GitHub valide (via `gh auth login` sur le host ou dans le container).
