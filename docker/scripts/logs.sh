#!/bin/bash
# View lmelp Docker container logs

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$(dirname "$SCRIPT_DIR")"

cd "$DOCKER_DIR"

# If argument provided, show logs for specific service
if [ -n "$1" ]; then
    echo "Showing logs for service: $1"
    docker compose logs -f "$1"
else
    echo "Showing logs for all services (use Ctrl+C to exit)"
    docker compose logs -f
fi
