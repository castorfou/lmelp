# 🚀 Déploiement lmelp - Portainer Stack

Ce répertoire contient la configuration pour déployer **lmelp** via Portainer en utilisant votre **MongoDB existant**.

## 📋 Prérequis

- Docker et Docker Compose installés
- Portainer installé et accessible (http://localhost:9000 ou https://localhost:9443)
- **MongoDB déjà installé** (sur l'hôte ou dans un conteneur Docker)
- 4 GB RAM minimum (8 GB recommandé)
- 50-100 GB espace disque pour les audios

## 🔧 Configuration

### 1. Créer votre fichier .env local

```bash
# Créer un répertoire pour votre config
mkdir -p ~/bin/lmelp/docker
cd ~/bin/lmelp/docker

# Copier le template depuis le repo Git
cp /path/to/lmelp/docker/deployment/.env.template .env

# Sécuriser le fichier
chmod 600 .env

# Éditer avec vos clés API
nano .env
```

### 2. Configurer les variables obligatoires

Éditez `.env` et remplissez au minimum :

```env
# Azure OpenAI (requis pour les résumés IA)
AZURE_API_KEY=votre_clé_azure
AZURE_ENDPOINT=https://votre-resource.openai.azure.com/
AZURE_DEPLOYMENT_NAME=gpt-4o
AZURE_API_VERSION=2024-05-01-preview

# MongoDB - IMPORTANT: Configurer selon votre environnement
# Pour PC avec MongoDB sur l'hôte (localhost) :
DB_HOST=172.17.0.1              # Linux
# DB_HOST=host.docker.internal  # Mac/Windows

# Pour NAS avec MongoDB dans un autre conteneur Docker :
# DB_HOST=mongo  # Nom du conteneur MongoDB

# Propriétaire des fichiers sur les volumes (audios, db, logs) - évite des
# fichiers root:root sur l'hôte. Trouvez vos UID/GID avec `id -u` / `id -g`.
PUID=1000  # ← Remplacer par votre UID (ex: 1027 sur NAS)
PGID=1000  # ← Remplacer par votre GID
```

**Vérifier que MongoDB est accessible :**

```bash
# Test de connexion
mongosh --host localhost --port 27017 --eval "db.adminCommand('ping')"
```

## 🚀 Déploiement dans Portainer

### Via Git Repository (Méthode recommandée)

Cette méthode permet les mises à jour automatiques via webhook ou pull manuel.

**1. Créer un Personal Access Token GitHub (une seule fois)**

- Aller sur : https://github.com/settings/tokens/new
- **Note** : "Portainer lmelp deployment"
- **Expiration** : No expiration (ou selon vos préférences)
- **Scopes** : Cocher `repo` (Full control of private repositories)
- **Generate token** et **copier le token**

**2. Déployer la stack dans Portainer**

- **Stacks** → **Add stack**
- **Name** : `lmelp`
- **Build method** : **Repository**
- **Authentication** : **On**
  - **Username** : votre_username_github
  - **Personal Access Token** : coller le token créé à l'étape 1
- **Repository URL** : `https://github.com/castorfou/lmelp`
- **Repository reference** : `refs/heads/main`
- **Compose path** : `docker/deployment/docker-compose.yml`
- **Environment variables** :
  - Cocher **"Load variables from .env file"**
  - Cliquer sur **"Upload"** et sélectionner votre fichier `.env`
  - ✅ Portainer va automatiquement charger toutes les variables
- **Deploy the stack**

**3. Vérifier le déploiement**

- Accéder à l'application : **http://localhost:8501**
- Vérifier les logs : `docker logs lmelp-app`
- Vérifier la connexion MongoDB :
  ```bash
  docker exec lmelp-app env | grep DB_HOST
  ```

## 🔄 Mises à jour

### Update manuel (via Portainer)

1. **Stacks** → `lmelp` → **Pull and redeploy**
2. Portainer va :
   - Pull la dernière image `ghcr.io/castorfou/lmelp:latest`
   - Redémarrer le conteneur

### Update automatique

Pour un update automatique, configurez Watchtower ou utilisez les webhooks Portainer (voir documentation Portainer).

## 📦 Volumes Persistants

La stack crée 3 volumes Docker :

| Volume | Description | Taille estimée |
|--------|-------------|----------------|
| `lmelp-audios` | Fichiers audio téléchargés | 50-100 GB |
| `lmelp-db-backup` | Sauvegardes DB | ~100 MB |
| `lmelp-logs` | Logs applicatifs | ~10 MB |

**Note** : MongoDB est géré en dehors de cette stack (sur votre hôte ou conteneur existant).

```bash
# Voir les volumes
docker volume ls | grep lmelp

# Backup des audios
docker run --rm -v lmelp-audios:/data -v $(pwd):/backup alpine tar czf /backup/audios-backup.tar.gz /data
```

## 🛠️ Commandes Utiles

```bash
# Logs en temps réel
docker logs -f lmelp-app

# Redémarrer
docker restart lmelp-app

# Shell dans le conteneur
docker exec -it lmelp-app bash

# Tester la connexion MongoDB
docker exec lmelp-app python -c "from pymongo import MongoClient; print(MongoClient('mongodb://172.17.0.1:27017').admin.command('ping'))"
```

## 🔍 Troubleshooting

### L'application ne démarre pas

```bash
# Vérifier les logs
docker logs lmelp-app

# Vérifier les variables d'environnement
docker exec lmelp-app env | grep DB

# Redémarrer
docker restart lmelp-app
```

### Erreur de connexion MongoDB

```
pymongo.errors.ServerSelectionTimeoutError: connection refused
```

**Causes possibles :**

1. **DB_HOST mal configuré** : Vérifiez la valeur dans votre `.env`
   - PC Linux : `DB_HOST=172.17.0.1`
   - PC Mac/Windows : `DB_HOST=host.docker.internal`
   - NAS : `DB_HOST=nom_conteneur_mongodb`

2. **MongoDB non accessible** : Vérifiez que MongoDB accepte les connexions externes
   ```bash
   # Sur l'hôte
   netstat -an | grep 27017

   # Tester la connexion
   mongosh --host localhost --port 27017
   ```

3. **Firewall** : Vérifiez que le port 27017 n'est pas bloqué

### Fichiers root:root sur les volumes (audios, db, logs)

Depuis [#105](https://github.com/castorfou/lmelp/issues/105), le conteneur
tourne sous un utilisateur non-root dont l'UID/GID sont configurables via
`PUID`/`PGID` dans votre `.env` (défaut : `1000`/`1000` si non défini).

**Si vous avez déjà des fichiers `root:root` sur vos volumes** (créés avant
ce fix, ou avec un `PUID`/`PGID` mal configuré) : un simple redémarrage du
conteneur suffit à corriger leur propriété — le conteneur ajuste
automatiquement les permissions vers `PUID`/`PGID` à chaque démarrage.

```bash
# 1. Vérifiez/ajustez PUID et PGID dans votre .env (id -u / id -g)
# 2. Redémarrez le conteneur
docker restart lmelp-app
# 3. Vérifiez côté hôte que les fichiers appartiennent bien à votre utilisateur
ls -la data/audios/
```

### Erreur "manifest unknown"

```
Error response from daemon: manifest unknown
```

**Solution** : Le package Docker n'est pas public. Contactez le mainteneur pour qu'il rende le package public sur GitHub Container Registry.

### Erreur "reference not found" lors du clone Git

```
Unable to clone git repository: failed to clone git repository: reference not found
```

**Cause** : La référence de branche est mal saisie dans Portainer.

**Solution** : Vérifiez le champ **Repository reference** dans Portainer :

- ✅ **Correct** : `refs/heads/main` (ou `refs/heads/nom-de-votre-branche`)
- ❌ **Incorrect** : `main` (sans préfixe), `ref/heads/main` (faute de frappe), etc.

**Exemples de références valides :**
- Branche main : `refs/heads/main`
- Branche de développement : `refs/heads/claude/review-code-01JpacPfALVvwqPorZfNeX6c`
- Tag : `refs/tags/v1.0.0`

**Astuce** : Copiez-collez la référence depuis la documentation pour éviter les erreurs de frappe.

### Port 8501 déjà utilisé

Modifier dans votre stack Portainer ou dans `docker-compose.yml` local :

```yaml
ports:
  - "8502:8501"  # Utiliser le port 8502 à la place
```

## 📚 Documentation

- [Documentation principale](https://castorfou.github.io/lmelp/)
- [Images Docker](https://github.com/castorfou/lmelp/pkgs/container/lmelp)
- [Configuration GitHub Actions](../../docs/deployment/github-actions-setup.md)

## 🆘 Support

En cas de problème :
1. Consulter les logs : `docker logs lmelp-app`
2. Vérifier la [documentation](https://github.com/castorfou/lmelp/tree/main/docker/deployment)
3. Créer une [GitHub Issue](https://github.com/castorfou/lmelp/issues)
