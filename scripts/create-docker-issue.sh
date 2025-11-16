#!/bin/bash
# Script to create GitHub issue for Docker deployment
# Usage: ./create-docker-issue.sh YOUR_GITHUB_TOKEN

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 GITHUB_TOKEN"
    echo ""
    echo "Create a GitHub Personal Access Token at:"
    echo "https://github.com/settings/tokens"
    echo "Required scopes: repo"
    exit 1
fi

GITHUB_TOKEN="$1"
REPO_OWNER="castorfou"
REPO_NAME="lmelp"

# Read the issue content
ISSUE_BODY=$(cat <<'EOF'
## Objectif

Packager l'application **lmelp** (Le Masque et la Plume) sous forme de conteneur Docker et permettre son déploiement aussi bien sur NAS Synology DS 923+ qu'en local sur PC avec gestion automatisée des mises à jour.

## Architecture cible

### Conteneurs

- **Application Streamlit** : Interface web + scripts de traitement (port 8501)
- **MongoDB** :
  - Sur NAS : Utilisation du conteneur existant `mongo` (pas de nouveau conteneur)
  - Sur PC : Conteneur MongoDB local ou service MongoDB installé

### Réseau

- Connexion au réseau bridge Docker existant (NAS) ou réseau dédié (PC)
- Application se connecte à MongoDB via `mongodb://mongo:27017/masque_et_la_plume` (NAS) ou `mongodb://localhost:27017/masque_et_la_plume` (PC)
- Reverse proxy via Application Portal Synology : `lmelp.ascot63.synology.me` (NAS uniquement)

### Volumes Docker

```
lmelp-audios/     → /app/audios      # Fichiers audio téléchargés (plusieurs Go)
lmelp-db-backup/  → /app/db          # Sauvegardes MongoDB
lmelp-logs/       → /app/logs        # Logs applicatifs (optionnel)
```

### Pipeline CI/CD

```
Git push/tag → GitHub Actions → Build image → ghcr.io →
  ├── Webhook Portainer → Déploiement NAS
  └── Pull manuel → Déploiement PC local
```

## Configuration

### Application Streamlit

**Variables d'environnement requises :**

```bash
# Base de données
DB_HOST=mongo                              # ou localhost pour PC
DB_NAME=masque_et_la_plume
DB_LOGS=true

# Flux RSS
RSS_LMELP_URL=https://radiofrance-podcast.net/podcast09/rss_14007.xml

# APIs LLM (au moins une requise)
AZURE_API_KEY=sk-...
AZURE_ENDPOINT=https://....openai.azure.com/
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Google Services (optionnel)
GOOGLE_PROJECT_ID=...
GOOGLE_CUSTOM_SEARCH_API_KEY=...
SEARCH_ENGINE_ID=...

# Chemins
AUDIO_BASE_PATH=/app/audios
```

### Tags Docker

- `latest` : Dernière version stable (auto-déployée via webhook sur NAS)
- `v1.0.0`, `v1.1.0`, etc. : Versions spécifiques
- Repository : `ghcr.io/castorfou/lmelp`

## Phase 1 : Préparation du Dockerfile

### Tâches

- [ ] Créer `docker/Dockerfile` avec multi-stage build optimisé
- [ ] Créer `docker/docker-compose.yml` (pour PC local)
- [ ] Créer `docker/docker-compose.nas.yml` (pour NAS Synology)
- [ ] Créer `docker/.env.template`
- [ ] Créer `.dockerignore`
- [ ] Créer `docker/entrypoint.sh` (support mode batch)

## Phase 2 : CI/CD GitHub Actions

### Tâches

- [ ] Créer `.github/workflows/docker-publish.yml`
- [ ] Configurer GitHub secrets (`PORTAINER_WEBHOOK_URL`)
- [ ] Tester build local des images

## Phase 3 : Configuration NAS Synology (Portainer)

### Tâches

- [ ] Vérifier/créer réseau Docker partagé
- [ ] Créer stack Portainer
- [ ] Configurer variables d'environnement dans Portainer
- [ ] Configurer webhook Portainer
- [ ] Configurer limites de ressources (4 GB RAM, 2 CPU)

## Phase 4 : Configuration PC local

### Tâches

- [ ] Créer fichier `.env` local
- [ ] Tester lancement avec Docker Compose
- [ ] Créer scripts de gestion (start.sh, stop.sh, update.sh, logs.sh, backup-db.sh)

## Phase 5 : Reverse Proxy Synology (NAS uniquement)

### Tâches

- [ ] Configurer Application Portal
- [ ] Configurer certificat SSL
- [ ] Tester accès externe via https://lmelp.ascot63.synology.me

## Phase 6 : Scripts batch en conteneur

### Tâches

- [ ] Créer service Docker pour scripts batch
- [ ] Créer tâches planifiées (cron sur NAS)

## Phase 7 : Documentation

### Tâches

- [ ] Créer `docs/deployment/docker-setup.md`
- [ ] Créer `docs/deployment/local-deployment.md`
- [ ] Créer `docs/deployment/nas-deployment.md`
- [ ] Créer `docs/deployment/update-guide.md`
- [ ] Créer `docs/deployment/troubleshooting.md`
- [ ] Créer `docs/deployment/batch-processing.md`
- [ ] Mettre à jour `README.md`

## Phase 8 : Tests et validation

### Tâches

- [ ] Test build local des images
- [ ] Test docker-compose local complet
- [ ] Test déploiement NAS Portainer
- [ ] Test webhook auto-deploy
- [ ] Test rollback
- [ ] Test scripts batch
- [ ] Test performance et ressources

## Spécifications techniques

### Ressources NAS

- **RAM :** 40 Go disponibles
- **Stockage :** 20 To disponibles
- **Modèle :** Synology DS 923+
- **Réseau :** Accessible depuis Internet

### Limites de ressources conteneurs

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
    reservations:
      cpus: '1'
      memory: 2G
```

**Justification :** Whisper + Transformers = modèles lourds en RAM/CPU

### Healthchecks

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s  # Temps de chargement des modèles ML
```

### Taille estimée

- **Image finale :** ~2.5-3 GB (avec torch, transformers)
- **Volumes :**
  - `lmelp-audios` : 50-100 GB (audio MP3)
  - `lmelp-db-backup` : 1-5 GB (dumps MongoDB)
  - `lmelp-logs` : < 100 MB

## Structure finale du projet

```
lmelp/
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml         # PC local
│   ├── docker-compose.nas.yml     # NAS Synology
│   ├── .env.template
│   ├── entrypoint.sh
│   └── scripts/
│       ├── start.sh
│       ├── stop.sh
│       ├── update.sh
│       ├── logs.sh
│       └── backup-db.sh
├── .github/
│   └── workflows/
│       └── docker-publish.yml
├── .dockerignore
└── docs/
    └── deployment/
        ├── docker-setup.md
        ├── local-deployment.md
        ├── nas-deployment.md
        ├── update-guide.md
        ├── troubleshooting.md
        └── batch-processing.md
```

## Notes importantes

- ⚠️ **Pas de conteneur MongoDB sur NAS** : Utiliser le conteneur `mongo` existant
- ⚠️ **MongoDB sur PC** : Inclus dans docker-compose.yml local
- ⚠️ **Réseau Docker** : NAS (réseau existant bridge) / PC (réseau dédié lmelp-network)
- ⚠️ **Volumes** : Persister les fichiers audio (plusieurs Go)
- ⚠️ **Secrets** : API keys via variables d'environnement
- ⚠️ **Modèles ML** : Téléchargés au premier lancement → temps de démarrage initial long
- ⚠️ **Transcription** : Opération TRÈS coûteuse en ressources
- ⚠️ **Webhook** : Actif uniquement sur NAS, PC fait pull manuel

## Critères de succès

- ✅ Image Docker buildée et publiée sur ghcr.io
- ✅ Application accessible sur http://localhost:8501 (PC) et https://lmelp.ascot63.synology.me (NAS)
- ✅ Connexion MongoDB fonctionnelle
- ✅ Volumes persistants
- ✅ Webhook GitHub → Portainer fonctionnel
- ✅ Scripts batch exécutables en conteneur
- ✅ Rollback possible
- ✅ Documentation complète
- ✅ RAM < 4 GB (utilisation normale)
- ✅ Healthchecks fonctionnels

## Références

- [CLAUDE.md - Documentation projet](../CLAUDE.md)
- [Documentation Portainer](https://docs.portainer.io/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Synology Application Portal](https://kb.synology.com/en-global/DSM/help/DSM/AdminCenter/application_appportal_config)
- [Streamlit Docker Deployment](https://docs.streamlit.io/knowledge-base/tutorials/deploy/docker)
EOF
)

# Create the issue using GitHub API
echo "Creating GitHub issue..."
RESPONSE=$(curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/issues" \
  -d "$(jq -n \
    --arg title "Dockerisation et déploiement multi-environnement" \
    --arg body "$ISSUE_BODY" \
    --argjson labels '["enhancement", "deployment", "docker"]' \
    '{title: $title, body: $body, labels: $labels}'
  )")

# Check if issue was created successfully
ISSUE_NUMBER=$(echo "$RESPONSE" | jq -r '.number')
ISSUE_URL=$(echo "$RESPONSE" | jq -r '.html_url')

if [ "$ISSUE_NUMBER" != "null" ]; then
    echo "✅ Issue #$ISSUE_NUMBER created successfully!"
    echo "🔗 URL: $ISSUE_URL"
else
    echo "❌ Failed to create issue"
    echo "Response: $RESPONSE"
    exit 1
fi
