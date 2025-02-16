#!/bin/bash
get_container() {
    container=$(for id in $(docker ps -q); do
        if docker inspect --format='{{range .Config.Env}}{{println .}}{{end}}' "$id" | grep -q "CONTAINER_NAME=vscode-dev-container-lmelp"; then
            docker inspect --format='{{.Name}}' "$id" | cut -d'/' -f2
            break
        fi
    done)
    
    if [ -z "$container" ]; then
        echo "No container found with CONTAINER_NAME=vscode-dev-container-lmelp" >&2
        exit 1
    fi
    echo "$container"
}