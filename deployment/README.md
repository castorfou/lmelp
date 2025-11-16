# 🚀 Déploiement lmelp - PC Local avec Portainer

Ce répertoire contient tout le nécessaire pour déployer **lmelp** sur votre PC local via Portainer.

## 📋 Prérequis

- Docker et Docker Compose installés
- Portainer installé et accessible (http://localhost:9000 ou https://localhost:9443)
- 4 GB RAM minimum (8 GB recommandé)
- 50-100 GB espace disque pour les audios

## 🔧 Installation

### 1. Copier ce répertoire sur votre PC

```bash
# Créer le répertoire de déploiement
mkdir -p ~/bin/lmelp/docker
cd ~/bin/lmelp/docker

# Copier les fichiers depuis le repo Git (y compris les fichiers cachés)
cp -r /path/to/lmelp/deployment/. .
```

### 2. Configurer les variables d'environnement

```bash
# Copier le template
cp .env.template .env

# Sécuriser le fichier (lecture/écriture uniquement pour le propriétaire)
chmod 600 .env

# Éditer .env avec vos clés API
nano .env  # ou vim, code, etc.
```

**Variables requises minimum :**
```env
# Azure OpenAI (pour les résumés IA)
AZURE_API_KEY=votre_clé_azure
AZURE_ENDPOINT=https://votre-resource.openai.azure.com/
AZURE_DEPLOYMENT_NAME=gpt-4o
AZURE_API_VERSION=2024-05-01-preview
```

Les autres variables (Google Search, etc.) sont optionnelles.

### 3. Déployer dans Portainer

#### Option A: Via l'interface Web Portainer (Recommandé)

1. **Ouvrir Portainer** : http://localhost:9000
2. **Stacks** → **Add stack**
3. **Name** : `lmelp`
4. **Build method** : Upload
   - Upload `docker-compose.yml`
5. **Environment variables** :
   - Cocher "Load variables from .env file"
   - Upload `.env`
6. **Deploy the stack**

⚠️ **Cette méthode est la plus simple** et ne nécessite pas de configurer l'authentification GitHub.

#### Option B: Via Git Repository (nécessite authentification GitHub)

⚠️ **Attention:** Cette méthode nécessite un Personal Access Token (PAT) GitHub.

1. **Créer un PAT GitHub** (si pas déjà fait):
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token (classic)
   - Cocher: `repo` (Full control of private repositories)
   - Copier le token généré

2. **Dans Portainer**:
   - **Stacks** → **Add stack**
   - **Name** : `lmelp`
   - **Build method** : Repository
   - **Authentication**: On
   - **Username**: votre nom d'utilisateur GitHub
   - **Personal Access Token**: coller votre PAT
   - **Repository URL**: `https://github.com/castorfou/lmelp`
   - **Repository reference**: `refs/heads/main`
   - **Compose path**: `deployment/docker-compose.yml`

3. **Environment variables**:
   - **Manuellement** copier le contenu de votre `.env` local dans les variables d'environnement

4. **Deploy the stack**

#### Option C: Via CLI Docker Compose

```bash
cd ~/bin/lmelp/docker
docker compose up -d
```

## 🌐 Accès à l'application

Une fois déployé, l'application est accessible sur :

**http://localhost:8501**

## 📊 Monitoring dans Portainer

### Vérifier l'état de la stack

1. **Portainer** → **Stacks** → `lmelp`
2. Vérifier que les 2 conteneurs sont "running" :
   - `lmelp-mongodb` (base de données)
   - `lmelp-app` (application Streamlit)

### Voir les logs

1. **Containers** → `lmelp-app` → **Logs**
2. Ou via CLI :
   ```bash
   docker logs -f lmelp-app
   ```

### Vérifier la santé

Les healthchecks sont configurés :
- MongoDB : vérifie toutes les 10s
- App : vérifie toutes les 30s

État visible dans **Containers** (icône de cœur).

## 🔄 Mises à jour

### Manuel (via Portainer)

1. **Stacks** → `lmelp` → **Pull and redeploy**
2. Portainer va :
   - Pull la dernière image `ghcr.io/castorfou/lmelp:latest`
   - Redémarrer les conteneurs

### Automatique (avec Watchtower)

Ajoutez Watchtower à votre stack :

```yaml
# Ajouter dans docker-compose.yml
services:
  watchtower:
    image: containrrr/watchtower:latest
    container_name: lmelp-watchtower
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WATCHTOWER_POLL_INTERVAL=21600  # 6 heures
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_INCLUDE_STOPPED=true
```

### Via Webhook Portainer

1. **Stacks** → `lmelp` → **Webhooks**
2. **Create a webhook**
3. Copier l'URL du webhook
4. Configurer dans GitHub Actions (voir documentation principale)

## 📦 Volumes Persistants

La stack crée 4 volumes Docker :

| Volume | Description | Taille estimée |
|--------|-------------|----------------|
| `lmelp-mongodb-data` | Base de données MongoDB | ~500 MB |
| `lmelp-audios` | Fichiers audio téléchargés | 50-100 GB |
| `lmelp-db-backup` | Sauvegardes DB | ~100 MB |
| `lmelp-logs` | Logs applicatifs | ~10 MB |

### Voir les volumes

```bash
docker volume ls | grep lmelp
```

### Backup des données

```bash
# Backup MongoDB
docker exec lmelp-mongodb mongodump --out=/dump
docker cp lmelp-mongodb:/dump ./mongodb-backup-$(date +%Y%m%d)

# Backup des audios
docker run --rm -v lmelp-audios:/data -v $(pwd):/backup alpine tar czf /backup/audios-backup.tar.gz /data
```

## 🛠️ Commandes Utiles

```bash
# Voir l'état de la stack
docker compose ps

# Logs en temps réel
docker compose logs -f

# Redémarrer la stack
docker compose restart

# Arrêter la stack
docker compose down

# Arrêter ET supprimer les volumes (⚠️ perte de données)
docker compose down -v

# Mettre à jour vers la dernière image
docker compose pull
docker compose up -d
```

## 🔍 Troubleshooting

### L'application ne démarre pas

```bash
# Vérifier les logs
docker logs lmelp-app

# Vérifier MongoDB
docker logs lmelp-mongodb

# Redémarrer
docker compose restart
```

### Erreur "No space left on device"

```bash
# Nettoyer les anciennes images
docker system prune -a

# Voir l'utilisation
docker system df
```

### Les résumés IA ne fonctionnent pas

Vérifier que les clés API sont bien configurées :

```bash
# Voir les variables d'environnement
docker exec lmelp-app env | grep AZURE
```

Si vide, vérifier votre fichier `.env`.

### Port 8501 déjà utilisé

Modifier dans `docker-compose.yml` :

```yaml
ports:
  - "8502:8501"  # Utiliser le port 8502 à la place
```

## 📚 Documentation Complète

- [Documentation principale](https://castorfou.github.io/lmelp/)
- [Guide Docker](https://github.com/castorfou/lmelp/tree/main/docker)
- [Images Docker](https://github.com/castorfou/lmelp/pkgs/container/lmelp)

## 🆘 Support

En cas de problème :
1. Consulter les logs : `docker logs lmelp-app`
2. Vérifier la [documentation](https://github.com/castorfou/lmelp/tree/main/docker)
3. Créer une [GitHub Issue](https://github.com/castorfou/lmelp/issues)
