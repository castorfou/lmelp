# 📦 Docker Images - Registry et Tags

Ce document décrit où trouver les images Docker de **lmelp** et comment les utiliser.

## 🔗 Registry GitHub Container Registry (ghcr.io)

**URL du package:** https://github.com/castorfou/lmelp/pkgs/container/lmelp

Toutes les images sont publiées sur GitHub Container Registry (ghcr.io), hébergé gratuitement par GitHub.

## 🏷️ Tags Disponibles

Les images sont taguées automatiquement selon la source du build :

### Images de production (branche `main`)

```bash
# Latest - pointe toujours vers la dernière version de main
ghcr.io/castorfou/lmelp:latest

# Branche main explicite
ghcr.io/castorfou/lmelp:main
```

### Images de test (branche `claude/review-code-01JpacPfALVvwqPorZfNeX6c`)

```bash
# Image de la branche de test
ghcr.io/castorfou/lmelp:claude-review-code-01JpacPfALVvwqPorZfNeX6c
```

### Images versionnées (tags Git)

Quand vous créez un tag Git `v1.2.3`, plusieurs tags Docker sont créés :

```bash
ghcr.io/castorfou/lmelp:v1.2.3    # Tag complet
ghcr.io/castorfou/lmelp:1.2.3     # Sans le 'v'
ghcr.io/castorfou/lmelp:1.2       # Version mineure
ghcr.io/castorfou/lmelp:1         # Version majeure
```

## 📥 Pull des Images

### Depuis GitHub Actions (publique)

Si le package est **public** :

```bash
docker pull ghcr.io/castorfou/lmelp:latest
```

### Depuis GitHub Actions (privé)

Si le package est **privé**, vous devez vous authentifier :

```bash
# 1. Créer un Personal Access Token (PAT)
# GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
# Permissions: read:packages

# 2. Se connecter à ghcr.io
echo "YOUR_GITHUB_TOKEN" | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin

# 3. Pull l'image
docker pull ghcr.io/castorfou/lmelp:latest
```

## 🚀 Utilisation

### Option 1: Docker Run direct

```bash
# Avec MongoDB local existant
docker run --rm -it \
  -p 8501:8501 \
  -e DB_HOST=172.17.0.1 \
  -e DB_NAME=masque_et_la_plume \
  --env-file .env \
  ghcr.io/castorfou/lmelp:latest
```

### Option 2: Docker Compose (production)

Fichier `docker-compose.yml` :

```yaml
services:
  app:
    image: ghcr.io/castorfou/lmelp:latest
    # ... reste de la config
```

```bash
cd docker/
docker compose pull
docker compose up -d
```

### Option 3: Docker Compose (test)

Pour tester une branche spécifique :

```yaml
services:
  app:
    image: ghcr.io/castorfou/lmelp:claude-review-code-01JpacPfALVvwqPorZfNeX6c
    # ... reste de la config
```

```bash
cd docker/
docker compose pull
docker compose up -d
```

### Option 4: Watchtower (auto-update)

Watchtower mettra à jour automatiquement vers la dernière version du tag spécifié :

```bash
# Avec latest (recommandé pour production)
docker compose -f docker-compose.yml -f docker-compose.watchtower.yml up -d
```

## 📊 Vérifier les Builds

### Suivi GitHub Actions

**Workflows en cours :** https://github.com/castorfou/lmelp/actions/workflows/docker-publish.yml

Chaque push sur `main` ou `claude/review-code-01JpacPfALVvwqPorZfNeX6c` déclenche automatiquement :
1. Build de l'image Docker
2. Push vers ghcr.io
3. Trigger du webhook Portainer (si configuré)

### Packages publiés

**Liste des images :** https://github.com/castorfou/lmelp/pkgs/container/lmelp

Vous y trouverez :
- Tous les tags disponibles
- Taille des images
- Date de publication
- Commandes pour pull

## 🔒 Visibilité du Package

Par défaut, les packages GitHub sont **privés**.

### Rendre le package public

1. Aller sur https://github.com/castorfou/lmelp/pkgs/container/lmelp
2. Cliquer sur **Package settings** (en bas à droite)
3. Section **Danger Zone** → **Change visibility**
4. Sélectionner **Public**
5. Taper le nom du repository pour confirmer

**Avantages du mode public :**
- Pas besoin d'authentification pour pull
- Plus simple pour les déploiements
- Accessible à tous

**Inconvénients :**
- Visible par tout le monde
- Peut contenir des informations sensibles si mal configuré

## 🔄 Workflow de Mise à Jour

```
┌─────────────┐
│ git push    │
│ sur main ou │
│ test branch │
└──────┬──────┘
       │
       v
┌─────────────────┐
│ GitHub Actions  │
│ - Build image   │
│ - Tag & Push    │
└──────┬──────────┘
       │
       v
┌─────────────────┐
│ ghcr.io         │
│ Package updated │
└──────┬──────────┘
       │
       ├──> Watchtower (auto-pull toutes les 6h)
       │
       └──> Portainer Webhook (update immédiat si configuré)
```

## 📝 Notes

- **Taille d'image :** ~2.5-3 GB (inclut les modèles ML)
- **Temps de build :** ~5-10 minutes sur GitHub Actions
- **Retention :** GitHub garde toutes les versions indéfiniment
- **Nettoyage :** Utilisez `docker image prune` localement pour supprimer les anciennes versions

## 🆘 Troubleshooting

### "Error response from daemon: pull access denied"

➡️ Le package est privé. Vous devez vous authentifier (voir section [Pull des Images](#-pull-des-images))

### "image not found"

➡️ Vérifiez que le build GitHub Actions s'est terminé avec succès : https://github.com/castorfou/lmelp/actions

### Watchtower ne détecte pas les mises à jour

➡️ Vérifiez les logs de Watchtower :
```bash
docker logs -f lmelp-watchtower
```

Si le package est privé, Watchtower a besoin d'accès au registry. Voir [documentation Watchtower](https://containrrr.dev/watchtower/private-registries/).
