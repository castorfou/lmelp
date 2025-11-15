# 🚀 Guide de Déploiement lmelp

Guide complet pour déployer **lmelp** sur PC local ou NAS Synology avec auto-updates.

## 📋 Table des matières

- [Déploiement PC Local](#-déploiement-pc-local)
- [Auto-Update avec Watchtower](#-auto-update-avec-watchtower)
- [Auto-Update avec Portainer](#-auto-update-avec-portainer)
- [Mises à jour manuelles](#-mises-à-jour-manuelles)
- [Troubleshooting](#-troubleshooting)

---

## 🖥️ Déploiement PC Local

### Prérequis

- Docker et Docker Compose installés
- 4 GB RAM minimum (8 GB recommandé)
- 50-100 GB espace disque (pour audios)

### Installation

#### 1. Cloner le repository

```bash
git clone https://github.com/castorfou/lmelp.git
cd lmelp/docker
```

#### 2. Configurer les variables d'environnement

```bash
# Copier le template
cp ../.env.example .env

# Éditer .env avec vos clés API
nano .env
```

**Variables requises pour les résumés IA :**
```env
# Azure OpenAI (recommandé)
AZURE_API_KEY=your_azure_api_key
AZURE_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_DEPLOYMENT_NAME=gpt-4o
AZURE_API_VERSION=2024-05-01-preview
```

**Variables optionnelles :**
```env
# Google Search (pour vérification auteurs)
GOOGLE_CUSTOM_SEARCH_API_KEY=your_key
SEARCH_ENGINE_ID=your_cse_id

# Autres LLMs (alternatives à Azure)
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
```

#### 3. Lancer l'application

```bash
# Avec MongoDB inclus (déploiement standalone)
./scripts/start.sh
```

L'application est accessible sur **http://localhost:8501** 🎉

#### 4. Vérifier le déploiement

```bash
# Voir les logs
./scripts/logs.sh

# Vérifier l'état des conteneurs
docker compose ps
```

### Scripts disponibles

```bash
./scripts/start.sh      # Démarrer lmelp
./scripts/stop.sh       # Arrêter lmelp
./scripts/update.sh     # Mettre à jour vers la dernière version
./scripts/logs.sh       # Voir les logs
./scripts/backup-db.sh  # Sauvegarder MongoDB
```

---

## 🔄 Auto-Update avec Watchtower

**Watchtower** surveille vos conteneurs et les met à jour automatiquement quand une nouvelle image est disponible.

### Installation

```bash
cd docker/

# Lancer avec Watchtower
docker compose -f docker-compose.yml -f docker-compose.watchtower.yml up -d
```

### Configuration

Watchtower est configuré pour :
- ✅ Vérifier les mises à jour **toutes les 6 heures**
- ✅ Mettre à jour **uniquement** les conteneurs lmelp
- ✅ Nettoyer les anciennes images après mise à jour
- ✅ Redémarrer automatiquement les conteneurs mis à jour

### Personnalisation

Éditez `docker-compose.watchtower.yml` :

```yaml
environment:
  # Vérifier toutes les heures (3600 secondes)
  - WATCHTOWER_POLL_INTERVAL=3600

  # Notifications par email (optionnel)
  - WATCHTOWER_NOTIFICATION_URL=smtp://user:pass@smtp.gmail.com:587/?fromAddress=from@gmail.com&toAddresses=to@gmail.com
```

### Vérifier Watchtower

```bash
# Voir les logs de Watchtower
docker logs -f lmelp-watchtower

# Forcer une vérification immédiate
docker exec lmelp-watchtower /watchtower --run-once
```

### Désactiver Watchtower

```bash
# Revenir au mode normal (sans auto-update)
docker compose -f docker-compose.yml up -d
```

---

## 🐙 Auto-Update avec Portainer

**Portainer** offre une interface web pour gérer vos conteneurs et configurer des webhooks pour les mises à jour automatiques.

### Installation Portainer

```bash
docker volume create portainer_data

docker run -d \
  -p 9000:9000 \
  -p 9443:9443 \
  --name portainer \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest
```

Accédez à Portainer : **https://localhost:9443**

### Configuration du Webhook

1. **Dans Portainer Web UI :**
   - Allez dans **Stacks** → sélectionnez `lmelp`
   - Activez **Automatic updates**
   - Copiez l'**URL du Webhook**

2. **Dans GitHub :**
   - Allez dans **Settings** → **Secrets and variables** → **Actions**
   - Ajoutez un secret : `PORTAINER_WEBHOOK_URL` avec l'URL copiée

3. **Workflow GitHub Actions :**

   Le workflow `.github/workflows/docker-publish.yml` est déjà configuré pour appeler le webhook automatiquement après chaque build :

   ```yaml
   - name: Trigger Portainer Webhook (NAS deployment)
     if: success() && github.ref == 'refs/heads/main'
     run: |
       curl -X POST "${{ secrets.PORTAINER_WEBHOOK_URL }}"
   ```

### Flux de mise à jour automatique

```
┌─────────────┐      ┌──────────────┐      ┌────────────┐      ┌──────────┐
│ git push    │ ───> │ GitHub       │ ───> │ Portainer  │ ───> │ Conteneur│
│ sur main    │      │ Actions      │      │ Webhook    │      │ mis à    │
│             │      │ build & push │      │            │      │ jour     │
└─────────────┘      └──────────────┘      └────────────┘      └──────────┘
                           │
                           v
                     ghcr.io/castorfou/lmelp:latest
```

### Vérifier les mises à jour

Dans Portainer Web UI :
- **Containers** → `lmelp-app` → **Logs** pour voir les redémarrages
- **Events** pour voir l'historique des updates

---

## 🔧 Mises à jour manuelles

Si vous n'utilisez ni Watchtower ni Portainer :

```bash
cd docker/

# Méthode 1: Script automatique
./scripts/update.sh

# Méthode 2: Commandes manuelles
docker compose pull            # Télécharger la dernière image
docker compose up -d           # Redémarrer avec la nouvelle image
docker image prune -f          # Nettoyer les anciennes images
```

### Rollback vers une version précédente

```bash
# Voir les versions disponibles sur ghcr.io
# https://github.com/castorfou/lmelp/pkgs/container/lmelp

# Modifier docker-compose.yml
nano docker-compose.yml
# Changer: image: ghcr.io/castorfou/lmelp:latest
# En:      image: ghcr.io/castorfou/lmelp:v1.2.0

# Relancer
docker compose up -d
```

---

## 🔍 Troubleshooting

### L'application ne démarre pas

```bash
# Vérifier les logs
docker compose logs app

# Vérifier MongoDB
docker compose logs mongodb

# Redémarrer les conteneurs
docker compose restart
```

### Problèmes de connexion MongoDB

```bash
# Vérifier que MongoDB est healthy
docker compose ps

# Tester la connexion
docker exec lmelp-app mongosh mongodb://mongodb:27017/masque_et_la_plume --eval "db.stats()"
```

### Les mises à jour ne fonctionnent pas

**Watchtower :**
```bash
# Vérifier les logs
docker logs lmelp-watchtower

# S'assurer que le scope est correct
docker inspect lmelp-app | grep watchtower.scope
```

**Portainer :**
- Vérifier que le webhook est bien configuré dans GitHub Secrets
- Vérifier les logs du workflow GitHub Actions
- Tester le webhook manuellement : `curl -X POST "WEBHOOK_URL"`

### Espace disque insuffisant

```bash
# Nettoyer les anciennes images
docker image prune -a -f

# Nettoyer les volumes inutilisés
docker volume prune -f

# Voir l'utilisation
docker system df
```

### Problèmes de performance

```bash
# Vérifier l'utilisation des ressources
docker stats lmelp-app

# Augmenter les limites dans docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 8G
```

### Clés API non reconnues

```bash
# Vérifier que le fichier .env est bien chargé
docker compose config | grep AZURE_API_KEY

# Vérifier les variables dans le conteneur
docker exec lmelp-app env | grep AZURE
```

---

## 📚 Ressources

- [Documentation complète](https://castorfou.github.io/lmelp/)
- [GitHub Repository](https://github.com/castorfou/lmelp)
- [Images Docker](https://github.com/castorfou/lmelp/pkgs/container/lmelp)
- [Watchtower Documentation](https://containrrr.dev/watchtower/)
- [Portainer Documentation](https://docs.portainer.io/)

---

## 🆘 Support

En cas de problème :
1. Consultez la section [Troubleshooting](#-troubleshooting)
2. Vérifiez les [GitHub Issues](https://github.com/castorfou/lmelp/issues)
3. Créez une nouvelle issue si nécessaire
