#!/bin/bash
set -e

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  lmelp - Script de test local Docker${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo ""

# 1. Pull des derniers changements
echo -e "${GREEN}[1/3]${NC} Récupération des derniers changements..."
git pull origin claude/review-code-01JpacPfALVvwqPorZfNeX6c
echo ""

# 2. Build du conteneur
echo -e "${GREEN}[2/3]${NC} Construction de l'image Docker..."
docker build -f docker/Dockerfile -t lmelp:local .
echo ""

# 3. Arrêt des conteneurs existants (si présents, sauf devcontainer)
echo -e "${YELLOW}[*]${NC} Arrêt des conteneurs lmelp existants..."
docker ps -a | grep lmelp | grep -v vsc-lmelp | awk '{print $1}' | xargs -r docker stop 2>/dev/null || true
docker ps -a | grep lmelp | grep -v vsc-lmelp | awk '{print $1}' | xargs -r docker rm 2>/dev/null || true
echo ""

# 4. Lancement du nouveau conteneur
echo -e "${GREEN}[3/3]${NC} Lancement du conteneur..."
echo -e "${YELLOW}Configuration:${NC}"
echo -e "  - DB_HOST: 172.17.0.1"
echo -e "  - DB_NAME: masque_et_la_plume"
echo -e "  - Port: 8502 → 8501 (pour éviter conflit avec devcontainer)"
echo ""

docker run --rm -it \
  --name lmelp-local \
  -p 8502:8501 \
  -e DB_HOST=172.17.0.1 \
  -e DB_NAME=masque_et_la_plume \
  -e DB_LOGS=true \
  lmelp:local

echo ""
echo -e "${GREEN}✓${NC} Conteneur arrêté"
echo -e "${YELLOW}Info:${NC} L'interface était accessible sur ${BLUE}http://localhost:8502${NC}"

# Note: Le script s'arrête ici car docker run est en mode interactif
# Pour arrêter: Ctrl+C
