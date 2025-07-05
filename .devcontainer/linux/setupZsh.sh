#!/bin/bash

cd ~
rm -rf .oh-my-zsh

sudo apt install -y fonts-powerline

sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.2.1/zsh-in-docker.sh)" -- \
    -p git \
    -p python \
    -p history \
    -p virtualenv \
    -p 'history-substring-search' \
    -p https://github.com/zsh-users/zsh-autosuggestions \
    -p https://github.com/zsh-users/zsh-completions
echo '[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh' >> .zshrc
cp /workspaces/lmelp/.devcontainer/.p10k.zsh ~/.p10k.zsh
# exec zsh