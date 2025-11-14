#!/bin/bash
# Start lmelp Docker containers

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$(dirname "$SCRIPT_DIR")"

cd "$DOCKER_DIR"

echo "Starting lmelp containers..."
docker compose up -d

echo ""
echo "✅ Containers started!"
echo ""
echo "Access the application at: http://localhost:8501"
echo ""
echo "Use './scripts/logs.sh' to view logs"
echo "Use './scripts/stop.sh' to stop containers"
