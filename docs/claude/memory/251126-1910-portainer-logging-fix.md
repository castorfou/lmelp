# Fix Portainer Logging Issues - Issue #83

**Date:** 2025-11-26 19:10
**Issue:** #83 - portainer - pas de log d'activite
**Branch:** 83-portainer-pas-de-log-dactivite

## Problème Initial

Les logs Portainer pour le conteneur lmelp présentaient deux problèmes :

1. **Affichage bizarre** : Caractère `^A` suivi de `b` dans les logs
2. **Absence de logs d'activité HTTP** : Contrairement à backoffice-frontend qui affiche des logs HTTP détaillés

### Logs avant correction
```
==================================
lmelp - Le Masque et la Plume
^Ab
==================================
Starting Streamlit web interface...
```

## Analyse du Problème

### Problème 1 : Caractères bizarres
- Le caractère `^A` (ASCII 0x01) est un caractère de contrôle terminal
- Causé par la bannière multi-lignes répétitive dans `entrypoint.sh`
- Les lignes avec beaucoup de `=` créent du bruit visuel

### Problème 2 : Absence de logs HTTP
- **Streamlit ne supporte PAS nativement le logging des requêtes HTTP**
- Contrairement à nginx/apache qui loggent chaque requête (GET, POST, status, IP, etc.)
- Les options de logging Streamlit concernent les logs internes de l'application, pas les requêtes HTTP
- Pour avoir de vrais logs HTTP, il faudrait un reverse proxy nginx (hors scope de cette issue)

## Solution Implémentée

### 1. Simplification du Banner de Démarrage

**Fichier modifié:** `docker/build/entrypoint.sh`

```bash
# AVANT
echo "=================================="
echo "lmelp - Le Masque et la Plume"
echo "Mode: $MODE"
echo "=================================="

# APRÈS
echo "[lmelp] Starting in $MODE mode..."
```

**Bénéfices:**
- Banner court et informatif
- Élimine les caractères de contrôle
- Format cohérent avec les standards de logging

### 2. Configuration Streamlit pour Logs Propres

**Nouveau fichier:** `.streamlit/config.toml`

```toml
[server]
port = 8501
address = "0.0.0.0"
headless = true
enableCORS = true
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[logger]
level = "info"
messageFormat = "%(asctime)s - %(levelname)s - %(message)s"

[theme]
base = "light"
primaryColor = "#FF4B4B"
```

**Points clés:**
- `enableCORS = true` requis si `enableXsrfProtection = true`
- Suppression de `enableClientLogs` (option invalide dans versions récentes)
- Format de log avec timestamp pour meilleure traçabilité

### 3. Ajout de l'Option Logger dans Entrypoint

```bash
exec streamlit run ui/lmelp.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --logger.level=info  # ← Ajouté
```

### 4. Copie de la Configuration dans Docker

**Fichier modifié:** `docker/build/Dockerfile`

```dockerfile
# Copy application code
COPY nbs/ /app/nbs/
COPY ui/ /app/ui/
COPY scripts/ /app/scripts/
COPY .streamlit/ /app/.streamlit/  # ← Ajouté
```

## Tests Ajoutés

**Nouveau fichier:** `tests/integration/test_streamlit_config.py`

**8 tests ajoutés:**
1. `test_streamlit_config_file_exists` - Vérifie présence du fichier
2. `test_streamlit_config_contains_logging_settings` - Valide les sections logger, server, browser
3. `test_streamlit_config_message_format` - Vérifie format avec timestamp/level/message
4. `test_entrypoint_exists` - Vérifie présence du script
5. `test_entrypoint_simplified_banner` - Valide le nouveau banner
6. `test_entrypoint_logger_level_option` - Vérifie l'option --logger.level=info
7. `test_dockerfile_exists` - Vérifie présence du Dockerfile
8. `test_dockerfile_copies_streamlit_config` - Valide la copie de .streamlit/

**Résultats:**
- ✅ 8/8 tests passent
- ✅ Suite complète : 296/296 tests passent
- ✅ Black formatting OK
- ✅ Mypy typecheck OK

## Résultats Après Correction

### Logs de démarrage propres
```
[lmelp] Starting in web mode...

  You can now view your Streamlit app in your browser.

  URL: http://0.0.0.0:8501
```

### Ce qui sera visible dans Portainer
✅ Logs de démarrage propres (sans `^A` + `b`)
✅ Logs d'erreurs applicatives Streamlit
✅ Logs de santé du healthcheck Docker
✅ Logs applicatifs (print, logging Python)

### Ce qui NE sera PAS visible
❌ Logs de requêtes HTTP individuelles (GET /, POST /api/..., status codes)

**Raison:** Limitation native de Streamlit - nécessiterait un reverse proxy nginx pour avoir ces logs

## Fichiers Modifiés

1. `.streamlit/config.toml` (nouveau)
2. `docker/build/entrypoint.sh`
3. `docker/build/Dockerfile`
4. `tests/integration/test_streamlit_config.py` (nouveau)

## Apprentissages Clés

### Limitation Streamlit
- **Streamlit n'est pas un serveur web classique** - il ne loggue pas les requêtes HTTP
- Les options de logging Streamlit concernent uniquement les logs internes de l'application
- Pour du monitoring HTTP détaillé, il faut une couche supplémentaire (nginx, middleware custom)

### Configuration CORS
- `enableCORS` doit être `true` si `enableXsrfProtection` est `true`
- Streamlit force cette contrainte pour la sécurité (protection CSRF via cookies)

### Options de Configuration Streamlit
- `logger.enableClientLogs` n'existe plus dans les versions récentes
- Toujours vérifier la documentation de la version utilisée

### Docker Entrypoint Best Practices
- Bannières courtes et informatives
- Format `[service] Action...` est standard
- Éviter les caractères de contrôle qui peuvent être mal interprétés par les viewers de logs

## Recommandations Futures

### Pour de vrais logs HTTP
Si besoin absolu de logs HTTP style nginx, créer une nouvelle issue pour :
- Ajouter nginx comme reverse proxy devant Streamlit
- Configurer nginx pour logger les requêtes (format combined)
- Modifier docker-compose pour inclure nginx

### Monitoring Alternatif
Alternatives à considérer :
- Utiliser le healthcheck Docker (`/_stcore/health`) pour monitoring uptime
- Logger les actions utilisateur dans l'application Streamlit elle-même
- Utiliser un APM (Application Performance Monitoring) comme Datadog, New Relic

## Commandes de Validation

```bash
# Tester localement
./ui/lmelp_ui.sh

# Tester l'entrypoint Docker
bash docker/build/entrypoint.sh

# Lancer les tests
PYTHONPATH=/workspaces/lmelp/src uv run pytest tests/integration/test_streamlit_config.py -v

# Build et test Docker
docker build -t lmelp:test -f docker/build/Dockerfile .
docker run -p 8501:8501 -e DB_HOST=172.17.0.1 lmelp:test
```

## Conclusion

✅ **Problème 1 résolu** : Banner propre, pas de caractères bizarres
⚠️ **Problème 2 partiellement résolu** : Logs Streamlit propres, mais pas de logs HTTP (limitation native)

L'issue #83 est considérée comme résolue pour le scope initial (banner et logs visibles). Les logs HTTP détaillés nécessiteraient une architecture différente (reverse proxy) et devraient faire l'objet d'une issue séparée si requis.
