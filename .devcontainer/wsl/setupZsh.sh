#!/bin/bash

# Charger le fichier repo_name.env depuis le répertoire parent du script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../repo_name.env"

cd ~
rm -rf .oh-my-zsh

apt install -y fonts-powerline

# get last version at https://github.com/deluan/zsh-in-docker
sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.2.1/zsh-in-docker.sh)" -- \
    -p git \
    -p python \
    -p history \
    -p 'history-substring-search' \
    -p https://github.com/zsh-users/zsh-autosuggestions \
    -p https://github.com/zsh-users/zsh-completions
echo '[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh' >> ~/.zshrc

cp /workspaces/${REPO_NAME}/.devcontainer/.p10k.zsh ~/.p10k.zsh

echo 'exec zsh' >> ~/.bashrc