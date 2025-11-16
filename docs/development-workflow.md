# Workflow de développement avec Docker et Portainer

Ce guide décrit le workflow recommandé pour développer lmelp tout en utilisant Portainer pour la production locale.

## Vue d'ensemble

Le workflow sépare clairement deux environnements :

- **Développement** : devcontainer (VS Code) sur une branche feature
- **Production locale** : Stack Portainer (auto-update) sur la branche main

Cette séparation évite les conflits de ports et permet une mise à jour automatique de la version "production" locale.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        MongoDB (hôte)                        │
│                    localhost:27017                           │
│              masque_et_la_plume database                     │
└─────────────┬─────────────────────────────┬─────────────────┘
              │                             │
    ┌─────────▼─────────┐         ┌────────▼─────────┐
    │   DÉVELOPPEMENT   │         │   PRODUCTION      │
    │                   │         │     LOCALE        │
    │  Devcontainer     │         │                   │
    │  (branche feature)│         │  Stack Portainer  │
    │                   │         │  (branche main)   │
    │  Port 8501        │         │  Port 8501        │
    │  DB: localhost    │         │  DB: 172.17.0.1   │
    └───────────────────┘         └───────────────────┘
         Actif pendant              Actif le reste
         le développement           du temps
```

## Workflow étape par étape

### 1. Démarrer un nouveau développement

**Sur une nouvelle branche feature :**

```bash
# Créer la branche feature
git checkout -b feature/ma-nouvelle-fonctionnalite

# Dans Portainer Web UI : Arrêter la stack lmelp
# Stacks → lmelp → Stop this stack
```

**Pourquoi arrêter Portainer ?**
- Libère le port 8501 pour Streamlit en dev
- Évite les accès concurrents à MongoDB (bien que MongoDB les supporte)
- Environnement propre pour le développement

### 2. Développer dans devcontainer

```bash
# Ouvrir VS Code dans le repo
code .

# VS Code détecte automatiquement le devcontainer
# Accept "Reopen in Container"
```

**Dans le devcontainer :**

- L'application se connecte à MongoDB sur l'hôte (localhost)
- Streamlit sur port 8501
- Hot-reload automatique des modifications Python
- Accès à tous les outils de dev (pytest, nbdev, etc.)

**Lancer l'interface :**

```bash
# Dans le terminal devcontainer
./ui/lmelp_ui.sh

# Ou via VS Code Tasks
# Ctrl+Shift+P → "Tasks: Run Task" → "run streamlit"
```

**Accès : http://localhost:8501**

### 3. Développer et tester

```bash
# Modifier le code (notebooks ou Python)
# Les changements sont automatiquement reflétés

# Exporter les notebooks si modifiés
nbdev_export

# Lancer les tests
pytest

# Formatter le code
black nbs/ ui/

# Commit réguliers
git add .
git commit -m "Add: nouvelle fonctionnalité"
git push origin feature/ma-nouvelle-fonctionnalite
```

### 4. Merger dans main

**Via Pull Request (recommandé) :**

1. Créer une PR sur GitHub
2. Review du code
3. Merger dans main

**Ou directement (si seul développeur) :**

```bash
git checkout main
git pull origin main
git merge feature/ma-nouvelle-fonctionnalite
git push origin main
```

### 5. Mise à jour automatique de la production locale

**Le workflow CI/CD se déclenche automatiquement :**

```
Push sur main
     ↓
GitHub Actions build Docker image
     ↓
Image publiée sur ghcr.io/castorfou/lmelp:latest
     ↓
Portainer auto-update détecte la nouvelle image
     ↓
Pull et redéploiement automatique
     ↓
Production locale à jour ! ✅
```

**Durée totale : ~20-30 minutes**
- Build Docker : ~19 minutes (GitHub Actions)
- Détection Portainer : 0-6 heures (selon config Watchtower)
- Pull et redéploiement : ~2 minutes

**Redémarrer la stack Portainer :**

```bash
# Dans Portainer Web UI
# Stacks → lmelp → Start this stack

# Ou forcer l'update immédiatement
# Stacks → lmelp → Pull and redeploy
```

**Accès production locale : http://localhost:8501**

### 6. Nettoyer la branche feature

```bash
# Supprimer la branche locale
git branch -d feature/ma-nouvelle-fonctionnalite

# Supprimer la branche distante
git push origin --delete feature/ma-nouvelle-fonctionnalite
```

## Avantages de ce workflow

### Séparation dev/prod claire

- **Dev** : Expérimentation libre, breakpoints, debug
- **Prod locale** : Version stable, testée, documentée

### Pas de conflits de ressources

- Port 8501 utilisé par un seul service à la fois
- MongoDB accessible des deux environnements (séquentiellement)

### Auto-update zéro intervention

- Push sur main → Image buildée → Portainer update
- Aucune commande manuelle à lancer
- Reproductible sur NAS Synology

### Données partagées

- Même base MongoDB pour dev et prod locale
- Pas besoin de restaurer des backups entre les deux
- Continuité des données de test

## Configuration Portainer auto-update

### Via Watchtower intégré

Si Portainer a Watchtower configuré globalement, aucune config nécessaire.

**Vérifier la configuration :**

```bash
# Voir si Watchtower tourne
docker ps | grep watchtower

# Voir les logs Watchtower
docker logs -f <watchtower-container-id>
```

### Via webhook Portainer

**Pour des updates instantanées (optionnel) :**

1. Dans Portainer : **Stacks** → **lmelp** → **Webhooks** → **Create webhook**
2. Copier l'URL du webhook
3. Dans GitHub : **Settings** → **Secrets** → **Actions** → **New secret**
   - Name: `PORTAINER_WEBHOOK_URL`
   - Value: URL copiée
4. Le workflow GitHub Actions triggera automatiquement le webhook

## Troubleshooting

### Port 8501 déjà utilisé

**Symptôme :** Impossible de lancer Streamlit en dev

**Cause :** La stack Portainer est toujours active

**Solution :**
```bash
# Vérifier quel processus utilise le port
sudo lsof -i :8501

# Arrêter la stack Portainer
# Via Web UI : Stacks → lmelp → Stop
```

### MongoDB connection refused en dev

**Symptôme :** `pymongo.errors.ServerSelectionTimeoutError`

**Cause :** MongoDB non démarré sur l'hôte

**Solution :**
```bash
# Vérifier MongoDB
sudo systemctl status mongod

# Démarrer MongoDB
sudo systemctl start mongod
```

### Portainer n'auto-update pas

**Symptôme :** Nouvelle version pushée mais Portainer reste sur l'ancienne

**Causes possibles :**

1. **Watchtower non configuré** : Configurer Watchtower ou utiliser webhook
2. **Délai de polling** : Watchtower vérifie toutes les 6h par défaut
3. **Image tag incorrect** : Vérifier que le compose utilise `:latest`

**Solutions :**
```bash
# Forcer l'update manuellement
# Portainer → Stacks → lmelp → Pull and redeploy

# Ou vérifier les logs Watchtower
docker logs watchtower | grep lmelp
```

### Image Docker pas à jour après le build

**Symptôme :** GitHub Actions build OK mais image pas mise à jour

**Cause :** GitHub Actions en cours ou échoué

**Solution :**
```bash
# Vérifier le statut du build
# https://github.com/castorfou/lmelp/actions/workflows/docker-publish.yml

# Attendre la fin du build (~19 minutes)
# Vérifier l'image publiée
# https://github.com/castorfou/lmelp/pkgs/container/lmelp
```

## Cas d'usage avancés

### Développer sur plusieurs branches en parallèle

**Problème :** Besoin de tester deux features simultanément

**Solution :** Utiliser différents ports

```bash
# Feature 1 : port 8501
streamlit run ui/lmelp.py --server.port 8501

# Feature 2 : port 8502 (autre terminal)
streamlit run ui/lmelp.py --server.port 8502
```

### Tester l'image Docker localement avant le merge

```bash
# Builder l'image localement
cd /path/to/lmelp
docker build -f docker/Dockerfile -t lmelp:test .

# Arrêter Portainer
# Dans Portainer Web UI : Stop stack lmelp

# Lancer l'image de test
docker run --rm -p 8501:8501 \
  -e DB_HOST=172.17.0.1 \
  -e DB_NAME=masque_et_la_plume \
  --env-file .env \
  lmelp:test

# Accès : http://localhost:8501
```

### Reproduire le workflow sur NAS Synology

**Identique au PC, avec ces différences :**

```bash
# DB_HOST différent dans .env Portainer
DB_HOST=mongo  # Nom du conteneur MongoDB sur le NAS

# Pas de devcontainer sur le NAS (développement sur PC uniquement)

# Même auto-update via Portainer
```

## Ressources

- [Guide Docker complet](../docker/README.md)
- [Déploiement Portainer](../deployment/README.md)
- [CI/CD GitHub Actions](deployment/github-actions-setup.md)
- [CLAUDE.md - Vue d'ensemble projet](../CLAUDE.md)

## Résumé du cycle complet

```
1. Stop Portainer
2. Dev dans devcontainer (branche feature)
3. Test, commit, push
4. Merge vers main (PR ou direct)
5. CI/CD build image (auto)
6. Portainer pull image (auto)
7. Start Portainer → Prod locale à jour ✅
8. Répéter pour la prochaine feature
```

**Durée du cycle :** 20-30 minutes (principalement build Docker)

**Intervention manuelle :** Stop/Start Portainer uniquement
