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

source ~/git/lmelp/scripts/from_host/get_container.sh

container=$(get_container)
echo "Using container: $container"

# Execute the UI script in the found container as the user vscode.
docker exec -u vscode "$container" /workspaces/lmelp/scripts/lmelp_store_all_auteurs.sh "${args[@]}"