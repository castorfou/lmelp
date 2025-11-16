# Docker - lmelp

Ce répertoire contient les fichiers Docker pour **lmelp** (Le Masque et la Plume).

## Structure

```
docker/
├── build/              # Utilisé par CI/CD pour construire l'image Docker
│   ├── Dockerfile      # Multi-stage build Python 3.11
│   └── entrypoint.sh   # Script d'entrée du conteneur
│
└── deployment/         # Utilisé pour déployer l'image (PC local ou NAS)
    ├── docker-compose.yml  # Configuration Docker Compose
    ├── .env.template       # Template de variables d'environnement
    └── README.md           # Guide de déploiement complet
```

## 🏗️ Build (CI/CD)

Le répertoire `build/` contient les fichiers utilisés par GitHub Actions pour construire l'image Docker :

- **Dockerfile** : Build multi-stage optimisé pour lmelp
- **entrypoint.sh** : Support de plusieurs modes (web, batch-update, batch-transcribe, batch-authors)

**Fichier utilisé par :** `.github/workflows/docker-publish.yml`

**Image publiée :** `ghcr.io/castorfou/lmelp:latest`

## 🚀 Deployment (Utilisation)

Le répertoire `deployment/` contient les fichiers pour déployer lmelp sur votre environnement :

- **docker-compose.yml** : Configuration pour PC local ou NAS (utilise MongoDB externe)
- **.env.template** : Variables d'environnement à configurer
- **README.md** : Guide complet de déploiement avec Portainer

**👉 Pour déployer lmelp, consultez :** [deployment/README.md](deployment/README.md)

## 📚 Documentation

- [Guide de déploiement complet](deployment/README.md)
- [Configuration GitHub Actions](../docs/deployment/github-actions-setup.md)
- [Documentation principale](https://castorfou.github.io/lmelp/)
- [Images Docker](https://github.com/castorfou/lmelp/pkgs/container/lmelp)

## 🔧 Workflow

### Build automatique (CI/CD)

Quand vous pushez sur `main` ou créez un tag :
1. GitHub Actions exécute `.github/workflows/docker-publish.yml`
2. Build l'image avec `docker/build/Dockerfile`
3. Publie sur `ghcr.io/castorfou/lmelp:latest`
4. (Optionnel) Trigger le webhook Portainer pour auto-deploy

### Déploiement local

```bash
cd docker/deployment/
cp .env.template .env
# Éditer .env avec vos clés API et configurer DB_HOST
docker compose up -d
```

Accéder à : **http://localhost:8501**

## ⚙️ Modes d'exécution

Le conteneur supporte plusieurs modes via `LMELP_MODE` :

| Mode | Description |
|------|-------------|
| `web` | Interface Streamlit (défaut) |
| `batch-update` | Mise à jour des épisodes depuis RSS |
| `batch-transcribe` | Transcription des épisodes (variable `EPISODE_ID` optionnelle) |
| `batch-authors` | Extraction des auteurs (variable `EPISODE_ID` optionnelle) |

Voir [deployment/README.md](deployment/README.md) pour plus de détails.
