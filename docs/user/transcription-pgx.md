# Transcription automatisée via PGX

lmelp transcrit les épisodes audio en s'appuyant sur une station GPU dédiée sur le réseau
local (surnommée **PGX**). Un service de transcription tourne en permanence sur cette
station : il surveille un répertoire, transcrit automatiquement tout fichier audio qui y
est déposé, et écrit le résultat dans un répertoire de sortie.

Depuis l'interface Streamlit (page d'accueil ou page **Épisodes**), les boutons
**📥 Télécharger transcriptions**, **▶️ Lancer la transcription** et **🔄 Relancer la
transcription** sont **désactivés** tant que la checklist de la page **PGX** n'est pas
entièrement verte (machine joignable, authentification SSH, répertoires distants) — un
message invite alors à consulter cette page pour le diagnostic avant de réessayer, plutôt
que de laisser échouer une transcription vouée à l'échec avec une erreur SSH brute.

Une fois PGX prête, le bouton **▶️ Lancer la transcription** (ou **🔄 Relancer la
transcription**) déclenche l'intégralité du pipeline :

1. Vérification que PGX est joignable sur le réseau.
2. Envoi du fichier audio vers PGX par `scp`.
3. Attente de la transcription générée par le service PGX.
4. Rapatriement du fichier de transcription.
5. Intégration du texte en base MongoDB.

Chaque étape est affichée dans l'interface au fur et à mesure. Si une étape échoue (PGX
injoignable, erreur de transfert, timeout), un message explicite s'affiche et la
transcription n'est pas modifiée en base — il n'y a pas de repli automatique vers un autre
mécanisme de transcription.

!!! info "Pas de réveil automatique"
    PGX doit être **allumée manuellement** avant de lancer une transcription. Le pipeline
    ne tente aucun réveil à distance (Wake-on-LAN) : sur une machine Wi-Fi uniquement avec
    la mise en veille système désactivée pour des raisons de stabilité GPU, ce mécanisme
    n'est pas fiable. Si PGX est injoignable, le pipeline s'arrête avec un message clair
    vous invitant à l'allumer puis à réessayer.

## Prérequis

- Une station PGX sur le **même réseau local** que l'endroit où tourne lmelp, avec :
    - Le service de transcription (surveillance de répertoire) déjà en place et démarré.
    - Un compte SSH accessible par clé (pas de mot de passe).
- Aucune génération manuelle de clé SSH n'est nécessaire pour un déploiement Docker : la
  clé dédiée est générée automatiquement au premier démarrage du conteneur (voir
  [Clé SSH dédiée](#cle-ssh-dediee) ci-dessous).

## Variables d'environnement

Toutes les variables suivantes doivent être définies dans `.env` (voir
[`.env.example`](https://github.com/castorfou/lmelp/blob/main/.env.example)) :

| Variable                        | Description                                                          | Exemple                                                       |
| -------------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------- |
| `PGX_HOST`                      | IP de la station PGX (**IP directe recommandée**, voir note ci-dessous) | `192.168.50.151`                                            |
| `PGX_USER`                      | Utilisateur SSH sur PGX                                              | `f279814`                                                     |
| `PGX_SSH_KEY_PATH`              | Chemin vers la clé privée SSH dédiée                                 | `/app/keys/pgx_lmelp_ed25519` (déploiement Docker)             |
| `PGX_REMOTE_AUDIO_ROOT`         | Répertoire distant surveillé par le service de transcription sur PGX | `/home/f279814/git/whisper-docker/docker/data/audios`         |
| `PGX_REMOTE_TRANSCRIPTION_ROOT` | Répertoire distant où PGX écrit les transcriptions                   | `/home/f279814/git/whisper-docker/docker/data/transcriptions` |

Optionnelles (valeurs par défaut entre parenthèses) :

| Variable                      | Rôle                                                                     | Défaut          |
| ------------------------------- | --------------------------------------------------------------------------- | ------------------ |
| `PGX_TRANSCRIPTION_TIMEOUT_S` | Délai d'attente maximal pour qu'une transcription apparaisse             | `1800` (30 min) |
| `PGX_POLL_INTERVAL_S`         | Intervalle entre deux vérifications de disponibilité de la transcription | `10`            |

Sur PGX, les fichiers audio envoyés par lmelp sont attendus sous
`PGX_REMOTE_AUDIO_ROOT/<année>/` et la transcription correspondante est cherchée sous
`PGX_REMOTE_TRANSCRIPTION_ROOT/<année>/<nom_du_fichier>.txt` — organisation à adapter selon
la configuration du service de transcription installé sur PGX. Le répertoire année est créé
automatiquement sur PGX s'il n'existe pas encore.

!!! warning "Utiliser une IP directe, pas un nom `.local`"
    Le nom mDNS (`thinkstationpgx-d7ba.local` par exemple) peut résoudre vers des adresses
    **différentes** selon l'endroit d'où la requête part (résolveur DNS local, cache mDNS,
    configuration réseau spécifique à une machine) — un même nom a pu pointer vers deux IP
    différentes selon qu'on interroge depuis le host ou depuis un conteneur sur cette même
    machine. Utilisez toujours l'**IP directe** de PGX pour `PGX_HOST`, idéalement une IP
    fixe (réservation DHCP côté routeur) pour qu'elle ne change pas dans le temps.

## Clé SSH dédiée {#cle-ssh-dediee}

### Déploiement Docker (recommandé)

La clé SSH dédiée à lmelp (distincte de toute clé personnelle) est **générée
automatiquement** au démarrage du conteneur si elle n'existe pas encore à l'emplacement
`PGX_SSH_KEY_PATH`, sur un volume persistant (`/app/keys`) — jamais intégrée à l'image
Docker elle-même, donc jamais exposée publiquement.

Après le premier démarrage, ouvrez la page **PGX** de l'interface Streamlit : elle affiche
la clé publique générée et la commande exacte à exécuter sur PGX pour l'autoriser :

```bash
echo '<contenu de la clé publique>' >> ~/.ssh/authorized_keys
```

La page **PGX** affiche aussi le statut de disponibilité de la machine (🟢/🔴).

### Usage hors conteneur (dev/scripts locaux)

Pour exécuter le pipeline en dehors du conteneur Docker, générez la clé vous-même :

```bash
ssh-keygen -t ed25519 -f ~/.ssh/pgx_lmelp_ed25519 -N ""
```

Puis déployez-la sur PGX, en contournant `ssh-copy-id` si nécessaire :

```bash
cat ~/.ssh/pgx_lmelp_ed25519.pub | ssh votre_utilisateur@thinkstationpgx-d7ba.local "cat >> ~/.ssh/authorized_keys"
```

!!! warning "Piège : ssh-agent peut fausser la vérification"
    Sans `-o IdentitiesOnly=yes`, `ssh -i` et `ssh-copy-id` peuvent s'authentifier via une
    **autre** clé déjà connue de votre agent SSH (une clé personnelle par exemple), sans
    jamais utiliser réellement la clé dédiée testée. `ssh-copy-id` peut alors afficher
    *"All keys were skipped because they already exist on the remote system"* alors que la
    clé dédiée n'a en réalité jamais été ajoutée à `authorized_keys`. Pour vérifier sans
    ambiguïté qu'une clé précise est bien déployée, comparez les empreintes :

    ```bash
    # Sur votre machine
    ssh-keygen -lf ~/.ssh/pgx_lmelp_ed25519.pub

    # Sur PGX (ou via ssh depuis votre machine)
    ssh-keygen -lf ~/.ssh/authorized_keys
    ```

    L'empreinte de la clé dédiée doit apparaître dans la liste retournée par la seconde
    commande.

## Vérifier la configuration

Avec PGX allumée, ouvrez la page **PGX** de l'interface Streamlit : une checklist de
diagnostic s'exécute **automatiquement** au chargement (et via le bouton
**🔄 Relancer les vérifications**), avec un statut 🟢/🔴/⚪ par étape :

1. **Machine joignable** — le port SSH répond.
2. **Authentification SSH (clé dédiée)** — une vraie connexion est testée (pas juste le
   port ouvert). En cas d'échec, le détail SSH réel (stderr de la tentative) est affiché
   entre parenthèses pour en identifier la cause précise (voir [Dépannage](#depannage)).
3. **Répertoire audio distant** — `PGX_REMOTE_AUDIO_ROOT` existe sur PGX.
4. **Répertoire transcriptions distant** — `PGX_REMOTE_TRANSCRIPTION_ROOT` existe sur PGX.

Chaque étape court-circuite les suivantes si elle échoue (inutile de tester
l'authentification si injoignable, par exemple).

Pour un diagnostic manuel en ligne de commande, depuis la machine qui exécute lmelp :

```bash
ping -c 3 "$PGX_HOST"
ssh -i "$PGX_SSH_KEY_PATH" -o IdentitiesOnly=yes \
    -o UserKnownHostsFile=/tmp/lmelp_pgx_known_hosts \
    "$PGX_USER@$PGX_HOST" echo ok
```

(`UserKnownHostsFile` pointe vers un fichier temporaire, pas le `~/.ssh/known_hosts` par
défaut — utile si ce dernier est en lecture seule, par exemple dans un devcontainer.)

Ensuite, ouvrez un épisode sans transcription et cliquez sur
**▶️ Lancer la transcription** pour un premier essai bout-en-bout.

## Dépannage {#depannage}

### "PGX injoignable"

- Vérifiez que PGX est bien sous tension et sur le réseau — aucun réveil automatique n'est
  tenté, elle doit être allumée manuellement au préalable.
- Vérifiez la page **PGX** de l'interface Streamlit pour un diagnostic rapide de
  disponibilité.

### "Authentification SSH (clé dédiée)" échoue malgré une clé bien déployée

Depuis la checklist de diagnostic de la page **PGX**, le message affiché pour cette étape
inclut désormais le **détail SSH réel** (stderr de la tentative de connexion), entre
parenthèses après le message générique — utile pour distinguer une clé effectivement
absente d'`authorized_keys` d'une tout autre cause :

- `Permissions ... are too open` / `UNPROTECTED PRIVATE KEY FILE!` : la clé privée
  pointée par `PGX_SSH_KEY_PATH` a des permissions trop ouvertes (ex: `777` au lieu de
  `600`) — ssh l'ignore alors silencieusement et retombe sur une authentification par mot
  de passe, qui échoue. Rencontré en déploiement Docker sur NAS Synology : un mécanisme
  externe au conteneur (probablement une resynchronisation ACL DSM sur le volume partagé)
  réapplique périodiquement de mauvaises permissions sur le fichier de clé — voir
  [castorfou/docker-lmelp#61](https://github.com/castorfou/docker-lmelp/issues/61) pour le
  correctif infra (watchdog qui réapplique `chmod 600`). Si le déploiement ne dispose pas
  de ce watchdog, un `chmod 600` manuel sur le volume suffit à débloquer la situation.
- `Host key verification failed` / avertissement de clé d'hôte : voir la section dédiée
  plus bas.
- Un stderr vide malgré l'échec (aucun détail entre parenthèses) : le message générique
  reste alors le seul indice — vérifiez bien le contenu d'`authorized_keys` sur PGX dans ce
  cas précis.

### Échec de l'envoi ou du rapatriement du fichier (`scp`)

- Vérifiez que `PGX_SSH_KEY_PATH` pointe vers une clé privée valide et lisible par le
  processus qui exécute lmelp.
- Vérifiez que la clé publique correspondante est bien dans le `authorized_keys` du compte
  `PGX_USER` sur PGX (voir la page **PGX** de l'interface pour la clé publique générée).
- Vérifiez que `PGX_REMOTE_AUDIO_ROOT`/`PGX_REMOTE_TRANSCRIPTION_ROOT` existent bien sur
  PGX et sont accessibles en écriture/lecture par `PGX_USER`.

### Timeout en attente de la transcription

- Vérifiez que le service de transcription tourne bien sur PGX et surveille effectivement
  `PGX_REMOTE_AUDIO_ROOT`.
- Pour un épisode particulièrement long, augmentez `PGX_TRANSCRIPTION_TIMEOUT_S`.

### "WARNING: POSSIBLE DNS SPOOFING DETECTED" ou avertissement de clé d'hôte changée

- Le plus souvent bénin sur un réseau local que vous contrôlez : la clé d'hôte de PGX a
  changé (réinstallation, reconfiguration de `sshd`), ou `PGX_HOST` était configuré avec un
  nom `.local` qui a résolu vers une IP différente entre deux connexions (voir l'avertissement
  plus haut sur l'IP directe).
- Si l'avertissement apparaît en dehors du pipeline lmelp (ex: en testant manuellement), et
  que `~/.ssh/known_hosts` est en lecture seule (devcontainer), utilisez un fichier
  temporaire : `-o UserKnownHostsFile=/tmp/un_fichier` avec `-o
  StrictHostKeyChecking=accept-new` pour contourner sans modifier le fichier par défaut.

## Voir aussi

- [`.env.example`](https://github.com/castorfou/lmelp/blob/main/.env.example) — liste
  complète des variables d'environnement du projet.
