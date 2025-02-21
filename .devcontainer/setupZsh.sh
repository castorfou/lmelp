#!/bin/bash

cd ~
rm -rf .oh-my-zsh

sudo apt install -y fonts-powerline

sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.2.1/zsh-in-docker.sh)" -- \
    -p git \
    -p ssh-agent \
    -p 'history-substring-search' \
    -p https://github.com/zsh-users/zsh-autosuggestions \
    -p https://github.com/zsh-users/zsh-completions
echo '[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh' >> .zshrc
# wget https://raw.githubusercontent.com/castorfou/dotfiles/refs/heads/framework/home/guillaume/.p10k.sh -O .p10k.zsh
wget https://raw.githubusercontent.com/chbroecker/dotfiles/main/zsh/.p10k.zsh -O .p10k.zsh
exec zsh