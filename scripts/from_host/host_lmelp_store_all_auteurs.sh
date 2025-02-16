#!/bin/bash

# Stocker les arguments dans un tableau
args=("$@")

# check arguments, valid ones are -v or --verbose, -d or --date, -h or --help and they are optional
while [ "$1" != "" ]; do
    case $1 in
        -v | --verbose )        shift
                                verbose=1
                                ;;
        -d | --date )           shift
                                date=$1
                                ;;
        -h | --help )           echo "Usage: $(basename "$0") [-v | --verbose] [-d | --date dd/mm/yyyy]"
                                exit
                                ;;
        * )                     echo "Usage: $(basename "$0") [-v | --verbose] [-d | --date dd/mm/yyyy]"
                                exit 1
    esac
    shift
done

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
docker exec -u vscode "$container" /workspaces/lmelp/scripts/lmelp_store_all_auteurs.sh "${args[@]}"