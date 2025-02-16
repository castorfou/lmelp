#!/bin/bash 

source ~/git/lmelp/scripts/from_host/get_container.sh

container=$(get_container)
echo "Using container: $container"

# Execute the UI script in the found container as the user vscode.
docker exec -u vscode "$container" /workspaces/lmelp/scripts/lmelp_get_one_transcription.sh