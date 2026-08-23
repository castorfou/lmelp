# Transcription automatisée via PGX

lmelp transcrit les épisodes audio en s'appuyant sur une station GPU dédiée sur le réseau
local (surnommée **PGX**). Un service de transcription tourne en permanence sur cette
station : il surveille un répertoire, transcrit automatiquement tout fichier audio qui y
est déposé, et écrit le résultat dans un répertoire de sortie.

Depuis l'interface Streamlit (page **Épisodes**), le bouton **▶️ Lancer la transcription**
(ou **🔄 Relancer la transcription**) déclenche l'intégralité du pipeline :

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
| `PGX_HOST`                      | Nom d'hôte ou IP de la station PGX                                   | `thinkstationpgx-d7ba.local`                                  |
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
la configuration du service de transcription installé sur PGX.

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

Avec PGX allumée, vérifiez la connectivité réseau et SSH depuis la machine qui exécute
lmelp :

```bash
ping -c 3 thinkstationpgx-d7ba.local
ssh -i "$PGX_SSH_KEY_PATH" -o IdentitiesOnly=yes "$PGX_USER@$PGX_HOST" echo ok
```

Ou, plus simplement, ouvrez la page **PGX** de l'interface Streamlit et cliquez sur
**🔄 Vérifier la disponibilité de PGX**.

Ensuite, ouvrez un épisode sans transcription et cliquez sur
**▶️ Lancer la transcription** pour un premier essai bout-en-bout.

## Dépannage

### "PGX injoignable"

- Vérifiez que PGX est bien sous tension et sur le réseau — aucun réveil automatique n'est
  tenté, elle doit être allumée manuellement au préalable.
- Vérifiez la page **PGX** de l'interface Streamlit pour un diagnostic rapide de
  disponibilité.

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

## Voir aussi

- [`.env.example`](https://github.com/castorfou/lmelp/blob/main/.env.example) — liste
  complète des variables d'environnement du projet.
