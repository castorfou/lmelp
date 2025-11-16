#!/bin/bash
# Update lmelp Docker containers to latest version

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$(dirname "$SCRIPT_DIR")"

cd "$DOCKER_DIR"

echo "Pulling latest lmelp image..."
docker compose pull

echo ""
echo "Restarting containers with new image..."
docker compose up -d

echo ""
echo "✅ Update complete!"
echo ""
echo "Access the application at: http://localhost:8501"
