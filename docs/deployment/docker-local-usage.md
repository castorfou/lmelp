# Utilisation Docker en local

Ce guide explique comment utiliser lmelp avec Docker sur votre machine locale (PC Linux/Mac/Windows).

## 📋 Prérequis

- Docker installé et fonctionnel
- MongoDB installé et accessible sur votre machine hôte
- Git configuré pour accéder au dépôt

## 🔧 Configuration MongoDB

### Configuration du réseau

Pour que le conteneur Docker puisse se connecter à MongoDB sur votre machine hôte, MongoDB doit être configuré pour accepter les connexions depuis le réseau Docker.

**1. Identifier l'adresse IP du bridge Docker :**

```bash
ip addr show docker0 | grep inet
# Résultat typique : inet 172.17.0.1/16
```

**2. Modifier la configuration MongoDB :**

Éditez `/etc/mongod.conf` :

```yaml
net:
  port: 27017
  bindIp: 127.0.0.1,172.17.0.1  # Ajouter l'IP du bridge Docker
```

Ou pour accepter toutes les connexions (moins sécurisé) :

```yaml
net:
  port: 27017
  bindIp: 0.0.0.0
```

**3. Redémarrer MongoDB :**

```bash
sudo systemctl restart mongod
```

**4. Vérifier que MongoDB écoute sur la bonne interface :**

```bash
sudo netstat -tulpn | grep 27017
# Devrait montrer : 0.0.0.0:27017 ou 172.17.0.1:27017
```

## 🚀 Utilisation des scripts de test

Deux scripts sont fournis pour faciliter le test local :

### Script 1 : Mode interactif

**Utilisation :**
```bash
./docker/test-local.sh
```

**Caractéristiques :**
- ✅ Pull automatique des derniers changements
- ✅ Build de l'image Docker
- ✅ Nettoyage des anciens conteneurs
- ✅ Lancement en mode interactif
- ✅ Logs affichés en direct dans le terminal
- ⚠️ Terminal bloqué (utiliser Ctrl+C pour arrêter)

**Quand l'utiliser :**
- Pour déboguer et voir les logs en temps réel
- Pour des tests rapides
- Pour développement actif

### Script 2 : Mode détaché (arrière-plan)

**Utilisation :**
```bash
./docker/test-local-detached.sh
```

**Caractéristiques :**
- ✅ Pull automatique des derniers changements
- ✅ Build de l'image Docker
- ✅ Nettoyage des anciens conteneurs
- ✅ Lancement en arrière-plan
- ✅ Terminal libre pour d'autres commandes
- ✅ Affiche les commandes utiles après le lancement

**Quand l'utiliser :**
- Pour laisser l'application tourner pendant que vous travaillez
- Pour des tests de longue durée
- Pour simuler un environnement de production

## 📊 Gestion du conteneur

### Voir les logs

```bash
# Logs en temps réel
docker logs -f lmelp-local

# Dernières 50 lignes
docker logs --tail 50 lmelp-local

# Logs depuis les 10 dernières minutes
docker logs --since 10m lmelp-local
```

### Arrêter le conteneur

```bash
# Arrêt propre
docker stop lmelp-local

# Arrêt forcé et suppression
docker rm -f lmelp-local
```

### Redémarrer le conteneur

```bash
docker restart lmelp-local
```

### Voir le statut

```bash
# Voir tous les conteneurs lmelp
docker ps -a | grep lmelp

# Voir les conteneurs en cours d'exécution
docker ps | grep lmelp
```

### Accéder au shell du conteneur

```bash
docker exec -it lmelp-local bash
```

## 🌐 Accès à l'interface web

Une fois le conteneur lancé :

**URL :** http://localhost:8501

L'application Streamlit est accessible sur le port 8501 de votre machine hôte.

## ⚙️ Configuration

Les scripts configurent automatiquement :

| Variable | Valeur | Description |
|----------|--------|-------------|
| `DB_HOST` | `172.17.0.1` | Adresse du bridge Docker pour accéder au MongoDB du hôte |
| `DB_NAME` | `masque_et_la_plume` | Nom de la base de données |
| `DB_LOGS` | `true` | Active les logs MongoDB |
| Port | `8501:8501` | Port de l'interface web |

## 🐛 Dépannage

### Erreur : "Connection refused" (MongoDB)

**Symptôme :**
```
ServerSelectionTimeoutError: 172.17.0.1:27017: [Errno 111] Connection refused
```

**Solutions :**

1. **Vérifier que MongoDB tourne :**
   ```bash
   sudo systemctl status mongod
   ```

2. **Vérifier la configuration bindIp :**
   ```bash
   grep bindIp /etc/mongod.conf
   # Devrait montrer : bindIp: 0.0.0.0 ou bindIp: 127.0.0.1,172.17.0.1
   ```

3. **Vérifier que MongoDB écoute sur la bonne interface :**
   ```bash
   sudo netstat -tulpn | grep 27017
   ```

4. **Redémarrer MongoDB après changement de config :**
   ```bash
   sudo systemctl restart mongod
   ```

### Erreur : "port is already allocated"

**Symptôme :**
```
Error: Bind for 0.0.0.0:8501 failed: port is already allocated
```

**Solutions :**

1. **Vérifier si un conteneur utilise déjà le port :**
   ```bash
   docker ps | grep 8501
   ```

2. **Arrêter l'ancien conteneur :**
   ```bash
   docker stop lmelp-local
   ```

3. **Ou utiliser un port différent :**
   ```bash
   docker run -d --name lmelp-local -p 8502:8501 \
     -e DB_HOST=172.17.0.1 -e DB_NAME=masque_et_la_plume \
     lmelp:local
   # Accès sur http://localhost:8502
   ```

### Erreur : "locale.Error: unsupported locale setting"

**Symptôme :**
```
locale.Error: unsupported locale setting (fr_FR.UTF-8)
```

**Solution :**
Ce problème est déjà corrigé dans le Dockerfile. Si vous le rencontrez :
1. Assurez-vous d'utiliser la dernière version de l'image
2. Rebuild l'image : `docker build -f docker/Dockerfile -t lmelp:local .`

### L'interface web ne charge pas

**Solutions :**

1. **Vérifier que le conteneur tourne :**
   ```bash
   docker ps | grep lmelp-local
   ```

2. **Voir les logs pour erreurs :**
   ```bash
   docker logs lmelp-local
   ```

3. **Vérifier le port mapping :**
   ```bash
   docker port lmelp-local
   # Devrait montrer : 8501/tcp -> 0.0.0.0:8501
   ```

## 🔄 Workflow de développement

### 1. Développement avec rebuild automatique

```bash
# Terminal 1 : Lancer en mode détaché
./docker/test-local-detached.sh

# Terminal 2 : Voir les logs
docker logs -f lmelp-local

# Après modifications du code :
# Stopper, rebuild et relancer
docker stop lmelp-local
./docker/test-local-detached.sh
```

### 2. Tests rapides

```bash
# Mode interactif pour voir les erreurs directement
./docker/test-local.sh

# Ctrl+C pour arrêter
# Modifier le code
# Relancer
./docker/test-local.sh
```

## 📝 Notes importantes

1. **Pull automatique** : Les scripts font automatiquement un `git pull` avant le build. Assurez-vous d'avoir commité vos changements locaux.

2. **Nettoyage** : Les scripts arrêtent et suppriment automatiquement les anciens conteneurs `lmelp` avant de lancer le nouveau.

3. **Image locale** : Les scripts créent une image nommée `lmelp:local` qui reste sur votre machine. Pour la supprimer :
   ```bash
   docker rmi lmelp:local
   ```

4. **Données persistantes** : Les conteneurs n'ont pas de volumes montés pour les données. Les données sont stockées dans MongoDB sur le hôte.

## 🔗 Voir aussi

- [Configuration Docker complète](./issue-dockerisation.md) - Plan de dockerisation complet
- [Configuration GitHub Actions](./github-actions-setup.md) - CI/CD et déploiement automatisé
- [README Docker](../../docker/README.md) - Documentation technique Docker
