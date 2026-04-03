# Dockerisation et déploiement multi-environnement

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

#### ✅ Créer `docker/Dockerfile`

```dockerfile
# Multi-stage build optimisé pour taille et performance
FROM python:3.11-slim as base

# Stage 1: Build dependencies
FROM base as builder
WORKDIR /build
RUN pip install uv
COPY .devcontainer/requirements.txt .
RUN uv pip install --system -r requirements.txt

# Stage 2: Runtime
FROM base as runtime
WORKDIR /app

# Copier Python + deps depuis builder
COPY --from=builder /usr/local /usr/local

# Copier code source
COPY nbs/ /app/nbs/
COPY ui/ /app/ui/
COPY scripts/ /app/scripts/

# Créer répertoires pour volumes
RUN mkdir -p /app/audios /app/db /app/logs

# Exposer port Streamlit
EXPOSE 8501

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Point d'entrée
CMD ["uv", "run", "streamlit", "run", "ui/lmelp.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Caractéristiques :**
- Multi-stage build pour optimiser la taille
- Utilise `uv` pour gestion rapide des dépendances
- Image de base Python 3.11 slim
- Healthcheck intégré pour monitoring
- Port 8501 exposé
- Support des volumes pour données persistantes

#### ✅ Créer `docker/docker-compose.yml` (pour PC local)

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7
    container_name: lmelp-mongodb
    restart: unless-stopped
    ports:
      - "27017:27017"
    volumes:
      - lmelp-mongodb-data:/data/db
    environment:
      - MONGO_INITDB_DATABASE=masque_et_la_plume
    networks:
      - lmelp-network

  app:
    image: ghcr.io/castorfou/lmelp:latest
    container_name: lmelp-app
    restart: unless-stopped
    depends_on:
      - mongodb
    ports:
      - "8501:8501"
    volumes:
      - lmelp-audios:/app/audios
      - lmelp-db-backup:/app/db
      - lmelp-logs:/app/logs
    environment:
      # Base de données
      - DB_HOST=mongodb
      - DB_NAME=masque_et_la_plume
      - DB_LOGS=true
      # Flux RSS
      - RSS_LMELP_URL=https://radiofrance-podcast.net/podcast09/rss_14007.xml
      # APIs (à configurer via .env)
      - AZURE_API_KEY=${AZURE_API_KEY}
      - AZURE_ENDPOINT=${AZURE_ENDPOINT}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      # Chemins
      - AUDIO_BASE_PATH=/app/audios
    networks:
      - lmelp-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  lmelp-mongodb-data:
  lmelp-audios:
  lmelp-db-backup:
  lmelp-logs:

networks:
  lmelp-network:
    driver: bridge
```

#### ✅ Créer `docker/docker-compose.nas.yml` (pour NAS Synology)

```yaml
version: '3.8'

services:
  app:
    image: ghcr.io/castorfou/lmelp:latest
    container_name: lmelp-app
    restart: unless-stopped
    ports:
      - "8501:8501"
    volumes:
      - lmelp-audios:/app/audios
      - lmelp-db-backup:/app/db
      - lmelp-logs:/app/logs
    environment:
      # Base de données (utilise MongoDB existant)
      - DB_HOST=mongo
      - DB_NAME=masque_et_la_plume
      - DB_LOGS=true
      # Flux RSS
      - RSS_LMELP_URL=https://radiofrance-podcast.net/podcast09/rss_14007.xml
      # APIs (à configurer dans Portainer)
      - AZURE_API_KEY=${AZURE_API_KEY}
      - AZURE_ENDPOINT=${AZURE_ENDPOINT}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      # Chemins
      - AUDIO_BASE_PATH=/app/audios
    networks:
      - bridge  # Réseau existant avec conteneur mongo
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  lmelp-audios:
  lmelp-db-backup:
  lmelp-logs:

networks:
  bridge:
    external: true  # Utilise réseau existant
```

#### ✅ Créer `docker/.env.template`

```bash
# Copier ce fichier vers .env et remplir les valeurs

# APIs LLM (au moins une requise)
AZURE_API_KEY=
AZURE_ENDPOINT=
OPENAI_API_KEY=
GEMINI_API_KEY=

# Google Services (optionnel)
GOOGLE_PROJECT_ID=
GOOGLE_CUSTOM_SEARCH_API_KEY=
SEARCH_ENGINE_ID=
```

#### ✅ Créer `.dockerignore`

```
# Git
.git/
.github/
.gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/
env/

# Tests
tests/
htmlcov/
.coverage
.pytest_cache/

# Documentation
docs/
site/
*.md
!CLAUDE.md

# Development
.devcontainer/
.vscode/
*.ipynb_checkpoints/

# Data (ne pas inclure dans l'image)
audios/
db/
*.db
*.sqlite

# Notebooks (déjà convertis en .py)
nbs/*.ipynb

# Build artifacts
dist/
build/
*.egg-info/

# Logs
*.log
logs/

# Environment
.env
.env.*
!.env.template
```

#### ✅ Créer `docker/entrypoint.sh` (optionnel, pour scripts batch)

```bash
#!/bin/bash
set -e

# Mode d'exécution : web (Streamlit) ou batch (scripts)
MODE=${LMELP_MODE:-web}

if [ "$MODE" = "web" ]; then
    echo "Starting Streamlit web interface..."
    exec uv run streamlit run ui/lmelp.py --server.port=8501 --server.address=0.0.0.0
elif [ "$MODE" = "batch-update" ]; then
    echo "Running RSS update script..."
    exec python scripts/update_emissions.py
elif [ "$MODE" = "batch-transcribe" ]; then
    echo "Running transcription script..."
    exec python scripts/get_all_transcriptions.py
elif [ "$MODE" = "batch-authors" ]; then
    echo "Running author extraction script..."
    exec python scripts/store_all_auteurs_from_all_episodes.py
else
    echo "Unknown mode: $MODE"
    echo "Available modes: web, batch-update, batch-transcribe, batch-authors"
    exit 1
fi
```

## Phase 2 : CI/CD GitHub Actions

### Tâches

#### ✅ Créer `.github/workflows/docker-publish.yml`

```yaml
name: Build and Publish Docker Image

on:
  push:
    branches:
      - main
    tags:
      - 'v*.*.*'
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=semver,pattern={{major}}
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: docker/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Trigger Portainer Webhook (NAS deployment)
        if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/v')
        run: |
          curl -X POST ${{ secrets.PORTAINER_WEBHOOK_URL }}
        continue-on-error: true
```

#### ✅ Configurer GitHub secrets

Aller dans `Settings > Secrets and variables > Actions` et ajouter :

- `PORTAINER_WEBHOOK_URL` : URL du webhook Portainer pour déploiement automatique sur NAS

**Note :** `GITHUB_TOKEN` est automatiquement fourni par GitHub Actions.

#### ✅ Tester build local

```bash
# Build de l'image
docker build -f docker/Dockerfile -t lmelp:test .

# Test de l'image
docker run --rm -p 8501:8501 \
  -e DB_HOST=localhost \
  -e GEMINI_API_KEY=your_key \
  lmelp:test

# Accéder à http://localhost:8501
```

## Phase 3 : Configuration NAS Synology (Portainer)

### Tâches

#### ✅ Vérifier/créer réseau Docker partagé

```bash
# SSH sur le NAS
ssh admin@nas-synology

# Vérifier que le conteneur mongo est sur le réseau bridge
docker network inspect bridge

# Si nécessaire, connecter mongo au réseau
docker network connect bridge mongo
```

#### ✅ Créer stack Portainer

1. Ouvrir Portainer web UI
2. Aller dans `Stacks > Add stack`
3. **Name:** `lmelp`
4. **Build method:** Repository (ou Web editor avec docker-compose.nas.yml)
5. **Repository URL:** `https://github.com/castorfou/lmelp`
6. **Repository reference:** `main`
7. **Compose path:** `docker/docker-compose.nas.yml`

#### ✅ Configurer variables d'environnement dans Portainer

Dans l'onglet **Environment variables** de la stack :

```
AZURE_API_KEY=sk-...
AZURE_ENDPOINT=https://....openai.azure.com/
GEMINI_API_KEY=...
OPENAI_API_KEY=...
GOOGLE_PROJECT_ID=...
GOOGLE_CUSTOM_SEARCH_API_KEY=...
SEARCH_ENGINE_ID=...
```

#### ✅ Configurer webhook Portainer

1. Dans la stack `lmelp`, aller dans **Webhooks**
2. Cliquer sur **Add webhook**
3. Copier l'URL générée (format : `https://portainer.nas/api/webhooks/xxx`)
4. Ajouter cette URL dans GitHub Secrets comme `PORTAINER_WEBHOOK_URL`

#### ✅ Configurer limites de ressources

Dans Portainer, éditer le service `lmelp-app` :
- **Memory limit:** 4 GB (Whisper + Transformers = lourd)
- **CPU limit:** 2 cores
- **Restart policy:** Unless stopped

## Phase 4 : Configuration PC local

### Tâches

#### ✅ Créer fichier `.env` local

```bash
cd lmelp/docker/
cp .env.template .env
# Éditer .env avec vos clés API
```

#### ✅ Lancer avec Docker Compose

```bash
# Première fois : pull de l'image
docker compose -f docker/docker-compose.yml pull

# Lancer les services
docker compose -f docker/docker-compose.yml up -d

# Voir les logs
docker compose -f docker/docker-compose.yml logs -f

# Accéder à l'application
open http://localhost:8501
```

#### ✅ Scripts de gestion (création de helpers)

Créer `docker/scripts/start.sh` :
```bash
#!/bin/bash
docker compose -f docker/docker-compose.yml up -d
```

Créer `docker/scripts/stop.sh` :
```bash
#!/bin/bash
docker compose -f docker/docker-compose.yml down
```

Créer `docker/scripts/update.sh` :
```bash
#!/bin/bash
docker compose -f docker/docker-compose.yml pull
docker compose -f docker/docker-compose.yml up -d
```

Créer `docker/scripts/logs.sh` :
```bash
#!/bin/bash
docker compose -f docker/docker-compose.yml logs -f
```

Créer `docker/scripts/backup-db.sh` :
```bash
#!/bin/bash
# Backup MongoDB depuis le conteneur
docker exec lmelp-mongodb mongodump \
  --db masque_et_la_plume \
  --out /data/db/backup/$(date +%Y%m%d_%H%M%S)
```

## Phase 5 : Reverse Proxy Synology (NAS uniquement)

### Tâches

#### ✅ Configurer Application Portal

1. Ouvrir **Control Panel > Login Portal > Advanced > Reverse Proxy**
2. Cliquer **Create**
3. **Configuration :**
   - **Reverse Proxy Name:** lmelp
   - **Source:**
     - Protocol: HTTPS
     - Hostname: lmelp.ascot63.synology.me
     - Port: 443
     - Enable HSTS: ✓
   - **Destination:**
     - Protocol: HTTP
     - Hostname: localhost
     - Port: 8501
   - **Custom Headers :**
     ```
     WebSocket: true
     ```

#### ✅ Configurer certificat SSL

1. Aller dans **Control Panel > Security > Certificate**
2. Utiliser un certificat existant ou créer un nouveau Let's Encrypt
3. Assigner le certificat à lmelp.ascot63.synology.me

#### ✅ Tester accès externe

```bash
# Test depuis Internet
curl -I https://lmelp.ascot63.synology.me

# Vérifier dans navigateur
open https://lmelp.ascot63.synology.me
```

## Phase 6 : Scripts batch en conteneur

### Tâches

#### ✅ Créer service Docker pour scripts batch

Optionnel : Ajouter dans `docker-compose.yml` un service pour les tâches planifiées :

```yaml
  batch-worker:
    image: ghcr.io/castorfou/lmelp:latest
    container_name: lmelp-batch
    restart: "no"  # Lancer manuellement ou via cron
    depends_on:
      - mongodb
    volumes:
      - lmelp-audios:/app/audios
      - lmelp-db-backup:/app/db
    environment:
      # Même config que app
      - DB_HOST=mongodb
      - LMELP_MODE=batch-update  # ou batch-transcribe, batch-authors
    networks:
      - lmelp-network
```

#### ✅ Créer tâches planifiées (cron sur NAS)

```bash
# SSH sur NAS
sudo crontab -e

# Ajouter :
# Mise à jour RSS quotidienne à 6h
0 6 * * * docker run --rm --network bridge \
  -e DB_HOST=mongo -e LMELP_MODE=batch-update \
  ghcr.io/castorfou/lmelp:latest

# Transcription hebdomadaire dimanche 2h
0 2 * * 0 docker run --rm --network bridge \
  -v lmelp-audios:/app/audios \
  -e DB_HOST=mongo -e LMELP_MODE=batch-transcribe \
  ghcr.io/castorfou/lmelp:latest
```

## Phase 7 : Documentation

### Tâches

#### ✅ Créer `docs/deployment/docker-setup.md`

Documentation complète de l'architecture Docker :
- Schéma d'architecture
- Prérequis système
- Ressources requises
- Réseau Docker

#### ✅ Créer `docs/deployment/local-deployment.md`

Guide de déploiement sur PC local :
- Installation Docker Desktop
- Configuration .env
- Commandes docker-compose
- Accès à l'application

#### ✅ Créer `docs/deployment/nas-deployment.md`

Guide de déploiement sur NAS Synology :
- Configuration Portainer
- Variables d'environnement
- Webhook configuration
- Reverse proxy Application Portal
- Troubleshooting spécifique NAS

#### ✅ Créer `docs/deployment/update-guide.md`

Guide de mise à jour :
- Mise à jour automatique (webhook)
- Mise à jour manuelle locale
- Mise à jour vers version spécifique
- Rollback vers version précédente
- Gestion des migrations de données

#### ✅ Créer `docs/deployment/troubleshooting.md`

Guide de dépannage :
- Problèmes courants (connexion MongoDB, APIs, transcription)
- Consultation des logs
- Vérification santé des conteneurs
- Tests de connectivité
- Nettoyage et maintenance

#### ✅ Mettre à jour `README.md`

Ajouter section complète sur le déploiement Docker :

```markdown
## Déploiement Docker

### 🐳 Déploiement local (PC)

voir [Guide de déploiement local](docs/deployment/local-deployment.md)

```bash
cd docker/
cp .env.template .env
# Éditer .env avec vos clés API
docker compose up -d
```

Accéder à http://localhost:8501

### 🖥️ Déploiement NAS Synology

voir [Guide de déploiement NAS](docs/deployment/nas-deployment.md)

Déploiement automatique via Portainer + GitHub Actions webhook.

### 📦 Images Docker

Images disponibles sur GitHub Container Registry :
- `ghcr.io/castorfou/lmelp:latest` - Dernière version stable
- `ghcr.io/castorfou/lmelp:v1.0.0` - Versions spécifiques

### 🔄 Mise à jour

voir [Guide de mise à jour](docs/deployment/update-guide.md)
```

#### ✅ Créer `docs/deployment/batch-processing.md`

Documentation des scripts batch en conteneur :
- Utilisation du mode batch
- Scripts disponibles
- Configuration cron
- Logs et monitoring

## Phase 8 : Tests et validation

### Tâches

#### ✅ Test build local des images

```bash
# Build
docker build -f docker/Dockerfile -t lmelp:test .

# Vérifier taille
docker images lmelp:test

# Vérifier layers
docker history lmelp:test

# Test démarrage
docker run --rm -p 8501:8501 \
  -e DB_HOST=localhost \
  -e GEMINI_API_KEY=test \
  lmelp:test
```

**Critères de succès :**
- Taille image < 3 GB (avec transformers + torch)
- Démarrage < 30 secondes
- Healthcheck OK après démarrage

#### ✅ Test docker-compose local complet

```bash
# Démarrer tous les services
docker compose -f docker/docker-compose.yml up -d

# Vérifier statut
docker compose -f docker/docker-compose.yml ps

# Vérifier logs
docker compose -f docker/docker-compose.yml logs app

# Vérifier MongoDB
docker exec -it lmelp-mongodb mongosh --eval "db.adminCommand('ping')"

# Test interface web
curl http://localhost:8501

# Test API MongoDB depuis app
docker exec -it lmelp-app python -c "
from nbs.mongo import get_mongodb_client
client = get_mongodb_client()
print(client.server_info())
"

# Arrêter
docker compose -f docker/docker-compose.yml down
```

**Critères de succès :**
- Tous les services démarrent sans erreur
- Application Streamlit accessible
- Connexion MongoDB fonctionnelle
- Volumes persistants créés

#### ✅ Test déploiement NAS Portainer

1. Déployer stack via Portainer
2. Vérifier logs dans Portainer UI
3. Vérifier connexion au MongoDB existant :
   ```bash
   docker exec -it lmelp-app python -c "
   from nbs.mongo import get_mongodb_client
   client = get_mongodb_client()
   print(client.list_database_names())
   "
   ```
4. Tester interface web via reverse proxy : https://lmelp.ascot63.synology.me

**Critères de succès :**
- Stack déployée sans erreur
- Connexion à MongoDB externe OK
- Interface accessible via domaine Synology
- HTTPS fonctionnel avec certificat valide

#### ✅ Test webhook auto-deploy

```bash
# Push sur main
git push origin main

# Vérifier GitHub Actions
# https://github.com/castorfou/lmelp/actions

# Vérifier logs Portainer pour auto-deploy
# Vérifier que nouvelle version est déployée
docker exec -it lmelp-app python -c "import sys; print(sys.version)"
```

**Critères de succès :**
- Build GitHub Actions réussie
- Image publiée sur ghcr.io
- Webhook déclenché automatiquement
- Stack Portainer mise à jour
- Application redémarrée avec nouvelle version

#### ✅ Test rollback

```bash
# Méthode 1 : Via Portainer
# 1. Éditer stack
# 2. Changer image vers version précédente (ex: v1.0.0)
# 3. Update stack

# Méthode 2 : En local
docker compose -f docker/docker-compose.yml down
docker pull ghcr.io/castorfou/lmelp:v1.0.0
# Éditer docker-compose.yml : image: ghcr.io/castorfou/lmelp:v1.0.0
docker compose -f docker/docker-compose.yml up -d

# Vérifier que l'application fonctionne avec ancienne version
```

**Critères de succès :**
- Rollback vers version précédente sans perte de données
- Application fonctionnelle
- Volumes préservés

#### ✅ Test scripts batch

```bash
# Test mise à jour RSS
docker run --rm --network lmelp-network \
  -e DB_HOST=mongodb \
  -e LMELP_MODE=batch-update \
  -e RSS_LMELP_URL=https://radiofrance-podcast.net/podcast09/rss_14007.xml \
  ghcr.io/castorfou/lmelp:latest

# Vérifier dans MongoDB que les épisodes sont ajoutés
docker exec -it lmelp-mongodb mongosh masque_et_la_plume \
  --eval "db.episodes.countDocuments()"

# Test transcription (avec épisode de test)
docker run --rm --network lmelp-network \
  -v lmelp-audios:/app/audios \
  -e DB_HOST=mongodb \
  -e LMELP_MODE=batch-transcribe \
  -e GEMINI_API_KEY=$GEMINI_API_KEY \
  ghcr.io/castorfou/lmelp:latest
```

**Critères de succès :**
- Scripts s'exécutent sans erreur
- Données ajoutées/modifiées dans MongoDB
- Fichiers audio persistés dans volume
- Logs clairs et informatifs

#### ✅ Test performance et ressources

```bash
# Surveiller ressources pendant utilisation
docker stats lmelp-app

# Test charge : ouvrir plusieurs pages Streamlit
# Vérifier utilisation CPU/RAM

# Test transcription : surveiller pendant transcription d'un épisode
docker stats lmelp-app
```

**Critères de succès :**
- RAM < 4 GB pendant utilisation normale
- RAM < 8 GB pendant transcription Whisper
- CPU < 100% en moyenne
- Pas de memory leak après plusieurs heures

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

**Justification :**
- Whisper + Transformers = modèles lourds en RAM
- Transcription = intensif CPU
- 4 GB permet de charger les modèles ML confortablement

### Healthchecks

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s  # Temps de chargement des modèles ML
```

### Taille estimée des images

- **Image finale :** ~2.5-3 GB (avec torch, transformers)
- **Volumes :**
  - `lmelp-audios` : 50-100 GB (audio MP3 des épisodes)
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
- ⚠️ **Réseau Docker** :
  - NAS : Connecter au réseau du conteneur mongo existant
  - PC : Réseau dédié `lmelp-network`
- ⚠️ **Volumes** : Persister les fichiers audio (plusieurs Go)
- ⚠️ **Secrets** : Toutes les API keys via variables d'environnement (Portainer sur NAS, .env sur PC)
- ⚠️ **Modèles ML** : Téléchargés au premier lancement (Whisper, Transformers) → temps de démarrage initial long
- ⚠️ **Transcription** : Opération **TRÈS** coûteuse en ressources (RAM + CPU/GPU)
- ⚠️ **Webhook** : Actif uniquement sur NAS pour auto-deploy, PC fait pull manuel

## Critères de succès

✅ Image Docker buildée et publiée sur ghcr.io
✅ Application déployée et accessible sur :
  - PC local : http://localhost:8501
  - NAS : https://lmelp.ascot63.synology.me
✅ Connexion MongoDB fonctionnelle (externe sur NAS, locale sur PC)
✅ Volumes persistants pour audios et backups
✅ Webhook GitHub → Portainer fonctionnel (déploiement automatique NAS)
✅ Scripts batch exécutables en conteneur
✅ Possibilité de rollback vers version précédente
✅ Documentation complète du déploiement et de la maintenance
✅ Tests de performance passants (RAM < 4 GB utilisation normale)
✅ Healthchecks fonctionnels

## Références

- [Configuration MongoDB existante](../mongo.md)
- [Documentation Portainer](https://docs.portainer.io/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Synology Application Portal](https://kb.synology.com/en-global/DSM/help/DSM/AdminCenter/application_appportal_config)
- [Docker Compose File Reference](https://docs.docker.com/compose/compose-file/)
- [Streamlit Docker Deployment](https://docs.streamlit.io/knowledge-base/tutorials/deploy/docker)

## Prochaines étapes

1. Commencer par Phase 1 : Création des Dockerfiles
2. Tester build local et fonctionnement de base
3. Setup CI/CD GitHub Actions
4. Déploiement test sur PC local
5. Déploiement production sur NAS avec webhook
6. Documentation et validation finale
