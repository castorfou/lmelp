# Instructions de Refactoring Docker

Tu dois refactoriser la structure Docker de ce repository pour séparer clairement les fichiers de **build** (utilisés par CI/CD) des fichiers de **deployment** (utilisés pour déployer).

## Objectif

Réorganiser les répertoires `/docker` et `/deployment` selon cette nouvelle structure :

```
docker/
├── build/              # Fichiers utilisés par CI/CD pour construire l'image
│   ├── Dockerfile
│   └── entrypoint.sh
│
└── deployment/         # Fichiers utilisés pour déployer l'image (PC local/NAS)
    ├── docker-compose.yml
    ├── .env.template
    └── README.md
```

## Étapes à suivre

### 1. Créer la nouvelle structure

```bash
mkdir -p docker/build docker/deployment
```

### 2. Déplacer les fichiers de build

```bash
# Déplacer Dockerfile et entrypoint.sh vers docker/build/
mv docker/Dockerfile docker/build/
mv docker/entrypoint.sh docker/build/
```

### 3. Déplacer les fichiers de deployment

```bash
# Déplacer les fichiers du répertoire /deployment vers docker/deployment/
mv deployment/docker-compose.yml docker/deployment/
mv deployment/.env.template docker/deployment/
mv deployment/README.md docker/deployment/
```

### 4. Mettre à jour le Dockerfile

Dans `docker/build/Dockerfile`, modifier la ligne qui copie `entrypoint.sh` :

**Chercher :**
```dockerfile
COPY docker/entrypoint.sh /app/entrypoint.sh
```

**Remplacer par :**
```dockerfile
COPY docker/build/entrypoint.sh /app/entrypoint.sh
```

### 5. Mettre à jour le workflow GitHub Actions

Dans `.github/workflows/docker-publish.yml`, modifier le chemin du Dockerfile :

**Chercher :**
```yaml
file: docker/Dockerfile
```

**Remplacer par :**
```yaml
file: docker/build/Dockerfile
```

**Et aussi modifier la section de mise à jour (si elle existe) :**

**Chercher :**
```bash
cd docker/
./scripts/update.sh
```

**Remplacer par :**
```bash
cd docker/deployment/
docker compose pull && docker compose up -d
```

### 6. Mettre à jour le README principal

Dans `README.md`, chercher toutes les références à `deployment/` ou `docker/scripts/` et les mettre à jour :

- `deployment/docker-compose.yml` → `docker/deployment/docker-compose.yml`
- `deployment/.env.template` → `docker/deployment/.env.template`
- `./docker/scripts/start.sh` → `docker compose up -d` (dans docker/deployment/)
- `./docker/scripts/stop.sh` → `docker compose down`
- `./docker/scripts/update.sh` → `docker compose pull && docker compose up -d`

### 7. Mettre à jour docker/deployment/README.md

Dans `docker/deployment/README.md`, chercher et remplacer :

- `deployment/docker-compose.yml` → `docker/deployment/docker-compose.yml`
- `deployment/.env.template` → `docker/deployment/.env.template`
- Supprimer les références à des fichiers qui n'existent plus (DEPLOYMENT.md, IMAGES.md, etc.)

### 8. Créer un nouveau docker/README.md

Créer `docker/README.md` avec ce contenu :

```markdown
# Docker - back-office-lmelp

Ce répertoire contient les fichiers Docker pour **back-office-lmelp**.

## Structure

```
docker/
├── build/              # Utilisé par CI/CD pour construire l'image Docker
│   ├── Dockerfile      # Multi-stage build
│   └── entrypoint.sh   # Script d'entrée du conteneur
│
└── deployment/         # Utilisé pour déployer l'image (PC local ou NAS)
    ├── docker-compose.yml  # Configuration Docker Compose
    ├── .env.template       # Template de variables d'environnement
    └── README.md           # Guide de déploiement complet
```

## 🏗️ Build (CI/CD)

Le répertoire `build/` contient les fichiers utilisés par GitHub Actions pour construire l'image Docker.

**Fichier utilisé par :** `.github/workflows/docker-publish.yml`

**Image publiée :** `ghcr.io/castorfou/back-office-lmelp:latest`

## 🚀 Deployment (Utilisation)

Le répertoire `deployment/` contient les fichiers pour déployer back-office-lmelp sur votre environnement.

**👉 Pour déployer, consultez :** [deployment/README.md](deployment/README.md)

### Déploiement rapide

```bash
cd docker/deployment/
cp .env.template .env
# Éditer .env avec vos clés API et configurer DB_HOST
docker compose up -d
```

Accéder à : **http://localhost:8501**

## 📚 Documentation

- [Guide de déploiement complet](deployment/README.md)
- [Configuration GitHub Actions](../../docs/deployment/github-actions-setup.md) (si existe)
- [Images Docker](https://github.com/castorfou/back-office-lmelp/pkgs/container/back-office-lmelp)
```

### 9. Supprimer les fichiers obsolètes

Supprimer tous les fichiers/répertoires inutiles dans `/docker` :

```bash
cd docker/
rm -f .env.template DEPLOYMENT.md IMAGES.md docker-compose.yml docker-compose.*.yml test-local.sh
rm -rf scripts/
```

Supprimer le répertoire `/deployment` à la racine (maintenant vide) :

```bash
rmdir deployment/
```

### 10. Mettre à jour la documentation (si elle existe)

Si le projet a des fichiers de documentation dans `docs/deployment/`, chercher et mettre à jour :

- `docker/Dockerfile` → `docker/build/Dockerfile`
- `docker/scripts/` → commandes docker compose directes
- `deployment/` → `docker/deployment/`

### 11. Vérifier et committer

```bash
# Vérifier la structure
tree docker/ -L 2  # ou ls -R docker/

# Ajouter tous les changements
git add -A

# Vérifier ce qui sera commité
git status

# Commiter
git commit -m "Refactor Docker directory structure

Reorganize Docker files into logical subdirectories:
- docker/build/ - Files used by CI/CD to build the image
- docker/deployment/ - Files used to deploy the image (PC/NAS)

Changes:
- Move Dockerfile and entrypoint.sh to docker/build/
- Move deployment files from /deployment to docker/deployment/
- Update CI/CD workflow to use docker/build/Dockerfile
- Remove unused files (old compose files, scripts, docs)
- Update all documentation references
- Create minimal docker/README.md explaining new structure

This simplifies the project by:
1. Clearly separating build (CI/CD) from deployment (usage)
2. Removing duplicate and unused files
3. Centralizing all Docker-related files under docker/"

# Pusher
git push
```

## Notes importantes

- **Adapter les chemins** : Si le projet a une structure différente, adapte les chemins en conséquence
- **Vérifier les références** : Chercher dans tous les fichiers `.md`, `.yml`, `.yaml` les références à l'ancienne structure
- **Tester** : Si possible, vérifier que le build Docker fonctionne après les changements

## Résultat attendu

Après ce refactoring :
- ✅ Structure claire en 2 répertoires distincts
- ✅ Suppression de tous les fichiers redondants/obsolètes
- ✅ Documentation mise à jour
- ✅ CI/CD fonctionnelle avec les nouveaux chemins
- ✅ Tous les fichiers Docker centralisés sous `docker/`

## Exemple de résultat (référence: lmelp)

Ce refactoring a été fait sur le repo `lmelp` dans la branche `claude/review-docker-directory-015pEs87qgU1f55k7g6BXVRx`.

**Statistiques du refactoring lmelp :**
- 22 fichiers modifiés
- 1452 lignes supprimées
- 89 lignes ajoutées
- Structure simplifiée et clarifiée

**Fichiers supprimés dans lmelp :**
- `docker/.env.template`
- `docker/DEPLOYMENT.md`
- `docker/IMAGES.md`
- `docker/docker-compose.yml`
- `docker/docker-compose.nas.yml`
- `docker/docker-compose.watchtower.yml`
- `docker/test-local.sh`
- `docker/scripts/backup-db.sh`
- `docker/scripts/logs.sh`
- `docker/scripts/start.sh`
- `docker/scripts/stop.sh`
- `docker/scripts/test-build.sh`
- `docker/scripts/update.sh`
- Répertoire `/deployment` (déplacé vers `docker/deployment/`)
