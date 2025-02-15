#!/bin/bash 

# Search for the container with the matching CONTAINER_NAME environment variable.
container=$(for id in $(docker ps -q); do
    if docker inspect --format='{{range .Config.Env}}{{println .}}{{end}}' "$id" | grep -q "CONTAINER_NAME=vscode-dev-container-lmelp"; then
        docker inspect --format='{{.Name}}' "$id" | cut -d'/' -f2
        break
    fi
done)

# Check if a container was found.
if [ -z "$container" ]; then
    echo "No container found with CONTAINER_NAME=vscode-dev-container-lmelp"
    exit 1
fi

echo "Using container: $container"

# Execute the UI script in the found container as the user vscode.
docker exec -u vscode "$container" /workspaces/lmelp/scripts/lmelp_store_all_auteurs.sh