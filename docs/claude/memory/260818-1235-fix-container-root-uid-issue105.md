# Fix Conteneur lmelp tourne en root - Issue #105

**Date:** 2026-08-18 12:35
**Issue:** #105 - Le conteneur lmelp tourne en root (fichiers audios/transcriptions créés root:root)
**Branch:** 105-le-conteneur-lmelp-tourne-en-root-fichiers-audiostranscriptions-créés-rootroot
**État:** Implémenté et validé côté hôte, commit pas encore effectué (workflow fix-issue en cours)

## Problème Initial

Le conteneur `lmelp` (image `ghcr.io/castorfou/lmelp`) ne définissait aucun utilisateur non-root. Le process tournait en root, donc tout fichier écrit sur les volumes bind-montés (`/app/audios`, `/app/db`, `/app/logs`) héritait de `root:root` côté hôte — constaté concrètement dans `data/audios/.../*.m4a`.

Contexte plus large : même problème sur `docker-lmelp` (mongo, castorfou/docker-lmelp#48, déjà résolu via `gosu`) et `back-office-lmelp` (castorfou/back-office-lmelp#258, encore ouvert). Trouvé pendant l'investigation castorfou/docker-lmelp#47 (migration NAS Synology).

## Contrainte clé (découverte pendant le plan, via retour utilisateur)

L'UID cible **n'est pas fixe** : `1000` sur le laptop, mais **`1027` sur le NAS**. L'image est publiée une seule fois sur `ghcr.io` (pas de `build:` local dans `docker-compose.yml`) et réutilisée telle quelle sur les deux machines → l'UID/GID doit être **configurable à l'exécution**, jamais figé au build.

## Solution Implémentée

### Convention retenue : `PUID`/`PGID`

Aucune variable d'env `PUID`/`PGID` n'était déjà documentée dans `docker-lmelp` ou `back-office-lmelp` (vérifié via `gh api`). Choix : convention *linuxserver.io* (standard reconnu), validé avec l'utilisateur — pourra être réutilisée sur les images sœurs plus tard.

### 1. `docker/build/Dockerfile`

- Ajout de `gosu` dans les paquets apt (stage `base`).
- `ARG APP_UID=1000` / `ARG APP_GID=1000` (défauts de build, référencés en variable — pas de littéral répété) + création de l'utilisateur `appuser` (`groupadd`/`useradd`).
- `ENV HOME=/home/appuser` (nécessaire pour que torch/transformers/whisper résolvent leur cache `~/.cache` dans un répertoire inscriptible en mode `batch-transcribe`/`batch-authors`).
- **Pas de directive `USER` statique** : le conteneur démarre root pour permettre le remap dynamique dans l'entrypoint (test dédié `test_dockerfile_does_not_hardcode_static_user_directive` pour documenter ce choix d'archi).

### 2. `docker/build/entrypoint.sh`

Bloc de setup ajouté en tête, exécuté uniquement à la première passe (`if [ "$(id -u)" = "0" ]; then ... fi`) :

```bash
PUID=${PUID:-1000}
PGID=${PGID:-1000}

CURRENT_UID=$(id -u appuser)
CURRENT_GID=$(id -g appuser)

if [ "$PUID" != "$CURRENT_UID" ] || [ "$PGID" != "$CURRENT_GID" ]; then
    groupmod -o -g "$PGID" appuser
    usermod -o -u "$PUID" appuser
fi

chown -R "$PUID:$PGID" /app/audios /app/db /app/logs

exec gosu appuser "$0" "$@"
```

Le `exec gosu appuser "$0" "$@"` relance le script sous `appuser` ; `id -u` n'étant plus `0`, le bloc est sauté à la deuxième passe et l'exécution continue normalement dans le `case $MODE` existant (inchangé).

**Bug trouvé et corrigé pendant la validation utilisateur** : la première version avait un `chown -R` conditionné à la propriété du **répertoire racine** du volume (`/app/audios`) pour éviter de reparcourir l'arbre à chaque redémarrage. Testé en conditions réelles par l'utilisateur (`docker top` + fichier `root:root` simulé dans un volume monté) : le test de migration échouait silencieusement, car le répertoire top-level était déjà `guillaume:guillaume` (créé sans sudo) alors que le fichier à l'intérieur restait `root:root` — condition fausse, `chown -R` jamais exécuté. C'est exactement le scénario réel de l'issue (dossier parent correct, fichiers dedans en root). **Fix : chown -R rendu inconditionnel**, exécuté à chaque démarrage, sans tenter d'optimiser — cohérent avec le pattern déjà en place dans `mongodb.Dockerfile` (docker-lmelp) qui ne fait pas non plus ce genre de raccourci.

### 3. `docker-compose.yml` / `.env.template` / `deployment/README.md`

Ajout et documentation de `PUID`/`PGID` (comment trouver son UID avec `id -u`/`id -g`, exemple laptop `1000` vs NAS `1027`), + section troubleshooting sur la reprise automatique des fichiers `root:root` existants au redémarrage.

## Tests Ajoutés

**Fichier modifié :** `tests/integration/test_streamlit_config.py` (classes `TestDockerfile` et `TestDockerEntrypoint` existantes, étendues — pas de nouveau fichier de test).

11 nouveaux tests (approche déjà en place dans ce fichier : assertions texte brut sur `Dockerfile`/`entrypoint.sh`, pas de build Docker réel) :
- `test_dockerfile_installs_gosu`, `test_dockerfile_declares_uid_gid_build_args`, `test_dockerfile_creates_non_root_user_from_args`, `test_dockerfile_sets_home_for_non_root_user`, `test_dockerfile_does_not_hardcode_static_user_directive`
- `test_entrypoint_reads_puid_pgid_with_defaults`, `test_entrypoint_remaps_uid_gid`, `test_entrypoint_chowns_volume_directories`, `test_entrypoint_drops_privileges_with_gosu`

**Résultats :** 17/17 tests du fichier passent, 313/313 tests de la suite complète passent. `pre-commit` clean sur les 6 fichiers modifiés.

## Faux positif detect-secrets rencontré

`docker/deployment/.env.template` contenait déjà (avant cette issue) `AZURE_API_KEY=your_azure_api_key_here` sans pragma — jamais détecté auparavant car aucun `.secrets.baseline` n'existe dans ce repo (`detect-secrets` rescane tout fichier passé en argument à chaque run, pas de baseline pour absorber les faux positifs connus). Comme ce fichier devait de toute façon être modifié pour ce fix, ajout du pragma documenté dans `CLAUDE.md` : `AZURE_API_KEY=your_azure_api_key_here  # pragma: allowlist secret`.

## Validation réelle côté hôte (par l'utilisateur, laptop)

1. `docker top` sur un conteneur lancé sans `PUID`/`PGID` → process `streamlit` tourne sous l'UID `1000`, résolu par Docker en `guillau+` (l'utilisateur hôte, confirmant l'absence de root).
2. `docker top` avec `-e PUID=1027 -e PGID=1027` → process tourne sous UID `1027` (non résolu en nom, cohérent puisqu'aucun user local ne matche cet UID sur le laptop — sera résolu en `guillaume` sur le NAS).
3. Fichier `root:root` pré-existant simulé dans un volume bind-monté (`/tmp/test-audios`) → après démarrage du conteneur avec `PUID=1000`/`PGID=1000`, le fichier apparaît bien `guillaume:guillaume` côté hôte (migration automatique confirmée, après le fix du bug ci-dessus).

## Apprentissages Clés

### `docker top` plutôt que `docker exec ... id` pour vérifier l'UID réel d'un process

`docker exec` démarre un nouveau process dans le conteneur avec l'utilisateur par défaut de l'image (root ici, faute de `USER` statique), donc ne reflète pas l'UID sous lequel tourne le process principal après le `gosu`. `docker top <container>` interroge la table de process du host et affiche l'UID réel de chaque process du conteneur — c'est le bon outil pour vérifier un drop de privilège dynamique.

### `entrypoint.sh` ignore les arguments de CMD

`docker run <image> id` ne fait PAS tourner `id` : `entrypoint.sh` ne regarde que `$LMELP_MODE`, jamais `"$@"`, pour décider quoi lancer. Comportement préexistant (pas une régression de ce fix). À garder en tête pour toute future tentative de debug via `docker run <image> <cmd>`.

### Piège du chown conditionnel par répertoire racine

Ne jamais déduire "le contenu d'un répertoire est à jour" à partir de la seule propriété du répertoire top-level — un bind mount peut très bien avoir un répertoire racine correctement possédé (créé par l'utilisateur hôte) tout en contenant des fichiers avec une propriété différente (créés par un ancien process root). Pour un chown de migration, soit chown -R inconditionnel, soit vérifier récursivement (`find ... ! -uid`), jamais se fier au seul stat du dossier racine.

### Process fix-issue : ne pas lancer `pre-commit run --all-files` sur ce repo

Ce repo n'a pas de `.secrets.baseline`, et contient beaucoup de fichiers legacy (notebooks, `vibe/`, scripts) qui ne passent pas `black`/`ruff`/`detect-secrets` proprement. Lancer `pre-commit run --all-files` reformate et modifie des dizaines de fichiers sans rapport avec la tâche en cours. **Toujours cibler `pre-commit run --files <fichiers modifiés>`** pour une tâche donnée.

## Fichiers Modifiés (à committer)

1. `docker/build/Dockerfile`
2. `docker/build/entrypoint.sh`
3. `docker/deployment/docker-compose.yml`
4. `docker/deployment/.env.template`
5. `docker/deployment/README.md`
6. `tests/integration/test_streamlit_config.py`
