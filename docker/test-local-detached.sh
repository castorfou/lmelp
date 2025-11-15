#!/bin/bash
set -e

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  lmelp - Script de test local Docker (détaché)${NC}"
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

# 3. Arrêt des conteneurs existants (si présents)
echo -e "${YELLOW}[*]${NC} Arrêt des conteneurs lmelp existants..."
docker ps -a | grep lmelp | awk '{print $1}' | xargs -r docker stop 2>/dev/null || true
docker ps -a | grep lmelp | awk '{print $1}' | xargs -r docker rm 2>/dev/null || true
echo ""

# 4. Lancement du nouveau conteneur en arrière-plan
echo -e "${GREEN}[3/3]${NC} Lancement du conteneur en arrière-plan..."
echo -e "${YELLOW}Configuration:${NC}"
echo -e "  - DB_HOST: 172.17.0.1"
echo -e "  - DB_NAME: masque_et_la_plume"
echo -e "  - Port: 8501 → 8501"
echo ""

docker run -d \
  --name lmelp-local \
  -p 8501:8501 \
  -e DB_HOST=172.17.0.1 \
  -e DB_NAME=masque_et_la_plume \
  -e DB_LOGS=true \
  lmelp:local

echo ""
echo -e "${GREEN}✓${NC} Conteneur lancé avec succès !"
echo ""
echo -e "${YELLOW}Commandes utiles:${NC}"
echo -e "  - Voir les logs:    ${BLUE}docker logs -f lmelp-local${NC}"
echo -e "  - Arrêter:          ${BLUE}docker stop lmelp-local${NC}"
echo -e "  - Supprimer:        ${BLUE}docker rm lmelp-local${NC}"
echo -e "  - Interface web:    ${BLUE}http://localhost:8501${NC}"
echo ""
