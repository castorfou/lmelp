#!/bin/bash
# =============================================================================
# lmelp - Script de démarrage du devcontainer (postStartCommand)
# Exécuté à chaque démarrage du container (contexte interactif)
# =============================================================================

echo "🚀 lmelp - Environnement prêt!"
echo ""

# Vérification de l'authentification GitHub
if command -v gh &>/dev/null; then
    if gh auth status &>/dev/null; then
        echo "✅ GitHub : authentifié ($(gh auth status 2>&1 | grep 'Logged in' | sed 's/.*Logged in to //'))"
    else
        echo "⚠️  GitHub : non authentifié"
        echo "   → Lancez : gh auth login --git-protocol https --web"
    fi
fi
